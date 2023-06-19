# Change Log
All changes to the SIMsalabim web application are documented here. <br>
Note: This does not include changes to the SIMsalabim simulation software itself.

## [1.00] - 09-01-2023 - SH
- Run SIMsalabim Steady State simulations
- Modify/adjust device parameters
- Upload device parameters, experimental JV curve, generation profile, traps
- Download simulation input and output
- Show band diagram based on the device parameters
- Show main simulation results (figures) as described in the SIMsalabim Manual
- Use optics/material characteristics to calculate a generation profile using the transfer matrix method

## [1.01] - 10-05-2023 - SH
- Updated to SIMsalabim v4.52
- Support multiple experiments
- Reworked internal structure, results pages are loaded as functions based on simulation state parameter.
- Creation of the ZIP file with the results can take some time when the files (Var file in specific) are large. Added a spinner to indicate that results are being processed
- Added Getting help page
- Improved readability of the code
- Added plot options, like lin/log scales or errorbars
- Added ZimT support (only for the experiments)
- The device parameters (between SimSS, ZimT and the experiments) are synchronized in the background using the ExchangeDevPar exec.
- Added hysteresis JV experiment
- Added impedance experiment
- Experimental and page template
- Modified functions to seperate web/streamlit parts to allow sharing between web and standalone scripts
- Updated the device parameters

## [1.02] - 31-05-2023 - SH
- Fixed a bug where the JV hysteresis and Impedance specific parameters were being reset after switching back from the simulation results.
- Increased the default minimum frequency from 1e-2 Hz to 1e-1 Hz
- Mask format of the generation rate in case of JV hysteresis and Impedance is updated to support values with number of digits > 2

## [1.03] - 08-06-2023 - SH
- Added a new experiment, IMPS. 
- The hysteresis result and the nyquist plot of impedance now have a colorbar to also indicate time or frequency in these results. The time/frequency values area added as weights to the colorbar.
- Updated the default device parameters
- Creation of the ZIP archive for the results is now done after pressing a button, not upon page initialisation. Results are shown immediately now.
