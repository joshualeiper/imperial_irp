import os
from phreeqpython import PhreeqPython
from master_database.__main__ import main

main()

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the directory above the current one
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Define the file name you're looking for
file_name = 'master_database.dat'

# Create the full path to the file
file_path = os.path.join(parent_dir, file_name)


def test_file_exists():
    assert os.path.exists(file_path), f"File {file_path} not found"


pp = PhreeqPython(file_path)
sol = {
    'pH': 3.0,
    'Cl': 0.02,
    'Na': 0.02,
    'Ni': 0.00001,
    'Citrate': 0.00001,
    'Dfoba': 0.00001,
    'Dma': 0.00001,
    'Dmaoh': 0.00001,
    'Malate': 0.00001,
    'Co': 0.000001,
    'Cu': 0.000001,
    'Fe': 0.000001,
    'Zn': 0.000001,
    'units': 'mol/kgw',
    'pe': 5.92,
    'temperature': 25
}


def test_add_solution():
    try:
        pp.add_solution(sol)
        assert True
    except Exception as e:
        assert False, e
