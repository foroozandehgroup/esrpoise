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


# NB: the compilation time of the .exp/.def files is 1s by default but can be
# modified with the global variable COMPILATION_TIME from Xepr_link.
# This can be used to:
#     - avoid bugs caused by a slow compilation time when Xepr does not finish
#       compiling before receiving its next instruction),
#     - accelerate an optimisation routine if the Xepr files are compiling
#       faster.
# To test a modification of the compilation time, uncomment the next line
# Xepr_link.COMPILATION_TIME = 2  # (s)

Xepr = Xepr_link.load_xepr()

# .exp and .def files location
location = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210906/flip/'
exp_f = location + '2pflip.exp'
def_f = location + '2pflip.def'

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

# run experiment with optimal parameters
Xepr_link.run2getdata_exp(Xepr, "Signal", exp_f)
