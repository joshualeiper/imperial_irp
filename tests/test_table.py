import pytest

from master_database.compile_tables import compile_master_solution_table
from master_database.parser_dat import MasterSolutionParser


class TestSmsTable:

    @pytest.fixture(autouse=True)
    def setup(self):
        db_list = ['tests/test_database.dat', 'tests/test_database_1.dat']
        self.result = compile_master_solution_table(db_list)

    def test_sms_shape(self):
        # Should have one duplicate row
        assert self.result.shape == (30-1, 6), f"Expected shape (30, 6), but got {self.result.shape}"
    def test_replace_elements(self):
        assert not self.result['element'].str.match(r'U[(]\d[)]').any()
        assert self.result['element'].str.match(r"U\(\+\d\)").sum() == 3
    def test_alk_type(self):
        assert self.result['alk'].dtype == float
    def test_source(self):
        assert self.result['source'].nunique() == 2
        assert self.result['source'].str.contains('#').all()