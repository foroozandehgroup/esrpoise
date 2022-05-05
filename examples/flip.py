"""
flip.py
----------

Optimisation of pulse flip angle. Use 2pflip.def and 2pflip.exp with the
'Hahn-echo' experiment and the 16-step phase cycle.

2 parameters optimisation with a parameter from the .def file.

SPDX-License-Identifier: GPL-3.0-or-later

"""

from esrpoise import xepr_link
from esrpoise import optimise
from esrpoise.costfunctions import maxabsint_echo


xepr = xepr_link.load_xepr()

# optimisation of pulse length and amplitude
xbest0, fbest0, message0 = optimise(xepr,
                                    pars=["p0", "Attenuation"],
                                    init=[8, 5],
                                    lb=[2, 0],
                                    ub=[36, 10],
                                    tol=[2, 0.5],
                                    cost_function=maxabsint_echo,
                                    optimiser="bobyqa", maxfev=20)

# run experiment with optimal parameters
xepr_link.run2getdata_exp(xepr)
