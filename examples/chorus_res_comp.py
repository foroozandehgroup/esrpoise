"""
chorus_res_comp.py
------------------

Optimisation of resonator compensation for CHORUS. Use chorus.exp, chorus.def,
(experiment and phase cycle automatically selected).

SPDX-License-Identifier: GPL-3.0-or-later

"""

import os
import copy
import numpy as np
import matplotlib.pyplot as plt
from esrpoise.costfunctions import maxabsint
from esrpoise import optimize, Xepr_link
from mrpypulse import sequence


def chorus_pulses():
    """
    Returns
    -------
    chorus : mrpypulse Exc_3fs object
        chorus pulse sequence
    """
    t90min = 80e-9
    t180min = 240e-9
    bw = 350e6
    tres = 0.625e-9
    chorus = sequence.Exc_3fs(t90min, t180min, bw, tres, polyfit=True,
                              pulse_args={"delta_f": 0, "sm": 12.5},
                              polyfit_args={"deg": 4})
    return chorus


def load_seq(pulses, shp_nb=400, shp_paths=[]):
    """
    Generate shape files for a sequence and load them into Xepr

    Parameters
    ----------
    Xepr : instance of XeprAPI.Xepr
        The instantiated Xepr object.
    seq : mrpypulse sequence
        sequence to load
    shp_nb: int
        number of the shape file
    shp_paths: string
        path of the shape files

    Returns
    -------
    None.

    """
    pulses0 = copy.deepcopy(pulses)
    for p in pulses0:

        # pulse shape files
        for phi0 in [0., np.pi/2, np.pi, 3*np.pi/2]:

            p.phi0 = phi0  # add phase cycle
            p.xepr_file(shp_nb)

            # add shape file name to shp_paths
            shp_paths.append(os.path.join(os.getcwd(), str(shp_nb) + '.shp'))
            shp_nb += 1

    shps_path = os.path.join(os.getcwd(),
                             str(shp_nb+len(pulses)*4) + '.shp')
    shapes2xepr(shp_paths, shps_path)
    Xepr_link.load_shp(Xepr, shps_path)


def shapes2xepr(shp_paths, shps_path):
    """
    Concatenate xepr shape files together
    """
    with open(shps_path, 'w') as merged_file:
        for names in shp_paths:
            with open(names) as infile:
                merged_file.write(infile.read())

    return None


def shape_impulse(callback_pars_dict, seq):
    """
    callback function for on the fly resonator compensation

    Parameters
    ----------
    callback_pars_dict: dictionary
        dictionary with the name of the parameters to optimize as key and their
        value as value
    seq: mrpypulse sequence object
        sequence whose pulses are to be compensated
    """

    c = [callback_pars_dict["&c1"], callback_pars_dict["&c2"],
         callback_pars_dict["&c3"], callback_pars_dict["&c4"]]

    seq0 = copy.deepcopy(seq)

    # pulse modification
    for p in seq0.pulses:

        # create impulse
        frq = 100
        s = np.linspace(-frq/2, frq/2, p.ns)
        H_numer = 1 + c[2] + 1j * c[3]
        H_denom = 1 + s*(c[0] + 1j * c[1])
        wfm = H_numer/H_denom

        # modify pulse with impulse
        gg = p.x + 1j * p.y
        aa = np.fft.fftshift(np.fft.fft(gg))/wfm
        new_pulse_g = np.fft.ifft(np.fft.ifftshift(aa))
        p.x = np.real(new_pulse_g)
        p.y = np.imag(new_pulse_g)

    load_seq(seq0.pulses, shp_paths=[])

    return None


def min_diff_FS(data):
    """
    Cost function for chorus on the fly resonator compensation

    Minimizes the difference between the spectrum and the field sweep data.

    """
    FS_path = os.path.join(os.getcwd(), '009_FS_inverted.txt')

    # read FS
    FS = np.loadtxt(FS_path, delimiter=' ')
    FS[:, 0] = FS[:, 0] * 1e9  # GHz to Hz

    # FS normalisation
    FS[:, 1] = FS[:, 1] - FS[1, 1]  # baseline
    FS[:, 1] = FS[:, 1]/np.max(FS[:, 1])

    # echo data
    echo = data.O.real + 1j * data.O.imag
    # echo interpolation for better precision on 1st order phase correction
    echo = np.interp(np.linspace(1, len(echo), 8*len(echo)),
                     np.linspace(1, len(echo), len(echo)),
                     echo)
    # find echo centre
    imax = np.argmax(np.abs(echo))
    # chop the echo for 1st order phase correction
    echo = echo[imax:]
    # adjust intensity of first point to avoid baseline error
    echo[1] = echo[1]/2

    # spectrum
    spec = np.fft.fftshift(np.fft.fft(echo, n=8*len(echo)))

    # automatic 0th order phase correction
    spec_ph = spec
    for phi0 in np.linspace(-180, 180, 4*360+1):
        spec_phi0 = spec * np.exp(-1j * phi0 * np.pi/180)
        if sum(np.real(spec_phi0)) > sum(np.real(spec_ph)):
            spec_ph = spec_phi0
    spec = np.real(spec_ph)
    spec = spec/np.max(spec)

    sf = 1 / (0.5e-9/8)  # 0.5ns echo resolution * 8 for interpolation
    x_spec = np.linspace(-sf / 2, sf / 2, len(spec))  # + 1.5*82.82e6

    # interpolate spectrum with xaxis of field sweep
    spec = np.interp(FS[:, 0], x_spec, spec)

    return np.linalg.norm(FS[:, 1] - spec)


f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/211209/CHORUS/'
exp_f = f_loc + 'CHORUS.exp'

Xepr = Xepr_link.load_xepr()
Xepr_link.COMPILATION_TIME = 1.5  # (s)
# change experiment name ("Experiment") if necessary
# NB: no space should be present in the experiment name ("echo") and in the
# phase cycle name ("64-step")
Xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELEXPSlct", "echo")
Xepr.XeprCmds.aqParSet("Experiment", "*ftEpr.PlsSPELLISTSlct", "64-step")

# get rid of potential alteration from previous optimisation
chorus = chorus_pulses()
load_seq(chorus.pulses)

# amplitudes optimization
xbest1, fbest1, msg1 = optimize(Xepr, pars=['aa0', 'aa1', 'aa2'],
                                init=[51.5, 92.5, 99.9],
                                lb=[10, 50, 50],
                                ub=[60, 100, 100],
                                tol=[0.5, 0.5, 0.5],
                                cost_function=maxabsint,
                                optimiser="bobyqa", maxfev=100, nfactor=75)

init = [51.5, np.finfo(float).eps, np.finfo(float).eps,
        np.finfo(float).eps, np.finfo(float).eps]
pars = ['aa0', '&c1', '&c2', '&c3', '&c4']
tol = [0.5, 0.005, 0.005, 0.005, 0.005]
xbest0, fbest, message = optimize(Xepr, pars=pars,
                                  init=init,
                                  lb=[10, -1.2, -1.2, -1.2, -1.2],
                                  ub=[60, 1.2, 1.2, 1.2, 1.2],
                                  tol=tol,
                                  cost_function=min_diff_FS,
                                  optimiser='bobyqa',
                                  maxfev=400, nfactor=80,
                                  callback=shape_impulse,
                                  callback_args=(chorus,))

# run experiment with optimal parameters
data = Xepr_link.run2getdata_exp(Xepr)

# result
FS_path = os.path.join(os.getcwd(), 'FS_inverted.txt')

# read FS
FS = np.loadtxt(FS_path, delimiter=' ')
FS[:, 0] = FS[:, 0] * 1e9  # GHz to Hz

# FS normalisation
FS[:, 1] = FS[:, 1] - FS[1, 1]  # baseline
FS[:, 1] = FS[:, 1]/np.max(FS[:, 1])

# echo data
echo = data.O.real + 1j * data.O.imag
# echo interpolation for better precision on 1st order phase correction
echo = np.interp(np.linspace(1, len(echo), 8*len(echo)),
                 np.linspace(1, len(echo), len(echo)),
                 echo)
# find echo centre
imax = np.argmax(np.abs(echo))
# chop the echo for 1st order phase correction
echo = echo[imax:]
# adjust intensity of first point to avoid baseline error
echo[1] = echo[1]/2

# spectrum
spec = np.fft.fftshift(np.fft.fft(echo, n=8*len(echo)))

# automatic 0th order phase correction
spec_ph = spec
for phi0 in np.linspace(-180, 180, 4*360+1):
    spec_phi0 = spec * np.exp(-1j * phi0 * np.pi/180)
    if sum(np.real(spec_phi0)) > sum(np.real(spec_ph)):
        spec_ph = spec_phi0
spec = np.real(spec_ph)
spec = spec/np.max(spec)

sf = 1 / (0.5e-9/8)  # 0.5ns echo resolution * 8 for interpolation
x_spec = np.linspace(-sf / 2, sf / 2, len(spec))

# interpolate spectrum with xaxis of field sweep
spec = np.interp(FS[:, 0], x_spec, spec)

plt.figure()
plt.plot(FS[:, 0], spec)
plt.plot(FS[:, 0], FS[:, 1])
plt.show()
