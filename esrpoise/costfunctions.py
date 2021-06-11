"""
costfunctions.py
----------------

Contains default cost functions. Custom cost functions should be added in
costfunctions_user.py (using the same format).

You can add custom cost functions in here (they will work), but they will be
shadowed by any similarly named cost functions in costfunctions_user.py. Also,
this file will be overwritten if POISE is reinstalled.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import numpy as np


def minabsint(data):
    """
    Cost function which minimises the absolute (magnitude-mode) intensity of
    the spectrum. This is probably the easiest cost function. :-)
    """
    mag = np.abs(np.fft(data.r + 1j * data.i))
    # The intensity of the magnitude-mode spectrum is just the sum of all
    # points.
    return np.sum(mag)


def maxabsint(data):
    """
    Cost function which maximises the absolute (magnitude-mode) intensity of
    the spectrum.
    """

    # This is the same as minabsint except that we have a negative sign.
    # Because the optimisation always seeks to *minimise* the cost function,
    # this essentially tries to *maximise* np.sum(...), i.e. maximise the
    # spectral intensity.
    return -np.sum(np.abs(np.fft(data.r + 1j * data.i)))


def minrealint(data):
    """
    Minimises the intensity of the real part of the spectrum. If the spectrum
    has negative peaks this cost function will try to maximise those.
    """
    return np.sum(np.fft(data.r))


def maxrealint(data):
    """
    Maximises the intensity of the real part of the spectrum.
    """
    return -np.sum(np.fft(data.r))


def zerorealint(data):
    """
    Tries to get the intensity of the real spectrum to be as close to zero as
    possible. This works by summation, so dispersion-mode peaks will not
    contribute to this cost function (as they add to zero).
    """
    return np.abs(np.sum(np.fft(data.r)))