import numpy as np
from esrpoise import round2tol_str


def test_round2tol_str():
    values_from_optimizer = np.array([12.10052498,
                                      251.0000003,
                                      86, 3.2600446,
                                      3511.05000526,
                                      0.456829])
    tols = [2, 4, 10, 0.2, 0.1, 0.005]
    expected_rounded_values = ['12', '252', '90', '3.2', '3511.1', '0.455']
    rounded_values = round2tol_str(values_from_optimizer, tols)
    assert rounded_values == expected_rounded_values

    value_list = [56.05648946581]
    tol = [0.04]
    expected_rounded_value = ['56.04']
    rounded_value = round2tol_str(value_list, tol)
    assert rounded_value == expected_rounded_value
