import pytest
from unittest.mock import patch
import importlib.resources as pkg_resources
import master_database.parser_dat as par


class TestPhreeqcParsers:

    @pytest.fixture(autouse=True)
    def setup(self):
        with pkg_resources.files('tests.testing_databases').joinpath('test_database.dat').open('r') as data_file:
            self.data_path = data_file.name
            soln_parser = par.SolutionParser(self.data_path)
            self.soln_df = soln_parser.parse_file()

        with pkg_resources.files('tests.testing_databases').joinpath('test_database_1.dat').open('r') as master_file_1:
            self.master_file_path_1 = master_file_1.name
            self.sms_parser = par.MasterSolutionParser(self.data_path)
            self.sms_df = self.sms_parser.data_frame

    def test_soln_shape(self):
        assert self.soln_df.shape == (11, 15), f"Expected shape (7, 15), but got {self.soln_df.shape}"

    def test_soln_columns(self):
        assert 'equation' in self.soln_df.columns, "Expected column 'equation' not found"

    def test_soln_first_row(self):
        assert self.soln_df.iloc[0, 0] == 'HAcetate =  11.0000HAcetate', "Unexpected equation in first row"
        print(self.soln_df.columns)

    def test_vm_parse(self):
        assert self.soln_df['v_m'].notna().any(), "No 'vm' values found"

    def test_sms_shape(self):
        print(self.sms_df.isnull().sum())
        assert self.sms_df.shape == (28, 6), f"Expected shape (7, 6), but got {self.sms_df.shape}"

    def test_sms_columns(self):
        assert 'species' in self.sms_df.columns, "Expected column 'species' not found"

    def test_sms_first_row(self):
        assert self.sms_df.iloc[0, 0] == 'Fe', "Unexpected species in first row"

    def test_combined_master_solution_parser(self):
        parser1 = par.MasterSolutionParser(self.master_file_path_1)
        combined_result = parser1 + self.sms_parser
        combined_result = combined_result.data_frame

        assert combined_result.shape == (30, 6), f"Expected shape (30, 6), but got {combined_result.shape}"
        assert 'element' in combined_result.columns, "Expected column 'element' not found"
        assert combined_result['species'].notna().all(), "Some 'species' values are NaN"
        assert combined_result['source'].nunique() == 2, "Expected 2 unique sources in combined DataFrame"


def test_file_name():
    valid_file_path = "/home/user/documents/file.txt"
    with patch("os.path.isfile", return_value=True):
        assert par.file_name(valid_file_path) == "file.txt"

    invalid_file_path = "/non/existent/path/file.txt"
    with patch("os.path.isfile", return_value=False):
        with pytest.raises(FileNotFoundError) as excinfo:
            par.file_name(invalid_file_path)
        assert str(excinfo.value) == f"File {invalid_file_path} not found"
