# record resonator profile

import os
import time
import numpy as np
from esrpoise import xepr_link, param_set

xepr = xepr_link.load_xepr()

f_loc = '/home/xuser/xeprFiles/Data/ORGANIC/MFgrp/JB/211209/Nutation/'
exp_f = f_loc + 'nutation.exp'
def_f = f_loc + 'nutation.def'

# --------  To be input by the user  --------
# field initial value (G)
start_field = 3300.1
# number of points
nb_pts=60
# number of steps (coarse step is around 3MHz)
nb_steps=3

# carrier frequency initial value (GHz)
cur_exp = xepr.XeprExperiment()
start_freq = cur_exp.getParam("FrequencyMon").value
# end frequency
end_freq = start_freq + nb_pts*nb_steps*0.003

print('Start frequency: ' + str(start_freq) + ' GHz')
print('Final frequency: ' + str(end_freq) + ' GHz')

nut = np.empty((nb_pts, 160), dtype=np.complex64)
freq = np.empty(nb_pts)
for i in range(nb_pts):

    # read carrier frequency
    cur_exp = xepr.XeprExperiment()
    new_freq = cur_exp.getParam("FrequencyMon").value
    freq[i] = new_freq

    # modify field accordingly
    new_field = new_freq * start_field / start_freq
    param_set(xepr, ["CenterField"], [new_field], [0.1], exp_f, def_f)
    time.sleep(1)

    print("")
    print(str(new_freq)+'GHz')
    print(str(new_field)+'G')

    # run experiment
    data = xepr_link.run2getdata_exp(xepr, "Signal", exp_f)

    # store nutation transient
    nut[i,:] = data.O.real + 1j * data.O.imag

    # carrier frequency stepping
    for j in range(nb_steps):
        xepr.XeprCmds.aqParStep("AcqHidden", "*cwBridge.Frequency", "Coarse 1")
    time.sleep(3)

# save data
np.savetxt('nutation_freq.txt', freq)
np.savetxt('nutation_ydata.txt', nut)
