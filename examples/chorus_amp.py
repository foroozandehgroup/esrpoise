"""
chorus_amp.py
-------------

Optimisation of CHORUS amplitudes. It is recommended use echo experiment and
64-steps phase cycle).

SPDX-License-Identifier: GPL-3.0-or-later

"""

from esrpoise.costfunctions import maxabsint
from esrpoise import optimise, xepr_link


xepr = xepr_link.load_xepr()

# amplitudes optimization
xbest1, fbest1, msg1 = optimise(xepr, pars=['aa0', 'aa1', 'aa2'],
                                init=[45, 90, 99],
                                lb=[10, 50, 50],
                                ub=[60, 100, 100],
                                tol=[1, 1, 1],
                                cost_function=maxabsint,
                                optimiser="bobyqa", maxfev=100, nfactor=40)

f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/220128/293K/'
exp_f = f_loc + 'CHORUS.exp'

# run experiment with optimal parameters
data = xepr_link.run2getdata_exp(xepr, "Signal", exp_f)
