Set up an optimisation
======================

To set up an optimisation, you can to create a small python script which:
 - loads an instance Xepr of the XeprAPI,
 - calls the function optimise from esrpoise.

with standard parameters
------------------------

When calling ``optimise()``, you should to at least pass:
 - the Xepr instance,
 - your parameters names, initial values, lower bounds and upper bounds as lists,
 - a cost function, which can be imported from the pre-existing ones (cf. :ref:`costfunctions.py`),
 - the maximum number of function evaluations (not technically mandatory but set to ``0`` by default).

Only a handful of Xepr parameters can be accessed through a simple optimisation (cf. :ref:`Built-in parameters`).

Example of standard parameter optimisation script::

    from esrpoise import xepr_link
    from esrpoise import optimise
    from esrpoise.costfunctions import maxabsint_echo
    
    # load Xepr instance
    xepr = xepr_link.load_xepr()
    
    # fine adjustment of centre field for bisnitroxide sample at X-band
    xbest, fbest, message = optimise(xepr,
                                     pars=['CenterField'],
                                     init=[3450],
                                     lb=[3445],
                                     ub=[3455],
                                     tol=[0.1],
                                     cost_function=maxabsint_echo,
                                     maxfev=20)

Note that ``xepr``, ``pars``, ``init``, ``lb``, ``ub``, ``tol`` need to be input in this order, all other parameters are keywords arguments whose order does not matter.

.. warning:: Make sure to chose an appropriate tolerance for your instrumentation. For example, delays and pulse duration need to be multiple of 2ns on our instrument. We therefore must choose a tolerance which is a multiple of 2ns when optimising those parameters.

with .def file parameters
-------------------------

Optimise parameters from your .def file by indicating their names. In addition to the standard parameter requirements, you should precise:
 - the path of your .exp file,
 - the path of your .def file.

Example (also note the use of several parameters in lists and the optimiser explicit choice)::

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

with user-defined parameters (advanced)
---------------------------------------

To optimise your own parameters, you should define a callback function, used to set up your parameters. The simplest is to define it in your optimisation script (after the imports and before your script code)::

        def my_callback(my_callback_pars_dict, *mycallback_args):
            ""
            Parameters
            ----------
            pars_dict: dictionary
                dictionary with the name of the parameters to optimise as key and
                their value as value
            *mycallback_args
                other possible arguments for callback function
            ""
            # user operations and parameters modifications

Indicate that your parameter is user-defined by including '&' at the start of its name::

        optimise(Xepr, pars=[... , '&_', ...], ...,
                       callback=my_callback, callback_args=my_callback_args)

You can pass arguments (as a tuple) to ``callback`` by using ``callback_pars``.

In the following example, we modify a shape parameter with the module ``mrpypulse`` (bandwidth ``bw`` of an HS1 pulse) ::

    import os
    from esrpoise import xepr_link
    from esrpoise import optimise
    from esrpoise.costfunctions import maxabsint_echo
    from mrpypulse import pulse
    
    
    def shape_bw(callback_pars_dict, shp_nb):
    
        # getting  bw value from the callback parameters to be optimised
        bw = callback_pars_dict["&bw"]
    
        # create hyperbolic sechant shape bw value
        p = pulse.Parametrized(bw=bw, tp=80e-9, Q=5, tres=0.625e-9,
                               delta_f=-65e6, AM="tanh", FM="sech")
    
        p.xepr_file(shp_nb)    # create shape file
    
        # shape path
        path = os.path.join(os.getcwd(), str(shp_nb) + '.shp')
    
        xepr_link.load_shp(xepr, path)  # send shape to Xepr
    
        return None
    
    
    xepr = xepr_link.load_xepr()
    
    #  HS pulse bandwidth optimisation
    xbest, fbest, message = optimise(xepr,
                                     pars=['&bw'],
                                     init=[80e6],
                                     lb=[30e6],
                                     ub=[120e6],
                                     tol=[1e6],
                                     cost_function=maxabsint_echo,
                                     maxfev=120,
                                     nfactor=5,
                                     callback=shape_bw,
                                     callback_args=(7770,))
    # NB: '(7770,)' is equivalent to 'tuple([7770])'

Note that we first have to import the modules, then defining the function before writing the actual optimisation script.

with user-defined cost function (advanced)
------------------------------------------

You can define your own cost function and pass it to the function optimise. Your cost function should treat the data from one of your experiment run to return a single number which will be minimised by the optimiser.

We can for example conduct an optmisation on the spectrum with a zero-filling operation (data is here a simple time-domain FID)::

    import numpy
    from esrpoise import xepr_link
    from esrpoise import optimise
    
    def maxabsint(data):
        """
        Maximises the absolute (magnitude-mode) intensity of the spectrum.
        """
        zero_filling = 4*length(data.O.real)
        spectrum = np.fft.fft(data.O.real + 1j * data.O.imag, n=zero_filling)
        
        return -np.sum(np.abs(spectrum(data)))
    
    
    # load Xepr instance
    xepr = xepr_link.load_xepr()
    
    # fine adjustment of center field for bisnitroxide sample at X-band
    xbest, fbest, message = optimise(xepr,
                                     pars=['CenterField'],
                                     init=[3450],
                                     lb=[3445],
                                     ub=[3455],
                                     tol=[0.1],
                                     cost_function=maxabsint,
                                     maxfev=20)

Setup Tips (advanced)
---------------------
 - Put several optimisations in one script.
 - Automate your actions by using XeprAPI commands, the functions from :ref:`Xepr_link.py` and ``param_set`` from :ref:`main.py`
 - Reuse the best parameter from the optimiser ``xbest``.
 - Use ``callbak`` to add user-specific operation at each iteration. You do not need to indicate user-defined parameters, ``callback_pars_dict`` is sent back empty if no user-defined parameters are found.
 - Use ``acquire_esr.calls`` in your callback function to access the current number of your iteration.
 - Use the parameter ``nfactor`` of ``optimise()`` to expand the distance between the first steps of the optimisers, in particular if you have a low tolerance.
 - Accelerate you optimisation routine if your .shp, .def and .exp file compile fast enough with ``xepr_link.COMPILATION_TIME`` (cf. :ref:``Compilation``)
 - When using a single script with functions, be aware of your variables scope.