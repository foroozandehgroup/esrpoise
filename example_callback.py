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
from esrpoise.costfunctions import maxabsint_echo
from esrpoise import Xepr_link


def shape_bw(callback_pars_dict, shp_nb):
    """
    Modifies the shape bandwidth

    Parameters
    ----------
    callback_pars_dict: dictionary
        dictionary with the name of the parameters to optimize as key and their
        value as value
    """
    bw = callback_pars_dict["&bw"]
    try:
        from mrpypulse import pulse
    except ImportError:
        print('mrpypulse import error')
    p = pulse.Parametrized(bw=bw, tp=64e-9, Q=5, tres=0.625e-9)

    # create shape file
    p.xepr_file(shp_nb)

    # send shape to Xepr
    path = os.path.join(os.getcwd(), str(shp_nb) + '.shp')
    Xepr_link.load_shp(Xepr, path)
    return None


exp_f = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210707/Prodel/DEER.exp'
def_f = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210707/Prodel/DEER.def'

Xepr = Xepr_link.load_xepr()

xbest0, fbest, message = optimize(Xepr,
                                  pars=['&bw'],
                                  init=[300e6],
                                  lb=[200e6],
                                  ub=[500e6],
                                  tol=[10e6],
                                  cost_function=maxabsint_echo,
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=120,
                                  nfactor=60,
                                  callback=shape_bw,
                                  callback_args=7777)
