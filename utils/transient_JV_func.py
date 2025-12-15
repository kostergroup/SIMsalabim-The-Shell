""" Functions specific for Transient JV simulations"""
######### Package Imports #########################################################################

import os
from datetime import datetime
import streamlit as st
from pySIMsalabim.experiments import hysteresis as transient_exp
from utils import device_parameters_UI as utils_devpar_UI

######### Function Definitions ####################################################################    

def run_Transient_JV(zimt_device_parameters, session_path, dev_par, layers, id_session, transient_par, transient_pars_file):
    """Run the transient JV simulation with the saved device parameters. 
    Display an error message (From SIMsalabim or a generic one) when the simulation did not succeed. 
    Save the used file names in global states to use them in the results.

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
    transient_par : dict
        The transient JV specific parameters
    transient_pars_file : str
        The name of the file to save the transient JV parameters to.

    Returns
    -------
    str
        'SUCCESS' if the simulation succeeded, 'FAILED' if it failed due to known issues (like creating tVG file), 
        'ERROR' for other errors.
    """
    with st.toast('Simulation started'):
        # Store all transient specific parameters into a single object.
        transient_keys = ["scan_speed", "direction", "G_frac", "UseExpData", "Vmin", "Vmax",'steps','expJV_Vmin_Vmax','expJV_Vmax_Vmin']
        transient_keys_extract = {"tVGFile"}
        transient_par_obj = utils_devpar_UI.read_exp_parameters(transient_par, dev_par[zimt_device_parameters], transient_keys, transient_keys_extract)

        # Run the Transient JV script
        result, message, output_vals = transient_exp.Hysteresis_JV(zimt_device_parameters, session_path, transient_par_obj['UseExpData'], 
                                                    transient_par_obj['scan_speed'], transient_par_obj['direction'], transient_par_obj['G_frac'], 
                                                    transient_par_obj['tVGFile'], run_mode = True, Vmin = transient_par_obj['Vmin'], 
                                                    Vmax =transient_par_obj['Vmax'],steps = transient_par_obj['steps'],
                                                    expJV_Vmin_Vmax=transient_par_obj['expJV_Vmin_Vmax'], 
                                                    expJV_Vmax_Vmin=transient_par_obj['expJV_Vmax_Vmin'])
    if result == 1:
        # Creating the tVG file for the transient loop failed                
        st.error(message)
        res = 'FAILED'
    else:
        if result == 0 or result == 95:
            # Simulation succeeded, continue with the process
            st.success(message)
            st.session_state['simulation_results'] = 'Transient JV' # Init the results page to display Steady State results

            # Save the Transient parameters in a file
            if os.path.isfile(os.path.join(session_path, transient_pars_file)):
                    os.remove(os.path.join(os.path.join(session_path, transient_pars_file)))
            with open(os.path.join(session_path, transient_pars_file), 'w') as fp_transient:
                for key,value in transient_par_obj.items():
                    fp_transient.write('%s = %s\n' % (key, value))

            st.session_state['expObject'] = transient_par_obj
            st.session_state['transientPars'] = transient_pars_file
            if transient_par_obj['UseExpData'] == 1:
                # Share the rms error with the results page
                st.session_state['hystRmsError'] = output_vals['rms']
            
            # Store the hysteresis index in the session state
            st.session_state['hystIndex'] = output_vals['hyst_index']

            # Set the state variable to true to indicate that a new simulation has been run and a new ZIP file with results must be created
            st.session_state['runSimulation'] = True

            # Store the assigned file names from the saved device parameters in session state variables.
            utils_devpar_UI.store_file_names(dev_par, 'zimt', zimt_device_parameters, layers)

            res = 'SUCCESS'

        else:
            # Simulation failed, show the error message
            st.error(message)

            res = 'ERROR'

    # Log the simulation result in the log file
    with open(os.path.join('Statistics', 'log_file.txt'), 'a') as f:
        f.write(id_session + ' Transient ' + res + ' ' + str(datetime.now()) + '\n')
