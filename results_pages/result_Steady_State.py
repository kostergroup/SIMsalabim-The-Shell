""" UI to display the Steady State (SimSS) results"""
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

def show_results_Steady_State(session_path, id_session):
    """Display the results from a Steady State (1) JV simulation.

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
            utils_gen_UI.prepare_results_download(session_path, id_session, 'simss', '')
        st.session_state['runSimulation'] = False

    ######### Parameter Initialisation #############################################################

    if not os.path.exists(session_path):
        # There is not a session folder yet, so nothing to show. Show an error.
        st.error('Save the device parameters first and run the simulation.')
    else:
        if not st.session_state['varFile'] in os.listdir(session_path):
            # The main results file (Var file by default) is not present, so no data can be shown. Show an error 
            st.error('No data available. SIMsalabim simulation did not run yet or the device parameters have been changed. Run the simulation first.')
        else:
            # Results data is present, or at least the files are there. 

            # Read the main files/data (Var, JV and optional ScPars)
            data_var = pd.read_csv(os.path.join(session_path,st.session_state['varFile']), sep=r'\s+')

            # In some very rare situations the JV file is empty. Check the size of the file first to prevent breaking the page
            if os.path.getsize(os.path.join(session_path,st.session_state['JVFile'])) != 0:
                data_jv = pd.read_csv(os.path.join(session_path,st.session_state['JVFile']), sep=r'\s+')
                showJV = True
            else:
                # JV file is empty (can occur under certain specific conditions) initialize an empty dict to continue
                showJV = False

            # Read the solar cell parameter data from memory/state variable, even when they are not present. This will just result in an empty dictionary.
            scpars_data = st.session_state['sc_par'] 

            # Define plot type options
            plot_type = [plt.plot, plt.scatter]
            
            # Convert all x positions in the Var object to nm. For display only!
            data_var['x'] = data_var['x']*1e9

            ######### Function Definitions ####################################################################

            ######### UI layout ###############################################################################
                
            with st.sidebar:
                st.subheader('Plots')

                #  List of checkboxes to show/hide different plotsz
                chk_potential = st.toggle('Potential')
                chk_QFLS = st.toggle('Quasi-Fermi level splitting')
                chk_energy = st.toggle('Energy band diagram')
                chk_density = st.toggle('Carrier densities')
                chk_fill = st.toggle('Filling levels')
                chk_transport = st.toggle('Transport')
                chk_gen_recomb = st.toggle('Generation and recombination')
                chk_current = st.toggle('Current densities')

                # Slider for Vext to update the parameter plots and show curves for the selected Vext. Using the slider updates the plots automatically.
                voltages = list(set(data_var['Vext']))
                voltages.sort()
                st.markdown('<h4>Voltage (Vext) to plot variables at</h4>', unsafe_allow_html=True)
                choice_voltage = st.select_slider('Voltage to plot variables at', voltages, label_visibility='collapsed')

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
                st.image('./Figures/SIMsalabim_logo_cut_trans.png')

            # Initialize the columns to display the results. Adjust based onthe solar cell parameters.
            if not scpars_data == {}:
                # When the simulation has been run before with experimental JV data, sc_pars_data can exist and still be filled. 
                # The state parameter 'experimental' is however leading. 
                if 'Experimental' in scpars_data:
                    if len(scpars_data['Experimental']) == 0:
                        # No expJV data used, use a wide column for the header title and a small column for the ScPars
                        exp_jv = False
                        col1_head, col2_head = st.columns([4, 2])
                    else:
                        # expJV data present, use a small column for the header title and a wide column for the ScPars
                        col1_head, col2_head = st.columns([2, 3])
                        exp_jv = True
                        df_exp_jv = pd.read_csv(os.path.join(session_path, st.session_state['expJV']), sep=r'\s+')
                else:
                    # No experimental ScPars data present, use the default column layout with a wide column for the header title.
                    col1_head, col2_head = st.columns([4, 2])
                    exp_jv = False

                # Header title column
                with col1_head:
                    st.title("Simulation Results")
                    st.subheader(str(st.session_state['simulation_results']))

                # Header ScPars column
                with col2_head:
                    st.subheader('Solar cell parameters')
                    # Show the solar cell parameters (simulated and experimental if available)
                    # Remove Experimental and Deviation column from dict when they are not filled. (UseExpData=0)
                    if 'Experimental' in scpars_data and len(scpars_data['Experimental']) == 0:
                        scpars_data.pop('Experimental')
                        scpars_data.pop('Deviation')
                    # Create a DataFrame from the dict and show in table (readonly)
                    df = pd.DataFrame.from_dict(scpars_data, orient='columns')
                    st.table(df)
            else:
                # No ScPars data at all, use the default column layout with a wide column for the header title.
                col1_head, col2_head = st.columns([4, 2])
                exp_jv = False
                with col1_head:
                    st.title("Simulation Results")
                    st.subheader(str(st.session_state['simulation_results']))

            # Show the plots
            st.markdown('<hr>', unsafe_allow_html=True)

            # JV curve [1]
            col1_1, col1_2, col1_3 = st.columns([1, 6, 3])

            with col1_3:
                # Figure options
                st.markdown('<br>', unsafe_allow_html=True)
                st.markdown('<hr>', unsafe_allow_html=True)

                # Show options to change scale and limits of the axis.
                # Note: when changing the y-axis (Current density) to log scale, the absolute value of the current density is shown.
                with st.expander('Figure options', expanded=True):
                    scale_options = ['linear', 'log']
                    
                    st.text('x-scale:')
                    xscale = st.radio('x-scale', scale_options, index = 0, key = 'JV-x-scale', label_visibility='collapsed',horizontal=True)
                    st.text('y-scale:')
                    yscale = st.radio('y-scale', scale_options, index = 0, key = 'JV-y-scale', label_visibility='collapsed',horizontal=True)
  
                    # Have input fields for the x and y axis range.
                    st.text('Set the x-axis range:')
                    col1_x, col2_x, = st.columns([1,1])
                    with col1_x:
                        # Initially add some margin around the curve to avoid the curve to be on the edge of the plot. We take 5% of the total interval of the data.
                        xlow_init = min(data_jv['Vext']) - abs((max(data_jv['Vext']) - min(data_jv['Vext'])) * 0.05)
                        xlow = st.number_input('X-range', value = xlow_init, key = 'JV-xrange_low',label_visibility="collapsed")
                    with col2_x:
                        # Initially add some margin around the curve to avoid the curve to be on the edge of the plot. We take 5% of the total interval of the data.
                        xup_init = max(data_jv['Vext']) + abs((max(data_jv['Vext']) - min(data_jv['Vext'])) * 0.05)
                        xup = st.number_input('X-range', value=xup_init, key = 'JV-xrange_up',label_visibility="collapsed")

                    st.text('Set the y-axis range:')
                    col1_y, col2_y, = st.columns([1,1])
    
                    with col1_y:
                        # Take into account whether experimental data is present or not, adjust the initial limits accordingly. Still take 5% of the total interval of the data.
                        if exp_jv:
                            if yscale == 'log':
                                # When using a log scale, we show tha abs value of the current density, adjust the initial lower limit accordingly
                                ylow_init = min(min(abs(data_jv['Jext'])),min(abs(df_exp_jv['Jext']))) - abs((max(max(abs(data_jv['Jext'])),max(abs(df_exp_jv['Jext']))) - min(min(abs(data_jv['Jext'])),min(abs(df_exp_jv['Jext'])))) * 0.05)
                            else:
                                ylow_init = min(min(data_jv['Jext']),min(df_exp_jv['Jext'])) - abs((max(max(data_jv['Jext']),max(df_exp_jv['Jext'])) - min(min(data_jv['Jext']),min(df_exp_jv['Jext']))) * 0.05)
                            ylow = st.number_input('Y-range', value=ylow_init, key = 'JV-yrange_low',label_visibility="collapsed")
                        else:
                            if yscale == 'log':
                                # When using a log scale, we show tha abs value of the current density, adjust the initial lower limit accordingly
                                ylow_init = min(abs(data_jv['Jext'])) - abs((max(abs(data_jv['Jext'])) - min(abs(data_jv['Jext']))) * 0.05)
                            else:
                                ylow_init = min(data_jv['Jext']) - abs((max(data_jv['Jext']) - min(data_jv['Jext'])) * 0.05)
                            ylow = st.number_input('Y-range', value=ylow_init, key = 'JV-yrange_low',label_visibility="collapsed")
                    with col2_y:
                        if exp_jv:
                            if yscale == 'log':
                                yup_init = max(max(abs(data_jv['Jext'])),max(abs(df_exp_jv['Jext']))) + abs((max(max(abs(data_jv['Jext'])),max(abs(df_exp_jv['Jext']))) - min(min(abs(data_jv['Jext'])),min(abs(df_exp_jv['Jext'])))) * 0.05)
                            else:
                                yup_init = max(max(data_jv['Jext']),max(df_exp_jv['Jext'])) + abs((max(max(data_jv['Jext']),max(df_exp_jv['Jext'])) - min(min(data_jv['Jext']),min(df_exp_jv['Jext']))) * 0.05)
                            yup = st.number_input('Y-range', value=yup_init, key = 'JV-yrange_up',label_visibility="collapsed")
                        else:
                            if yscale == 'log':
                                yup_init = max(abs(data_jv['Jext'])) + abs((max(abs(data_jv['Jext'])) - min(abs(data_jv['Jext']))) * 0.05)
                            else:
                                yup_init = max(data_jv['Jext']) + abs((max(data_jv['Jext']) - min(data_jv['Jext'])) * 0.05)
                            yup = st.number_input('Y-range', value=yup_init, key = 'JV-yrange_up',label_visibility="collapsed")

            with col1_2:
                # Show the JV curve. Should always be visible, unless something went wrong.

                if not showJV:
                    st.warning('No data to show for the JV curve, the JV file did not contain any data.')
                else:
                    fig1, ax1 = plt.subplots()
                    if exp_jv is True:
                        # Plot simulation and experimental curve. (Line and Scatter)
                        ax1 = utils_plot_UI.plot_result_JV(data_jv, choice_voltage, plot_type[0], ax1, exp_jv, df_exp_jv, xscale = xscale, yscale = yscale)
                        ax1 = utils_plot_UI.plot_result_JV(data_jv, choice_voltage, plot_type[1], ax1, exp_jv, df_exp_jv, xscale = xscale, yscale = yscale)
                    else:
                        # plot only the simulation curve (Line and Scatter)
                        ax1 = utils_plot_UI.plot_result_JV(data_jv, choice_voltage, plot_type[0], ax1, exp_jv, xscale = xscale, yscale = yscale)
                        ax1 = utils_plot_UI.plot_result_JV(data_jv, choice_voltage, plot_type[1], ax1, exp_jv, xscale = xscale, yscale = yscale)

                    # Set the x,y range, independent of plot type and/or errorbars
                    ax1.set_xlim(xlow, xup)
                    ax1.set_ylim(ylow, yup)

                    st.pyplot(fig1, format='png')

            # Show these output plot when sidebar checkbox is checked
            # Potential[2]
            if chk_potential:
                # Init plot parameters
                pars_potential = {'V' : 'V'}
                par_x_potential = 'x'
                xlabel_potential = '$x$ [nm]'
                ylabel_potential = '$V$ [V]'
                title_potential = 'Potential'
                fig2, ax2 = plt.subplots()
                col2_1, col2_2, col2_3 = st.columns([1, 6, 3])

                fig2, ax2 = utils_plot_UI.create_UI_component_plot(data_var, pars_potential, par_x_potential, xlabel_potential, ylabel_potential, 
                                title_potential, 2, fig2, ax2, plot_type[0], [col2_1, col2_2, col2_3], choice_voltage, source_type = 'Var', yrange_format="%.2e", show_plot_param=False)
                with col2_2:
                    st.pyplot(fig2, format='png')

            if chk_QFLS:
                # Init plot parameters
                # print all column names from data_jv dataframe
                JV_cols = data_jv.columns.values
                # Only keep the columns that contain 'QFLS' in the name
                JV_cols = [col for col in JV_cols if 'QFLS' in col]

                # Put a space between QFLS and layer number for display purposes
                JV_cols = {col:col.replace('QFLS', 'QFLS ') for col in JV_cols}

                pars_QFLS = JV_cols
                par_x_QFLS = 'Vext'
                xlabel_QFLS = '$V_{ext}$ [V]'
                ylabel_QFLS = 'QFLS [eV]'
                title_QFLS = 'Quasi-Fermi Level Splitting'
                fig2a, ax2a = plt.subplots()
                col2a_1, col2a_2, col2a_3 = st.columns([1, 6, 3])

                fig2a, ax2a = utils_plot_UI.create_UI_component_plot(data_jv, pars_QFLS, par_x_QFLS, xlabel_QFLS, ylabel_QFLS, 
                                title_QFLS, 22, fig2a, ax2a, plot_type[0], [col2a_1, col2a_2, col2a_3],yrange_format="%.2f", show_yscale=False)
                with col2a_2:
                    st.pyplot(fig2a, format='png')

            # Energy [3]
            if chk_energy:
                # Init plot parameters
                # Create a dictionary for all potential parameters to plot. Key matches the name in the dataFrame, value is the corresponding label. 
                pars_energy = {'Evac':'$E_{vac}$', 'Ec':'$E_{c}$', 'Ev':'$E_{v}$', 'phin':'$E_{Fn}$', 'phip':'$E_{Fp}$'}
                xlabel_energy =  '$x$ [nm]'
                par_x_energy = 'x' 
                ylabel_energy = 'Energy level [eV]'
                title_energy = 'Energy Band Diagram'
                fig3, ax3 = plt.subplots()
                col3_1, col3_2, col3_3 = st.columns([1, 6, 3])

                fig3, ax3 = utils_plot_UI.create_UI_component_plot(data_var, pars_energy, par_x_energy, xlabel_energy, ylabel_energy, 
                                title_energy, 3, fig3, ax3, plot_type[0], [col3_1, col3_2, col3_3],choice_voltage, source_type = 'Var',yrange_format="%.2f", show_yscale=False)
                with col3_2:
                    st.pyplot(fig3, format='png')

            # Carrier Density [4]
            if chk_density:
                # Init plot parameters
                pars_density = {'n':'$n$', 'p':'$p$','ND':'$N_{D}$','NA':'$N_{A}$', 'anion':'$n_{anion}$', 'cation':'$p_{cation}$'}
                xlabel_density = '$x$ [nm]'
                par_x_density = 'x'
                ylabel_density = 'Carrier density [m$^{-3}$]'
                title_density = 'Carrier Densities'
                fig4, ax4 = plt.subplots()
                col4_1, col4_2, col4_3 = st.columns([1, 6, 3])

                fig4, ax4 = utils_plot_UI.create_UI_component_plot(data_var, pars_density,par_x_density, xlabel_density, ylabel_density, 
                                title_density, 4, fig4, ax4, plot_type[0], [col4_1, col4_2, col4_3],choice_voltage, source_type = 'Var',yrange_format="%.2e", yscale_init=1)                
                with col4_2:
                    st.pyplot(fig4, format='png')

            # Density of electrons trapped [5]
            if chk_fill:
                # Init plot parameters
                pars_fill = {'ntb':'$n_{t,b}$', 'nti':'$n_{t,i}$'}
                par_x_fill = 'x'
                xlabel_fill = '$x$ [nm]'
                ylabel_fill = 'Density of trapped electrons [m$^{-3}$,m$^{-2}$]'
                title_fill = 'Electrons in traps'
                fig5, ax5 = plt.subplots()
                col5_1, col5_2, col5_3 = st.columns([1, 6, 3])

                fig5, ax5 = utils_plot_UI.create_UI_component_plot(data_var, pars_fill,par_x_fill, xlabel_fill, ylabel_fill, 
                                title_fill, 5, fig5, ax5, plot_type[0], [col5_1, col5_2, col5_3], choice_voltage, source_type = 'Var',yrange_format="%.2e")
                with col5_2:
                    st.pyplot(fig5, format='png')

            # Transport [6]
            if chk_transport:
                # Init plot parameters
                pars_transport = {'mun':r'$\mu_{n}$', 'mup':r'$\mu_{p}$'}
                par_x_transport = 'x'
                xlabel_transport = '$x$ [nm]'
                ylabel_transport = 'Mobility [m$^{-2}$V$^{-1}$s$^{-1}$]'
                title_transport = 'Mobilities'
                fig6, ax6 = plt.subplots()
                col6_1, col6_2, col6_3 = st.columns([1, 6, 3])

                fig6, ax6 = utils_plot_UI.create_UI_component_plot(data_var, pars_transport,par_x_transport, xlabel_transport, ylabel_transport, 
                               title_transport, 6, fig6, ax6, plot_type[0], [col6_1, col6_2, col6_3],choice_voltage, source_type = 'Var',yrange_format="%.2e", yscale_init=1)
                with col6_2:
                    st.pyplot(fig6, format='png')

            # Generation and Recombination [7]
            if chk_gen_recomb:
                # Init plot parameters
                pars_gen_recomb = {'G_ehp':'$G_{ehp}$', 'Gfree':'$G_{free}$', 'Rdir':'$R_{dir}$', 'BulkSRHn':'$BulkSRH_{n}$', 'BulkSRHp':'$BulkSRH_{p}$', 'IntSRHn':'$IntSRH_{n}$', 'IntSRHp':'$IntSRH_{p}$'}
                par_x_gen_recomb = 'x'                
                xlabel_gen_recomb = '$x$ [nm]'
                ylabel_gen_recomb = 'Generation/Recombination Rate [m$^{-3}$s$^{-1}$]'
                title_gen_recomb = 'Generation and Recombination Rates'
                fig7, ax7 = plt.subplots()
                col7_1, col7_2, col7_3 = st.columns([1, 6, 3])

                fig7, ax7 = utils_plot_UI.create_UI_component_plot(data_var, pars_gen_recomb, par_x_gen_recomb, xlabel_gen_recomb, ylabel_gen_recomb, 
                                title_gen_recomb, 7, fig7, ax7, plot_type[0], [col7_1, col7_2, col7_3], choice_voltage, source_type = 'Var',yrange_format="%.2e")
                with col7_2:
                    st.pyplot(fig7, format='png')

            # Current [8]
            if chk_current:
                # Init plot parameters
                pars_current = {'Jn':'$J_{n}$', 'Jp':'$J_{p}$', 'Jint':'$J_{int}$'}
                par_x_current = 'x'                
                xlabel_current = '$x$ [nm]'
                ylabel_current = 'Current density [Am$^{-2}$]'
                title_current = 'Current densities'
                fig8, ax8 = plt.subplots()
                col8_1, col8_2, col8_3 = st.columns([1, 6, 3])
                
                fig8, ax8 = utils_plot_UI.create_UI_component_plot(data_var, pars_current, par_x_current, xlabel_current, ylabel_current, 
                                title_current, 8, fig8, ax8, plot_type[0], [col8_1, col8_2, col8_3], choice_voltage, source_type = 'Var',yrange_format="%.2e")
                with col8_2:
                    st.pyplot(fig8, format='png')
