"""
chorus_amp.py
-------------

Optimisation of CHORUS amplitudes. Use chorus.exp, chorus.def, with the 'echo'
experiment and the 64-step phase cycle.

SPDX-License-Identifier: GPL-3.0-or-later

"""

import os
from esrpoise.costfunctions import maxabsint
from esrpoise import optimise, xepr_link


xepr = xepr_link.load_xepr()

# script assumed to be located in the same directory as the .exp/.def files
f_loc = os.getcwd()
exp_f = os.path.join(f_loc, 'CHORUS.exp')
def_f = os.path.join(f_loc, 'CHORUS.def')

# amplitudes optimization
xbest1, fbest1, msg1 = optimise(xepr, pars=['aa0', 'aa1', 'aa2'],
                                init=[45, 90, 99],
                                lb=[10, 50, 50],
                                ub=[60, 100, 100],
                                tol=[1, 1, 1],
                                cost_function=maxabsint,
                                exp_file=exp_f, def_file=def_f,
                                optimiser="bobyqa", maxfev=100, nfactor=40)

# run experiment with optimal parameters
data = xepr_link.run2getdata_exp(xepr)
