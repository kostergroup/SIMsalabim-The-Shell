# Change Log
All changes to the The Shell | SIMsalabim web application are documented here. <br>
Note: This does not include changes to the SIMsalabim simulation software itself.

## [1.08] - 18-12-2023 - SH
- Added nk-files for FAPbI and FACsPbIBr
- Updated device parameters
- The results of IMPS are now shown in a Cole-Cole plot instead of a Bode plot

## [1.07] - 28-08-2023 - SH
- Added session logging with: id, simulation_type, result and date/time
- Removed standard console writing for the Impedance/IMPS experiments

## [1.06] - 21-08-2023 - SH
- Updated to SIMsalabim v4.56
- Switched standard materials/nk files for the transport layers
- Reduced timeout from 3600 to 600

## [1.05] - 04-07-2023 - SH
- Updated to SIMsalabim v4.54
- Added Fransien Elhorst to the contributors/copyright

## [1.04] - 28-06-2023 - SH
- When downloading the simulation results, a txt file is created which contains a summary/reproduction sceneario of the simulation including all relevant files. It also contains also contains all the references needed for citation.
- A hysteresis JV experiment can now be compared to experimental data and results in a rms error. 
- Added the SIMsalabim reference as an info box on the home page
- Updated the default device paramters file to include more realitic DOS for the transport layers
- Cleaned up the default nk files
- Bug fix: When uploading a device parameters file, the user is now warned when a nk/spectrum file cannot be found or does not exist. If this is the case, it is forced to --none-- in the device parameters file.

## [1.03] - 08-06-2023 - SH
- Added a new experiment, IMPS. 
- The hysteresis result and the nyquist plot of impedance now have a colorbar to also indicate time or frequency in these results. The time/frequency values area added as weights to the colorbar.
- Updated the default device parameters
- Creation of the ZIP archive for the results is now done after pressing a button, not upon page initialisation. Results are shown immediately now.

## [1.02] - 31-05-2023 - SH
- Fixed a bug where the JV hysteresis and Impedance specific parameters were being reset after switching back from the simulation results.
- Increased the default minimum frequency from 1e-2 Hz to 1e-1 Hz
- Mask format of the generation rate in case of JV hysteresis and Impedance is updated to support values with number of digits > 2

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

## [1.00] - 09-01-2023 - SH
- Run SIMsalabim Steady State simulations
- Modify/adjust device parameters
- Upload device parameters, experimental JV curve, generation profile, traps
- Download simulation input and output
- Show band diagram based on the device parameters
- Show main simulation results (figures) as described in the SIMsalabim Manual
- Use optics/material characteristics to calculate a generation profile using the transfer matrix method
