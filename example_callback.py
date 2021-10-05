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
import numpy as np

from esrpoise import optimize
from esrpoise.costfunctions import max_n2p
from esrpoise import Xepr_link
from mrpypulse import pulse


def shape_bw(callback_pars_dict, shp_nb):
    """
    Modifies the shape bandwidth

    Parameters
    ----------
    callback_pars_dict: dictionary
        dictionary with the name of the parameters to optimize as key and their
        value as value
    """

    k = callback_pars_dict["&k"]

    # NB: Q doesn't matter much as the shape is at max amplitude in Xepr
    tp = 64e-9
    p = pulse.Parametrized(bw=60e6, tp=tp, Q=15, tres=0.625e-9,
                           delta_f=-65e6, B=k/tp,
                           AM="tanh", FM="sech")

    # create shape files (phase 0 and 180)
    p.xepr_file(shp_nb)
    p.phi0 += np.pi
    p.xepr_file(shp_nb+1)

    # send shape to Xepr
    path = os.path.join(os.getcwd(), str(shp_nb) + '.shp')
    Xepr_link.load_shp(Xepr, path)

    # TODO note on AWG memory overloading
    # present it as a note/remark in case the user encounters this bug
    # the user should be able to get the number of iterations in the
    # callback function
    # # Xepr reset needed for 114 sequential shape load and run
    # if acquire_esr.calls % 114 == 0 and acquire_esr.calls != 0:
    #     print('reset required')
    #     Xepr_link.reset_exp(Xepr)

    return None


def shapes2Xepr(shp_paths, shps_path):
    """
    Concatenate xepr files together
    """
    with open(shps_path, 'w') as merged_file:
        for names in shp_paths:
            with open(names) as infile:
                merged_file.write(infile.read())

    return None


Xepr = Xepr_link.load_xepr()

f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210823/deer/'
exp_f = f_loc + '4pDEER.exp'
def_f = f_loc + '4pDEER.def'

#  HS pump pulse selectivity factor optimization
xbest0, fbest, message = optimize(Xepr, pars=['&k'], init=[10],
                                  lb=[1], ub=[15], tol=[1],
                                  cost_function=max_n2p,
                                  exp_file=exp_f, def_file=def_f,
                                  maxfev=112, nfactor=5,
                                  callback=shape_bw,
                                  callback_args=(7770,))

# TODO add comment about tuple([7770])
