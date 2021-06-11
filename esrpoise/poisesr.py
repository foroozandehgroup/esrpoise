"""
 Optimizer (largely taken from Jon's code backend.py)
"""

import os
#import sys
#import json
#from traceback import print_exc
from datetime import datetime
#from pathlib import Path
#from contextlib import contextmanager

import numpy as np

from .optpoise import (scale, unscale, deco_count,
                       nelder_mead, multid_search, pybobyqa_interface)
from .shared import _g
from .cfhelpers import *
from . import costfunctions
from . import costfunctions_user

import Xepr_link

def optimize(routine):
    """
    Wrapper for main(). This performs several tasks:
      1. Reads in the global variables printed by the frontend.
      2. Implements a context manager to print the backend PID to a file
         ($ts/py/user/poise_backend/pid.log), deleting the file after the
         backend completes.
      3. Catches all exceptions, propagates them to the frontend by printing to
         stdout, and prints the full traceback to the backend error log.
    """
    with pidfile() as _:
        try:
            from .shared import _g
            
            # Set global variables with input parameters
            
            _g.optimiser = routine.optimizer_type
            _g.routine_id = routine.name
            _g.maxfev = routine.maxfev
            
            # paths for log save in current directory
            _g.p_optlog = os.getcwd() / "poise.log"
            _g.p_errlog = os.getcwd() / "poise_err_backend.log"

            
            # run main
            main(routine)
        except Exception as e:
            print(f"Main wrapper error")


def main(routine):
    
    tic = datetime.now()
        
    # Load the cost function. Try to get from user first.
    cost_function = getattr(costfunctions_user, routine.cf, None)
    # If it failed, get from system.
    if cost_function is None:
        cost_function = getattr(costfunctions, routine.cf, None)
    # If that failed too, then error out.
    if cost_function is None:
        raise AttributeError(f"No such cost function {routine.cf}.")
        
    # Choose the optimisation function. optpoise implements a PyBOBYQA
    # interface so that the returned result has the same attributes as our
    # other optimisers.
    optimfndict = {"nm": nelder_mead,
                   "mds": multid_search,
                   "bobyqa": pybobyqa_interface
                   }
    try:
        optimfn = optimfndict[_g.optimiser.lower()]
    except KeyError:
        raise ValueError(f"Invalid optimiser {_g.optimiser} specified.")

    # Scale the initial values and tolerances
    npars = len(routine.pars)
    scaled_x0, scaled_lb, scaled_ub, scaled_xtol = scale(routine.init,
                                                         routine.lb,
                                                         routine.ub,
                                                         routine.tol,
                                                         scaleby="tols")

    # Some logging
    with open(_g.p_optlog, "a") as log:
        print("\n\n\n", file=log)
        print("=" * 40, file=log)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file=log)
        fmt = "{:25s} - {}"
        print(fmt.format("Routine name", routine.name), file=log)
        print(fmt.format("Optimisation parameters", routine.pars), file=log)
        print(fmt.format("Cost function", routine.cf), file=log)
        print(fmt.format("Initial values", routine.init), file=log)
        print(fmt.format("Lower bounds", routine.lb), file=log)
        print(fmt.format("Upper bounds", routine.ub), file=log)
        print(fmt.format("Tolerances", routine.tol), file=log)
        print(fmt.format("Optimisation algorithm", _g.optimiser), file=log)
        print("", file=log)
        fmt = "{:^10s}  " * (npars + 1)
        print(fmt.format(*routine.pars, "cf"), file=log)
        print("-" * 12 * (npars + 1), file=log)
        
    # Set up optimisation arguments
    optimargs = (cost_function, routine)
    # Carry out the optimisation
    opt_result = optimfn(acquire_esr, scaled_x0, scaled_xtol,
                         scaled_lb, scaled_ub,
                         args=optimargs, maxfev=_g.maxfev)

    best_values = unscale(opt_result.xbest, routine.lb,
                          routine.ub, routine.tol, scaleby="tols")
    
    print(f"optima: {' '.join([str(i) for i in best_values])}")
    
    # Strip newlines from the opt result message, just in case (because the
    # frontend only expects one line of text here, feeding it more than one
    # line of text will confuse it)
    print(opt_result.message.replace("\n", " ").replace("\r", " ")) # not needed?

    # More logging
    toc = datetime.now()
    time_taken = str(toc - tic).split(".")[0]  # remove microseconds
    with open(_g.p_optlog, "a") as log:
        print("", file=log)
        fmt = "{:27s} - {}"
        print(fmt.format("Best values found", best_values.tolist()), file=log)
        print(fmt.format("Cost function at minimum", opt_result.fbest),
              file=log)
        print(fmt.format("Number of experiments ran", acquire_esr.calls),
              file=log)
        print(fmt.format("Total time taken", time_taken), file=log)


@deco_count
def acquire_esr(x, cost_function, routine):
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
        User-defined cost function object.
    routine : Routine
        The active optimisation routine.

    Returns
    -------
    cf_val : float
        Value of the cost function.
    """
    unscaled_val = unscale(x, routine.lb, routine.ub,
                           routine.tol, scaleby="tols")
    # Format string for logging.
    fstr = "{:^10.4f}  " * (len(x) + 1)

    with open(_g.p_optlog, "a") as logf:
        
        # Enforce constraints on optimisation.
        # This doesn't need to be done for BOBYQA, because we pass the `bounds`
        # parameter, which automatically stops it from sampling outside the
        # bounds. If we *do* enforce the constraints on BOBYQA, this can lead
        # to bad errors, as due to floating-point inaccuracy sometimes it tries
        # to sample a point that is ___just___ outside of the bounds (see #39).
        # Instead, we should just let it evaluate the point as usual.
        if (_g.optimiser in ["nm", "mds"] and
                (np.any(unscaled_val < routine.lb)
                 or np.any(unscaled_val > routine.ub))):
            
            # Set the value of the cost function to infinity.
            cf_val = np.inf
            
            # Log that.
            print(fstr.format(*unscaled_val, cf_val), file=logf)
            
            # Return immediately.
            return cf_val

        # Print unscaled values
        print("values: " + " ".join([str(i) for i in unscaled_val]))
        
        # load exp file
        Xepr_link.load_exp(routine.exp_file)
    
        # load def file
        Xepr_link.load_def(routine.def_file)
        
        # send unscaled values to Xepr
        Xepr_link.modif_def(routine.pars, x)

        # run experiment to get data
        data = Xepr_link.run2getdata_exp("Signal", routine.exp_file)
    
        # Evaluate the cost function
        cf_val = cost_function(data)
        
        # log
        fstr = "{:^10.4f}  " * (len(x) + 1)
        print(fstr.format(*unscaled_val, cf_val), file=logf)
        print(f"cf: {cf_val}")
        
        return cf_val
