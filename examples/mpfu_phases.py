"""
mpfu_phases.py

Set up individual channel phases for RIDME.


It includes modificationo of the RIDME .def file and 4 consecutive
optimisation to set up the 4 pulse channels.

SPDX-License-Identifier: GPL-3.0-or-later
"""

from esrpoise import Xepr_link
from esrpoise import optimize
from esrpoise.costfunctions import maxrealint_echo


Xepr = Xepr_link.load_xepr()

location = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210906/mpfu_phases/'
exp_f = location + '5pRIDME.exp'
def_f = location + '5pRIDME.def'

# adjusting echo delay time to get nicer primary echo
Xepr_link.modif_def(Xepr, def_f, ['d1'], ['200'])
Xepr_link.load_exp(Xepr, exp_f)

# optimisation parameters
init = [50]
lb = [0]
ub = [100]
tol = [1]

# +<x> channel phase adjustment
Xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "mpfu+x")
pars = ["BrXPhase"]
xbest0, fbest0, msg0 = optimize(Xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# -<x> channel phase adjustment
Xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "mpfu-x")
pars = ["BrMinXPhase"]
xbest1, fbest1, msg1 = optimize(Xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# +<y> channel phase adjustment
Xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "mpfu+y")
pars = ["BrYPhase"]
xbest2, fbest2, msg2 = optimize(Xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# -<y> channel phase adjustment
Xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "mpfu-y")
pars = ["BrMinYPhase"]
xbest3, fbest3, msg3 = optimize(Xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# readjusting echo time to shorter duration for RIDME
Xepr_link.modif_def(Xepr, def_f, ['d1'], ['140'])
Xepr_link.load_exp(Xepr, exp_f)
