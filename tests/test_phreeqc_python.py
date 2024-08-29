import os
import pandas as pd
import pytest
import importlib.resources as pkg_resources
from build_database.__main__ import main
from phreeqpython import PhreeqPython
import sys
from unittest.mock import patch


class TestPhreeqPython:
    @pytest.fixture(autouse=True)
    def setup_module(self):
        """Run the main function to create the master database"""
        self.file_dir = os.path.dirname(os.path.abspath(__file__))
        self.master_database_path = os.path.join(self.file_dir, 'master_database.dat')
        print(self.master_database_path)
        test_args = ["__main__.py", "--output", self.master_database_path]
        with patch.object(sys, 'argv', test_args):
            main()

    def test_main(self):
        """Test if master_database.dat is created"""
        assert os.path.exists(self.master_database_path), f"File {self.master_database_path} not found"

    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'

    @pytest.mark.skipif(is_github_actions, reason="Skipping test on GitHub Actions")
    def test_add_solution(self):
        """Tests if the database compiles"""
        self.master_database_path = pkg_resources.files('tests').joinpath('master_database.dat')
        pp = PhreeqPython(self.master_database_path)
        sol = {
            'pH': 3.0,
            'Cl': 0.1,
            'Na': 0.1,
            'As(+5)': 0.00000303,
            'units': 'mol/kgw',
            'temperature': 25,
        }
        try:
            pp.add_solution(sol)
            assert True
        except Exception as e:
            assert False, e


def test_module():
    """Tests if the results from PHREEQCPython are the same as PHREEQC"""
    db = pkg_resources.files('tests.testing_databases').joinpath('PdmaDatabase1.dat')
    pp = PhreeqPython(db)
    sol = {
        'units': 'mol/kgw',
        'pH': 3.0,
        'Cl': 0.02,
        'Na': 0.02,
        'K': 0.02,
        'Pdma': 0.00001,
        'Zn': 0.000001,
        'temperature': 25,
        'pe': 5.92,
    }
    solution = pp.add_solution(sol)
    val = 'ZnPdmaSpeciation.xls'
    val = pkg_resources.files('tests').joinpath(val)
    df_phreeqc = pd.read_csv(val, sep='\t')
    df_phreeqc.columns = [c.replace('m_', '').strip() for c in df_phreeqc.columns]
    df_pyphreeqc = pd.DataFrame(solution.species, index=[0])
    df_val = pd.concat([df_phreeqc, df_pyphreeqc], axis=0)
    df_val = df_val.dropna(axis=1, how='any')
    pd.testing.assert_series_equal(df_val.iloc[0], df_val.iloc[1])


def test_exampls():
    """Tests if the results from PHREEQCPython are the same as PHREEQC"""
    db = pkg_resources.files('build_database.databases').joinpath('llnl.dat')
    pp = PhreeqPython(db)
    val = 'output.xls'
    keep = ['AsO4-3', 'HAsO4-2', 'H2AsO4-', 'H3AsO4']
    val_path = pkg_resources.files('tests').joinpath(val)
    df_val = pd.read_csv(val_path, sep='\t')
    df_val.columns = [c.replace('m_', '').strip() for c in df_val.columns]
    df_val.set_index('pH', inplace=True)
    df_val = df_val[keep]
    result = pd.DataFrame()
    for pH in df_val.index:
        sol = {
            'units': 'mol/kgw',
            'pH': pH,
            'Cl': 0.1,
            'Na': 0.1,
            'As(+5)': 0.0000030,
        }
        solution = pp.add_solution(sol)
        temp_df = pd.DataFrame(solution.species, index=[pH])
        result = pd.concat([result, temp_df])

    result = result[keep]
    result.index.name = 'pH'
    result.head()

    pd.testing.assert_frame_equal(result, df_val)
