"""
xepr_link.py
------------

Xepr interface functions, communicate with Xepr usingXeprAPI.

Pause times necesary to let Xepr process command are accessed through the
global variable ``COMPILATION_TIME`` (s, ``1`` by default).
It applies pauses of lengths:

 - ``COMPILATION_TIME`` after compilation of .exp file

 - ``COMPILATION_TIME`` after compilation of .def file

 - ``COMPILATION_TIME/4`` after compilation of .shp file

 - ``2*COMPILATION_TIME`` before and after Xepr reset

SPDX-License-Identifier: GPL-3.0-or-later

"""

import time
import XeprAPI         # load the Xepr API module
from typing import List


# global variable to control Xepr files compilation time
COMPILATION_TIME = 1  # (s)


def load_xepr():
    """
    Initialise the Xepr module and return the Xepr object thus created.

    Parameters
    ----------
    None

    Returns
    -------
    xepr : instance of XeprAPI.Xepr
        The instantiated Xepr object, used for communication with
        Xepr-the-programme.
    """
    xepr = XeprAPI.Xepr()  # start Xepr API module

    return xepr


def load_exp(xepr, exp_file: str) -> None:
    """
    Load and compile an Xepr experiment file.

    Parameters
    ----------
    xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    exp_file : str
        The Xepr experiment file (the full path with .exp extension).

    Returns
    -------
    None
    """
    try:
        xepr.XeprCmds.aqPgLoad(exp_file)
        xepr.XeprCmds.aqPgShowPrg()
        xepr.XeprCmds.aqPgCompValid()
        xepr.XeprCmds.aqPgCompile()

        # wait for Xepr to finish compiling
        time.sleep(COMPILATION_TIME)
    except Exception:
        raise RuntimeError("Error loading and compiling experiment file")


def modif_exp(xepr, exp_file: str, line_nb: int, new_line: str) -> None:
    """
    Modify the Xepr .exp file by overwriting a line.

    Parameters
    ----------
    xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    exp_file : str
        Name of the Xepr definition file (full path with .def extension).
    line_nb : int
        Number of the lines to overwrite
    new_line : str
        DESCRIPTION.

    Returns
    -------
    None
    """
    with open(exp_file, 'r') as exp_f:
        fullExp = exp_f.read()

    # write new line
    fullExp = fullExp.split("\n")
    fullExp[line_nb-1] = new_line

    # replace .exp file with modifications
    with open(exp_file, 'w') as exp_f:
        exp_f.write('\n'.join(fullExp))

    if xepr is not None:  # to allow test without Xepr
        load_exp(xepr, exp_file)


def load_def(xepr, def_file: str) -> None:
    """
    Load and compile an Xepr definition file.

    Parameters
    ----------
    xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    def_file : str
        Name of the Xepr definition file (full path with .def extension).

    Returns
    -------
    None
    """
    try:
        xepr.XeprCmds.aqPgDefLoad(def_file)
        xepr.XeprCmds.aqPgShowDef()
        xepr.XeprCmds.aqPgCompile()

        # wait for Xepr to finish compiling
        time.sleep(COMPILATION_TIME)
    except Exception:
        raise RuntimeError("Error loading and compiling definition file")


def modif_def_PlsSPELGlbTxt(xepr, def_file: str,
                            var_name: List[str], var_value: List[str]) -> None:
    """
    Directly modify definitions in the current experiment.

    !will not modify parameters which rely on dependency in the .def (e.g.
                                                                   'p0 = 2*p1')
    !can lead to bugs if forbiden charachters are used in the .def file (e.g.
                                                                           '%')
    !can create a bug where the Xepr stays stuck at the .def file modification
                                           (cf. documentation for more details)
    but faster than modif_def() as no compilation required

    Parameters
    ----------
    xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    def_file : str
        Name of the Xepr definition file (full path with .def extension).
    var_name : list of strings
        Variable names as named in the .def file.
    var_value : list of strings
        List of variable values to be input.

    Returns
    -------
    None
    """
    try:
        currentExp = xepr.XeprExperiment()
    except Exception:
        raise RuntimeError("No experiment has been selected in the"
                           " primary viewport of Xepr.")

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

        for line in fullDefs:
            line = line.replace(" ", "")  # getting rid of spaces
            line = line[0:len(var_name_i) + 1]  # selecting first characters
            if var_name_i + "=" == line:
                currentExp["ftEPR.PlsSPELSetVar"].value = cmdStr


def modif_def(xepr, def_file: str,
              var_name: List[str], var_value: List[str]) -> None:
    """
    Modify definitions by modifying the .def file and reloading it.

    Parameters
    ----------
    xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    def_file : str
        Name of the Xepr definition file (full path with .def extension).
    var_name : list of strings
        Variable names as named in the .def file.
    var_value : list of strings
        List of variable values to be input.

    Returns
    -------
    None
    """
    with open(def_file, 'r') as def_f:
        fullDefs = def_f.read()
    fullDefs = fullDefs.split("\n")

    for name, value in zip(var_name, var_value):

        for j, line in enumerate(fullDefs):

            equal_partition = line.partition("=")

            if name == equal_partition[0].replace(" ", ""):
                fullDefs[j] = equal_partition[0] + "= " + value

                # preserve possible comment at the end of the line
                comment_partition = equal_partition[-1].partition(";")
                if comment_partition[1] == ";":
                    fullDefs[j] += " " ";" + comment_partition[-1]

    # replace definition file with modifications
    with open(def_file, 'w') as def_f:
        def_f.write('\n'.join(fullDefs))

    if xepr is not None:  # to allow test without Xepr
        load_def(xepr, def_file)


def load_shp(xepr, shp_file: str) -> None:
    """
    Load and compile an Xepr shape file.

    Parameters
    ----------
    xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    shp_file : str
        Shape file name (full path, including .shp extension).

    Returns
    -------
    None
    """
    try:
        xepr.XeprCmds.aqPgShpLoad(shp_file)
        xepr.XeprCmds.aqPgShowShp()
        xepr.XeprCmds.aqPgCompile()

        # wait for Xepr to finish compiling
        time.sleep(COMPILATION_TIME*0.25)
    except Exception:
        raise RuntimeError("Error loading and compiling Xepr shape file")


def run2getdata_exp(xepr, SignalType: str = None, exp_name: str = None):
    """
    Run an experiment and get the data from it.

    Parameters
    ----------
    xepr : XeprAPI.Xepr object
        The instantiated Xepr object.
    SignalType : str, by default None
        To change the signal type (pick from {"TM", "Signal", "RM"})
    exp_name : str, by default None
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
        currentExp = xepr.XeprExperiment()
        hiddenExp = xepr.XeprExperiment("AcqHidden")
    except Exception:
        raise RuntimeError("No experiment has been selected in the"
                           " primary viewport of Xepr.")

    # change detection mode and experiment select if needed
    try:
        if SignalType is not None and \
                hiddenExp["ftBridge.Detection"].value != SignalType:
            hiddenExp["ftBridge.Detection"].value = SignalType
        if exp_name is not None and \
                currentExp["ftEpr.PlsSPELEXPSlct"].value != exp_name:
            currentExp["ftEpr.PlsSPELEXPSlct"].value = exp_name
    except Exception:
        raise RuntimeError("Error changing detection mode to TM,"
                           " or in experiment selection")

    # run new experiment
    try:
        currentExp.aqExpRunAndWait()
    except Exception:
        raise RuntimeError("Error running current experiment")

    # retrieve data
    data = xepr.XeprDataset()

    # no data? -- try to run current experiment (if possible)
    if not data.datasetAvailable():
        try:
            print("Trying to run current experiment to create some data...")
            xepr.XeprExperiment().aqExpRunAndWait()
        except XeprAPI.ExperimentError:
            raise RuntimeError("No dataset available and no (working)"
                               " experiment to run; aborting")
    if not data.datasetAvailable():
        raise RuntimeError("No dataset available; aborting")

    return data


def reset_exp(xepr) -> None:
    """
    Copy the current experiment and use it to replace the current experiment.

    Needed to reset the AWG after 114 sequential shape load and run.

    Parameters
    ----------
    xepr : XeprAPI.Xepr object
        The instantiated Xepr object.

    Returns
    -------
    None
    """
    # wait for Xepr to be ready to reset the experiment
    time.sleep(2*COMPILATION_TIME)

    # get current experiment name
    curr_exp = xepr.XeprExperiment()
    expt_name = curr_exp.aqGetExpName()

    # duplicate current experiment
    print(f"replacing experiment <{expt_name}> with new"
          " instance of its copy...")
    xepr.XeprCmds.aqExpCut(expt_name)

    print(f"new instance of experiment <{expt_name}> created...")
    xepr.XeprCmds.aqExpPaste()

    # select new experiment
    xepr.XeprCmds.aqExpSelect(expt_name)
    print(f"new instance of experiment <{expt_name}> selected...")

    # activate new experiment
    xepr.XeprCmds.aqExpActivate(expt_name)
    print(f"new instance of experiment <{expt_name}> activated.")

    # open parameter panel
    xepr.XeprCmds.aqParOpen()

    # ask user to allow .exp file to be loaded
    print('Experiment reset')
    print('clik twice the PulseSPEL button to load the .exp file')
    print('(located at the bottom of FT EPR parameters window)')
    input('when done, press enter in python console to continue:')

    # wait for Xepr to reset the experiment
    time.sleep(2*COMPILATION_TIME)

    # prevent Xepr from reseting high power attenuation value
    xepr.XeprCmds.aqParStep("AcqHidden", "ftBridge.Attenuation", "Fine 1")
    xepr.XeprCmds.aqParStep("AcqHidden", "ftBridge.Attenuation", "Fine -1")
