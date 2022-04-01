"""
callback.py
-----------

A minimal example (not meant to be actually run) on how to use the esrpoise
interface with user defined function callback and user defined parameters '&_'.

User parameters to be optimised should be indicated by a preceding '&'
    optimise(Xepr, pars=[... , '&_', ...], ...,
                   callback=my_callback, callback_args=my_callback_args)

User defined parameter function guidelines:
    def my_callback(my_callback_pars_dict, *mycallback_args):
        ""
        Parameters
        ----------
        pars_dict: dictionary
            dictionary with the name of the parameters to optimise as key and
            their value as value
        *mycallback_args
            other possible arguments for callback function
        ""
        # user operations and parameters modifications

callbak should not necessarily add user parameters to optimise, it can just
add user-specific operation (callback_pars_dict is sent back empty if no user
                             parameters are found)

SPDX-License-Identifier: GPL-3.0-or-later

"""

import os
from esrpoise import xepr_link
from esrpoise import optimise
from esrpoise.costfunctions import maxabsint_echo
from mrpypulse import pulse


def shape_bw(callback_pars_dict, shp_nb):
    """
    Modifies a hyperbolic sechant pulse bandwidth.

    Parameters
    ----------
    callback_pars_dict: dictionary
        dictionary with one entry ({'&bw': bw_value})
    shp_nb: int
        number of the shape to be modified
    """

    # getting  bw value from the callback parameters to be optimised
    bw = callback_pars_dict["&bw"]

    # create hyperbolic sechant shape with k value
    p = pulse.Parametrized(bw=bw, tp=80e-9, Q=5, tres=0.625e-9,
                           delta_f=-65e6, AM="sech", FM="sech")

    # create shape file
    p.xepr_file(shp_nb)

    # shape path
    path = os.path.join(os.getcwd(), str(shp_nb) + '.shp')

    # send shape to Xepr
    xepr_link.load_shp(xepr, path)

    # NB: AWG memory overloading
    # If a bug with shape loading is encountered after a certain number
    # of iterations (typically 114 on older version of Xepr), it can be solved
    # by reseting Xepr. Uncomment the following lines:
    # # Xepr reset needed for 114 sequential shape load and run
    # if acquire_esr.calls % 114 == 0 and acquire_esr.calls != 0:
    #     print('reset required')
    #     xepr_link.reset_exp(Xepr)

    return None


xepr = xepr_link.load_xepr()

#  HS pulse bandwidth optimisation
xbest0, fbest, message = optimise(xepr,
                                  pars=['&bw'],
                                  init=[80e6],
                                  lb=[30e6],
                                  ub=[120e6],
                                  tol=[1e6],
                                  cost_function=maxabsint_echo,
                                  maxfev=120,
                                  nfactor=5,
                                  callback=shape_bw,
                                  callback_args=(7770,))

# NB: callback_args needs to be input as a tupple
# '(7770,)' is equivalent to 'tuple([7770])'
