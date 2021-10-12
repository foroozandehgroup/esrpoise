"""
example.py
----------

A minimal example of how to use the esrpoise module.

Run parameter optimization of any ESR experiment:
  1. [in Xepr] Run the experiment to be optimized once.
  2. [Python script] Initialise Xepr.
  2. [Python script] Pick the parameters to optimized, their initial values,
                     bounds and tolerances.
  3. [Python script] Pick a cost function (data treatment applied to the data
                                           at each step).
  4. [Terminal] Launch the Python script.

For .def file parameters, indicate the .def and .exp file path if .def file
parameters are to be optimised.

For user defined parameters, cf. example_callback.py

For other examples, cf. example folder

SPDX-License-Identifier: GPL-3.0-or-later
"""

from esrpoise import optimize
from esrpoise.costfunctions import maxabsint_echo
from esrpoise import Xepr_link

# load Xepr instance
Xepr = Xepr_link.load_xepr()

# Fine adjustment of center field
init = [3450]
xbest, fbest, message = optimize(Xepr, pars=['CenterField'], init=init,
                                 lb=[init[0]-5], ub=[init[0]+5],
                                 tol=[0.1], cost_function=maxabsint_echo,
                                 maxfev=20, nfactor=10)
