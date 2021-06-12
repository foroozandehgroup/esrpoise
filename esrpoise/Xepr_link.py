# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 15:43:08 2021

@author: jbv

Xepr interface functions (largely taken from David's code)  

modif_def should be enough to modify any parameter in the def file
TBD: modif_exp, modif_shp +modif_def_file?


###  Code inherited from David ###

[Grouped in one package] Python functions to communicate with Xepr using XeprAPI
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
"""

import os
import sys

# xepr import -> use XeprAPI compatible with Python 3.7
try:
    # The correct location of the XeprAPI module should be inserted into the 
    # code below
    # -> could be avoided if installed with pip3?
	sys.path.insert(0, os.popen("Xepr --apipath").read());  # this locates the XeprAPI module
	sys.path.append('/opt/Bruker/xepr/sharedProDeL/Examples/XeprAPI-examples');
	sys.path.append('/opt/Bruker/xepr/sharedProDeL/Standard/XeprAPI');
    
	import XeprAPI      # load the Xepr API module
	Xepr=XeprAPI.Xepr() # start Xepr API module
except:
	print("xepr_import_error")
	sys.exit(1)


# =============================================================================
#  
# =============================================================================
    
# some problem may arise as it was written in Python 2

def load_exp(exp_file): 
    """ Load and compile Xepr experiment file
        Input:
            - exp_file, the Xepr experiment file (full path with .exp extension)
    """
    try:
    	Xepr.XeprCmds.aqPgLoad(exp_file)
    	Xepr.XeprCmds.aqPgShowPrg()
    	Xepr.XeprCmds.aqPgCompValid()
    	Xepr.XeprCmds.aqPgCompile()
    except:
    	print("program_load_compile_error")
    	sys.exit(3)


def load_def(def_file):
    """ Load and compile an Xepr definition file
        
        Input:
            - def_file, name of the Xepr definition file (full path with .def extension)
    """
    try:
    	Xepr.XeprCmds.aqPgDefLoad(def_file)
    	Xepr.XeprCmds.aqPgShowDef()
    	Xepr.XeprCmds.aqPgCompile()
    except:
    	print("definitions_load_compile_error")
    	sys.exit(3)


def modif_def(var_name, var_value):
    """ Directly modify definitions defined in the current experiment. 
        Input:
            - var_name, string list of variable names as named in the .def file
            - var_value, string list of variable value to be input
    """    
    try:
    	currentExp = Xepr.XeprExperiment()
    except:
    	print("No Experiment in Primary: "+"No Experiment has been selected in the Primary Viewport of Xepr.")
    	sys.exit(2)
    
    # get the start value for the variable
    # search for our desired variable
    # first get the text of the full PulseSpel def
    fullDefs = currentExp.getParam("PlsSPELGlbTxt").value
    # need to check if fullDefs is empty and exit cause pulsespel not being loaded
    fullDefs = fullDefs.split("\n")
    
    no_defs=(len(sys.argv)-1)/2
    
    try:
    	for value in fullDefs:
    		for index in range(1,no_defs+1):
    			if str(var_name[(2*index)-1]) in value:
    				cmdStr = var_name[(2*index)-1] + " = " + var_value[2*index]
    				currentExp["ftEPR.PlsSPELSetVar"].value = cmdStr
    except:
    	print("error changing pulseSPEL defs")
    	sys.exit(4)


def load_shp(shp_file):
    """ load and compile an Xepr a shape file
    
        Input:
            - shp_file, shape file name (full path with .shp extension
    """
    try:
    	Xepr.XeprCmds.aqPgShpLoad(shp_file)
    	Xepr.XeprCmds.aqPgShowShp()
    	Xepr.XeprCmds.aqPgCompile()
    except:
    	print("shape_load_compile_error")
    	sys.exit(3)


def run2getdata_exp(SignalType, exp_name):
    """To run the experiement and get the data from it
    
    Input:
        - SignalType, string, "TM", "Signal", or "RM"
        - exp_name, string containing the name of the experiment to run, usually 
        "AWGTransient" for the Signal or "AWG_1pulseSHP" for the TM.
    Output
        - data, the data retrieved from Xepr. Of interest:
            - data.X
            - data.O, the signal with its real and imaginary parts, dset.O.real
            and data.O.imag
    """
    try:
    	currentExp = Xepr.XeprExperiment()
    	hiddenExp = Xepr.XeprExperiment("AcqHidden")
    except:
    	print("No Experiment in Primary: " + "No Experiment has been selected in the Primary Viewport of Xepr.")
    	sys.exit(2)
    
    # change detection mode and experiement select
    try:
    	if hiddenExp["ftBridge.Detection"].value != SignalType:
    		hiddenExp["ftBridge.Detection"].value = SignalType
    	if currentExp["ftEpr.PlsSPELEXPSlct"].value != exp_name:
    		currentExp["ftEpr.PlsSPELEXPSlct"].value = exp_name
    except:
    	print("error changing detection mode to TM, or experiment selection")
    	sys.exit(3)
    
    # run new experiment
    try:
        currentExp.aqExpRunAndWait()
    except:
        print("error running current experiment")
        sys.exit(4)
    
    #retrieve data
    data = Xepr.XeprDataset()
    
    # TBD: type of the data +convert data to numpy arrays?
    
    # no data? -- try to run current experiment (if possible)
    if not data.datasetAvailable():
        try:
            print("Trying to run current experiment to create some data...")
            Xepr.XeprExperiment().aqExpRunAndWait()
        except XeprAPI.ExperimentError:
            print("No dataset available and no (working) experiment to run...giving up...")
            sys.exit(5)
    if not data.datasetAvailable():
        print("(Still) no dataset available...giving up...")
        sys.exit(6)
        
    return data


def reset_exp():
    """ Copy the current experiment and use it to replace the current experiment
    
        Needed to reset the AWG after 114 sequential shape load and run
    """

    # get current experiment name
    curr_exp=Xepr.XeprExperiment()
    expt_name=curr_exp.aqGetExpName()
    
    # duplicate current experiment
    print("replacing experiment <" + expt_name + "> with new instance of its copy...")
    Xepr.XeprCmds.aqExpCut(expt_name)
    
    print("new instance of experiment <" + expt_name + "> created...")
    Xepr.XeprCmds.aqExpPaste()
    
    # select new experiment
    Xepr.XeprCmds.aqExpSelect(expt_name)
    print("new instance of experiment <" + expt_name + "> selected...")
    
    # activate new experiment
    Xepr.XeprCmds.aqExpActivate(expt_name)
    print("new instance of experiment <" + expt_name + "> activated.")
    
    # open parameter panel
    Xepr.XeprCmds.aqParOpen()
