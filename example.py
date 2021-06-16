# -*- coding: utf-8 -*-
"""
example.py
----------

A minimal example of how to use the esrpoise interface.

###  Principle  ###

Run parameter optimization of any ESR experiment:
  1. experiment -> retrieved from Xepr
      - .exp, .def, .shp
  2. run_exp, function to run the experiment
  3. data treatment to retrieve cost function value (user input)
  4. optimization
  5. modification of experiment
  6. loop to 2 (optimization)
  7. exit -> parameter value

SPDX-License-Identifier: GPL-3.0-or-later
"""

import numpy as np
from esrpoise import optimize
from esrpoise.costfunctions import maxabsint, maxrealint

# TBD: parameter "parstype" to be able to input any parameter

# Note that esrpoise.optimize() doesn't actually return anything yet

"""
# Hahn echo lengths optimization
xbest, fbest, message = optimize(pars=["p0", "p1"],
                                 init=[4, 6],
                                 lb=[2, 4],
                                 ub=[16, 32],
                                 tol=[2, 2],
                                 cost_function=maxabsint,   # imported, see above
                                 exp_file="echo_decay.exp",
                                 def_file="descrESEEM_jb.def",
                                 maxfev=50)
"""

# Hahn echo quadrature error optimization
xbest, fbest, message = optimize(pars=['aa0', 'aa1', 'b', 'c'],
                                 init=[95, 95, 1, 1],
                                 lb=[80, 80, 0, 0],
                                 ub=[100, 100, 180, 180],
                                 tol=[1, 1, 1, 1],
                                 cost_function=maxrealint,   # imported, see above
                                 exp_file='/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/Prodel/awg2p_jb.exp',
                                 def_file='/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/Prodel/awg2p_jb.def',
                                 maxfev=120)

print()
print('-' * 60)
print('Optimisation completed.')
print('Best values found: ', xbest)
print('Minimal cost function: ', fbest)
print('Optimisation message: ', message)
print('-' * 60)










