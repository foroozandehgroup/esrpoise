"""
Xepr_link.py
------------

Xepr interface functions (largely taken from David's code)

modif_def should be enough to modify any parameter in the def file
TBD: modif_exp, modif_shp +modif_def_file?


###  Code inherited from David ###

[Grouped in one package] Python functions to communicate with Xepr using
XeprAPI
    - Xepr_getdata.py -> run2getdata_exp
    - Xepr_plsspel_deffile.py -> load_def
    - Xepr_plsspel_moddefs.py -> modif_def
    - Xepr_plsspel_expfile.py -> load_exp
    - Xepr_restexpt.py        -> reset_exp
    - Xepr_plsspel_shpfile.py -> load_shp
Other functions from David:
    - plsspel2spinach_ox.m -> create .exp file
    - spinach2plsspel_ox.m -> select experiment and dimension in the .exp file
    - awg_shp_ox.m         -> create .shp file
    - [to be replaced by something simpler?] awg_interface_ox.m -> interface
    using py_run_ox to run the  ifferent Python files
        - contains different cases (def file, no def file ...)
    - [not needed] py_run_ox.m -> allows to run a Python file
    - [not needed] optimization functions

SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
import sys


def load_xepr():
    """
    Initialise the Xepr module and return the Xepr object thus created.

    Parameters
    ----------
    None

    Returns
    -------
    Xepr : instance of XeprAPI.Xepr
        The instantiated Xepr object, used for communication with
        Xepr-the-programme.
    """
    # xepr import -> use XeprAPI compatible with Python 3.7
    #try:
    # The correct location of the XeprAPI module should be inserted into
    # the code below -> could be avoided if installed with pip3?
    # This locates the XeprAPI module
    """sys.path.insert(0, os.popen("Xepr --apipath").read())
        sys.path.extend([
            '/opt/Bruker/xepr/sharedProDeL/Examples/XeprAPI-examples',
            '/opt/Bruker/xepr/sharedProDeL/Standard/XeprAPI',
    ])"""
    import XeprAPI         # load the Xepr API module
    Xepr = XeprAPI.Xepr()  # start Xepr API module

    return Xepr


def load_exp(Xepr, exp_file):
    """
    Load and compile an Xepr experiment file.

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    exp_file : str
        The Xepr experiment file (the full path with .exp extension).

    Returns
    -------
    None
    """
    try:
        Xepr.XeprCmds.aqPgLoad(exp_file)
        Xepr.XeprCmds.aqPgShowPrg()
        Xepr.XeprCmds.aqPgCompValid()
        Xepr.XeprCmds.aqPgCompile()
    except Exception:
        print("program_load_compile_error")
        sys.exit(3)


def load_def(Xepr, def_file):
    """
    Load and compile an Xepr definition file.

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    def_file : str
        Name of the Xepr definition file (full path with .def extension).

    Returns
    -------
    None
    """
    try:
        Xepr.XeprCmds.aqPgDefLoad(def_file)
        Xepr.XeprCmds.aqPgShowDef()
        Xepr.XeprCmds.aqPgCompile()
    except Exception:
        print("definitions_load_compile_error")
        sys.exit(3)


def modif_def(Xepr, def_file, var_name, var_value):
    """
    Directly modify definitions in the current experiment.

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    var_name : list of str)
        Variable names as named in the .def file.
    var_value : list of str
        List of variable values to be input.

    Returns
    -------
    None
    """
    try:
        currentExp = Xepr.XeprExperiment()
    except Exception:
        print("No Experiment has been selected in the"
              " Primary Viewport of Xepr.")
        sys.exit(2)

    # get the start value for the variable
    # search for our desired variable
    # first get the text of the full PulseSpel def
    fullDefs = currentExp.getParam("PlsSPELGlbTxt").value
    # need to check if fullDefs is empty and exit cause pulsespel not being
    # loaded

    fullDefs = fullDefs.split("\n")

    for i, var_name_i in enumerate(var_name):
        cmdStr = (var_name_i
                  + " = "
                  + var_value[i])
        #print(cmdStr)
        for line in fullDefs:
    
            l = line.replace(" ", "") # getting rid of spaces
    
            l = l[0:len(var_name_i)+1] # selecting the first characters
    
            if var_name_i+"=" == l:
                currentExp["ftEPR.PlsSPELSetVar"].value = cmdStr
   
    # only works with short files and simple expressions
    #     ex: aa0 = 5+c can reset to aa0 = 5)

def modif_def2(Xepr, def_file, var_name, var_value):
    """
    Modify definitions by modifying the .def file and reloading it

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    var_name : list of str)
        Variable names as named in the .def file.
    var_value : list of str
        List of variable values to be input.

    Returns
    -------
    None
    """

    with open(def_file, 'r') as def_f:
        fullDefs = def_f.read()

    fullDefs = fullDefs.split("\n")

    for i, var_name_i in enumerate(var_name):
        cmdStr = (var_name_i
                  + " = "
                  + var_value[i])
        #print(cmdStr)
        for j, line in enumerate(fullDefs):
    
            l = line.replace(" ", "") # getting rid of spaces
    
            l = l[0:len(var_name_i)+1] # selecting the first characters
    
            if var_name_i+"=" == l:
                fullDefs[j] = var_name_i+" = "+str(var_value[i]) + " "
    
    def_file_modif = def_file[0:-4] + "_modif.def" # new definition file with modifications
    
    with open(def_file_modif, 'w') as def_f:
        def_f.write('\n'.join(fullDefs))
    
    load_def(Xepr, def_file_modif)


def load_shp(Xepr, shp_file):
    """
    Load and compile an Xepr shape file.

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    shp_file : str
        Shape file name (full path, including .shp extension).

    Returns
    -------
    None
    """
    try:
        Xepr.XeprCmds.aqPgShpLoad(shp_file)
        Xepr.XeprCmds.aqPgShowShp()
        Xepr.XeprCmds.aqPgCompile()
    except Exception:
        print("shape_load_compile_error")
        sys.exit(3)


def run2getdata_exp(Xepr, SignalType, exp_name):
    """
    Run an experiment and get the data from it.

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    SignalType : str from {"TM", "Signal", "RM"}
    exp_name : str
        The name of the experiment to run, usually "AWGTransient" for the
        Signal or "AWG_1pulseSHP" for the TM.

    Returns
    -------
    data : XeprAPI.Dataset
        The data retrieved from Xepr. Attributes of interest are:
            - data.X      : the X-abscissa values of the dataset
            - data.O      : complex-valued numpy.ndarray of the signal
            - data.O.real : real part of the signal
            - data.O.imag : imaginary part of the signal
    """
    try:
        currentExp = Xepr.XeprExperiment()
        hiddenExp = Xepr.XeprExperiment("AcqHidden")
    except Exception:
        print("No Experiment has been selected in the"
              " Primary Viewport of Xepr.")
        sys.exit(2)

    # change detection mode and experiement select
    try:
        if hiddenExp["ftBridge.Detection"].value != SignalType:
            hiddenExp["ftBridge.Detection"].value = SignalType
        if currentExp["ftEpr.PlsSPELEXPSlct"].value != exp_name:
            currentExp["ftEpr.PlsSPELEXPSlct"].value = exp_name
    except Exception:
        print("error changing detection mode to TM, or experiment selection")
        sys.exit(3)

    # run new experiment
    try:
        currentExp.aqExpRunAndWait()
    except Exception:
        print("error running current experiment")
        sys.exit(4)

    # retrieve data
    data = Xepr.XeprDataset()

    # no data? -- try to run current experiment (if possible)
    if not data.datasetAvailable():
        try:
            print("Trying to run current experiment to create some data...")
            Xepr.XeprExperiment().aqExpRunAndWait()
        except XeprAPI.ExperimentError:
            print("No dataset available and no (working) experiment"
                  " to run... giving up...")
            sys.exit(5)
    if not data.datasetAvailable():
        print("(Still) no dataset available...giving up...")
        sys.exit(6)  

    return data


def reset_exp(Xepr):
    """
    Copy the current experiment and use it to replace the current experiment.

    Needed to reset the AWG after 114 sequential shape load and run.

    Parameters
    ----------
    Xepr : XeprAPI.Xepr object
        The instantiated Xepr object.

    Returns
    -------
    None
    """
    # get current experiment name
    curr_exp = Xepr.XeprExperiment()
    expt_name = curr_exp.aqGetExpName()

    # duplicate current experiment
    print(f"replacing experiment <{expt_name}> with new"
          " instance of its copy...")
    Xepr.XeprCmds.aqExpCut(expt_name)

    print(f"new instance of experiment <{expt_name}> created...")
    Xepr.XeprCmds.aqExpPaste()

    # select new experiment
    Xepr.XeprCmds.aqExpSelect(expt_name)
    print(f"new instance of experiment <{expt_name}> selected...")

    # activate new experiment
    Xepr.XeprCmds.aqExpActivate(expt_name)
    print(f"new instance of experiment <{expt_name}> activated.")

    # open parameter panel
    Xepr.XeprCmds.aqParOpen()
