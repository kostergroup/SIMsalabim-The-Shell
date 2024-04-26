""" UI to display the Impedance spectroscopy results"""
######### Package Imports #########################################################################

import os
from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from utils import plot_functions as utils_plot
from utils import general_web as utils_gen_web

######### Page configuration ######################################################################

def show_results_impedance(session_path, id_session):
    """Display the results from a Impedance (3) simulation.

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
            utils_gen_web.prepare_results_download(session_path, id_session, 'zimt', 'impedance')
        st.session_state['run_simulation'] = False

    ######### Parameter Initialisation #############################################################
    if not os.path.exists(session_path):
        # There is not a session folder yet, so nothing to show. Show an error.
        st.error('Save the device parameters first and run the simulation.')
    else:
        if not st.session_state['freqZ_file'] in os.listdir(session_path):
            # The main results file (tj file by default) is not present, so no data can be shown. Show an error 
            st.error('No data available. SIMsalabim simulation did not run yet or the device parameters have been changed. Run the simulation first.')
        else:
            # Results data is present, or at least the files are there. 

            # Read the main files/data (tj_file)
            data_freqZ = pd.read_csv(os.path.join(session_path,st.session_state['freqZ_file']), sep=r'\s+')
            data_freqZ["ImZ"] = data_freqZ["ImZ"]*-1

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

            # Bode [1]
            col1_1, col1_2, col1_3 = st.columns([1, 5, 1])

            with col1_2:
                fig1, ax11 = plt.subplots()
                ax12 = ax11.twinx()
                pars_bode = {'ReZ' : 'Re Z [Ohm m$^2$]', 'ImZ' : '-Im Z [Ohm m$^2$]' }
                selected_1_bode = ['ReZ']
                selected_2_bode = ['ImZ']
                par_x_bode = 'freq'
                xlabel_bode = 'frequency [Hz]'
                ylabel_1_bode = 'Re Z [Ohm m$^2$]'
                ylabel_2_bode = '-Im Z [Ohm m$^2$]'
                title_bode = 'Bode plot'

                utils_plot.create_UI_component_plot_twinx(data_freqZ, pars_bode, selected_1_bode, selected_2_bode, par_x_bode, xlabel_bode, ylabel_1_bode, 
                                                          ylabel_2_bode, title_bode,fig1, ax11, ax12, [col1_1, col1_2, col1_3], show_plot_param=False)

            # Nyquist [1]
            col2_1, col2_2, col2_3 = st.columns([1, 6, 1])

            with col2_2:
                fig2, ax2 = plt.subplots()
                pars_nyq = {'ImZ' : '-Im Z [Ohm m$^2$]'}
                par_x_nyq = 'ReZ'
                par_weight_nyq = 'freq'
                xlabel_nyq = 'Re Z [Ohm m$^2$]'
                ylabel_nyq = '-Im Z [Ohm m$^2$]'
                weightlabel_nyq = 'frequency [Hz]'
                weight_norm_nyq = 'log'
                title_nyq = 'Nyquist plot'

                # Plot the nyquist plot with or without errorbars
                fig2, ax2 = utils_plot.create_UI_component_plot(data_freqZ, pars_nyq, par_x_nyq, xlabel_nyq, ylabel_nyq, 
                                title_nyq, 1, fig2, ax2, plt.colorbar, [col2_1, col2_2, col2_3], show_plot_param=False, show_yscale=True, show_xscale=True,
                                weight_key=par_weight_nyq, weight_label=weightlabel_nyq, weight_norm=weight_norm_nyq)
                st.pyplot(fig2, format='png')

            # Capacitance & Conductance 
            col3_1, col3_2, col3_3 = st.columns([1, 5, 1])

            with col3_2:
                fig3, ax31 = plt.subplots()
                ax32 = ax31.twinx()
                pars_cap_cond = {'G' : 'G [S m$^{-2}$]', 'C' : 'C [F m$^{-2}$]', }
                selected_1_cap_cond = ['G']
                selected_2_cap_cond = ['C']
                par_x_cap_cond= 'freq'
                xlabel_cap_cond = 'frequency [Hz]'
                ylabel_1_cap_cond = 'Conductance [S m$^{-2}$]'
                ylabel_2_cap_cond = 'Capacitance [F m$^{-2}$]'
                title_cap_cond = 'Conductance & Capacitance'

                utils_plot.create_UI_component_plot_twinx(data_freqZ, pars_cap_cond, selected_1_cap_cond, selected_2_cap_cond, par_x_cap_cond, xlabel_cap_cond, ylabel_1_cap_cond, 
                                                          ylabel_2_cap_cond, title_cap_cond,fig3, ax31, ax32, [col3_1, col3_2, col3_3], show_plot_param=False, show_errors=False, yscale_init_2 = 1)
