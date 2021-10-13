"""
basic.py
----------

A minimal example of how to use the esrpoise module.

Run parameter optimization of any ESR experiment:
  1. [in Xepr] Run the experiment to be optimized once.
  2. [Terminal] Run the Python script. It should at least:
          - Initialise Xepr.
          - Call esrpoise.optimise() with the parameters to optimized, their
          initial values, bounds , tolerances and a cost function (data
          treatment applied to the data at each step).

For .def file parameters, cf. flip.py.

For user defined parameters, cf. callback.py and deer_pump.py.

For other examples, cf. example folder.

SPDX-License-Identifier: GPL-3.0-or-later
"""

from esrpoise import Xepr_link
from esrpoise import optimize
from esrpoise.costfunctions import maxabsint_echo


# load Xepr instance
Xepr = Xepr_link.load_xepr()

# fine adjustment of center field for bisnitroxide sample at X-band
init = [3450]
xbest, fbest, message = optimize(Xepr, pars=['CenterField'],
                                 init=init,
                                 lb=[init[0]-5],
                                 ub=[init[0]+5],
                                 tol=[0.1],
                                 cost_function=maxabsint_echo,
                                 maxfev=20)
