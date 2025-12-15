""" UI to display the Transient JV results"""
######### Package Imports #########################################################################

import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from pySIMsalabim.experiments import hysteresis as transient_exp
from utils import plot_functions_UI as utils_plot_UI
from utils import general_UI as utils_gen_UI
from utils import plot_def

######### Page configuration ######################################################################

def show_results_Transient_JV(session_path, id_session):
    """Display the results from a transient JV simulation.

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
        if not st.session_state['tJFile'] in os.listdir(session_path):
            # The main results file (tj file by default) is not present, so no data can be shown. Show an error 
            st.error('No data available. SIMsalabim simulation did not run yet or the device parameters have been changed. Run the simulation first.')
        else:
            # Results data is present, or at least the files are there. 

            # Read the main files/data (tJFile)
            data_tj = pd.read_csv(os.path.join(session_path,st.session_state['tJFile']), sep=r'\s+')

            if st.session_state["expObject"]['UseExpData'] == 1:
                data_JVExp = transient_exp.concatJVs(session_path, st.session_state["expObject"]['expJV_Vmin_Vmax'], st.session_state["expObject"]['expJV_Vmax_Vmin'], 
                                                st.session_state["expObject"]['direction'])

            # Define plot type options
            plot_type = [plt.plot, plt.scatter]

            with st.sidebar:
                # Before downloading, prepare the results package into a ZIP file. This is executed upon loading the page.
                st.write('<strong>Download Simulation results</strong>', unsafe_allow_html=True)
                if st.button("Prepare result package", key='prep_result'):
                    # Create a ZIP file with all relevant files and folders. 
                    utils_gen_UI.prepare_results(session_path, id_session, 'zimt', 'Transient_JV')

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

            # JV curve [1]
            col1_1, col1_2, col1_3 = st.columns([2, 8, 4])

            with col1_1:
                st.markdown('<br>', unsafe_allow_html=True)
                st.markdown(f'<h4>Hysteresis Index (HI): {st.session_state["hystIndex"]:.3f}</h4>', unsafe_allow_html=True)

                st.markdown('<br>', unsafe_allow_html=True)

                # Create a popover window where the defintion of the Hysteresis Index is shown
                with st.popover("Show Hysteresis Index definition"):
                    HI_def = r'''
                    #### Hysteresis Index (HI) defintion
                    The Hysteresis Index is defined as the difference area between the forward and backward scan of the JV curve normalised by the maximum spanned area.
                    $$ 
                    \mathrm{HI} = \frac{\int_{V_{\rm min}}^{V_{\rm max}} \left|J_{1} - J_{2}\right|\mathrm{d}V}{\left(J_{\rm max}-J_{\rm min}\right)\left(V_{\rm max}-V_{\rm min}\right)}
                    $$ 

                    '''
                    st.write(HI_def)
                    st.image('Figures/Hysteresis_Index_def.png')

                # Show the rms error when comparing to experimental data
                if st.session_state["expObject"]['UseExpData'] == 1:
                    st.markdown('<br><br>', unsafe_allow_html=True)
                    st.write(f'**RMS error between simulated and experimental data: {st.session_state["hystRmsError"]:.5f}**')
            with col1_2:
                # Init plot parameters
                pars_transient = {'Jext' : '$J_{ext}$'}
                par_x_transient = 'Vext'
                par_weight_transient = 't'
                xlabel_transient = '$V_{ext}$ [V]'
                ylabel_transient = '$J_{ext}$ [Am$^{-2}$]'
                weightlabel_transient = '$t$ [s]'
                title_transient = ''
                fig1, ax1 = plt.subplots()

                # Create the plot
                fig1,ax1 = utils_plot_UI.create_UI_component_plot(data_tj, pars_transient, par_x_transient, xlabel_transient, ylabel_transient, 
                                title_transient, 1, fig1, ax1, plot_type[0], [col1_1, col1_2, col1_3], show_plot_param=False, show_yscale=False, 
                                weight_key=par_weight_transient, weight_label=weightlabel_transient,yrange_format="%.2e")
                # Add the experimental data points to the plot
                if st.session_state["expObject"]['UseExpData'] == 1:
                    # Plot the experimental data and move it behind the simulated curve.
                    ax1.plot(data_JVExp['Vext'],data_JVExp['Jext'],'.b', zorder=0, markersize = 5)
                    ax1.legend(['Simulation', 'Experiments'])
                # Show the plot
                st.pyplot(fig1, format='png')        