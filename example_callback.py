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
from esrpoise.costfunctions import maxabsint_echo, maxrealint_echo
from esrpoise.costfunctions import sumrealint_echo, max_n2p
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
    bw = callback_pars_dict["&bw"]
    delta_f = callback_pars_dict["&delta_f"]
    k = callback_pars_dict["&k"]

    # NB: Q doesn't matter much as the shape is at max amplitude in Xepr
    tp = 64e-9
    p = pulse.Parametrized(bw=bw, tp=tp, Q=15, tres=0.625e-9,
                           delta_f=delta_f, B=k/tp,
                           AM="tanh", FM="sech")

    # create shape files (phase 0 and 180)
    p.xepr_file(shp_nb)
    p.phi0 += np.pi
    p.xepr_file(shp_nb+1)

    # send shapes to Xepr
    path1 = os.path.join(os.getcwd(), str(shp_nb) + '.shp')
    path2 = os.path.join(os.getcwd(), str(shp_nb+1) + '.shp')

    shp_paths = [path1, path2]
    shps_path = os.path.join(os.getcwd(), str(shp_nb+2) + '.shp')
    shapes2Xepr(shp_paths, shps_path)
    Xepr_link.load_shp(Xepr, shps_path)

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


f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210823/deer/'
exp_f = f_loc + '4pDEER_Will.exp'
def_f = f_loc + '4pDEER_Will.def'

Xepr = Xepr_link.load_xepr()

"""
# flip angle optimization
xbest0, fbest, message = optimize(Xepr,
                                  pars=['p0', 'Attenuation', 'd1'],
                                  init=[26, 0.2, 200],
                                  lb=[8, 0, 150],
                                  ub=[32, 5, 250],
                                  tol=[2, 0.2, 2],
                                  cost_function=maxabsint_echo,  # imported
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=80,
                                  nfactor=10)
"""

"""
# x phase optimization
xbest0, fbest, message = optimize(Xepr,
                                  pars=['ap1'],
                                  init=[0],
                                  lb=[-200],
                                  ub=[200],
                                  tol=[1],
                                  cost_function=maxrealint_echo,  # imported
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=60,
                                  nfactor=90)

"""


"""
# -x, y, -y phase optimization
ap1 = 175
pars = ['ap2', 'ap3', 'ap4']
init = np.array([-90, 180, 90]) + ap1
lb = init - 170
ub = init + 170
tol = np.ones(len(pars))

xbest0, fbest, message = optimize(Xepr,
                                  pars=pars,
                                  init=init,
                                  lb=lb,
                                  ub=ub,
                                  tol=tol,
                                  cost_function=sumrealint_echo,  # imported
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=80,
                                  nfactor=80)
"""

"""
# observer pulses amplitudes optimization
# get 5-10% more on PE
# not really seen on RVE but data is noisy
xbest0, fbest, message = optimize(Xepr,
                                  pars=['aa0', 'aa1'],
                                  init=[43, 99],
                                  lb=[10, 50],
                                  ub=[80, 100],
                                  tol=[1, 1],
                                  cost_function=maxrealint_echo,  # imported
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=60,
                                  nfactor=10)
"""

"""
# pump pulse optimization
# 58 100
xbest0, fbest, message = optimize(Xepr,
                                  pars=['p3', 'aa2'],
                                  init=[40, 80],
                                  lb=[40, 70],
                                  ub=[80, 100],
                                  tol=[1, 1],
                                  cost_function=max_n2p,
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=30,
                                  nfactor=10)

"""


# TODO tupple input -> a bit awkward
f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210823/deer/'
exp_f = f_loc + '4pDEER_Will_shp.exp'
def_f = f_loc + '4pDEER_Will_shp.def'
# pulse bandwidth and spectral position optimization
xbest0, fbest, message = optimize(Xepr,
                                  pars=['&bw', '&delta_f', '&k'],
                                  init=[50e6, -65e6, 10.6],
                                  lb=[30e6, -85e6, 5.8],
                                  ub=[70e6, -45e6, 15.4],
                                  tol=[2.5e6, 2.5e6, 0.6],
                                  cost_function=max_n2p,
                                  exp_file=exp_f,
                                  def_file=def_f,
                                  maxfev=112,
                                  nfactor=5,
                                  callback=shape_bw,
                                  callback_args=tuple([7770]))
