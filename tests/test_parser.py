import pytest
from master_database.parser_dat import SolutionParser, MasterSolutionParser, phreeqc_database_list


class TestPhreeqcParsers:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup code for initializing file paths
        self.data_path = 'tests/test_database.dat'
        self.master_file_path_1 = 'tests/test_database_1.dat'
        soln_parser = SolutionParser(self.data_path)
        self.soln_df = soln_parser.parse_file()
        self.sms_parser = MasterSolutionParser(self.data_path)
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
        parser1 = MasterSolutionParser(self.master_file_path_1)
        combined_result = parser1 + self.sms_parser
        combined_result = combined_result.data_frame

        assert combined_result.shape == (30, 6), f"Expected shape (30, 6), but got {combined_result.shape}"
        assert 'element' in combined_result.columns, "Expected column 'element' not found"
        assert combined_result['species'].notna().all(), "Some 'species' values are NaN"
        assert combined_result['source'].nunique() == 2, "Expected 2 unique sources in combined DataFrame"

    def test_phreeqc_database_warning(self):
        with pytest.warns(UserWarning):
            phreeqc_database_list('tests')
