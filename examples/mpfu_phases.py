"""
mpfu_phases.py
--------------

Set up individual channel phases for RIDME. Use 5pRIDME.def and 5pRIDME.exp
with the 'PE transient' experiment and the 16-step phase cycle.

It includes modificationo of the RIDME .def file and 4 consecutive
optimisation to set up the 4 pulse channels.

SPDX-License-Identifier: GPL-3.0-or-later

"""

import os
from esrpoise import xepr_link
from esrpoise import optimise
from esrpoise.costfunctions import maxrealint_echo


xepr = xepr_link.load_xepr()

# script assumed to be located in the same directory as the .def files
f_loc = os.getcwd()
def_f = os.path.join(f_loc, '5pRIDME.def')

# get experiment name for Xepr commands
curr_exp = xepr.XeprExperiment()
expt_name = curr_exp.aqGetExpName()

# adjusting echo delay time to get nicer primary echo
xepr_link.modif_def(xepr, def_f, ['d1'], ['200'])

# optimisation parameters
init = [50]
lb = [0]
ub = [100]
tol = [1]

# +<x> channel phase adjustment
# NB: no space should be present in the phase cycle name ("mpfu+x")
xepr.XeprCmds.aqParSet(expt_name, "*ftEpr.PlsSPELLISTSlct", "mpfu+x")
pars = ["BrXPhase"]
xbest0, fbest0, msg0 = optimise(xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# -<x> channel phase adjustment
xepr.XeprCmds.aqParSet(expt_name, "*ftEpr.PlsSPELLISTSlct", "mpfu-x")
pars = ["BrMinXPhase"]
xbest1, fbest1, msg1 = optimise(xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# +<y> channel phase adjustment
xepr.XeprCmds.aqParSet(expt_name, "*ftEpr.PlsSPELLISTSlct", "mpfu+y")
pars = ["BrYPhase"]
xbest2, fbest2, msg2 = optimise(xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# -<y> channel phase adjustment
xepr.XeprCmds.aqParSet(expt_name, "*ftEpr.PlsSPELLISTSlct", "mpfu-y")
pars = ["BrMinYPhase"]
xbest3, fbest3, msg3 = optimise(xepr, pars=pars, init=init, lb=lb, ub=ub,
                                tol=tol, cost_function=maxrealint_echo,
                                optimiser="bobyqa", maxfev=100, nfactor=20)

# readjusting echo time to shorter duration for RIDME
xepr_link.modif_def(xepr, def_f, ['d1'], ['140'])
