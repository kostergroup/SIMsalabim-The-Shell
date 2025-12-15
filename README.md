# SIMsalabim - The Shell
An easy-to-use graphical user (GUI) interface for SIMsalabim, build on the Streamlit framework and Python.

## Table of Contents
1. [Introduction](#Introduction)
2. [Installation instructions](#installation-instructions)
3. [How to use The Shell](#how-to-use-the-shell)
4. [Copyright and license](#copyrigth-and-license)
5. [How to contribute](#how-to-contribute)

## Introduction

The Shell is a user-friendely grpahical interface for running simulations with the [SIMsalabim](https://github.com/kostergroup/SIMsalabim) drift-diffusion simulator. It allows users to define multi-layer device structures, set material parameters, run experiments such as steady-state and transient JV, impedance spectroscopy, IMPS, and CV, and directly visualize results, without the need for editing text based input files or running thorugh the command line. By providing an intuitive interface, based on the extensive model implemented in SIMsalabim, The Shell streamlines device simulation workflows, reduces long input and setup times, enables quick comparison of different experiments, and provides immediate visualization of results.

The Shell can be used in two ways:
- The GUI is deployed online and can be accessed through the browser: [www.simsalabim-online.com](http://www.simsalabim-online.com)
- The GUI can be run on a local machine, see the [Installation instructions](#installation-instructions) below

Note1: This repository only provides the components needed to create and build the UI. For SIMsalabim refer to the [SIMsalabim repository](https://github.com/kostergroup/SIMsalabim). For the implementation of several well-known experiments and useful tools to set up and run simulations as well as tools to analyze and visualize the results refer to the [pySIMsalabim repository](https://github.com/kostergroup/pySIMsalabim).

Note2: The Shell does not yet support all features and functionality that SIMsalabim has to offer. To use all functionality, download and run the SIMSalabim project on your machine as described in the [SIMsalabim Project readme](https://github.com/kostergroup/SIMsalabim). For a full overview of the functionality of SIMSalabim, refer to the [SIMsalabim manual](https://raw.githubusercontent.com/kostergroup/SIMsalabim/master/Docs/Manual.pdf).

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
- Simulate a Transient JV experiment and compare it to an experimental JV curve
- Simulate an impedance spectroscopy experiment
- Simulate an IMPS experiment
- Simulate a capacitance-voltage experiment

## Installation instructions

The setup and deployment steps of The Shell have been packaged in the run_The_Shell_local.sh script. 
Note: The Shell is designed to run on a Linux machine, and has not been prepared to natively run on a Windows machine.

### Prerequisites
- Python3
- (optional) Free Pascal Compiler

### Running the install script

- Download the 'The Shell' folder from this Github repository and unpack it in your desired location. 

- Execute the run_The_Shell.sh script in its current folder
```
./run_The_Shell_local.sh
```

- To run the application, we use a Python virtual environemnt (venv), as this is included by default into a Python3 distribution

- Required python packages will be installed as defined in the requirements.txt file and are: Streamlit, pandas, numpy, scipy, matplotlib

- The Python package [pySIMsalabim](https://github.com/kostergroup/pySIMsalabim) will be included in the directory. If there already is a pySIMsalabim folder in your current working directory, you can overwrite this directory with the latest release or use the existing pySIMsalabim version in the folder.

- The script will either compile the SIMsalabim binaries or use the pre-compiled binaries based on the presence of the Free Pascal Compiler (fpc) package (version 3.2.0 or higher).

- If there already is a SIMsalabim folder in your current working directory, you can overwrite this directory with the latest release from the SIMsalabim Github or use the existing SIMsalabim version in the folder.

- When the virtual environment is set up, The Shell is started on a local server. The URL to find The Shell is provided via the console. The default port is 8501, but this can be changed in .streamlit/config.toml

- Navigate to the URL to use The Shell.

## How to use The Shell
- Select an experiment to simulate, where each has its own tab:
    - Steady State JV
    - Transient JV
    - Impedance spectroscopy
    - Intensity Modulated Photo Spectropscopy (IMPS)
    - Capacitance-Voltage (CV) profiling

- Modify the parameters to match the desired device strcuture and material properties -or- upload your own device. These parameters are shared among the different experiments
- Depending on the chosen experiment, set the experiment specific parameters such as voltage scan speed, frequency range and voltage step size
- Save the parameters, and a band diagram will show based on the defined device, providing a quick way of validating the basics of the defined device
- Run the simulation
- Inspect the results through the 'Simulation Results' page

## Copyright and License
The Shell is licensed under the GNU Lesser General Public Licence version 3. The details of this licence can be found in the files COPYING.txt and COPYING.LESSER.txt. Several authors have contributed to the code:

- S. (Sander) Heester (University of Groningen)
- F.D. (Fransien) Elhorst (University of Groningen)
- P. (Patricia) Martin Fernandez (University of Groningen)
- Dr. M. (Marten) Koopmans (University of Groningen)
- Dr. V.M. (Vincent) Le Corre (University of Southern Denmark)
- Prof. Dr. L.J.A. (Jan Anton) Koster (University of Groningen)

## How to contribute
For detailed instructions on coding conventions, contribution workflow, and best practices, please refer to the [Developer Guidelines](https://github.com/kostergroup/SIMsalabim-The-Shell/blob/master/Docs/Developer_guidelines.md) document. All contributors are encouraged to read this guide before submitting new features, experiments, or bug fixes.
