import pandas as pd
from io import StringIO
from master_database.compile_file import write_tuple, write_mst, write_sp


def test_write_tuple():
    att = "test_attribute"
    value = (1, 2, 3)
    file = StringIO()

    write_tuple(att, value, file)

    file.seek(0)
    result = file.read()
    assert result == "\ttest_attribute\t1 2 3 \n"


def test_write_mst():
    row = pd.Series(["a", "b", "c"])
    file = StringIO()

    write_mst(row, file)

    file.seek(0)
    result = file.read()
    assert result == "a\tb\tc\n"


def test_write_sp():
    data = {"equation": "H2O = H+ + OH-", "log_k": -14.0, "delta_h": (0, 0, 1)}
    row = pd.Series(data)
    file = StringIO()

    write_sp(row, file)

    file.seek(0)
    result = file.read()
    expected = "H2O = H+ + OH-\n\tlog_k\t-14.0\n\t-delta_h\t0 0 1 \n"
    assert result == expected
