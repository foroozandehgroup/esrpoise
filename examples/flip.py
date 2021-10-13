"""
flip.py
----------

Optimization of pulse flip angle.

2 parameters optimisation with a parameter from the .def file. It therefore
requires .def and . exp files paths.

SPDX-License-Identifier: GPL-3.0-or-later
"""

from esrpoise import Xepr_link
from esrpoise import optimize
from esrpoise.costfunctions import maxabsint_echo


Xepr = Xepr_link.load_xepr()

# .exp and .def files location
location = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210906/flip/'
exp_f = location + 'flip.exp'
def_f = location + 'flip.def'

# optimization of pulse length and amplitude
xbest0, fbest0, message0 = optimize(Xepr,
                                    pars=["p0", "Attenuation"],
                                    init=[8, 5],
                                    lb=[2, 0],
                                    ub=[36, 10],
                                    tol=[2, 0.5],
                                    cost_function=maxabsint_echo,
                                    exp_file=exp_f, def_file=def_f,
                                    optimiser="bobyqa", maxfev=20)
