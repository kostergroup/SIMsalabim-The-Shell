# Change Log
All changes to the The Shell | SIMsalabim web application are documented here. <br>
Note: This does not include changes to the SIMsalabim simulation software itself.

## [1.19] - 29-01-2025 - SH
Small bug fixes: 
- Upon loading/reading the parameters, the parameter files that were not defined in the device setup are now read properly. Previously this could give an error in some cases because of a missing argument
- Removed the warning which would show up when the lower axis limit was <=0 when switching to logarithmic scale

## [1.18] - 15-12-2025 - SH
- Placed fileupload functions + dialogs into single file
- cleaned pages of duplicate code
- Removed all non-UI functionality from the pages and placed it in the Utils folder. Some functions have been replaced by wrappers to ensure proper functionality and synchronization
- Updated SIMsalabim to v5.25
- Added unit tests for all functions in utils, included them in Github Actions
- Renamed Hysteresis JV to the more appropiate Transient JV
- Added a manual and developer guidelines

## [1.17] - 09-10-2025 - SH
- Fixed bug in FileUploader related to uploading n,k files. As multiple files can be uploaded here, the uploadedFile variable was not initialized, resulting in a failure upon submitting the selected files. The uploadedFile variable is now initialized as None.
- Updated to pySIMsalabim v1.03
- Changed how SS JV and scPars are handled to comply with pySIMsalabim v1.03
- Removed custom styling of scPars table to correctly switch between light and dark mode

## [1.16] - 26-06-2025 - SH
- Updated to SIMsalabim v5.24
- Replaced the URL for the pdf version of the SIMsalabim manual to the URL for the online SIMsalabim manual: http://simsalabim-online.com/manual

## [1.15] - 21-03-2025 - SH
- Updated to SIMsalabim v5.21
- Added labels for cathode/anode to the band diagram figure
- Switched order of buttons in the sidebar menu
- Fixed warning for future deprecation when selecting the min/max value of a dataframe for x,y limits

## [1.14] - 21-03-2025 - SH
- Updated to SIMsalabim v5.19
- Added QFLS to the results of Steady State JV
- One can now set the x,y limits for all figures/plots in the all results. 
- In the steady state results, the checkboxes for different plots have been replaced with toggle switches
- Changed the way to run The Shell locally from the run_The_Shell_local.py file. Instead of running the pipenv on the system, we now create and use a python virtual environment (venv) in which we run The Shell, still through pipenv. This prevents any potential package conflicts/restrictions on the system. 
- Improved message/information handling (including errors and failures) when setting up The Shell locally and retrieving (py)SIMsalabim from the repository. 


## [1.13] - 18-02-2025 - SH
- Updated to SIMsalabim v5.18
- Updated to pySIMsalabim v1.01
- Removed extra lines in several nk_files
- Updated parameter files to run faster and better, i.e. maxAcc is now 0.1 and tolVint is now 1E-8
- Added option to change aaxis scaling JV plot in Steady State
- Fixed bug in band diagram, where one could not use the option 'sfb' for work function, because drawing the band diagram expected a float and not a string. We now calculate a value when 'sfb' is used with the same procedure as in SIMsalabim
- Reset device parameters did not work because of missing argument/incorrect default setting
- We now display the Hysteresis Index, including its definition when showing the results of a Hysteresis JV simualtion
- Created Figures folder to hold all static figures, such as SIMsalabim logo and HI definition

## [1.12] - 20-11-2024 - SH, VLC
- Refactored The Shell to fully separate UI components from Python utility functions for SIMsalabim. All Python utility functions have been moved to the pySIMsalabim repository, including experimental scripts.

## [1.11] - 20-08-2024 - SH
- Minor Bug Fix: When selecting a different layer file from the dropdown, the selected file name was not assigned correctly to a variable, hence it was not written to the main simulation_setup.txt file which resulted in the file being ignored.
- Updated to SIMsalabim v5.14

## [1.10] - 27-06-2024 - SH, PMF
Major update
- Updated to use SIMsalabim v5.11
- Reworked core functions to support SIMsalabim v5.11.
- The main object that holds the parameters after reading the files is now a dictionary with the file names as keys instead of a List object. This dictionary contains all the available layer files in the current session, not just the ones written in the simulation setup file.
- Updated many of the parameter and variable names to be coherent with the new notation in SIMsalabim v5.11.
- Added functionality to add/remove layers from the device. The layers and their relative position defined here are leading for the device structure used for the simulations. Parameters are now shown per layer and can be selected for editing or viewing using a dropdown menu.
- Changed the file upload options from selectboxes per file type, to a single dialog window.
- Implementation of the navigation menu in the sidebar is now custom and dynamic. When editing parameters, one can navigate between all the different pages. However, when one visits the simulation results, only the option to return back the last visited page is present. The sidebar would become overcrowded otherwise, especially in case of Steady State simulations.
- Added the option to plot errorbars for scatter plots
- The calculated conductivity and capacitance now include the respective error margins.
- Added option to do an EQE calculation for the device. This can be done on the Steady State JV definition page. One needs to specify the wavelength bounds and step size accompanied by the applied voltage. The used spectrum is taken from the device parameter definition.

## [1.09] - 21-12-2023 - SH, FE, VLC
- The impedance simulations with Rseries and Rshunt often did not converge. To improve this,  we now first run a steady state simulation to get the internal voltage and then run the impedance simulation with Rseries = 0 and Rshunt = -Rshunt. We will correct the impedance afterwards. This is a workaround to improve the convergence of the impedance simulation that  remains accurate to estimate the impedance. This is only done when Rseries <> 0. 
- Added a Capacitance/Conductance vs. frequency plot to the impedance results
- Split the device_parameters utility functions to decouple the streamlit dependent functions
- Added a new experiment, capacitance-voltage (CV) 

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

## [1.00] - 09-01-2023 - SH, MK
- Run SIMsalabim Steady State simulations
- Modify/adjust device parameters
- Upload device parameters, experimental JV curve, generation profile, traps
- Download simulation input and output
- Show band diagram based on the device parameters
- Show main simulation results (figures) as described in the SIMsalabim Manual
- Use optics/material characteristics to calculate a generation profile using the transfer matrix method
