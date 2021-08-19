import numpy as np
from esrpoise import round2tol


def test_round2tol():
    values_from_optimizer = np.array([12.10052498,
                                      251.0000003,
                                      86, 3.2600446,
                                      3511.05000526,
                                      0.456829])
    tols = [2, 4, 10, 0.2, 0.1, 0.005]
    excepted_rounded_values = ['12', '252', '90', '3.2', '3511.1', '0.455']
    rounded_values = round2tol(values_from_optimizer, tols)
    assert excepted_rounded_values == rounded_values
