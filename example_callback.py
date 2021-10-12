"""
example_callback.py
----------

A minimal example of how to use the esrpoise interface with user defined
function callback and user defined parameters '&_'.


User parameters to be optimized should be indicated by a preceding '&'
    optimize(Xepr, pars=[... , '&_', ...], ...,
                   callback=my_callback, callback_args=my_callback_args)

User defined parameter function guidelines:
    def my_callback(my_callback_pars_dict, *mycallback_args):
        ""
        Parameters
        ----------
        pars_dict: dictionary
            dictionary with the name of the parameters to optimize as key and
            their value as value
        *mycallback_args
            other possible arguments for callback function
        ""
        # user operations and parameters modifications

callbak should not necessarily add user parameters to optimize, it can just
add user-specific operation (callback_pars_dict is sent back empty if no user
                             parameters are found)

SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
from esrpoise import optimize
from esrpoise.costfunctions import max_n2p
from esrpoise import Xepr_link
from mrpypulse import pulse


def shape_bw(callback_pars_dict, shp_nb):
    """
    Modifies a hyperbolic sechant pulse shape via its selectivity k (B=k/tp).

    Parameters
    ----------
    callback_pars_dict: dictionary
        dictionary with the name of the parameters to optimize as key and their
        value as value
    shp_nb: int
        number of the shape to be modified
    """

    # getting k value from the callback parameters to be optimised
    k = callback_pars_dict["&k"]

    # create hyperbolic sechant shape with k value
    tp = 64e-9
    p = pulse.Parametrized(bw=60e6, tp=tp, Q=15, tres=0.625e-9,
                           delta_f=-65e6, B=k/tp,
                           AM="tanh", FM="sech")

    # create shape file
    p.xepr_file(shp_nb)

    # shape path
    path = os.path.join(os.getcwd(), str(shp_nb) + '.shp')

    # send shape to Xepr
    Xepr_link.load_shp(Xepr, path)

    # NB: AWG memory overloading
    # If a bug with shape loading is encountered after a certain number
    # of iterations (typically 114 on older version of Xepr), it can be solved
    # by reseting Xepr. Uncomment the following lines:
    # # Xepr reset needed for 114 sequential shape load and run
    # if acquire_esr.calls % 114 == 0 and acquire_esr.calls != 0:
    #     print('reset required')
    #     Xepr_link.reset_exp(Xepr)

    return None


# load Xepr instance
Xepr = Xepr_link.load_xepr()

#  HS pump pulse selectivity factor optimization
xbest0, fbest, message = optimize(Xepr, pars=['&k'], init=[10],
                                  lb=[1], ub=[15], tol=[1],
                                  cost_function=max_n2p,
                                  maxfev=112, nfactor=5,
                                  callback=shape_bw,
                                  callback_args=(7770,))

# NB: callback_args needs to be input as a tupple
# (7770,) is equivalent to tuple([7770])
