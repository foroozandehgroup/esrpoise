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
from esrpoise import optimize, round2tol_str
from esrpoise.costfunctions import maxrealint_echo, maxabsint_echo
from esrpoise import Xepr_link

# Note that esrpoise.optimize() doesn't actually return anything yet

"""
# Hahn echo lengths optimization
xbest, fbest, message = optimize(pars=["p0", "p1"],
                                 init=[4, 6],
                                 lb=[2, 4],
                                 ub=[16, 32],
                                 tol=[2, 2],
                                 cost_function=maxabsint,   # imported
                                 exp_file="echo_decay.exp",
                                 def_file="descrESEEM_jb.def",
                                 maxfev=50)

# Hahn echo quadrature error optimization
xbest, fbest, message = optimize(pars=['aa0', 'aa1', 'b', 'c', 'r', 's'],
                                 init=[90, 90, 50, 50, 50, 50],
                                 lb=[80, 80, 0, 0, 0, 0],
                                 ub=[100, 100, 100, 100, 100, 100],
                                 tol=[1, 1, 1, 1, 1, 1],
                                 cost_function=maxrealint_echo,   # imported
                                 exp_file='/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210706/Prodel/awg2p_jb.exp',
                                 def_file='/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210706/Prodel/awg2p_jb.def',
                                 maxfev=4,
                                 nfactor=10)
"""
# Hahn echo set-up: amplitude (Attenuation) and length (p1 = 2p0) of pulses
# Center field can be added

exp_f = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB' \
        '/210823/Prodel/awg2p_jb.exp'
def_f = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB' \
        '/210823/Prodel/awg2p_jb.def'

# Initialise Xepr module
# needed to conduct several optimization (no method found to close XeprAPI
# wihout closing python/requiring the user to touch Xepr)
Xepr = Xepr_link.load_xepr()

xbest0, fbest, message = optimize(Xepr,
                                  pars=['BrMinXPhase', 'BrMinxAmp'],
                                  init=[90, 90],
                                  lb=[10, 10],
                                  ub=[100, 100],
                                  tol=[0.049, 0.049],
                                  cost_function=maxabsint_echo,  # imported
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=40,
                                  nfactor=50)

"""
# consecutive optimizations (not working)


tol0 = [2, 10, 0.5]
xbest0, fbest, message = optimize(Xepr,
                                  pars=['p0', 'd1','Attenuation'],
                                  init=[12, 250, 5],
                                  lb=[6, 150, 0],
                                  ub=[36, 350, 10],
                                  tol=tol0,
                                  cost_function=maxabsint_echo,
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=2,12
                                  nfactor=10)


xbest, fbest, message = optimize(Xepr,
                                 pars=['CenterField'],
                                 init=[3510],
                                 lb=[3500],
                                 ub=[3520],
                                 tol=[0.1],
                                 cost_function=maxabsint_echo,
                                 exp_file=exp_f,
                                 def_file=def_f,
                                 maxfev=2,
                                 nfactor=10)

xbest, fbest, message = optimize(Xepr,
                                 pars=['p0', 'd1','Attenuation'],
                                 init=xbest0,
                                 lb=[6, 150, 0],
                                 ub=[36, 350, 10],
                                 tol=[2, 2, 0.1],
                                 cost_function=maxabsint_echo,
                                 exp_file=exp_f,
                                 def_file=def_f,
                                 maxfev=2,
                                 nfactor=10)

"""

"""
TODO

Optimizer
    # add check for same size of pars, init, lb, ub, tol
    # more flexibility in exploration
        # different factor size of simplex for each parameter
        # bounce?
        # launch several consecutive optimization from same script
    # add some kind of brute force optimizer for easy comparison?

Main
    # parameters input/set-up
        # make exp/def files optional (in case the user does not optimize
        anything from .def)
    # add stop
    # .exp file modif?
    # cleaner def modif (no comment/spaces scrapped)
"""
