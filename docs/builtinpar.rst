Built-in parameters
===================

Built-in parameters can have different constraints depending on your spectrometer. Values documented here are just indications. All parameters currently supported are indicated below.

Bridge - Receiver Unit
----------------------
 - ``"VideoGain"`` (dB), video gain, indicative minimum tolerances: 3dB, 6dB
 - ``"Attenuation"`` (dB), high power attenuation, indicative minimum tolerance: 0.01dB
 - ``"SignalPhase"`` (~0.129deg), signal phase, indicative minimum tolerance: 1
 - ``"TMLevel"`` (%), transmitter level, 0 to 100

Bridge - MPFU control
---------------------
 - ``"BrXPhase"``, +<x> Phase
 - ``"BrXAmp"``, +<x> Amplitude
 - ``"BrYPhase"``, +<y> Phase
 - ``"BrYAmp"``, +<y> Amplitude
 - ``"BrMinXPhase"``, -<x> Phase
 - ``"BrMinXAmp"``, -<x> Amplitude
 - ``"BrMinYPhase"``, -<y> Phase
 - ``"BrMinYAmp"``, -<y> Amplitude

These are rounded in Xepr to closest 0.049% (approximately, not linear).

FT EPR Parameters
-----------------
 - ``"CenterField"``, field position (G), indicative minimum tolerance: 0.05G