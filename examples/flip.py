"""
flip.py
----------

Optimisation of pulse flip angle.

2 parameters optimisation with a parameter from the .def file.

SPDX-License-Identifier: GPL-3.0-or-later

"""

from esrpoise import xepr_link
from esrpoise import optimise
from esrpoise.costfunctions import maxabsint_echo


xepr = xepr_link.load_xepr()

# optimisation of pulse length and amplitude
xbest0, fbest0, message0 = optimise(xepr,
                                    pars=["p0", "Attenuation"],
                                    init=[8, 5],
                                    lb=[2, 0],
                                    ub=[36, 10],
                                    tol=[2, 0.5],
                                    cost_function=maxabsint_echo,
                                    optimiser="bobyqa", maxfev=20)

# .exp file location
location = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210906/flip/'
exp_f = location + '2pflip.exp'

# run experiment with optimal parameters
xepr_link.run2getdata_exp(xepr, "Signal", exp_f)
