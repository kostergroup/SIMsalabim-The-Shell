"""Steady State JV (SimSS) Simulations"""
######### Package Imports #########################################################################

import os
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from menu import menu
from pySIMsalabim.experiments import EQE as eqe_exp
from pySIMsalabim.utils import device_parameters as utils_devpar
from utils import device_parameters_UI as utils_devpar_UI
from utils import band_diagram as utils_bd
from utils import general_UI as utils_gen_UI
from utils import steady_state as utils_simss
from utils import plot_functions_UI as utils_plot_UI
from utils import dialog_UI as utils_dialog_UI

######### Page configuration ######################################################################

st.set_page_config(layout="wide", page_title="SIMsalabim Steady State JV",
                   page_icon='./Figures/SIMsalabim_logo_HAT.jpg')

# Set the session identifier as query parameter in the URL
st.query_params.from_dict({'session':st.session_state['id']})

# Load custom CSS
utils_gen_UI.local_css('./utils/style.css')

# Remove the +/- toggles on number inputs
st.markdown("""<style>
                button.step-up {display: none;}
                button.step-down {display: none;}
                div[data-baseweb] {border-radius: 4px;}
                </style>""",unsafe_allow_html=True)

# Session states for page navigation
st.session_state['pagename'] = 'Steady State JV'
st.session_state['def_pagename'] = 'Steady State JV'

######### Parameter Initialisation ################################################################

# Only load the contents of the page (also the function definitions!) when a session id has been created including the necessary files and folders. 
# This means the whole page need to be in a conditional statement related related to the session id state variable.
if 'id' not in st.session_state:
    st.error('SIMsalabim simulation has not been initialized yet, return to SIMsalabim page to start a session.')
else:
    # Get Session ID & Folder paths from session states and store them in local variables
    id_session = str(st.session_state['id'])
    resource_path = str(st.session_state['resource_path']) 
    simss_path = str(st.session_state['simss_path'])
    simss_device_parameters = str(st.session_state['simss_devpar_file'])
    zimt_device_parameters = str(st.session_state['zimt_devpar_file'])
    session_path = os.path.join(str(st.session_state['simulation_path']), id_session)
    
    # Object to hold device parameters
    dev_par = {}

    # UI Containers
    layer_container_SS = st.empty()
    main_container_SS = st.empty()
    bd_container_title = st.empty()
    bd_container_plot = st.empty()

    ######### Function Warppers ####################################################################

    def run_SS_JV(simss_device_parameters, session_path, dev_par, layers, id_session):
        """
        UI wrapper to run the steady state simulation. This function exists so Streamlit on_click can call an external 
        function with local variables. It simply forwards args to the utils function that implements the full run.

        Parameters
        ----------
        simss_device_parameters : str
            Name of the device parameters file
        session_path : str
            Path to the session folder
        dev_par : List
            List with nested lists for all parameters in all sections.
        layers : List
            List with all layers in the device.
        id_session : str
            Session ID string.
        Returns
        -------
        None
        """
        return utils_simss.run_SS_JV(simss_device_parameters, session_path, dev_par, layers, id_session, G_fracs=None)

    def save_parameters_local():
        """ local function to save the device parameters when selecting a different layer to edit, 
            as arguments cannot be passed to on_change callback.

        Parameters
        ----------
        None

        Returns
        -------
        None                    
        """
        utils_gen_UI.save_parameters(dev_par, layers, session_path, simss_device_parameters, zimt_device_parameters)

    def save_parameters_BD():
        """ Save device parameters and create the band diagram.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        utils_gen_UI.save_parameters(dev_par, layers, session_path, simss_device_parameters, zimt_device_parameters, show_toast=True)
        # Draw the band diagram
        utils_bd.get_param_band_diagram(dev_par, layers, simss_device_parameters)

    # Dialog window wrappers. Placed within each page file due to the decorator.
    # Dialog window to upload a file.
    @st.experimental_dialog("Upload a file")
    def uploadFileDialogWrapper(session_path, dev_par, layers, simss_device_parameters, zimt_device_parameters,simtype):
        dev_par, layers = utils_dialog_UI.uploadFileDialog(session_path, dev_par, layers, simss_device_parameters, zimt_device_parameters,simtype)

    # Dialog window to add a new layer to the device
    @st.experimental_dialog("Add a layer")
    def addLayerDialogWrapper(session_path, dev_par, layers, resource_path, simss_device_parameters, zimt_device_parameters):
        dev_par, layers = utils_dialog_UI.addLayerDialog(session_path, dev_par, layers, resource_path, simss_device_parameters, zimt_device_parameters)

    # Dialog window to remove a layer from the device
    @st.experimental_dialog("Remove a layer")
    def removeLayerDialogWrapper(dev_par, layers, session_path, simss_device_parameters, zimt_device_parameters):
        dev_par, layers = utils_dialog_UI.removeLayerDialog(dev_par, layers, session_path, simss_device_parameters, zimt_device_parameters)

    ######### UI layout ###############################################################################

    # Create lists containing the names of available nk and spectrum files. Including user uploaded ones.
    nk_file_list, spectrum_file_list = utils_devpar_UI.create_nk_spectrum_file_array(session_path)
    # Sort them alphabetically
    nk_file_list.sort(key=str.casefold)
    spectrum_file_list.sort(key=str.casefold)

    # Load the device_parameters file and create a List object.
    dev_par, layers = utils_devpar.load_device_parameters(session_path, simss_device_parameters, simss_path, availLayers = st.session_state['availableLayerFiles'][:-3])

    ## Create the sidebar with apges and buttons
    with st.sidebar:
        # Show custom menu
        menu()

        # Run simulation
        st.button('Run Simulation', on_click=run_SS_JV, args=(simss_device_parameters, session_path, dev_par, layers, id_session))

        # Device Parameter button to save, download or reset a file
        st.button('Save device parameters', on_click=save_parameters_BD)

        # Open a dialog window to upload a file
        if st.button('Upload a file'):
            # uploadFileDialog()
            uploadFileDialogWrapper(session_path, dev_par, layers, simss_device_parameters, zimt_device_parameters,st.session_state['pagename'])

        # Prepare a ZIP archive to download the device parameters
        zip_filename = utils_gen_UI.create_zip(session_path, layers)

        # Show a button to download the ZIP archive
        with open(zip_filename, 'rb') as fp:
            btn = st.download_button(label='Download device parameters', data = fp, file_name = os.path.basename(zip_filename), mime='application/zip')

        # Reset the device parameters to the default values.
        reset_device_parameters = st.button('Reset device parameters')

    # When the reset button is pressed, empty the container and create a List object from the default .txt file. Next, save the default parameters to the parameter file.
    if reset_device_parameters:
        main_container_SS.empty()
        dev_par, layers = utils_devpar.load_device_parameters(session_path, simss_device_parameters, resource_path, True, availLayers=st.session_state['availableLayerFiles'][:-3],run_mode = True)
        utils_gen_UI.save_parameters(dev_par, layers, session_path, simss_device_parameters, zimt_device_parameters)

    # Start building the UI for the actual page
    with layer_container_SS.container():
        st.title("Steady State JV & EQE")
        for par_section in dev_par[simss_device_parameters]:
            if par_section[0] == 'Description': 
                # The first section of the page is a 'special' section and must be treated seperately.
                # The SIMsalabim version number and general remarks to show on top of the page
                version = [i for i in par_section if i[1].startswith('version:')]
                st.write("SIMsalabim " + version[0][1])
                # Reference to the SIMsalabim manual
                st.write("""For more information about the device parameters or SIMsalabim itself, refer to the
                                [Manual](http://simsalabim-online.com/manual)""")
       
        st.info("Go to: [External quantum efficiency (EQE)](#external-quantum-efficiency-eqe)")

        # Device layer setup        
        st.subheader("Device setup")

        # Show the Ddd layer button
        if st.button('Add a layer'):
            addLayerDialogWrapper(session_path, dev_par, layers, resource_path, simss_device_parameters, zimt_device_parameters)
            
        # Display the layers
        for layer in layers:
            if not layer[1] == 'setup':
                col_par, col_val, col_desc = st.columns([2, 4, 8]) 
                with col_par:
                    st.text_input(layer[1], value=layer[1], key=layer[1], disabled=True, label_visibility="collapsed")
                with col_val:
                    # create a list with the layer names to choose from
                    layer_names = st.session_state['availableLayerFiles'][:-3]
                    selected_layer = utils_gen_UI.safe_index(layer[2], layer_names, default=0)
                    layer[2] = st.selectbox(layer[2],key=layer[1] + ' ' + layer[2], options=layer_names,index = selected_layer,format_func=lambda x: x, label_visibility="collapsed")
                with col_desc:
                    st.text_input(layer[3], value=layer[3],key=layer[1] + ' ' + layer[3], disabled=True, label_visibility="collapsed")

        # Show the remove layer button. Only when more than 1 layer is present!
        if len(layers) >2:
            if st.button('Remove a layer'):
                removeLayerDialogWrapper(dev_par, layers, session_path, simss_device_parameters, zimt_device_parameters)

        st.markdown('<hr>', unsafe_allow_html=True)

    # Section to edit the device parameters
    with main_container_SS.container():
        filesDisplay = [simss_device_parameters]
        filesDisplay.extend(st.session_state['availableLayerFiles'][:-3])

        # Selectbox to choose which layer to edit
        selected_layer = st.selectbox('Select a file to edit', filesDisplay, on_change=save_parameters_local)

        st.markdown('<br>', unsafe_allow_html=True)

        # Build the UI components for the various sections
        for par_section in dev_par[selected_layer]:

            # Skip the first section, this is the description section and is already shown at the top of the page.
            # Skip the layers section, this is already shown in the layer_container_SS container.
            if not par_section[0] == 'Layers' and not par_section[0] == 'Description':
                # Initialize expander components for each section
                if (par_section[0]== 'Optics'):
                    # Do not expand the optics section by default and add a custom description string
                    expand=False
                    section_title = par_section[0] + ' (Optional, use only when calculating the generation profile i.e. Gen_profile=calc)'
                elif (par_section[0]== 'Numerical Parameters' or par_section[0]== 'Voltage range of simulation' or par_section[0]== 'User interface'):
                    # Do not expand these sections by default but use the section name as section title
                    expand = False
                    section_title = par_section[0]
                else:
                    # Expand all other sections and use the section name as section title
                    expand = True
                    section_title = par_section[0]
                
                # Fill the expanders/sections with the parameters
                with st.expander(section_title, expanded=expand):
                    # Split component into three columns [name, value, description]
                    col_par, col_val, col_desc = st.columns([2, 2, 8],)
                    
                    for item in par_section[1:]:
                        if item[0] == 'comm': # Item is just a comment, do not use column layout for this.
                            st.write(item[1])
                            # Reset the column layout layout to force a break between the parameters to place the comment in the correct position. 
                            # Otherwise all comments will be placed at either the top or bottom of the components 
                            col_par, col_val, col_desc = st.columns([2, 2, 8]) 

                        if item[0] == 'par': # Item contains a parameter, fill all three columns
                            # Parameter name
                            with col_par:
                                st.text_input(item[1], value=item[1], disabled=True, label_visibility="collapsed")

                            # Parameter value
                            with col_val:
                                # Handle exceptions/special cases.
                                if item[1].startswith('nk'): # nk file name, use a selectbox.
                                    if item[2] not in nk_file_list:
                                        item[2] = '--none--'
                                    nk_idx = utils_gen_UI.safe_index(item[2], nk_file_list, default=0)
                                    item[2] = st.selectbox(selected_layer + item[1] + '_val', options=nk_file_list, format_func=utils_gen_UI.format_func, index=nk_idx, label_visibility="collapsed")
                                elif item[1] == 'spectrum': # spectrum file name, use a selectbox.
                                    if item[2] not in spectrum_file_list:
                                        item[2] = '--none--'
                                    spec_idx = utils_gen_UI.safe_index(item[2], spectrum_file_list, default=0)
                                    item[2] = st.selectbox(selected_layer + item[1] + '_val', options=spectrum_file_list, format_func=utils_gen_UI.format_func, index=spec_idx, label_visibility="collapsed")
                                elif item[1]== 'pauseAtEnd':
                                    # This parameter must not be editable and forced to 0, otherwise the program will not exit/complete and hang forever.
                                    item[2] = 0
                                    item[2] = st.text_input(selected_layer + item[1] + '_val', value=item[2], disabled=True, label_visibility="collapsed")
                                elif (item[1] == 'intTrapFile') or (item[1] == 'bulkTrapFile'):
                                    # This could be uploaded trap files,so display a list of available ones. 
                                    if item[2] not in st.session_state['trapFiles']:
                                        # Value from file is not recognized, replace with none
                                        st.toast(f'Could not find file "{item[2]}" for parameter {item[1]} and has been set to none. If you want to use this file, please upload it using the "Upload trap distribution" option and associate it with the {item[1]} parameter.')
                                        item[2] = 'none'
                                    trap_idx = utils_gen_UI.safe_index(item[2], st.session_state['trapFiles'], default=0)
                                    item[2] = st.selectbox(selected_layer + item[1]+ '_val', options=st.session_state['trapFiles'], index=trap_idx, label_visibility="collapsed")
                                else:
                                    item[2] = st.text_input(selected_layer + item[1] + '_val', value=item[2], label_visibility="collapsed")
                            
                            # Parameter description
                            with col_desc:
                                st.text_input(item[1] + '_desc', value=item[3], disabled=True, label_visibility="collapsed")
        
    #  Show the SIMsalabim logo in the sidebar
    with st.sidebar:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.image('./Figures/SIMsalabim_logo_cut_trans.png')


######### External Quantum Efficiency (EQE) ##########################################################
    st.markdown('<hr>', unsafe_allow_html=True)

    st.header("External quantum efficiency (EQE)")
    st.subheader("Calculate the EQE for the device")

    # Load the spectrum file from the simulation setup
    for section in dev_par[simss_device_parameters]:
            if section[0] == 'Optics': 
                for par in section[1:]:
                    if par[1] == 'spectrum':
                        spectrum_file = par[2]

    # Set up UI to adjust input parameters for the EQE calculation
    col_left, col_right = st.columns([1,1],)
    with col_left:
        lambda_min = st.number_input('Lower wavelength bound [nm]', value=280.0, disabled=False, label_visibility="visible", format="%f")
        lambda_step = st.number_input('Wavelength step [nm]', value=20.0, disabled=False, label_visibility="visible", format="%f")
    with col_right:
        lambda_max = st.number_input('Upper wavelength bound [nm]', value=1000.0, disabled=False, label_visibility="visible", format="%f")
        applied_voltage = st.number_input('Applied voltage [V]', value=0.0, disabled=False, label_visibility="visible", format="%f")
    
    # Run the EQE calculation
    if st.button('Calculate EQE'):
        # Check if the output file already exists and if so remove it
        if os.path.isfile(os.path.join(session_path,'output.dat')):
            os.remove(os.path.join(session_path,'output.dat'))

        # Check the EQE input values
        if lambda_min < 280.0:
            st.error('The lower wavelength bound must be at least 280 nm.')
        elif lambda_min > lambda_max:
            st.error('The lower wavelength bound can not be larger than the upper wavelength bound.')
        elif lambda_max > 4000.0: 
            st.error('The upper wavelength bound can at most 4000 nm.')
        elif lambda_step < 0.5:
            st.error('The wavelength step must be at least 0.5 nm.')
        elif lambda_step > (lambda_max - lambda_min) and not (lambda_min == lambda_max):
            st.error('The wavelength step cannot be larger than the difference between the lower and upper wavelength bounds.')
        else:
            if lambda_min == lambda_max:
                # Show an info message when a single wavelength is used
                st.info('Calculating the EQE for a single wavelength. Wavelength step parameter is ignored.')
        # Run the EQE script
        with st.spinner('Calculating EQE...'):
        
            result, msg_list = eqe_exp.run_EQE(simss_device_parameters,session_path,spectrum_file,lambda_min,lambda_max,lambda_step,applied_voltage,'output.dat',remove_dirs=True,run_mode=True)
            
            if result != 0:
                msg_str = 'Calculation of the EQE was not successfull.\n\n'
                for substr in msg_list:
                    msg_str += substr + '\n'
                st.error(msg_str)
            else:
                # Log the EQE simulation result in the log file
                with open(os.path.join('Statistics', 'log_file.txt'), 'a') as f:
                    f.write(id_session + ' EQE ' + 'SUCCESS' + ' ' + str(datetime.now()) + '\n')

    # check if output file exists
    if os.path.isfile(os.path.join(session_path,'output.dat')):
        st.success('EQE calculation complete')
        st.markdown('Download the EQE data file')
        with open(os.path.join(session_path,'output.dat'), encoding='utf-8') as fo:
            st.download_button('Download EQE data', fo, file_name='output.dat')
            fo.close()
        
        # Plot the EQE data
        data_EQE = pd.read_csv(os.path.join(session_path,'output.dat'), sep=r'\s+')

        # Get EQE in % for plot
        data_EQE['EQE'] = data_EQE['EQE']*100
        # Get wavelength in nm for plot
        data_EQE['lambda'] = data_EQE['lambda']*1E9

        #Plot EQE spectrum
        col1_1, col1_2, col1_3 = st.columns([1, 5, 1])

        with col1_2:
            fig1, ax1 = plt.subplots()
            pars_EQE = {'EQE':'EQE [%]'}
            xlabel_EQE =  'Wavelength [nm]'
            par_x_EQE = 'lambda' 
            ylabel_EQE = 'EQE [%]'
            title_EQE = 'External quantum efficiency (EQE)'

            fig1, ax1 = utils_plot_UI.create_UI_component_plot(data_EQE, pars_EQE, par_x_EQE, xlabel_EQE, ylabel_EQE, 
                            title_EQE, 1, fig1, ax1, plt.errorbar, [col1_1, col1_2, col1_3], show_yscale=False, error_y = 'EQEerr', show_plot_param=False, show_legend=False, error_fmt = '-o')
                 
            with col1_2:
                st.pyplot(fig1, format='png')            
