"""
deer_pump.py
------------

Set up of DEER experiment and optimisation of DEER pump pulse.

SPDX-License-Identifier: GPL-3.0-or-later

"""

import os
import numpy as np
from esrpoise import xepr_link
from esrpoise import optimise
from esrpoise.costfunctions import max_n2p
from mrpypulse import pulse


def shape_HS(callback_pars_dict, shp_nb):
    """
    Modifies the shape bandwidth

    Parameters
    ----------
    callback_pars_dict: dictionary
        dictionary with the name of the parameters to optimise as key and their
        value as value
    """
    B = callback_pars_dict["&B"]

    # NB: Q doesn't matter much as the shape is at max amplitude in Xepr
    tp = 100e-9
    p = pulse.Parametrized(bw=60e6, tp=tp, Q=4, tres=0.625e-9,
                           delta_f=-65e6, B=B,
                           AM="sech", FM="sech")

    # create shape files (phase 0 and 180)
    p.xepr_file(shp_nb)
    p.phi0 += np.pi
    p.xepr_file(shp_nb+1)

    # .shp files paths
    path1 = os.path.join(os.getcwd(), str(shp_nb) + '.shp')
    path2 = os.path.join(os.getcwd(), str(shp_nb+1) + '.shp')
    shp_paths = [path1, path2]

    # create a single .shp file
    shps_path = os.path.join(os.getcwd(), str(shp_nb+2) + '.shp')
    merge_xepr_shps(shp_paths, shps_path)

    # send .shp file to Xepr
    xepr_link.load_shp(xepr, shps_path)

    return None


def merge_xepr_shps(shp_paths, shps_path):
    """
    Concatenate Xepr shape files into one shape file.

    Parameters
    ----------
    shp_paths: list of strings
        list of the shapes paths
    shps_path
         path of the merged shape file
    """
    with open(shps_path, 'w') as merged_file:
        for names in shp_paths:
            with open(names) as infile:
                merged_file.write(infile.read())

    return None


# NB: the compilation time of the .exp/.def files is 1s by default (0.25s for
# .shp file) but can be modified with the global variable COMPILATION_TIME from
# xepr_link.
# This can be used to:
#     - avoid bugs caused by a slow compilation time when Xepr does not finish
#       compiling before receiving its next instruction),
#     - accelerate an optimisation routine if the Xepr files are compiling
#       faster.
# To test a modification of the compilation time, uncomment the next line
# xepr_link.COMPILATION_TIME = 2  # (s)

xepr = xepr_link.load_xepr()

f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210906/deer_pump_pulse/'
exp_f = f_loc + '4pDEER.exp'
def_f = f_loc + '4pDEER.def'

# 1. HS pulse selectivity optimisation
# select n2p measurement experiment
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELEXPSlct", "4P-ELDOR-n2p")
xepr_link.modif_def(xepr, ['n', 'h'], ['1', '1024'])
xepr_link.load_exp(xepr, exp_f)
xbest0, fbest, message = optimise(xepr, pars=['&B'],
                                  init=[10], lb=[1], ub=[12], tol=[1],
                                  cost_function=max_n2p, optimiser='bobyqa',
                                  maxfev=30, nfactor=5, callback=shape_HS,
                                  callback_args=tuple([800]))

# 2. DEER measurement
# select DEER measurement
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELEXPSlct", "Deer-2DtauAvg")
xepr_link.modif_def(xepr, ['h'], ['256'])
xepr_link.load_exp(xepr, exp_f)
# run DEER
data = xepr_link.run2getdata_exp(xepr)
