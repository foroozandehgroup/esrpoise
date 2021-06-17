"""
main.py
-------

Contains the main code required for executing an optimisation.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
from datetime import datetime
import time

import numpy as np

from .optpoise import (scale, unscale, deco_count,
                       nelder_mead, multid_search, pybobyqa_interface)
from . import costfunctions
from . import Xepr_link


def optimize(pars,
             init,
             lb,
             ub,
             tol,
             cost_function,
             exp_file,
             def_file,
             optimiser="nm",
             maxfev=0
             ) -> None:
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
    print("\n\n\n")
    print("=" * 40)
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

    # Initialise Xepr module
    Xepr = Xepr_link.load_xepr()

    # Set up optimisation arguments. Basically, this needs to be everything
    # that acquire_esr() uses apart from x itself.
    optimargs = (cost_function, pars, lb, ub, tol,
                 optimiser, Xepr, exp_file, def_file)
    # Carry out the optimisation
    opt_result = optimfn(acquire_esr, scaled_x0, scaled_xtol,
                         scaled_lb, scaled_ub,
                         args=optimargs, maxfev=maxfev)
    best_values = unscale(opt_result.xbest, lb, ub, tol, scaleby="tols")

    print(f"optima: {' '.join([str(i) for i in best_values])}")

    # More logging
    toc = datetime.now()
    time_taken = str(toc - tic).split(".")[0]  # remove microseconds
    print()
    fmt = "{:27s} - {}"
    print(fmt.format("Best values found", best_values.tolist()))
    print(fmt.format("Cost function at minimum", opt_result.fbest))
    print(fmt.format("Number of experiments ran", acquire_esr.calls))
    print(fmt.format("Total time taken", time_taken))

    return best_values, opt_result.fbest, opt_result.message


@deco_count
def acquire_esr(x, cost_function, pars, lb, ub, tol,
                optimiser, Xepr, exp_file, def_file):
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

    # Otherwise, here we should trigger acquisition.
    # TODO
    # make different cases depending on the parameter type?
    #    - rounding of specific parameters
    #         ex: param_val = np.round(unscaled_val/2)*2 # round to 2 ns for
    #             pulse lengths
    #    - modify exp file?
    #
    # create some space that the user can use to implement his own parameter
    # modif
    #    - pulse shapes -> require to modify acquire_esr
    #    - exp/def file -> not useful?

    # round parameters and transform them into integers
    param_val = np.round(unscaled_val)
    param_val = param_val.astype(int)

    # def file modification and load
    Xepr_link.modif_def2(Xepr, def_file, pars, param_val.astype(str))

    # exp file load
    Xepr_link.load_exp(Xepr, exp_file)

    # time to let Xepr finish compiling
    time.sleep(1)

    # record data
    data = Xepr_link.run2getdata_exp(Xepr, "Signal", exp_file)

    # evaluate the cost function
    cf_val = cost_function(data)

    # log
    fstr = "{:^10.4f}  " * (len(x) + 1)  # Format string for logging
    print(fstr.format(*unscaled_val, cf_val))
    print(fstr.format(*param_val, cf_val))

    return cf_val
