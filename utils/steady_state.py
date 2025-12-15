""" Functions specific for Steady State (SimSS) case"""
######### Package Imports #########################################################################

import streamlit as st
from pySIMsalabim.experiments import JV_steady_state as JV_exp
import os
from datetime import datetime
from utils import device_parameters_UI as utils_devpar_UI

######### Function Definitions ####################################################################

def split_line_scpars(item, solar_cell_param, par, unit):
    """Read string line and split into the different parameters (Simualted, Experimental, Deviation)

    Parameters
    ----------
    item : string
        Parameter line
    solar_cell_param : dict
        Dict to hold the solar cell parameters
    par : string
        Paramemeter name
    unit : string
        Unit of the parameter

    Returns
    -------
    solar_cell_param : dict
        Updated Dict to hold the solar cell parameters
    """
    val_list_compact = []

    # Remove the parameter name
    item = item.replace(par + ':', '')

    # If not already done, remove the unit
    if not par == 'Jsc' and not par == 'FF' and not par == 'MPP':
        item = item.replace(unit, '')

    # Place the units in square brackets. Not for the Fill Factor (FF)
    if not par == 'FF':
        unit = '[' + unit + ']'

    # Split the different values per parameter 
    val_list = item.split(' ') 

    # Remove empty values/entries due to e.g. spaces etc.
    for val_list_split in val_list:
        if not val_list_split == '':
            val_list_compact.append(val_list_split)

    # Store the scPars parameters in the object. Use the number of parameters to determine whether experimental parameters/deviations are present
    for i in val_list_compact:
        if len(val_list_compact) > 0:
            # Standard simualted scPars
            solar_cell_param['Simulated'][par + ' ' + unit] = (
                ((val_list_compact[0])))+val_list_compact[1]+(((val_list_compact[2])))
        if len(val_list_compact) > 3:
            # Experimental scPars
            solar_cell_param['Experimental'][par + ' ' + unit] = (
                ((val_list_compact[3])))+val_list_compact[4]+(((val_list_compact[5])))
        if len(val_list_compact) > 5:
            # Deviations
            solar_cell_param['Deviation'][par + ' ' +
                                          unit] = (((val_list_compact[6])))
            
    return solar_cell_param


def write_scpars(item, solar_cell_param, solar_cell):
    """Read and write the solar cell parameters from the txt line. Store them in a dictionary.

    Parameters
    ----------
    item : string
        String containing a solar cell parameter
    solar_cell_param : dict
        The dict object to hold the solar cell parameters
    solar_cell : boolean
        True if a solar cell has been simulated, False if not

    Returns
    -------
    dict
        Updated dict object to hold the solar cell parameters
    """
    if 'Jsc' in item:
        item = item.replace('A/m2', '')
        solar_cell_param = split_line_scpars(
            item, solar_cell_param, 'Jsc', 'Am\u207b\u00b2')
        solar_cell = True
    if 'Vmpp' in item:
        solar_cell_param = split_line_scpars(
            item, solar_cell_param, 'Vmpp', 'V')
        solar_cell = True
    if 'MPP' in item:
        item = item.replace('W/m2', '')
        solar_cell_param = split_line_scpars(
            item, solar_cell_param, 'MPP', 'Wm\u207b\u00b2')
        solar_cell = True
    if 'Voc' in item:
        solar_cell_param = split_line_scpars(
            item, solar_cell_param, 'Voc', 'V')
        solar_cell = True
    if 'FF' in item:
        solar_cell_param = split_line_scpars(item, solar_cell_param, 'FF', '')
        solar_cell = True
    return solar_cell_param, solar_cell

def store_scPar_state(sc_par, solar_cell, dev_par, dev_par_name):
    """Store the solar cell parameters in a state.

    Parameters
    ----------
    sc_par : dict
        Dict object with the solar cell parameters from the terminal
    solar_cell : boolean
        True if a solar cell has been simulated, False if not
    dev_par : List
        Device parameters as a list of nested lists
    dev_par_name : string
        Name of the device parameter file
    """
    # Find and store the experimental JV file name parameter from the device parameters in a state. 
    # When not simulating a solar cell, this parameter will later be forced to 'none' again
    for section in dev_par[dev_par_name][1:]:
        if section[0] == 'User interface':
            for param in section:
                if param[1] == 'expJV':
                    st.session_state['expJV'] = param[2]

    if solar_cell is False:
        # Simulation was not for a solar cell. Empty the experimental JV object.
        st.session_state['expJV'] = 'none'
        sc_par = {}

    # Store the solar cell parameters in memory
    st.session_state['sc_par'] = sc_par

def read_scPar(console_output_decoded, dev_par, dev_par_name, run_mode=True):
    """Read the solar cell parameters from the txt line. Store them in a dictionary.

    Parameters
    ----------
    console_output_decoded : string
        complete console output from running the executable
    dev_par : dict
        List object with all parameters and comments.
    dev_par_name : string
        Name of the device parameter file
    run_mode : boolean
        True if function is called as part of The Shell, False when called directly. 
        Prevents using streamlit components outside of The Shell.
    """
    # Solar Cell Parameters from console
    # Set <NA> values for the simulation dict to setup all the avaialble rows
    sc_par = {'Simulated': {'Jsc [Am\u207b\u00b2]': '<NA>', 'Vmpp [V]': '<NA>', 'MPP [Wm\u207b\u00b2]': '<NA>', 'Voc [V]': '<NA>', 'FF ': '<NA>'},
                'Experimental': {},
                'Deviation': {}}

    # Parameters to indicate whether a solar cell has been simulated. If True, try to read and use the solar cell parameters from the console.
    solar_cell = False

    # Write the solar cell parameters to a dict
    for line_console in console_output_decoded.split('\n'):
        sc_par, solar_cell = write_scpars(
            line_console, sc_par, solar_cell)

    if run_mode:
        # Running as part of The Shell, store the parameters as a state
        store_scPar_state(sc_par, solar_cell, dev_par, dev_par_name)
    else:
        # Running standalone, return the dict with solar cell parameters, force empty it when not a solar cell has been simulated.
        if solar_cell is False:
            sc_par = {}
        return sc_par  


def run_SS_JV(simss_device_parameters, session_path, dev_par, layers, id_session, G_fracs=None, varFile=None):
    """Run the CV simulation with the saved device parameters. 
    Display an error message (From SIMsalabim or a generic one) when the simulation did not succeed. 
    Save the used file names in global states to use them in the results.
    Read and store the solar cell parameters from the console output if present. 
       
    Parameters
    ----------
    zimt_device_parameters : str
        The device parameter file name
    session_path : str
        The path to the session folder
    dev_par : list
        The device parameters as a list of nested lists
    layers : List
        List with all layers in the device.
    id_session : str
        Session ID string.
    G_fracs : list, optional
        List of generation fractions for steady state JV, by default None
    varFile : str, optional
        Name of the variable file for steady state JV, by default None

    Returns
    -------
    str
        'SUCCESS' if the simulation succeeded, 'FAILED' if it failed due to known issues (like creating tVG file), 
        'ERROR' for other errors.    
    """
    # We need to ge the varFile name to prevent it from being init as none
    if varFile is None and dev_par is not None:
        try:
            for section in dev_par[simss_device_parameters][1:]:
                if section[0] == 'User interface':
                    for param in section:
                        if param[1] == 'varFile':
                            varFile = param[2]
                            break
                    if varFile is not None:
                        break
        except Exception:
            # If dev_par is malformed, keep varFile_local as None, this will never be reached
            varFile = None

    # Check if there is an old scPars file, and if so, remove it to correctly update the result page
    if dev_par is not None:
        # Find the "User interface" section
        ui_section = next((s for s in dev_par[simss_device_parameters][1:] if s[0] == 'User interface'), [])
        
        # Find the scParsFile parameter
        scParsFile = next((param[2] for param in ui_section if param[1] == 'scParsFile'), None)
    
    # Remove old scParsFile if it exists
    if scParsFile:
        scPars_path = os.path.join(session_path, scParsFile)
        if os.path.isfile(scPars_path):
            os.remove(scPars_path)

    with st.toast('Simulation started'):

        # Call the SS simulation
        result, message = JV_exp.run_SS_JV(simss_device_parameters, session_path, G_fracs=G_fracs, varFile=varFile)

    if result == 0 or result == 95:
        # Simulation succeeded, continue with the process
        st.success(message)
        st.session_state['simulation_results'] = 'Steady State JV' # Init the results page to display Steady State results
        
        # Set the state variable to true to indicate that a new simulation has been run and a new ZIP file with results must be created
        st.session_state['runSimulation'] = True

        # Store the assigned file names from the saved device parameters in session state variables.
        utils_devpar_UI.store_file_names(dev_par, 'simss', simss_device_parameters, layers)

        res = 'SUCCESS'
    else:
        # Simulation failed, show the error message
        st.error(message)
        res = 'ERROR'

    # Log the simulation result in the log file
    with open(os.path.join('Statistics', 'log_file.txt'), 'a') as f:
        f.write(str(id_session) + ' Steady_State ' + res + ' ' + str(datetime.now()) + '\n')
