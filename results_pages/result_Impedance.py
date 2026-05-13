""" UI to display the Impedance spectroscopy results""" 
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

def show_results_impedance(session_path, id_session):
    """Display the results from a Impedance simulation.

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
        if not st.session_state['freqZFile'] in os.listdir(session_path):
            # The main results file (tj file by default) is not present, so no data can be shown. Show an error 
            st.error('No data available. SIMsalabim simulation did not run yet or the device parameters have been changed. Run the simulation first.')
        else:
            # Results data is present, or at least the files are there. 

            # Read the main files/data (freqZFile)
            data_freqZ = pd.read_csv(os.path.join(session_path,st.session_state['freqZFile']), sep=r'\s+')
            data_freqZ["ImZ"] = data_freqZ["ImZ"]*-1

            with st.sidebar:
                # Before downloading, prepare the results package into a ZIP file. This is executed upon loading the page.
                st.write('<strong>Download Simulation results</strong>', unsafe_allow_html=True)
                if st.button("Prepare result package", key='prep_result'):
                    # Create a ZIP file with all relevant files and folders. 
                    utils_gen_UI.prepare_results(session_path, id_session, 'zimt', 'Impedance')

                # Button to download the ZIP file. Only appears after the Prepare Result Package button has been pressed.
                if not st.session_state['runSimulation']:
                    with open('Simulations/simulation_results_' + id_session + '.zip', 'rb') as ff:
                        id_to_time_string = datetime.fromtimestamp(float(id_session) / 1e6).strftime("%Y-%d-%mT%H-%M-%SZ")
                        filename = 'simulation_result_' + id_to_time_string
                        btn = st.download_button(label="Download Simulation Results (ZIP)", data=ff, file_name=filename, mime="application/zip")

                st.markdown('<hr>', unsafe_allow_html=True) # Add a horizontal line to separate the download section from the navigation section

                # Create quick navigation links to the different figures on the page
                st.write('<strong>Navigate to figure: ', unsafe_allow_html=True)
                st.markdown(
                    '<ul>'
                    '<li><a href="#Bode">Bode</a></li>'
                    '<li><a href="#Nyquist">Nyquist </a></li>'
                    '<li><a href="#MagPhase">Magnitude-phase</a></li>'
                    '<li><a href="#CapCond">Conductance & Capacitance</a></li>'
                    '</ul>',
                    unsafe_allow_html=True
                )

                #  Show the SIMsalabim logo in the sidebar
                st.markdown('<hr>', unsafe_allow_html=True)
                st.image('./Figures/SIMsalabim_logo_cut_trans.png')

            st.title("Simulation Results")
            st.subheader(str(st.session_state['simulation_results']))

            # # Create a link at the top of the page
            # st.markdown(
            #     'Go to: <a href="#Nyquist">Jump to Figure</a><a href="#my-figure">Jump to Figure</a><a href="#my-figure">Jump to Figure</a><a href="#my-figure">Jump to Figure</a>',
            #     unsafe_allow_html=True
            # )

            st.markdown('<br>', unsafe_allow_html=True) # Add some space between the title and the log file button
            # Popover window to show the latest SIMsalabim log file
            if 'simulation_log' in st.session_state:
                # get the key from the dict
                if list(st.session_state['simulation_log'].keys())[0] == 'Impedance':
                    with st.popover("**View SIMsalabim log file**"):
                        st.text(st.session_state['simulation_log']['Impedance'])

            # Show the plots, add a horizontal line first to separate the title section from the plot section
            st.markdown('<hr>', unsafe_allow_html=True)

            # Bode [1]
            # Set the navigation id for the plot, so that it can be navigated to from the sidebar
            st.markdown(
                '<span id="Bode"></span>',
                unsafe_allow_html=True
            )

            # Add double break between the plots to ensure that quick navigation shows the complete plot
            st.markdown('<br><br>', unsafe_allow_html=True) # Add a horizontal line to separate the plots

            col1_1, col1_2, col1_3 = st.columns([1, 6, 3])

            with col1_2:
                fig1, ax11 = plt.subplots()
                ax12 = ax11.twinx()
                pars_bode = {'ReZ' : 'Re Z [Ohm m$^2$]', 'ImZ' : '-Im Z [Ohm m$^2$]' }
                selected_1_bode = ['ReZ']
                selected_2_bode = ['ImZ']
                y_error_1 = data_freqZ["ReErrZ"]
                y_error_2 = data_freqZ["ImErrZ"]
                par_x_bode = 'freq'
                xlabel_bode = 'frequency [Hz]'
                ylabel_1_bode = 'Re Z [Ohm m$^2$]'
                ylabel_2_bode = '-Im Z [Ohm m$^2$]'
                title_bode = 'Bode plot'

                utils_plot_UI.create_UI_component_plot_twinx(data_freqZ, pars_bode, selected_1_bode, selected_2_bode, par_x_bode, xlabel_bode, ylabel_1_bode, 
                                                          ylabel_2_bode, title_bode,fig1, ax11, ax12, [col1_1, col1_2, col1_3], show_plot_param=False, yerror_1 = y_error_1, yerror_2 = y_error_2)

            # Nyquist [1]
            # Set the navigation id for the plot, so that it can be navigated to from the sidebar
            st.markdown(
                '<span id="Nyquist"></span>',
                unsafe_allow_html=True
            )

            # Add double break between the plots to ensure that quick navigation shows the complete plot
            st.markdown('<br><br>', unsafe_allow_html=True) # Add a horizontal line to separate the plots

            col2_1, col2_2, col2_3 = st.columns([1, 6, 3])

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
                fig2, ax2 = utils_plot_UI.create_UI_component_plot(data_freqZ, pars_nyq, par_x_nyq, xlabel_nyq, ylabel_nyq, 
                                title_nyq, 1, fig2, ax2, plt.colorbar, [col2_1, col2_2, col2_3], show_plot_param=False, show_yscale=True, show_xscale=True,
                                weight_key=par_weight_nyq, weight_label=weightlabel_nyq, weight_norm=weight_norm_nyq, xrange_format = "%.2e",yrange_format="%.2e")
                st.pyplot(fig2, format='png')

            # Magnitude-phase [3]
            # Set the navigation id for the plot, so that it can be navigated to from the sidebar
            st.markdown(
                '<span id="MagPhase"></span>',
                unsafe_allow_html=True
            )

            # Add double break between the plots to ensure that quick navigation shows the complete plot
            st.markdown('<br><br>', unsafe_allow_html=True) # Add a horizontal line to separate the plots

            col3_1, col3_2, col3_3 = st.columns([1, 6, 3])

            with col3_2:
                fig3, ax31 = plt.subplots()
                ax32 = ax31.twinx()
                pars_magphase = {'magZ' : 'Magnitude [Ohm m$^2$]', 'phaseZ' : 'Phase [deg.]' }
                selected_1_magphase = ['magZ']
                selected_2_magphase = ['phaseZ']
                y_error_1 = data_freqZ["errMagZ"]
                y_error_2 = data_freqZ["errPhaseZ"]
                par_x_magphase = 'freq'
                xlabel_magphase = 'frequency [Hz]'
                ylabel_1_magphase = 'Magnitude [Ohm m$^2$]'
                ylabel_2_magphase = 'Phase [deg.]'
                title_magphase = 'Magnitude-phase plot'

                utils_plot_UI.create_UI_component_plot_twinx(data_freqZ, pars_magphase, selected_1_magphase, selected_2_magphase, par_x_magphase, xlabel_magphase, ylabel_1_magphase, 
                                                          ylabel_2_magphase, title_magphase,fig3, ax31, ax32, [col3_1, col3_2, col3_3], show_plot_param=False, yerror_1 = y_error_1, yerror_2 = y_error_2)

            # Capacitance & Conductance [4]
            # Set the navigation id for the plot, so that it can be navigated to from the sidebar
            st.markdown(
                '<span id="CapCond"></span>',
                unsafe_allow_html=True
            )

            # Add double break between the plots to ensure that quick navigation shows the complete plot
            st.markdown('<br><br>', unsafe_allow_html=True) # Add a horizontal line to separate the plots

            col4_1, col4_2, col4_3 = st.columns([1, 6, 3])

            with col4_2:
                fig4, ax41 = plt.subplots()
                ax42 = ax41.twinx()
                pars_cap_cond = {'G' : 'G [S m$^{-2}$]', 'C' : 'C [F m$^{-2}$]', }
                selected_1_cap_cond = ['G']
                selected_2_cap_cond = ['C']
                y_error_1 = data_freqZ["errG"]
                y_error_2 = data_freqZ["errC"]
                par_x_cap_cond= 'freq'
                xlabel_cap_cond = 'frequency [Hz]'
                ylabel_1_cap_cond = 'Conductance [S m$^{-2}$]'
                ylabel_2_cap_cond = 'Capacitance [F m$^{-2}$]'
                title_cap_cond = 'Conductance & Capacitance'

                utils_plot_UI.create_UI_component_plot_twinx(data_freqZ, pars_cap_cond, selected_1_cap_cond, selected_2_cap_cond, par_x_cap_cond, xlabel_cap_cond, ylabel_1_cap_cond, 
                                                          ylabel_2_cap_cond, title_cap_cond,fig4, ax41, ax42, [col4_1, col4_2, col4_3], show_plot_param=False, yerror_1 = y_error_1, yerror_2 = y_error_2,show_errors=True, yscale_init_2 = 1)
