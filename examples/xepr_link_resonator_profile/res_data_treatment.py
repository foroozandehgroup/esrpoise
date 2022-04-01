import numpy as np
import matplotlib.pyplot as plt 

nut = np.loadtxt('nutation_ydata.txt', dtype=np.complex64)

n_res = nut.shape[0]
n_nut = nut.shape[1]

zero_fill = 4

t = 1e-9*np.arange(12, 320+12, 2)  # only for indication, not used
# 12ns -> first length of the nutation pulse

# nutation experiments frequency axis
sf = 1 / 2e-9  # the pulse length increase by 2ns
x = np.linspace(sf / 2, -sf / 2, zero_fill*n_nut)

# need to implement baseline correction

res = np.empty(n_res)

for i in range(n_res):
    nut[i,:] = nut[i,:] - np.mean(nut[i,:])

    t = np.linspace(0,1,n_nut)

    # exponential window
    nut[i,:] = nut[i,:] * np.exp(-3*t)

    # spectra and zero-filling
    spec = np.abs(np.fft.fftshift(
                  np.fft.fft(nut[i,:], zero_fill*n_nut)))

    imax = np.argmax(spec)

    # find maximum and its frequency
    res[i] = np.abs(x[imax])

# resonator frequency axis
freq = np.loadtxt('nutation_freq.txt')

np.savetxt('resonator_profile_f_211210.txt', freq)
np.savetxt('resonator_profile_H_f_211210.txt', res)

plt.figure()
plt.plot(freq, res)
plt.ylim(bottom=0)
plt.show()
