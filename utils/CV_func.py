""" Functions specific for CV simulations"""
######### Package Imports #########################################################################

import os
from datetime import datetime
import streamlit as st
from pySIMsalabim.experiments import CV as CV_exp
from utils import device_parameters_UI as utils_devpar_UI

######### Function Definitions ####################################################################    

def run_CV(zimt_device_parameters, session_path, dev_par, layers, id_session, CV_par, CV_pars_file):
    """Run the CV simulation with the saved device parameters. 
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
    CV_par : dict
        The CV specific parameters
    CV_pars_file : str
        The name of the file to save the CV parameters to.

    Returns
    -------
    str
        'SUCCESS' if the simulation succeeded, 'FAILED' if it failed due to known issues (like creating tVG file), 
        'ERROR' for other errors.
    """
    with st.toast('Simulation started'):
        # Store all CV specific parameters into a single object.
        CV_keys = ["freq", "Vmin", "Vmax", "delV", "Vstep", "G_frac"]
        CV_keys_extract = {"tVGFile", "tJFile"}
        CV_par_obj = utils_devpar_UI.read_exp_parameters(CV_par, dev_par[zimt_device_parameters], CV_keys, CV_keys_extract)

        # Run the CV script
        result, message = CV_exp.run_CV_simu(zimt_device_parameters, session_path, CV_par_obj["freq"], CV_par_obj["Vmin"],CV_par_obj["Vmax"],
                                                            CV_par_obj["Vstep"],CV_par_obj["G_frac"], CV_par_obj["delV"], run_mode =True, 
                                                            tVG_name = CV_par_obj["tVGFile"], tj_name=CV_par_obj['tJFile'])
    
    if result == 1:
        # Creating the tVG file for the CV failed                
        st.error(message)
        res = 'FAILED'
    else:
        if result == 0 or result == 95:
            # Simulation succeeded, continue with the process
            st.success('Simulation complete. Output can be found in the Simulation results.')
            st.session_state['simulation_results'] = 'CV' # Init the results page to display Steady State results

            # Save the CV parameters in a file
            if os.path.isfile(os.path.join(session_path, CV_pars_file)):
                    os.remove(os.path.join(os.path.join(session_path, CV_pars_file)))
            with open(os.path.join(session_path, CV_pars_file), 'w') as fp_CV:
                for key,value in CV_par_obj.items():
                    fp_CV.write('%s = %s\n' % (key, value))

            st.session_state['expObject'] = CV_par_obj
            st.session_state['CVPars'] = CV_pars_file
            st.session_state['CapVolFile'] = 'CapVol.dat' # Currently a fixed name

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
        f.write(id_session + ' CV ' + res + ' ' + str(datetime.now()) + '\n')
