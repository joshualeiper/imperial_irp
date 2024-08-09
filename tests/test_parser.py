import pytest
from master_database.parser_dat import SolutionParser, PhaseParser, MasterSolutionParser

class TestPhreeqcParsers:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup code for initializing file paths
        self.data_path = 'tests/test_database.dat'
        self.data_path = 'tests/test_database.dat'
        self.master_file_path_1 = 'tests/test_database_1.dat'
        self.master_file_path_2 = 'tests/test_database_2.dat'
        parser = SolutionParser(self.data_path)
        self.result = parser.parse_file()

    def test_shape(self):
        assert self.result.shape == (7, 15), f"Expected shape (7, 15), but got {self.result.shape}"
    
    def test_columns(self):
        assert 'equation' in self.result.columns, "Expected column 'equation' not found"
    
    def test_first_row(self):
        assert self.result.iloc[0, 0] == 'HAcetate =  HAcetate', "Unexpected equation in first row"
        print(self.result.columns)
    def test_vm_parse(self):
        assert self.result['v_m'].notna().any(), "No 'vm' values found"
"""
    def test_phase_parser(self):
        parser = PhaseParser(self.data_path)
        result = parser.parse_file()

        assert result.shape == (4, 9), f"Expected shape (4, 9), but got {result.shape}"
        assert 'phase_name' in result.columns, "Expected column 'phase_name' not found"
        assert result['log_k'].notna().all(), "Some 'log_k' values are NaN"
        assert result.loc[0, 'phase_name'] == 'H2O', "Unexpected phase name in first row"

    def test_master_solution_parser(self):
        parser = MasterSolutionParser(self.master_file_path)
        result = parser.data_frame

        assert result.shape == (7, 6), f"Expected shape (7, 6), but got {result.shape}"
        assert 'element' in result.columns, "Expected column 'element' not found"
        assert result['species'].notna().all(), "Some 'species' values are NaN"
        assert result.loc[0, 'element'] == 'HAcetate', "Unexpected element in first row"

    def test_combined_master_solution_parser(self):
        parser1 = MasterSolutionParser(self.master_file_path_1)
        parser2 = MasterSolutionParser(self.master_file_path_2)
        combined_result = parser1 + parser2

        assert combined_result.shape == (14, 6), f"Expected shape (14, 6), but got {combined_result.shape}"
        assert 'element' in combined_result.columns, "Expected column 'element' not found"
        assert combined_result['species'].notna().all(), "Some 'species' values are NaN"
        assert combined_result['source'].nunique() == 2, "Expected 2 unique sources in combined DataFrame"
"""

