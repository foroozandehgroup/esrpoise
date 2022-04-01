"""
basic.py
--------

A minimal example of how to use the esrpoise module.

Run parameter optimisation of any ESR experiment:
  1. [in Xepr] Run the experiment to be optimised once.
  2. [Terminal] Run the Python script. It should at least:
          - Initialise Xepr.
          - Call esrpoise.optimise() with the parameters to optimised, their
          initial values, bounds , tolerances and a cost function (data
          treatment applied to the data at each step).

For .def file parameters, cf. flip.py.

For user defined parameters, cf. callback.py and deer_pump.py.

For other examples, cf. example folder.

SPDX-License-Identifier: GPL-3.0-or-later

"""

from esrpoise import xepr_link
from esrpoise import optimise
from esrpoise.costfunctions import maxabsint_echo


# load Xepr instance
xepr = xepr_link.load_xepr()

# adjustment of centre field for bisnitroxide sample at X-band
xbest, fbest, message = optimise(xepr,
                                 pars=['CenterField'],
                                 init=[3415],
                                 lb=[3390],
                                 ub=[3425],
                                 tol=[0.25],
                                 cost_function=maxabsint_echo,
                                 maxfev=20)
