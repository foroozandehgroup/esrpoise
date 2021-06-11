# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 15:43:08 2021

@author: jbv


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

Presented here: example of optimization

"""

import numpy as np
import poisesr
from collections import namedtuple

# script from the user to select options regrouped in routine
#   - pars, names of the parameters to optimize
#   - init, initial values of the parameters
#   - lb, lower bound of the parameters
#   - ub, upper bound of the parameters
#   - tol, optimization tolerance
#   - name, routine name
#   - cf, cost function of the routine


# TBP: parameter "parstype" to be able to input any parameter

# create Routine class namedtuple with desired fields
Routine = namedtuple("Routine", "name pars lb ub init tol cf maxfev optimizer_type exp_file def_file")

routine = Routine()

# fields similar to NMRpoise
routine.name = "pulse_2_intensities"
routine.pars = ["p1", "p2"]
routine.init = [6, 12] # should be numbers
routine.lb = [0, 0]
routine.ub = [100, 100]
routine.tol = [1, 1]
routine.cf = "maxabsint"

# fields added for code adaptation
routine.maxfev = 10
routine.optimizer_type = "nm"

# fields added for ESR
routine.exp_file = "spin_echo.exp"
routine.def_file = "spin_echo.def"

par_opt = poisesr.optimize(routine)







