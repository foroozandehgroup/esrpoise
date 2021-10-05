"""
main.py
-------

Contains the main code required for executing an optimisation.

SPDX-License-Identifier: GPL-3.0-or-later

"""

from datetime import datetime
import numpy as np

from .optpoise import (scale, unscale, deco_count,
                       nelder_mead, multid_search, pybobyqa_interface,
                       brute_force)
from . import Xepr_link


def optimize(Xepr,
             pars,
             init,
             lb,
             ub,
             tol,
             cost_function,
             exp_file=None,
             def_file=None,
             optimiser="nm",
             maxfev=0,
             nfactor=10,
             callback=None,
             callback_args=None) -> None:
    """
    Run an optimisation.

    Parameters
    ----------
    Xepr : instance of XeprAPI.Xepr
        The instantiated Xepr object.
    pars : list of str
        Parameter names. Parameters starting with the character & are
        considered user parameters which needs to be modified with the callback
        function.
    lb : list of float
        Lower bounds for each parameter.
    ub : list of float
        Upper bounds for each parameter.
    tol : list of float
        Optimisation tolerances for each parameter.
    cost_function : function
        A function which takes the data object and returns a float.
    exp_file : str, default None
        Experiment file (.exp) path to be used for the experiment in Xepr.
        Required to modify parameters in .def file.
    def_file : str, default None
        Definition file (.exp) path to be used for the experiment in Xepr.
        Required to modify parameters in .def file.
    optimiser : str from {"nm", "mds", "bobyqa", "brute"}, default "nm"
        Optimisation algorithm to use. The options correspond to Nelder-Mead,
        multidimensional search, BOBYQA, and brute-force search respectively.
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

    To quit the optimization, simply type 'ctlr+C' in the terminal.
    It is recommended to do so during an acquisition phase of Xepr to avoid
    Xepr crashes.
    """
    # Get start time
    tic = datetime.now()

    # Choose the optimisation function. optpoise implements a PyBOBYQA
    # interface so that the returned result has the same attributes as our
    # other optimisers.
    optimfndict = {"nm": nelder_mead,
                   "mds": multid_search,
                   "bobyqa": pybobyqa_interface,
                   "brute": brute_force,
                   }
    try:
        optimfn = optimfndict[optimiser.lower()]
    except KeyError:
        raise ValueError(f"Invalid optimiser {optimiser} specified."
                         f" Allowed values are: {list(optimfndict.keys())}")

    # Scale the initial values and tolerances
    npars = len(pars)
    # input length chek
    if npars != len(init):
        raise ValueError("pars and init should have the same length.")
    if npars != len(lb):
        raise ValueError("pars and lb should have the same length.")
    if npars != len(ub):
        raise ValueError("pars and ub should have the same length.")
    if npars != len(tol):
        raise ValueError("pars and tol should have the same length.")
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
    optimargs = (cost_function, pars, lb, ub, tol, optimiser,
                 Xepr, exp_file, def_file,
                 callback, callback_args)

    # Carry out the optimisation
    acquire_esr.calls = 0  # ensures that each optim starts from 0
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
    print(fmt.format("Best values found", round2tol_str(best_values, tol)))
    print(fmt.format("Cost function at minimum", opt_result.fbest))
    print(fmt.format("Number of experiments ran", acquire_esr.calls))
    print(fmt.format("Total time taken", time_taken))
    print(fmt.format("Optimisation message", opt_result.message))
    print("=" * 60)
    print("\n")

    # TODO return string actually input for parameters?
    # context: reuse previously optimized values
    # in particular, check with mpfu phases values
    # return best_values as string
    # Jon's advice: return a class with all the information

    return best_values, opt_result.fbest, opt_result.message


def run_optimized(Xepr, pars, best_values,
                  exp_file=None, def_file=None,
                  callback=None, callback_args=None):
    """
    Run the experiments with the optimized parameters
    """
    # TODO fix this function
    # run experiment with optimal parameters
    param_set(Xepr, pars, best_values,
              exp_file, def_file,
              callback=callback, callback_args=callback_args)

    Xepr_link.run2getdata_exp(Xepr, "Signal", exp_file)


@deco_count
def acquire_esr(x, cost_function, pars, lb, ub, tol, optimiser,
                Xepr, exp_file=None, def_file=None,
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
    pars : list of str
        Parameter names. Parameters starting with the character & are
        considered user parameters which needs to be modified with the callback
        function.
    lb : list of float
        Lower bounds for each parameter.
    ub : list of float
        Upper bounds for each parameter.
    tol : list of float
        Optimisation tolerances for each parameter.
    optimiser : str from {"nm", "mds", "bobyqa", "brute"}, default "nm"
        Optimisation algorithm to use. The options correspond to Nelder-Mead,
        multidimensional search, BOBYQA, and brute-force search respectively.
    Xepr : instance of XeprAPI.Xepr TODO doc
        The instantiated Xepr object.
    cost_function : function
        A function which takes the data object and returns a float.
    exp_file : str, default None
        Experiment file (.exp) path to be used for the experiment in Xepr.
        Required to modify parameters in .def file.
    def_file : str, default None
        Definition file (.exp) path to be used for the experiment in Xepr.
        Required to modify parameters in .def file.
    callback: function, default None
        User defined function called when setting up parameters.
    callback_args: tuple, default None
        Arguments for callback function

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

    # set parameters values
    param_set(Xepr, pars, unscaled_val, tol,
              exp_file, def_file, callback, callback_args)

    # record data
    data = Xepr_link.run2getdata_exp(Xepr)

    # evaluate the cost function
    cf_val = cost_function(data)

    # log
    fstr = "{:^10.4f}  " * (len(x) + 1)  # Format string for logging

    # print(fstr.format(*unscaled_val, cf_val)) # optimizer values

    # print values sent to Xepr
    print(fstr.format(*np.array(
        round2tol_str(unscaled_val, tol)).astype(np.float), cf_val))

    return cf_val


def round2tol_str(values, tols):
    """
    Round values to closest multiple of tolerance

    Parameters
    ----------
    values : list or ndarray
        values to round
    tol : list or ndarray
        values tolerances

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


def param_set(Xepr, pars, val, tol,
              exp_file=None, def_file=None,
              callback=None, callback_args=None):
    """
    Set a variety of parameters in Xepr

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    pars : list of str
        Parameter names. Parameters starting with the character & are
        considered user parameters which needs to be modified with the callback
        function.
    val : list of floats or ndarray
        values of the parameters
    tol : list of float
        Optimisation tolerances for each parameter.
    exp_file : str, default None
        Experiment file (.exp) path to be used for the experiment in Xepr.
        Required to modify parameters in .def file.
    def_file : str, default None
        Definition file (.exp) path to be used for the experiment in Xepr.
        Required to modify parameters in .def file.
    callback: function, default None
        User defined function called when setting up parameters.
    callback_args: tuple, default None
        Arguments for callback function

    Returns
    -------
    None
    """

    # convert parameters values to string with the same number of decimals as
    # tolerances
    val_str = round2tol_str(val, tol)

    def_modif = False
    pars_def = list()
    val_str_def = list()

    for par, v_str in zip(pars, val_str):
        # Remarks:
        #  - Xepr.XeprCmds.aqParSet does not accept v_str if numpy array of
        #    strings

        # user parmeters
        if '&' in par:
            if callback is None:
                raise TypeError('callback should not be None if user '
                                'parameters (name starting with &) are used.')

        # Xepr parameters: Bridge - Receiver Unit
        elif par == "VideoGain":
            # Video gain (dB), 0 to 48 (1MHz bandwidth),min tolerance of 6
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.VideoGain", v_str)
        elif par == "Attenuation":
            # High power attenuation (dB), ,min tolerance of 0.01
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.Attenuation", v_str)
        elif par == "SignalPhase":
            # Signal phse (~0.129deg), min tolerance of 1
            Xepr.XeprCmds.aqParSet("AcqHidden", "cwBridge.SignalPhase", v_str)
        elif par == "TMLevel":
            # Transmitter level (%), min tolerance of 0.049
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.TMLevel", v_str)

        # Xepr parameters: Bridge - MPFU control
        # (%), 0 to 100, rounded in Xepr to closest 0.049
        # (approximately, not linear)
        elif par == "BrXPhase":  # +<x> Phase
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrXPhase", v_str)
        elif par == "BrXAmp":  # +<x> Amplitude
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrXAmp", v_str)
        elif par == "BrYPhase":  # +<y> Phase
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrYPhase", v_str)
        elif par == "BrYAmp":  # +<y> Amplitude
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrYAmp", v_str)
        elif par == "BrMinXPhase":  # -<x> Phase
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrMinXPhase", v_str)
        elif par == "BrMinXAmp":  # -<x> Amplitude
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrMinXAmp", v_str)
        elif par == "BrMinYPhase":  # -<y> Phase
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrMinYPhase", v_str)
        elif par == "BrMinYAmp":  # -<y> Amplitude
            Xepr.XeprCmds.aqParSet("AcqHidden", "ftBridge.BrMinYAmp", v_str)

        # Xepr parameters: FT EPR Parameters
        elif par == "CenterField":
            # Field Position (G), variation around expected value, min
            # tolerance of 0.05
            Xepr.XeprCmds.aqParSet(
                "Experiment", "fieldCtrl.CenterField", v_str)

        # Xepr parameters: .def file
        else:
            def_modif = True
            # save .def file parameters in list
            pars_def.append(par)
            val_str_def.append(v_str)

    # set user parameters
    if callback is not None:
        # user parameters grouped in a dictionary
        callback(dict(zip(pars, val)), *callback_args)

    # set parameters in definition file
    if def_modif:

        if def_file is None:
            raise ValueError('Some parameters are considered .def file '
                             'parameters. The file path def_file is '
                             'required to modify them.')
        Xepr_link.modif_def(Xepr, def_file, pars_def, val_str_def)

        if exp_file is None:
            raise ValueError('Some parameters are considered .def file '
                             'parameters. The experiment file path '
                             'exp_file is required to modify them.')
        Xepr_link.load_exp(Xepr, exp_file)
