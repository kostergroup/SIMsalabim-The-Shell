""" UI to display the Hysteresis JV results"""
######### Package Imports #########################################################################

import os
from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from utils import plot_functions as utils_plot
from utils import general_web as utils_gen_web

######### Page configuration ######################################################################

def show_results_Hysteresis_JV(session_path, id_session):
    """Display the results from a Hysteresis (2) JV simulation.

    Parameters
    ----------
    session_path : string
        Path to folder with the simulation results
    id_session : string
        Current session id
    """

    ######### Function Definition #################################################################

    def prepare_results(session_path, id_session):
        """Create a ZIP file with the relevant results.Update the session state variable to show/hide the download button when preparing is complete

        Parameters
        ----------
        session_path : string
            Path to folder with the simulation results
        id_session : string
            Current session id
        """
        # Because this can take sme time show a spinner to indicate that something is being done and the program did not freeze
        with st.spinner('Preparing results...'):
            utils_gen_web.prepare_results_download(session_path, id_session, 'zimt', 'hysteresis')
        st.session_state['run_simulation'] = False

    ######### Parameter Initialisation #############################################################

    if not os.path.exists(session_path):
        # There is not a session folder yet, so nothing to show. Show an error.
        st.error('Save the device parameters first and run the simulation.')
    else:
        if not st.session_state['tj_file'] in os.listdir(session_path):
            # The main results file (tj file by default) is not present, so no data can be shown. Show an error 
            st.error('No data available. SIMsalabim simulation did not run yet or the device parameters have been changed. Run the simulation first.')
        else:
            # Results data is present, or at least the files are there. 

            # Read the main files/data (tj_file)
            data_tj = pd.read_csv(os.path.join(session_path,st.session_state['tj_file']), delim_whitespace=True)

            # Define plot type options
            plot_type = [plt.plot, plt.scatter]

            with st.sidebar:
                st.write('<strong>Download Simulation results</strong>', unsafe_allow_html=True)
                if st.button("Prepare result package", key='prep_result'):
                    # Create a ZIP file with all relevant files and folders. 
                    prepare_results(session_path, id_session)

                # Button to download the ZIP file
                if not st.session_state['run_simulation']:
                    with open('Simulations/simulation_results_' + id_session + '.zip', 'rb') as ff:
                        id_to_time_string = datetime.fromtimestamp(float(id_session) / 1e6).strftime("%Y-%d-%mT%H-%M-%SZ")
                        filename = 'simulation_result_' + id_to_time_string
                        btn = st.download_button(label="Download Simulation Results (ZIP)", data=ff, file_name=filename, mime="application/zip")

                #  Show the SIMsalabim logo in the sidebar
                st.markdown('<hr>', unsafe_allow_html=True)
                st.image('./logo/SIMsalabim_logo_cut_trans.png')

            st.title("Simulation Results")
            st.subheader(str(st.session_state['simulation_results']))

            # Show the plots, add a horizontal line first to separate the title section from the plot section
            st.markdown('<hr>', unsafe_allow_html=True)

            # JV curve [1]
            col1_1, col1_2, col1_3 = st.columns([2, 5, 2])

            with col1_2:
                # Init plot parameters
                pars_hyst = {'Jext' : '$J_{ext}$'}
                par_x_hyst = 'Vext'
                par_weight_hyst = 't'
                xlabel_hyst = '$V_{ext}$ [V]'
                ylabel_hyst = 'Current density [Am$^{-2}$]'
                weightlabel_hyst = '$t$ [s]'
                title_hyst = 'JV curve'
                fig1, ax1 = plt.subplots()

                # Create the plot
                utils_plot.create_UI_component_plot(data_tj, pars_hyst, par_x_hyst, xlabel_hyst, ylabel_hyst, 
                                title_hyst, 1, fig1, ax1, plot_type[0], [col1_1, col1_2, col1_3], show_plot_param=False, show_yscale=False, 
                                weight_key=par_weight_hyst, weight_label=weightlabel_hyst)
            
