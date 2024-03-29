"""
deer_pump.py
------------

Set up of DEER experiment and optimisation of DEER pump pulse. Use 4pdeer.exp
, 4pdeer.def  and 8-step phase cycle (experiment automatically loaded).

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


xepr = xepr_link.load_xepr()

# script assumed to be located in the same directory as the .exp/.def files
f_loc = os.getcwd()
exp_f = os.path.join(f_loc, '4pDEER.exp')
def_f = os.path.join(f_loc, '4pDEER.def')

# get experiment name for Xepr commands
curr_exp = xepr.XeprExperiment()
expt_name = curr_exp.aqGetExpName()

# 1. HS pulse selectivity optimisation
# select n2p measurement experiment
# NB: no space should be present in the experiment name ("4P-ELDOR-Setup")
xepr.XeprCmds.aqParSet(expt_name, "*ftEpr.PlsSPELEXPSlct", "4P-ELDOR-n2p")
xepr_link.modif_def(xepr, def_f, ['n', 'h'], ['1', '1024'])
xbest0, fbest, message = optimise(xepr, pars=['&B'],
                                  init=[10], lb=[1], ub=[12], tol=[1],
                                  cost_function=max_n2p, optimiser='bobyqa',
                                  exp_file=exp_f, def_file=def_f,
                                  maxfev=30, nfactor=5, callback=shape_HS,
                                  callback_args=tuple([800]))

# 2. DEER measurement
# select DEER measurement
xepr.XeprCmds.aqParSet(expt_name, "*ftEpr.PlsSPELEXPSlct", "Deer-2DtauAvg")
xepr_link.modif_def(xepr, def_f, ['h'], ['256'])
# run DEER
data = xepr_link.run2getdata_exp(xepr)
