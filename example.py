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
from esrpoise.costfunctions import maxabsint

# TBP: parameter "parstype" to be able to input any parameter

# Note that esrpoise.optimize() doesn't actually return anything yet
xbest, fbest, message = optimize(pars=["p1", "p2"],
                                 init=[6, 12],
                                 lb=[0, 0],
                                 ub=[100, 100],
                                 tol=[1, 1],
                                 cost_function=maxabsint,   # imported, see above
                                 exp_file="spin_echo.exp",
                                 def_file="spin_echo.def",
                                 maxfev=10)

print()
print('-' * 60)
print('Optimisation completed.')
print('Best values found: ', xbest)
print('Minimal cost function: ', fbest)
print('Optimisation message: ', message)
print('-' * 60)
