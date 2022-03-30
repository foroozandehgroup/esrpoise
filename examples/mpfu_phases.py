"""
mpfu_phases.py

Set up individual channel phases for RIDME.

It includes modificationo of the RIDME .def file and 4 consecutive
optimisation to set up the 4 pulse channels.

SPDX-License-Identifier: GPL-3.0-or-later

"""

from esrpoise import xepr_link
from esrpoise import optimise
from esrpoise.costfunctions import maxrealint_echo


xepr = xepr_link.load_xepr()

location = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210906/mpfu_phases/'
exp_f = location + '5pRIDME.exp'
def_f = location + '5pRIDME.def'

# adjusting echo delay time to get nicer primary echo
xepr_link.modif_def(xepr, ['d1'], ['200'])
xepr_link.load_exp(xepr, exp_f)

# optimisation parameters
init = [50]
lb = [0]
ub = [100]
tol = [1]

# +<x> channel phase adjustment
# NB: no space should be present in the experiment name
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "mpfu+x")
pars = ["BrXPhase"]
xbest0, fbest0, msg0 = optimise(xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# -<x> channel phase adjustment
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "mpfu-x")
pars = ["BrMinXPhase"]
xbest1, fbest1, msg1 = optimise(xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# +<y> channel phase adjustment
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "mpfu+y")
pars = ["BrYPhase"]
xbest2, fbest2, msg2 = optimise(xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# -<y> channel phase adjustment
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "mpfu-y")
pars = ["BrMinYPhase"]
xbest3, fbest3, msg3 = optimise(xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# readjusting echo time to shorter duration for RIDME
xepr_link.modif_def(xepr, ['d1'], ['140'])
xepr_link.load_exp(xepr, exp_f)
