"""
costfunctions.py
----------------

Contains some typical cost functions. You can choose to take your cost
functions from here, or create your own.

Cost functions must be defined as follows. They must take one parameter (named
anything you like), which is an instance of the XeprDataset class and
represents a set of ESR data. Then they must return a float, which corresponds
to how 'bad' the spectrum is. The worse the spectrum, the larger the return
value should be.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import numpy as np


def minabsint(data):
    """
    Cost function which minimises the absolute (magnitude-mode) intensity of
    the spectrum.
    """
    mag = np.abs(np.fft.fft(data.O.real + 1j * data.O.imag))
    return np.sum(mag)


def maxabsint(data):
    """
    Cost function which maximises the absolute (magnitude-mode) intensity of
    the spectrum.
    """
    return -np.max(np.abs(np.fft.fft(data.O.real + 1j * data.O.imag)))


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
    return -np.sum(np.real(np.fft.fft(data.O.real,2*len(data.O.real))))


def zerorealint(data):
    """
    Tries to get the intensity of the real spectrum to be as close to zero as
    possible. This works by summation, so dispersion-mode peaks will not
    contribute to this cost function (as they add to zero).
    """
    return np.abs(np.sum(np.fft(data.r)))
