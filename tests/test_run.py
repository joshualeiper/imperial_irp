from phreeqpython import PhreeqPython

pp = PhreeqPython('/home/jjl122/repos/irp-jjl122/master_database.dat')
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
