""" Functions specific for Steady State (SimSS) case"""
######### Package Imports #########################################################################

import streamlit as st

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
    dev_par : dict
        Dict object with all parameters and comments.
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
