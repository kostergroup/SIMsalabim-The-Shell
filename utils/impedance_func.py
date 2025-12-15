""" Functions specific for impedance spectroscopy simulations"""
######### Package Imports #########################################################################

import os
from datetime import datetime
import streamlit as st
from pySIMsalabim.experiments import impedance as imp_exp
from utils import device_parameters_UI as utils_devpar_UI

######### Function Definitions ####################################################################    

def run_Impedance(zimt_device_parameters, session_path, dev_par, layers, id_session, impedance_par, impedance_pars_file):
    """Run the Impedance simulation with the saved device parameters. 
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
    impedance_par : dict
        The Impedance specific parameters
    impedance_pars_file : str
        The name of the file to save the Impedance parameters to.

    Returns
    -------
    str
        'SUCCESS' if the simulation succeeded, 'FAILED' if it failed due to known issues (like creating tVG file), 
        'ERROR' for other errors.
    """
    with st.toast('Simulation started'):
        # Store all impedance specific parameters into a single object.
        impedance_keys = ["fmin", "fmax", "fstep", "V0", "delV", "G_frac"]
        impedance_keys_extract = {"tVGFile", "tJFile"}
        impedance_par_obj = utils_devpar_UI.read_exp_parameters(impedance_par, dev_par[zimt_device_parameters], impedance_keys, impedance_keys_extract)

        # Run the impedance script
        result, message = imp_exp.run_impedance_simu(zimt_device_parameters, session_path, impedance_par_obj["fmin"], impedance_par_obj["fmax"],
                                                            impedance_par_obj["fstep"],impedance_par_obj["V0"], impedance_par_obj["G_frac"],
                                                            impedance_par_obj["delV"],True, tVG_name = impedance_par_obj["tVGFile"], 
                                                            tj_name=impedance_par_obj['tJFile'])
    
    if result == 1:
        # Creating the tVG file for the impedance failed                
        st.error(message)
        res = 'FAILED'
    else:
        if result == 0 or result == 95:
            # Simulation succeeded, continue with the process
            st.success('Simulation complete. Output can be found in the Simulation results.')
            st.session_state['simulation_results'] = 'Impedance' # Init the results page to display Steady State results

            # Save the impedance parameters in a file

            if os.path.isfile(os.path.join(session_path, impedance_pars_file)):
                    os.remove(os.path.join(os.path.join(session_path, impedance_pars_file)))
            with open(os.path.join(session_path, impedance_pars_file), 'w') as fp_impedance:
                for key,value in impedance_par_obj.items():
                    fp_impedance.write('%s = %s\n' % (key, value))

            st.session_state['expObject'] = impedance_par_obj
            st.session_state['impedancePars'] = impedance_pars_file
            st.session_state['freqZFile'] = 'freqZ.dat' # Currently a fixed name

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
        f.write(id_session + ' Impedance ' + res + ' ' + str(datetime.now()) + '\n')