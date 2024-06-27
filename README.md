# SIMsalabim - The Shell
An easy-to-use web interface for SIMsalabim, build on the Streamlit framework and Python. 

Note: The Shell does not support all features and functionality that SIMsalabim has to offer. To use all functionality, download and run the SIMSalabim project on your machine as described in the [SIMsalabim Project readme](https://github.com/sheester/SIMsalabim-web/tree/development/SIMsalabim#quickstart-guide). For a full overview of the functionality of SIMSalabim, refer to the [SIMsalabim manual](https://raw.githubusercontent.com/kostergroup/SIMsalabim/master/Docs/Manual.pdf).

Currently supported functionality in The Shell is:
- Define your device via the device parameters on a template or upload your own device parameters.
- Full flexibility in defining the number of layers and their parameters
- Use optics (based on the Transfermatrix method) to calculate a generation profile
- Upload an experimental JV curve and compare it to a simulated JV curve
- Upload and use a generation profile
- Upload and use a definition of multiple trap levels
- Plot, analyze and download the simulation results
- Simulate Steady State JV curves
- Simulate the EQE of a device
- Simulate a JV hysteresis experiment and compare it to an experimental JV curve
- Simulate an impedance spectroscopy experiment
- Simulate an IMPS experiment
- Simulate a capacitance-voltage experiment


## Table of Contents
1. [Installation instructions](#installation-instructions)
2. [How to use The Shell](#how-to-use-the-shell)
2. [Copyright and license](#copyrigth-and-license)

## Installation instructions
Setting up The Shell to run locally on your machine is straightforward using the run_SIMsalabim_local.sh script. 

### Prerequisites
- Python3
- (optional) Free Pascal Compiler (Preferred)

### Running the install script

- Download the 'The Shell' folder from this Github repository and unpack it in your desired location. 

- Run the run_SIMsalabim_local.sh script in its current folder
```
bash run_The_Shell_local.sh
```

The script will either compile the SIMsalabim binaries (preferred) or use the pre-compiled binaries based on the presence of the Free Pascal Compiler (fpc) package (version 3.2.0 or higher).

- If there already is a SIMsalabim folder in your current working directory, you can overwrite this directory with the latest release from the SIMsalabim Github or use the existing SIMsalabim version in the folder.

- The script will compile both SimSS and ZimT.

- If you do not have the fpc package installed or your version is not 3.2.0 or higher, you can either abort the script and install/update fpc or continue using the pre-compiled SIMsalabim binaries from the repository.

- To run The Shell, a pip environment will be setup. If the pipenv package is not installed on your machine, the script will install it for you. 

- When a pip environment / Pipfile already exists for this SIMsalabim folder, overwrite/update the environment. If it does not yet exists, a new one will be created. Required python packages will be installed as defined in the requirements.txt file. 

- When the pip environment is set up, The Shell is started on a local server. The URL to find The Shell is provided via the console. The default port is 8001, but this can be changed in .streamlit/config.toml

- Navigate to the URL to use The Shell.

## How to use The Shell
- Navigate to the device parameters page to define your device parameters
- Use the default device parameters, modify the default parameters or upload your own device parameters file.
- Optional: Upload your desired input/data files (.txt). Do not forget to include the name of the file in the relevant device parameter.
- Save the device parameters when done. A band diagram will show based on the defined device parameters.
- Run the Simulation (SimSS) and once complete navigate to the Simulation results.
- Show the resulting plots of interest. 
- Vary the Voltage (Vext) to show the data for this voltage using the slider

## Copyright and License
The Shell is licensed under the GNU Lesser General Public Licence version 3. The details of this licence can be found in the files COPYING.txt and COPYING.LESSER.txt. Several authors have contributed to the code:

- S. (Sander) Heester (University of Groningen)
- F.D. (Fransien) Elhorst (University of Groningen)
- P. (Patricia) Martin Fernandez (University of Groningen)
- Dr. M. (Marten) Koopmans (University of Groningen)
- Dr. V.M. (Vincent) Le Corre (University of Erlangen-Nuremberg)
- Prof. Dr. L.J.A. (Jan Anton) Koster (University of Groningen)

