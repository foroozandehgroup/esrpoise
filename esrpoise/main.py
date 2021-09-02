"""
main.py
-------

Contains the main code required for executing an optimisation.

SPDX-License-Identifier: GPL-3.0-or-later
"""

from datetime import datetime
import numpy as np

from .optpoise import (scale, unscale, deco_count,
                       nelder_mead, multid_search, pybobyqa_interface)
from . import Xepr_link


def optimize(Xepr,
             pars,
             init,
             lb,
             ub,
             tol,
             cost_function,
             exp_file,
             def_file,
             optimiser="nm",
             maxfev=0,
             nfactor=10,
             callback=None,
             callback_args=None) -> None:
    """
    Run an optimisation.

    TODO: Document inputs properly.

    Parameters
    ----------
    pars : list of str
        Parameter names.
    lb : list of float
        Lower bounds for each parameter.
    ub : list of float
        Upper bounds for each parameter.
    tol : list of float
        Optimisation tolerances for each parameter.
    cost_function : function
        A function which takes the data object and returns a float.
    exp_file : str
        ...
    def_file : str
        ...
    optimiser : str from {"nm", "mds", "bobyqa"}, default "nm"
        Optimisation algorithm to use. The options correspond to Nelder-Mead,
        multidimensional search, and BOBYQA respectively.
    maxfev : int, default 0
        Maximum number of spectra to acquire during the optimisation. The
        default of '0' sets this to 500 times the number of parameters.
    nfactor : int, default 10
        Initial search region relative to tols
    callback: function, default None
        User defined function called when setting up parameters.
    callback_args: tuple, default None
        Arguments for callback function

    Returns
    -------
    xbest : numpy.ndarray
        Numpy array of best values found. First element corresponds to the
        first parameter optimised, etc.
    fbest : float
        Value of the cost function at x = xbest.
    message : str
        A message indicating why the optimisation terminated.
    """
    # Get start time
    tic = datetime.now()

    # Choose the optimisation function. optpoise implements a PyBOBYQA
    # interface so that the returned result has the same attributes as our
    # other optimisers.
    optimfndict = {"nm": nelder_mead,
                   "mds": multid_search,
                   "bobyqa": pybobyqa_interface,
                   }
    try:
        optimfn = optimfndict[optimiser.lower()]
    except KeyError:
        raise ValueError(f"Invalid optimiser {optimiser} specified."
                         f" Allowed values are: {list(optimfndict.keys())}")

    # Scale the initial values and tolerances
    npars = len(pars)
    scaled_x0, scaled_lb, scaled_ub, scaled_xtol = scale(init, lb, ub, tol,
                                                         scaleby="tols")

    # Some logging
    print("\n")
    print("=" * 60)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    fmt = "{:25s} - {}"
    print(fmt.format("Optimisation parameters", pars))
    print(fmt.format("Cost function", cost_function))
    print(fmt.format("Initial values", init))
    print(fmt.format("Lower bounds", lb))
    print(fmt.format("Upper bounds", ub))
    print(fmt.format("Tolerances", tol))
    print(fmt.format("Optimisation algorithm", optimiser))
    print("")
    fmt = "{:^10s}  " * (npars + 1)
    print(fmt.format(*pars, "cf"))
    print("-" * 12 * (npars + 1))

    # Set up optimisation arguments. Basically, this needs to be everything
    # that acquire_esr() uses apart from x itself.
    optimargs = (cost_function, pars, lb, ub, tol,
                 optimiser, Xepr, exp_file, def_file,
                 callback, callback_args)

    # Carry out the optimisation
    opt_result = optimfn(acquire_esr, scaled_x0, scaled_xtol,
                         scaled_lb, scaled_ub,
                         args=optimargs, maxfev=maxfev, nfactor=nfactor)
    best_values = unscale(opt_result.xbest, lb, ub, tol, scaleby="tols")

    # final logging
    toc = datetime.now()
    time_taken = str(toc - tic).split(".")[0]  # remove microseconds

    fmt = "{:27s} - {}"

    print('-' * 40)
    print()
    print(fmt.format("Best values found", round2tol(best_values, tol)))
    print(fmt.format("Cost function at minimum", opt_result.fbest))
    print(fmt.format("Number of experiments ran", acquire_esr.calls))
    print(fmt.format("Total time taken", time_taken))
    print(fmt.format("Optimisation message", opt_result.message))

    # run experiment with optimal parameters
    param_set(Xepr, pars, round2tol(best_values, tol),
              exp_file, def_file,
              callback=callback, callback_args=callback_args)

    Xepr_link.run2getdata_exp(Xepr, "Signal", exp_file)

    print("=" * 60)
    print("\n")

    return best_values, opt_result.fbest, opt_result.message


@deco_count
def acquire_esr(x, cost_function, pars, lb, ub, tol,
                optimiser, Xepr, exp_file, def_file,
                callback=None, callback_args=None):
    """
    This is the function which is actually passed to the optimisation function
    as the "cost function", and is responsible for triggering acquisition in
    Xepr.

    Briefly, this function does the following:

     - Returns np.inf immediately if the values are outside the given bounds.
     - Otherwise, prints the values to stdout, which triggers acquisition by
       the frontend.
     - Waits for the frontend to pass the message "done" back, indicating that
       the spectrum has been acquired and processed.
     - Calculates the cost function using the user-defined cost_function().
     - Performs logging throughout.

    Parameters
    ----------
    x : ndarray
        Scaled values to be used for spectrum acquisition and cost function
        evaluation.
    cost_function : function
        User-defined cost function.

    Returns
    -------
    cf_val : float
        Value of the cost function.
    """

    # Unscale values for acquisition.
    unscaled_val = unscale(x, lb, ub, tol, scaleby="tols")

    # Enforce constraints on optimisation. This doesn't need to be done for
    # BOBYQA, because we pass the `bounds` parameter, which automatically stops
    # it from sampling outside the bounds. If we *do* enforce the constraints
    # on BOBYQA, this can lead to bad errors, as due to floating-point
    # inaccuracy sometimes it tries to sample a point that is *just*
    # outside of the bounds (see foroozandehgroup/nmrpoise#39).  Instead, we
    # should just let it evaluate the point as usual.
    if (optimiser in ["nm", "mds"] and
            (np.any(unscaled_val < lb) or np.any(unscaled_val > ub))):
        # Set the value of the cost function to infinity.
        cf_val = np.inf
        # Log that.
        # print(fstr.format(*unscaled_val, cf_val))
        # Return immediately.
        return cf_val

    # convert parameters values to string with the same number of decimals as
    # tolerances
    val_str = round2tol(unscaled_val, tol)

    # Xepr reset needed for 114 sequential shape load and run
    if acquire_esr.calls % 114 == 0 and acquire_esr.calls != 0:
        print('reset required')
        # Xepr_link.reset_exp(Xepr) # reset currently not working

    # set parameters values
    param_set(Xepr, pars, val_str, exp_file, def_file, callback, callback_args)

    # record data
    data = Xepr_link.run2getdata_exp(Xepr, "Signal", exp_file)

    # evaluate the cost function
    cf_val = cost_function(data)

    # log
    fstr = "{:^10.4f}  " * (len(x) + 1)  # Format string for logging

    # print(fstr.format(*unscaled_val, cf_val)) # optimizer values

    # print values sent to Xepr
    print(fstr.format(*np.array(val_str).astype(np.float), cf_val))

    return cf_val


def round2tol(values, tols):
    """
    Round values to closest multiple of tolerance

    Parameters
    ----------
    values :
        numpy 1D-array of the values to round
    tol :
        numpy 1D-array of the parameters tolerances

    Returns
    -------
    values_str :
        rounded values as a list of strings
    """

    values_str = list()
    for val, tol in zip(values, tols):

        # round to tolerance multiple
        val = tol * np.round(val / tol)
        tol_str = str(tol)

        if '.' not in tol_str:  # integer case # tol.is_integer()
            values_str.append(str(int(val)))
        elif tol.is_integer():  # float which is an integer case
            values_str.append(str(int(val)))
        else:  # float case
            decimal_nb = len(tol_str[tol_str.index('.'):-1])
            # round to same number of decimal numbers
            values_str.append(str(np.round(val, decimal_nb)))

    return values_str


def param_set(Xepr, pars, val_str,
              exp_file, def_file,
              callback=None, callback_args=None):
    """
    Set a variety of parameters in Xepr

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    pars :
        name of parameters to be set in Xepr
    val_str:
        values of the parameters in string format
    exp_file: string
        experiment file path
    def_file: string
        definition file path
    callback: function
        user defined function
    callback_args: tuple
        arguments for the user defined function

    Returns
    -------
    None
    """
    callback_pars_dict = dict()

    def_modif = False
    pars_def = list()
    val_str_def = list()

    for par, val in zip(pars, val_str):
        # Remarks:
        #  - Xepr.XeprCmds.aqParSet does not accept val_str if numpy array of
        #    strings
        #  - Parameters set up with sliders need compensation for an
        #    automatic step made by Xepr (Fine -1)

        # User - callback parameters
        callback_pars_dict[par] = float(val)  # TODO look into better way
        if '&' in par:
            pass

        # Bridge - Receiver Unit
        elif par == "VideoGain":
            # Video gain (dB), 0 to 48 (1MHz bandwidth),min tolerance of 6
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.VideoGain", val)
        elif par == "Attenuation":
            # High power attenuation (dB), ,min tolerance of 0.01
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.Attenuation", val)
        elif par == "SignalPhase":
            # Signal phse (~0.129deg), min tolerance of 1
            Xepr.XeprCmds.aqParSet("AcqHidden", "cwBridge.SignalPhase", val)
        elif par == "TMLevel":
            # Transmitter level (%), min tolerance of 0.049
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.TMLevel", val)
            Xepr.XeprCmds.aqParStep("AcqHidden", "ftBridge.TMLevel", "Fine 1")

        # Bridge - MPFU control
        # (%), 0 to 100, rounded in Xepr to closest 0.049 (approximately)
        elif par == "BrXPhase":  # +<x> Phase
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrXPhase", val)
        elif par == "BrXAmp":  # +<x> Amplitude
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrXAmp", val)
        elif par == "BrYPhase":  # +<y> Phase
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrYPhase", val)
        elif par == "BrYAmp":  # +<y> Amplitude
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrYAmp", val)
        elif par == "BrMinXPhase":  # -<x> Phase
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrMinXPhase", val)
        elif par == "BrMinXAmp":  # -<x> Amplitude
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrMinXAmp", val)
        elif par == "BrMinYPhase":  # -<y> Phase
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrMinYPhase", val)
        elif par == "BrMinYAmp":  # -<y> Amplitude
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrMinYAmp", val)

        # FT EPR Parameters
        elif par == "CenterField":
            # Field Position (G), variation around expected value, min
            # tolerance of 0.05
            Xepr.XeprCmds.aqParSet("Experiment", "fieldCtrl.CenterField", val)

        # save .def file parameters in list
        else:
            def_modif = True
            pars_def.append(par)
            val_str_def.append(val)

    # set user parameters
    if callback is not None:
        callback(callback_pars_dict, *callback_args)

    # set parameters in definition file
    if def_modif:

        Xepr_link.modif_def(Xepr, def_file, pars_def, val_str_def)

        # .exp file load (necessary to update .def)
        Xepr_link.load_exp(Xepr, exp_file)
