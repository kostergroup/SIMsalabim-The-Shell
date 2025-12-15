""" Functions specific for IMPS simulations"""
######### Package Imports #########################################################################

import os
from datetime import datetime
import streamlit as st
from pySIMsalabim.experiments import imps as imps_exp
from utils import device_parameters_UI as utils_devpar_UI

######### Function Definitions ####################################################################    

def run_IMPS(zimt_device_parameters, session_path, dev_par, layers, id_session, imps_par, imps_pars_file):
    """Run the IMPS simulation with the saved device parameters. 
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
    imps_par : dict
        The IMPS specific parameters
    imps_pars_file : str
        The name of the file to save the IMPS parameters to.

    Returns
    -------
    str
        'SUCCESS' if the simulation succeeded, 'FAILED' if it failed due to known issues (like creating tVG file), 
        'ERROR' for other errors.
    """
    with st.toast('Simulation started'):
        # Store all imps specific parameters into a single object.
        imps_keys = ["fmin", "fmax", "fstep", "V0", "fracG", "G_frac"]
        imps_keys_extract = {"tVGFile", "tJFile"}
        imps_par_obj = utils_devpar_UI.read_exp_parameters(imps_par, dev_par[zimt_device_parameters], imps_keys, imps_keys_extract)

        # Run the imps script
        result, message = imps_exp.run_IMPS_simu(zimt_device_parameters, session_path, imps_par_obj["fmin"], imps_par_obj["fmax"],
                                                    imps_par_obj["fstep"],imps_par_obj["V0"], imps_par_obj["fracG"],imps_par_obj["G_frac"],
                                                    run_mode = True, tVG_name=imps_par_obj["tVGFile"], tj_name=imps_par_obj['tJFile'])
    
    if result == 1:
        # Creating the tVG file for the IMPS failed                
        st.error(message)
        res = 'FAILED'
    else:
        if result == 0 or result == 95:
            # Simulation succeeded, continue with the process
            st.success('Simulation complete. Output can be found in the Simulation results.')
            st.session_state['simulation_results'] = 'IMPS' # Init the results page to display Steady State results

            # Save the imps parameters in a file

            if os.path.isfile(os.path.join(session_path, imps_pars_file)):
                    os.remove(os.path.join(os.path.join(session_path, imps_pars_file)))
            with open(os.path.join(session_path, imps_pars_file), 'w') as fp_imps:
                for key,value in imps_par_obj.items():
                    fp_imps.write('%s = %s\n' % (key, value))

            st.session_state['expObject'] = imps_par_obj
            st.session_state['IMPSPars'] = imps_pars_file
            st.session_state['freqYFile'] = 'freqY.dat' # Currently a fixed name

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
        f.write(id_session + ' IMPS ' + res + ' ' + str(datetime.now()) + '\n')