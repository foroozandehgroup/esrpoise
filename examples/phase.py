"""
phase.py
--------

Adjust the signal phase with a first coarse optimisation maximizing the real
part of the echo and a second finer, more targeted optimisation minimising the
signal imaginary part.

Use 2pflip.def and 2pflip.exp with the 'Hahn-echo' experiment and the 16-step
phase cycle.

SPDX-License-Identifier: GPL-3.0-or-later

"""

from esrpoise import xepr_link
from esrpoise import optimise, round2tol_str
from esrpoise.costfunctions import maxrealint_echo, zeroimagint_echo


# load Xepr instance
xepr = xepr_link.load_xepr()

xbest0, fbest, message = optimise(xepr,
                                  pars=['SignalPhase'],
                                  init=[1200],
                                  lb=[300],
                                  ub=[3800],
                                  tol=[10],
                                  cost_function=maxrealint_echo,
                                  maxfev=50,
                                  nfactor=50)

xbest0 = int(round2tol_str(xbest0, [5])[0])
xbest, fbest, message = optimise(xepr,
                                 pars=['SignalPhase'],
                                 init=[xbest0],
                                 lb=[xbest0-200],
                                 ub=[xbest0+200],
                                 tol=[1],
                                 cost_function=zeroimagint_echo,
                                 maxfev=100,
                                 nfactor=50)
