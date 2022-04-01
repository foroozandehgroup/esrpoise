Troubleshoot
============

Compilation
-----------

Bugs can be created if ``xepr_link`` does not allow enough time for compilation.

Increase the compilation time of the .exp, .def and .shp files (1s by default) with the global variable ``COMPILATION_TIME`` from ``Xepr_link``:: 

    xepr_link.COMPILATION_TIME = 2  # (s)
    
    xepr = xepr_link.load_xepr()
    
    # .exp and .def files location
    location = '/home/xuser/xeprFiles/Data/'
    exp_f = location + '2pflip.exp'
    def_f = location + '2pflip.def'
    
    # optimisation of pulse length and amplitude
    xbest, fbest, message = optimise(xepr,
                                     pars=["p0", "Attenuation"],
                                     init=[8, 5],
                                     lb=[2, 0],
                                     ub=[36, 10],
                                     tol=[2, 0.5],
                                     cost_function=maxabsint_echo,
                                     exp_file=exp_f,
                                     def_file=def_f,
                                     optimiser="bobyqa",
                                     maxfev=20)
    
    # run experiment with optimal parameters
    xepr_link.run2getdata_exp(xepr, "Signal", exp_f)

When decreased, ``COMPILATION_TIME`` can be used to accelerate an optimisation routine if the files are compiling fast enough.

Shape loading
-------------

If a bug with shape loading is encountered after a certain number of iterations (typically 114 on older versions of Xepr), it should be solved by reseting Xepr to avoid AWG overloading.
Use the following lines in your callback function (requires to import ``acquire_esr`` from ``esrpoise``):: 

    if acquire_esr.calls % 114 == 0 and acquire_esr.calls != 0:
        print('reset required')
        xepr_link.reset_exp(Xepr)
