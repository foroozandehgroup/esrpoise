"""
costfunctions.py
----------------

Contains some typical cost functions. You can choose to take your cost
functions from here, or create your own.

Cost functions must be defined as follows. They must take one parameter (named
anything you like), which is an instance of the XeprDataset class and
represents a set of ESR data. Then they must return a float, which corresponds
to how 'bad' the data is. The worse the data, the larger the return
value should be.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import numpy as np


# spectrum.
def spectrum(data):
    return np.fft.fft(data.O.real + 1j * data.O.imag)


def minabsint(data):
    """
    Minimises the absolute (magnitude-mode) intensity of the spectrum.
    """
    return np.sum(spectrum(data))


def maxabsint(data):
    """
    Maximises the absolute (magnitude-mode) intensity of the spectrum.
    """
    return -minabsint(data)


def minrealint(data):
    """
    Minimises the intensity of the real part of the spectrum. If the spectrum
    has negative peaks this cost function will try to maximise those.
    """
    return np.sum(np.real(spectrum(data)))


def maxrealint(data):
    """
    Maximises the intensity of the real part of the spectrum.
    """
    return -minrealint(data)


def minmagint(data):
    """
    Minimises the intensity of the imagignary part of the spectrum. If the
    spectrum has negative peaks this cost function will try to maximise those.
    """
    return np.sum(np.imag(spectrum(data)))


def maximagint(data):
    """
    Maximises the intensity of the real part of the spectrum.
    """
    return -minmagint(data)


def zerorealint(data):
    """
    Tries to get the intensity of the real spectrum to be as close to zero as
    possible. This works by summation, so dispersion-mode peaks will not
    contribute to this cost function (as they add to zero).
    """
    return np.abs(np.sum(np.fft(data.O.real)))


def zeroimagint(data):
    """
    Tries to get the intensity of the imaginary spectrum to be as close to zero
    as possible.
    """
    return np.abs(np.sum(np.fft(data.O.imag)))


# echo
def minabsint_echo(data):
    """
    Minimises the absolute (magnitude-mode) intensity of the echo.
    """
    return np.sum(np.abs(data.O.real + 1j * data.O.imag))


def maxabsint_echo(data):
    """
    Maximises the absolute (magnitude-mode) intensity of the echo.
    """
    return -minabsint_echo(data)


def minrealint_echo(data):
    """
    Minimises the maximum intensity of the real part of the echo.
    """
    return np.sum(data.O.real)


def maxrealint_echo(data):
    """
    Maximises the maximum intensity of the real part of the echo.
    """
    return -minrealint_echo(data)


def minimagint_echo(data):
    """
    Minimises the maximum intensity of the imaginary part of the echo.
    """
    return np.sum(data.O.imag)


def maximagint_echo(data):
    """
    Maximises the maximum intensity of the real part of the echo.
    """
    return -minimagint_echo(data)


def minabsmax_echo(data):
    """
    Minimises the absolute (magnitude-mode) maximum of the echo.
    """
    return np.max(np.abs(data.O.real + 1j * data.O.imag))


def maxabsmax_echo(data):
    """
    Maximises the absolute (magnitude-mode) maximum of the echo.
    """
    return -minabsmax_echo(data)


def minrealmax_echo(data):
    """
    Minimises the maximum of the real part of the echo.
    """
    return np.max(data.O.real)


def maxrealmax_echo(data):
    """
    Maximises the maximum of the real part of the echo.
    """
    return -minrealmax_echo(data)


def minimagmax_echo(data):
    """
    Minimises the maximum of the imaginary part of the echo.
    """
    return np.max(data.O.imag)


def maximagmax_echo(data):
    """
    Maximises the maximum of the imaginary part of the echo.
    """
    return -minimagmax_echo(data)


# DEER trace modulation depth
def max_n2p(data):
    """
    Maximizes n2p parameter for DEER trace
    Data should contain the 2 points of interest in position 0 and 1.
    """
    return -np.abs(data.O.real[0]-data.O.real[1])
