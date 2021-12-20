"""
deer_pump.py
----------

Set up of DEER experiment and optimization of DEER pump pulse.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
import numpy as np
from esrpoise import Xepr_link
from esrpoise import optimize, round2tol_str
from esrpoise.costfunctions import maxrealint_echo, max_n2p
from mrpypulse import pulse


def shape_HS(callback_pars_dict, shp_nb):
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
    tp = 100e-9
    p = pulse.Parametrized(bw=60e6, tp=tp, Q=20, tres=0.625e-9,
                           delta_f=-65e6, B=k/tp,
                           AM="tanh", FM="sech")

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
    Xepr_link.load_shp(xepr, shps_path)

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


xepr = Xepr_link.load_xepr()

f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/210906/deer_pump_pulse/'
exp_f = f_loc + '4pDEER.exp'
def_f = f_loc + '4pDEER.def'

# 1. observer pi pulse length
# set up a p0-2p0 Hahn echo without phase cycling
Xepr_link.modif_def(xepr, def_f,
                    ['p0', 'p1', 'aa0', 'aa1'],
                    ['32', '2*p0', '100', 'aa0'])
Xepr_link.load_exp(xepr, exp_f)
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "none")
# adjust phase on x channel to get real part of the echo
xbest0, fbest, message = optimize(xepr, pars=['ap1'],
                                  init=[0], lb=[-200], ub=[200], tol=[1],
                                  cost_function=maxrealint_echo,
                                  exp_file=exp_f, def_file=def_f,
                                  optimiser="bobyqa", maxfev=60, nfactor=90)
# add phase cycle
# NB: no space should be present in the phase
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "8-steps-2p")
# find flip angle
xbest0, fbest0, mesg0 = optimize(xepr, pars=['p0', 'aa0'],
                                 init=[40, 90],
                                 lb=[20, 70],
                                 ub=[70, 100],
                                 tol=[2, 1],
                                 cost_function=maxrealint_echo,
                                 exp_file=exp_f, def_file=def_f,
                                 optimiser="bobyqa", maxfev=40, nfactor=10)

p0 = round2tol_str([2*xbest0[0]], [2])[0]
aa1 = round2tol_str([xbest0[1]], [1])[0]

# 2. observer pulses amplitudes optimization
# set up a p0-p0 Hahn echo
Xepr_link.modif_def(xepr, def_f, ['p0', 'p1', 'aa1'], [p0, 'p0', aa1])
xbest1, fbest1, msg1 = optimize(xepr, pars=['aa0'],
                                init=[25], lb=[10], ub=[80], tol=[1],
                                cost_function=maxrealint_echo,
                                exp_file=exp_f, def_file=def_f,
                                optimiser="bobyqa", maxfev=40, nfactor=20)

xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "8-steps-2p")

# adjust phase on x channel to get real part of the echo
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELEXPSlct", "4P-ELDOR-Setup")
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "8-step")
init = xbest0[0]
xbest0, fbest, message = optimize(xepr, pars=['ap1'], init=[init],
                                  lb=[init-50], ub=[init+50], tol=[1],
                                  cost_function=maxrealint_echo,
                                  exp_file=exp_f, def_file=def_f,
                                  optimiser="bobyqa", maxfev=60, nfactor=90)

# 3. pulse selectivity optimization
# select n2p measurement experiment
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELEXPSlct", "4P-ELDOR-n2p")
Xepr_link.modif_def(xepr, def_f, ['n', 'h'], ['1', '1024'])
Xepr_link.load_exp(xepr, exp_f)
xbest0, fbest, message = optimize(xepr, pars=['&k'],
                                  init=[10], lb=[1], ub=[12], tol=[1],
                                  cost_function=max_n2p, optimiser='bobyqa',
                                  exp_file=exp_f, def_file=def_f,
                                  maxfev=30, nfactor=5, callback=shape_HS,
                                  callback_args=tuple([8000]))

# 4. DEER measurement
# select DEER measurement
xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELEXPSlct", "Deer-2DtauAvg")
Xepr_link.modif_def(xepr, def_f, ['h'], ['256'])
Xepr_link.load_exp(xepr, exp_f)
# run DEER
data = Xepr_link.run2getdata_exp(xepr)
