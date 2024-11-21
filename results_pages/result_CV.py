""" UI to display the CV results"""
######### Package Imports #########################################################################

import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from utils import plot_functions_UI as utils_plot_UI
from utils import general_UI as utils_gen_UI
from utils import plot_def

######### Page configuration ######################################################################

def show_results_CV(session_path, id_session):
    """Display the results from a CV (5) simulation.

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
            utils_gen_UI.prepare_results_download(session_path, id_session, 'zimt', 'CV')
        st.session_state['runSimulation'] = False

    ######### Parameter Initialisation #############################################################
    if not os.path.exists(session_path):
        # There is not a session folder yet, so nothing to show. Show an error.
        st.error('Save the device parameters first and run the simulation.')
    else:
        if not st.session_state['CapVolFile'] in os.listdir(session_path):
            # The main results file (tj file by default) is not present, so no data can be shown. Show an error 
            st.error('No data available. SIMsalabim simulation did not run yet or the device parameters have been changed. Run the simulation first.')
        else:
            # Results data is present, or at least the files are there. 

            # Read the main files/data (tJFile)
            data_CapVol = pd.read_csv(os.path.join(session_path,st.session_state['CapVolFile']), sep=r'\s+')

            with st.sidebar:
                st.write('<strong>Download Simulation results</strong>', unsafe_allow_html=True)
                if st.button("Prepare result package", key='prep_result'):
                    # Create a ZIP file with all relevant files and folders. 
                    prepare_results(session_path, id_session)

                # Button to download the ZIP file
                if not st.session_state['runSimulation']:
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

            # Capacitance-Voltage [1]
            col1_1, col1_2, col1_3 = st.columns([1, 5, 1])

            with col1_2:
                # Create a dictionary for all potential parameters to plot. Key matches the name in the dataFrame, value is the corresponding label. 
                fig1, ax1 = plt.subplots()
                pars_CV = {'C':'C [F m$^{-2}$]'}
                xlabel_CV =  'Voltage [V]'
                par_x_CV = 'V' 
                ylabel_CV = 'Capacitance [F m$^{-2}$]'
                title_CV = 'Capacitance-Voltage'

                fig1, ax1 = utils_plot_UI.create_UI_component_plot(data_CapVol, pars_CV, par_x_CV, xlabel_CV, ylabel_CV, 
                                title_CV, 1, fig1, ax1, plt.errorbar, [col1_1, col1_2, col1_3], show_yscale=True, error_y = 'errC', show_plot_param=False)
                with col1_2:
                    st.pyplot(fig1, format='png')
