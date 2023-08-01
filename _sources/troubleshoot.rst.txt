Troubleshoot
============

Compilation
-----------

Bugs can be created if ``xepr_link`` does not allow for enough time to let Xepr compile.

Increase the compilation time of the .exp, .def and .shp files (1s by default) with the global variable ``COMPILATION_TIME`` from :ref:`xepr_link.py`:: 

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

If the files are compiling fast enough, decrease ``COMPILATION_TIME`` to accelerate the optimisation routine.


fast .def file modification
---------------------------

ESR-POISE does not use the function ``modif_def_PlsSPELGlbTxt()`` from :ref:`xepr_link.py` despite its ability to modify the .def file variables without referring to the .def file location.

While this function would save a couple of seconds per iteration, it can cause a freeze of the .def file modification, forcing the user to manually interrupt its script::

    Traceback (most recent call last):
      File "crash_def.py", line 6, in <module>
        xepr_link.modif_def(xepr, ['p0'], ['8'])
      File "/home/xuser/xeprFiles/Data/Organic/JB/220511/esrpoise-dev/esrpoise/xepr_link.py", line 190, in modif_def
        currentExp["ftEPR.PlsSPELSetVar"].value = cmdStr
      File "/home/xuser/.local/lib/python3.6/site-packages/XeprAPI/main.py", line 1195, in __getitem__
        return Parameter(self, name)
      File "/home/xuser/.local/lib/python3.6/site-packages/XeprAPI/main.py", line 1243, in __init__
        self._name = self._parent.findParam(name, findall=True)
      File "/home/xuser/.local/lib/python3.6/site-packages/XeprAPI/main.py", line 1139, in findParam
        for par in self.getFuParList(fu):
      File "/home/xuser/.local/lib/python3.6/site-packages/XeprAPI/main.py", line 1096, in getFuParList
        self.aqGetExpFuParList(fu, buf, 10000)
      File "<string>", line 1, in <lambda>
      File "<string>", line 1, in <lambda>
      File "/home/xuser/.local/lib/python3.6/site-packages/XeprAPI/main.py", line 510, in _callXeprfunc
        if self._API.XeprCallFunction(funcidx) != 0:

This bug was observed and reproduced after a few hundred to a few thousand calls to ``modif_def_PlsSPELGlbTxt()``.

Shape loading
-------------

If a bug with shape loading is encountered after a certain number of iterations (typically 114 on older versions of Xepr), it should be solved by reseting Xepr to avoid AWG overloading.
Use the following lines in your callback function (requires to import ``acquire_esr`` from ``esrpoise``):: 

    if acquire_esr.calls % 114 == 0 and acquire_esr.calls != 0:
        print('reset required')
        xepr_link.reset_exp(Xepr)
