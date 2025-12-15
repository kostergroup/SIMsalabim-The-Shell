""" UI to display the IMPS results"""
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

def show_results_imps(session_path, id_session):
    """Display the results from an IMPS simulation.

    Parameters
    ----------
    session_path : string
        Path to folder with the simulation results
    id_session : string
        Current session id
    """

    ######### Function Definition #################################################################

    ######### Parameter Initialisation #############################################################

    if not os.path.exists(session_path):
        # There is not a session folder yet, so nothing to show. Show an error.
        st.error('Save the device parameters first and run the simulation.')
    else:
        if not st.session_state['freqYFile'] in os.listdir(session_path):
            # The main results file (tj file by default) is not present, so no data can be shown. Show an error 
            st.error('No data available. SIMsalabim simulation did not run yet or the device parameters have been changed. Run the simulation first.')
        else:
            # Results data is present, or at least the files are there. 

            # Read the main files/data (tJFile)
            data_freqY = pd.read_csv(os.path.join(session_path,st.session_state['freqYFile']), sep=r'\s+')
            data_freqY["ImZ"] = data_freqY["ImY"]*-1

            # Define plot type options
            plot_type = [plt.plot, plt.scatter]

            with st.sidebar:
                # Before downloading, prepare the results package into a ZIP file. This is executed upon loading the page.
                st.write('<strong>Download Simulation results</strong>', unsafe_allow_html=True)
                if st.button("Prepare result package", key='prep_result'):
                    # Create a ZIP file with all relevant files and folders. 
                    utils_gen_UI.prepare_results(session_path, id_session, 'zimt', 'IMPS')

                # Button to download the ZIP file. Only appears after the Prepare Result Package button has been pressed.
                if not st.session_state['runSimulation']:
                    with open('Simulations/simulation_results_' + id_session + '.zip', 'rb') as ff:
                        id_to_time_string = datetime.fromtimestamp(float(id_session) / 1e6).strftime("%Y-%d-%mT%H-%M-%SZ")
                        filename = 'simulation_result_' + id_to_time_string
                        btn = st.download_button(label="Download Simulation Results (ZIP)", data=ff, file_name=filename, mime="application/zip")

                #  Show the SIMsalabim logo in the sidebar
                st.markdown('<hr>', unsafe_allow_html=True)
                st.image('./Figures/SIMsalabim_logo_cut_trans.png')

            st.title("Simulation Results")
            st.subheader(str(st.session_state['simulation_results']))

            # Show the plots, add a horizontal line first to separate the title section from the plot section
            st.markdown('<hr>', unsafe_allow_html=True)

            # ImZ plot [1]
            col1_1, col1_2, col1_3 = st.columns([1, 6, 3])

            with col1_2:
                fig2, ax2 = plt.subplots()
                pars_nyq = {'ImY' : '-Im Y [A/m$^2$]'}
                par_x_nyq = 'ReY'
                par_weight_nyq = 'freq'
                xlabel_nyq = 'Re Y [A/m$^2$]'
                ylabel_nyq = '-Im Y [A/m$^2$]'
                weightlabel_nyq = 'frequency [Hz]'
                weight_norm_nyq = 'log'
                title_nyq = 'Cole-Cole plot'

                # Plot the Cole-Cole plot with or without errorbars
                fig2, ax2 = utils_plot_UI.create_UI_component_plot(data_freqY, pars_nyq, par_x_nyq, xlabel_nyq, ylabel_nyq, 
                                title_nyq, 1, fig2, ax2, plt.colorbar, [col1_1, col1_2, col1_3], show_plot_param=False, show_yscale=True, show_xscale=True,
                                weight_key=par_weight_nyq, weight_label=weightlabel_nyq, weight_norm=weight_norm_nyq, xrange_format="%.2e", yrange_format="%.2e")
                st.pyplot(fig2, format='png')
