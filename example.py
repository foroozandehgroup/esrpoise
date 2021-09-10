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

import time
from esrpoise import optimize
from esrpoise.costfunctions import maxabsint_echo
from esrpoise import Xepr_link

exp_f = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB' \
        '/210823/Prodel/awg2p_jb.exp'
def_f = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB' \
        '/210823/Prodel/awg2p_jb.def'

# Initialise Xepr module
# needed to conduct several optimization (no method found to close XeprAPI
# wihout closing python/requiring the user to touch Xepr)
Xepr = Xepr_link.load_xepr()


# consecutive optimizations

# Pulse flip angle
tol0 = [2, 10, 0.5]
xbest0, fbest, message = optimize(Xepr, pars=['p0', 'Attenuation'],
                                  init=[12, 5],
                                  lb=[6, 0],
                                  ub=[36, 10],
                                  tol=[2, 0.5],
                                  cost_function=maxabsint_echo,
                                  exp_file=exp_f, def_file=def_f,
                                  maxfev=20, nfactor=10)

# let time for Xepr to record an experiment
# with the previous optimized value
time.sleep(10)

# Fine adjustment of center field
init = [3450]
xbest, fbest, message = optimize(Xepr, pars=['CenterField'],
                                 init=init, lb=[init[0]-5], ub=[init[0]+5],
                                 tol=[0.1], cost_function=maxabsint_echo,
                                 maxfev=20, nfactor=10)
