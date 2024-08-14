import os
import pandas as pd
from phreeqpython import PhreeqPython
from master_database.__main__ import main

main()


def get_database_path(db_name: str) -> str:
    """PHREEQCPython requires the full path to the database.
    This function returns the full path to the database."""

    if not db_name.endswith('.dat'):
        db_name += '.dat'

    current_dir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.exists(os.path.join(current_dir, 'testing_databases')):
        raise FileNotFoundError("The testing_databases folder does not exist")
    try:
        return os.path.join(current_dir, 'testing_databases', db_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"The database {db_name} does not exist in the testing_databases folder")


def test_file_exists():
    # Get the current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the directory above the current one
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

    # Define the file name you're looking for
    file_name = 'master_database.dat'

    # Create the full path to the file
    file_path = os.path.join(parent_dir, file_name)
    assert os.path.exists(file_path), f"File {file_path} not found"


def test_add_solution():
    """Tests if the database compiles"""
    db = get_database_path('master_database')
    pp = PhreeqPython(db)
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
    db = get_database_path('llnl')
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
