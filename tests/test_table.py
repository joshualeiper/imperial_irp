import pytest
import os
import numpy as np
import pandas as pd
import master_database.compile_tables as ct

current_dir = os.path.dirname(os.path.abspath(__file__))

DB_LIST = ['test_database.dat', 'test_database_1.dat']
DB_LIST = [os.path.join(current_dir, x) for x in DB_LIST]


class TestSmsTable:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = ct.compile_master_solution_table(DB_LIST)

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


class TestSolutionTable:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = ct.compile_solution_species_table(DB_LIST)

    def test_log_k(self):
        assert self.result['log_k'].dtype == float
        assert self.result['log_k'].notna().all()

    def test_check_floats(self):
        # Ensure 1.0000 is not present
        print(self.result['equation'].head(10))
        assert not self.result['equation'].str.contains('1.0000').all()
        # Make sure 11.0000 -> 11
        assert self.result['equation'].str.contains(r"11(?!.\.)[ ]?[a-zA-Z]").any()
        assert not self.result['equation'].str.contains(r"\b11\.000\b").any()

    def test_ions(self):
        assert not self.result['equation'].str.contains(r"----").any(), "---- not converted to -4"
        assert not self.result['equation'].str.contains(r"---").any(), "--- not converted to -3"
        assert not self.result['equation'].str.contains(r"--").any(), "-- not converted to -2"
        assert self.result['equation'].str.contains(r"-4").any(), "Converstion failed"
        assert self.result['equation'].str.contains(r"-3").any(), "Converstion failed"
        assert self.result['equation'].str.contains(r"-2").any(), "Converstion failed"


def clean_function_test(prefix, clean_function, sample_tuples, expected_answer):
    for i, sample in enumerate(sample_tuples):
        cleaned_sample = clean_function(sample)
        assert isinstance(cleaned_sample, tuple), f"Test case {i}: Expected tuple, but got {type(cleaned_sample)}"
        long_message = f"Test case {i}: Expected '{prefix}' to be removed, but got {cleaned_sample}"
        assert prefix.lower() not in cleaned_sample, long_message
        long_message = f"Test case {i}: Expected all floats, but got {[type(item) for item in cleaned_sample]}"
        assert all(isinstance(item, float) for item in cleaned_sample), long_message
        assert cleaned_sample == expected_answer, f"Test case {i}: Expected {expected_answer}, but got {cleaned_sample}"


class TestExpandTC:

    def test_expand_tc_basic_case(self):
        row = pd.Series({'t_c': ['25.0', 'P_c', '101.3', 'Omega', '0.8']})
        expected = pd.Series({'t_c': 25.0, 'p_c': 101.3, 'omega': 0.8})
        result = ct.expand_tc(row)

        for key in ['t_c', 'p_c', 'omega']:
            assert isinstance(result[key], float), f"Expected {key} to be of type float, but got {type(result[key])}"
            assert result[key] == expected[key], f"Expected {key} to be {expected[key]}, but got {result[key]}"

    def test_expand_tc_tc_and_pc_only(self):
        row = pd.Series({'t_c': ['25.0', 'P_c', '101.3']})
        expected = pd.Series({'t_c': 25.0, 'p_c': 101.3, 'omega': np.nan})
        result = ct.expand_tc(row)

        for key in ['t_c', 'p_c']:
            assert isinstance(result[key], float), f"Expected {key} to be of type float, but got {type(result[key])}"
            assert result[key] == expected[key], f"Expected {key} to be {expected[key]}, but got {result[key]}"
        assert np.isnan(result['omega']), f"Expected omega to be NaN, but got {result['omega']}"

    def test_expand_tc_tc_and_omega_only(self):
        row = pd.Series({'t_c': ['25.0', 'Omega', '0.8']})
        expected = pd.Series({'t_c': 25.0, 'p_c': np.nan, 'omega': 0.8})
        result = ct.expand_tc(row)

        for key in ['t_c', 'omega']:
            assert isinstance(result[key], float), f"Expected {key} to be of type float, but got {type(result[key])}"
            assert result[key] == expected[key], f"Expected {key} to be {expected[key]}, but got {result[key]}"
        assert np.isnan(result['p_c']), f"Expected p_c to be NaN, but got {result['p_c']}"

    def test_expand_tc_empty_list(self):
        row = pd.Series({'t_c': []})
        result = ct.expand_tc(row)

        for key in ['t_c', 'p_c', 'omega']:
            assert np.isnan(result[key]), f"Expected {key} to be NaN, but got {result[key]}"

    def test_expand_tc_mixed_noise_data(self):
        row = pd.Series({'t_c': ['25.0', 'Noise', 'P_c', '101.3', 'Random', 'Omega', '0.8', 'Extra']})
        expected = pd.Series({'t_c': 25.0, 'p_c': 101.3, 'omega': 0.8})
        result = ct.expand_tc(row)

        for key in ['t_c', 'p_c', 'omega']:
            assert isinstance(result[key], float), f"Expected {key} to be of type float, but got {type(result[key])}"
            assert result[key] == expected[key], f"Expected {key} to be {expected[key]}, but got {result[key]}"


def test_clean_vm():
    vm_samples = [
        ('-Vm', '-9.66', '28.5', '80.0', '-22.9', '1.89', '0', '1.09', '0', '0', '1'),
        ('vm', '-9.66', 28.5, '80.0', '-22.9', '1.89', '0', '1.09', '0', '0', '1'),
        ('Vm', '-9.66', '28.5', '80.0', '-22.9', '1.89', '0', '1.09', '0', '0', '1'),
        ('-9.66', '28.5', '80.0', '-22.9', '1.89', '0', '1.09', '0', '0', '1')
    ]
    vm_expected_answer = (-9.66, 28.5, 80.0, -22.9, 1.89, 0, 1.09, 0, 0, 1)

    clean_function_test('vm', ct.clean_vm, vm_samples, vm_expected_answer)


def test_clean_dw():
    dw_samples = [
        ('-dw', '0.955e-9', '0', '1.12', '2.84'),
        ('dw', '0.955e-9', '0', 1.12, '2.84'),
        ('-Dw', '0.955e-9', '0', '1.12', '2.84'),
        ('0.955e-9', '0', '1.12', '2.84')
    ]
    dw_expected_answer = (0.955e-9, 0, 1.12, 2.84)

    clean_function_test('dw', ct.clean_dw, dw_samples, dw_expected_answer)


def test_strfloat_to_stringint_():
    data = pd.Series(['5.0000', '789.000', '1000.0000 '])
    expected = pd.Series(['5', '789', '1000'])
    result = ct.strfloat_to_stringint(data)
    pd.testing.assert_series_equal(result, expected)
