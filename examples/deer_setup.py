"""
deer_pump.py
------------

Set up of DEER experiment. Use 4pdeer.exp, 4pdeer.def, the '4P-ELDOR-Setup' and
the 8-step phase cycle (experiment automatically loaded).

SPDX-License-Identifier: GPL-3.0-or-later

"""

from esrpoise import xepr_link
from esrpoise import optimise, round2tol_str
from esrpoise.costfunctions import maxrealint_echo


xepr = xepr_link.load_xepr()

f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210906/deer_pump/'
exp_f = f_loc + '4pDEER.exp'
def_f = f_loc + '4pDEER.def'

# 1. observer pi pulse length
# set up a p0-2p0 Hahn echo without phase cycling
xepr_link.modif_def(xepr, def_f,
                    ['p0', 'p1', 'aa0', 'aa1'],
                    ['32', '2*p0', '100', 'aa0'])
xepr_link.load_exp(xepr, exp_f)

# change experiment name ("Experiment") if necessary
# NB: no space should be present in the phase cycle name ("none")
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "none")
# adjust phase on x channel to get real part of the echo
xbest0, fbest, message = optimise(xepr, pars=['ap1'],
                                  init=[0], lb=[-200], ub=[200], tol=[1],
                                  cost_function=maxrealint_echo,
                                  exp_file=exp_f, def_file=def_f,
                                  optimiser="bobyqa", maxfev=60, nfactor=90)
# add phase cycle
# NB: no space should be present in the phase
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "8-steps-2p")
# find flip angle
xbest0, fbest0, mesg0 = optimise(xepr, pars=['p0', 'aa0'],
                                 init=[40, 90],
                                 lb=[20, 70],
                                 ub=[70, 100],
                                 tol=[2, 1],
                                 cost_function=maxrealint_echo,
                                 exp_file=exp_f, def_file=def_f,
                                 optimiser="bobyqa", maxfev=40, nfactor=10)

p0 = round2tol_str([2*xbest0[0]], [2])[0]
aa1 = round2tol_str([xbest0[1]], [1])[0]

# 2. observer pulses amplitudes optimisation
# set up a p0-p0 Hahn echo
xepr_link.modif_def(xepr, def_f, ['p0', 'p1', 'aa1'], [p0, 'p0', aa1])
xepr_link.load_exp(xepr, exp_f)
xbest1, fbest1, msg1 = optimise(xepr, pars=['aa0'],
                                init=[25], lb=[10], ub=[80], tol=[1],
                                cost_function=maxrealint_echo,
                                exp_file=exp_f, def_file=def_f,
                                optimiser="bobyqa", maxfev=40, nfactor=20)

xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "8-steps-2p")

# adjust phase on x channel to get real part of the echo
# NB: no space should be present in the experiment name ("4P-ELDOR-Setup")
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELEXPSlct", "4P-ELDOR-Setup")
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "8-step")
init = xbest0[0]
xbest0, fbest, message = optimise(xepr, pars=['ap1'], init=[init],
                                  lb=[init-50], ub=[init+50], tol=[1],
                                  cost_function=maxrealint_echo,
                                  exp_file=exp_f, def_file=def_f,
                                  optimiser="bobyqa", maxfev=60, nfactor=90)
