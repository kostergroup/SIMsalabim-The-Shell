"""IMPS Simulations"""
######### Package Imports #########################################################################

import os
import streamlit as st
from menu import menu
from pySIMsalabim.utils import device_parameters as utils_devpar
from utils import band_diagram as utils_bd
from utils import device_parameters_UI as utils_devpar_UI
from utils import general_UI as utils_gen_UI
from utils import imps_func as utils_imps
from utils import dialog_UI as utils_dialog_UI

######### Page configuration ######################################################################

st.set_page_config(layout="wide", page_title="SIMsalabim IMPS",
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
st.session_state['pagename'] = 'IMPS'
st.session_state['def_pagename'] = 'IMPS'

######### Parameter Initialisation ################################################################

# Only load the contents of the page (also the function definitions!) when a session id has been created including the necessary files and folders. 
# This means the whole page need to be in a conditional statement related related to the session id state variable.
if 'id' not in st.session_state:
    st.error('SIMsalabim simulation has not been initialized yet, return to SIMsalabim page to start a session.')
else:
    # Get Session ID & Folder paths from session states and store them in local variables
    id_session = str(st.session_state['id'])
    resource_path = str(st.session_state['resource_path']) 
    zimt_path = str(st.session_state['zimt_path'])
    simss_device_parameters = str(st.session_state['simss_devpar_file'])
    zimt_device_parameters = str(st.session_state['zimt_devpar_file'])
    session_path = os.path.join(str(st.session_state['simulation_path']), id_session)
    imps_pars_file = 'imps_pars.txt'
    
    # default IMPS parameters
    imps_par = [['fmin', 1E-1, 'Hz, Minimum frequency'],
                ['fmax', 5E+06, 'Hz, Maximum frequency'],
                ['fstep', 20, 'Number of frequency steps'],
                ['V0', 0.3, 'V, Applied voltage'],
                ['fracG', 5e-2, 'Fraction to increase the intensity/generation rate with. Sets the size of the initial pertubation'],
                ['G_frac',1.0, 'Fractional generation rate']]

    # Object to hold device parameters and IMPS specific parameters (with defaults)
    dev_par = {}
    if os.path.isfile(os.path.join(session_path, imps_pars_file)):
        imps_skip_keys = {"tVGFile","tJFile"}
        imps_int_keys = {"fstep"}
        imps_par = utils_devpar_UI.read_exp_file(session_path, imps_pars_file, imps_par, skip_keys=imps_skip_keys,int_keys=imps_int_keys)

    # UI Containers
    main_container_imps = st.empty()
    container_imps_par = st.empty()
    layer_container_imps = st.empty()
    container_device_par = st.empty()
    bd_container_title = st.empty()
    bd_container_plot = st.empty()

    ######### Function Definitions ####################################################################
    def run_IMPS(zimt_device_parameters, session_path, dev_par, layers, id_session, imps_par, imps_pars_file):
        """
        UI wrapper to run the IMPS simulation. This function exists so Streamlit on_click can call an external 
        function with local variables. It simply forwards args to the utils function that implements the full run.

        Parameters
        ----------
        zimt_device_parameters : str
            Name of the device parameters file
        session_path : str
            Path to the session folder
        dev_par : List
            List with nested lists for all parameters in all sections.
        layers : List
            List with all layers in the device.
        id_session : str
            Session ID string.
        imps_par : List
            List with nested lists for all IMPS parameters.
        imps_pars_file : str
            Name of the IMPS parameters file.

        Returns
        -------
        None
        """
        return utils_imps.run_IMPS(zimt_device_parameters, session_path, dev_par, layers, id_session, imps_par, imps_pars_file)

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
        utils_gen_UI.save_parameters(dev_par, layers, session_path, zimt_device_parameters, simss_device_parameters)    

    def save_parameters_BD():
        """ Save device parameters and create the band diagram.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        utils_gen_UI.save_parameters(dev_par, layers, session_path, zimt_device_parameters, simss_device_parameters, show_toast=True)
        # Draw the band diagram
        utils_bd.get_param_band_diagram(dev_par, layers, zimt_device_parameters)

    # Dialog window wrappers. Placed within each page file due to the decorator.
    # Dialog window to upload a file.
    @st.experimental_dialog("Upload a file")
    def uploadFileDialogWrapper(session_path, dev_par, layers, zimt_device_parameters, simss_device_parameters,simtype):
        dev_par, layers = utils_dialog_UI.uploadFileDialog(session_path, dev_par, layers, zimt_device_parameters, simss_device_parameters,simtype)

    # Dialog window to add a new layer to the device
    @st.experimental_dialog("Add a layer")
    def addLayerDialogWrapper(session_path, dev_par, layers, resource_path, zimt_device_parameters, simss_device_parameters):
        dev_par, layers = utils_dialog_UI.addLayerDialog(session_path, dev_par, layers, resource_path, zimt_device_parameters, simss_device_parameters)

    # Dialog window to remove a layer from the device
    @st.experimental_dialog("Remove a layer")
    def removeLayerDialogWrapper(dev_par, layers, session_path, zimt_device_parameters, simss_device_parameters):
        dev_par, layers = utils_dialog_UI.removeLayerDialog(dev_par, layers, session_path, zimt_device_parameters, simss_device_parameters)    

    ######### UI layout ###############################################################################

    # Create lists containing the names of available nk and spectrum files. Including user uploaded ones.
    nk_file_list, spectrum_file_list = utils_devpar_UI.create_nk_spectrum_file_array(session_path)
    # Sort them alphabetically
    nk_file_list.sort(key=str.casefold)
    spectrum_file_list.sort(key=str.casefold)

    # Load the device_parameters file and create a List object.
    dev_par, layers = utils_devpar.load_device_parameters(session_path, zimt_device_parameters, zimt_path, availLayers = st.session_state['availableLayerFiles'][:-3],run_mode=True)

    with st.sidebar:
        # Show custom menu
        menu()
        
        # Run simulation
        st.button('Run Simulation', on_click=run_IMPS,args=(zimt_device_parameters, session_path, dev_par, layers, id_session, imps_par, imps_pars_file))

        # Device Parameter button to save, download or reset a file
        st.button('Save device parameters', on_click=save_parameters_BD)

        # Open a dialog window to upload a file
        if st.button('Upload a file'):
            uploadFileDialogWrapper(session_path, dev_par, layers, zimt_device_parameters, simss_device_parameters, st.session_state['pagename'])

        # Prepare a ZIP archive to download the device parameters
        zip_filename = utils_gen_UI.create_zip(session_path, layers)

        # Show a button to download the ZIP archive
        with open(zip_filename, 'rb') as fp:
            btn = st.download_button(label='Download device parameters', data = fp, file_name = os.path.basename(zip_filename), mime='application/zip')

        # Reset the device parameters to the default values.
        reset_device_parameters = st.button('Reset device parameters')

    # When the reset button is pressed, empty the container and create a List object from the default .txt file. Next, save the default parameters to the parameter file.
    if reset_device_parameters:
        main_container_imps.empty()
        dev_par, layers = utils_devpar.load_device_parameters(session_path, zimt_device_parameters, resource_path, True, availLayers=st.session_state['availableLayerFiles'][:-3],run_mode = True)
        utils_gen_UI.save_parameters(dev_par, layers, session_path, zimt_device_parameters, simss_device_parameters)

    with main_container_imps.container():
    # Start building the UI for the actual page
        st.title("Intensity Modulated PhotoSpectroscopy (IMPS)")
        st.write("""
            Simulate an IMPS experiment with SIMsalabim. The admittance is calculated at the applied voltage. 
            A small one time pertubation in light intensity at t=0 is introduced, defined as a fraction with which the generation rate is increased. 
            The admittance is calculated using Fourier decomposition, based on the method desrcibed in *S.E. Laux, IEEE Trans. Electron Dev. 32 (10), 2028 (1985)*.
        """)

        for par_section in dev_par[zimt_device_parameters]: # ToDo check if correct
            if par_section[0] == 'Description': 
                # The first section of the page is a 'special' section and must be treated seperately.
                # The SIMsalabim version number and general remarks to show on top of the page
                version = [i for i in par_section if i[1].startswith('version:')]
                st.write("SIMsalabim " + version[0][1])
                # Reference to the SIMsalabim manual
                st.write("""For more information about the device parameters or SIMsalabim itself, refer to the
                                [Manual](http://simsalabim-online.com/manual)""")
                
        with container_imps_par.container():
            st.subheader('IMPS parameters')
            col_par_imps, col_val_imps, col_desc_imps = st.columns([2, 2, 8],)
            for imps_item in imps_par:
                with col_par_imps:
                    st.text_input(imps_item[0], value=imps_item[0], disabled=True, label_visibility="collapsed")

                 # Parameter value
                with col_val_imps:
                    if imps_item[0] == 'fstep':
                        # Show these parameters as a float
                        imps_item[1] = st.number_input(imps_item[0] + '_val', value=imps_item[1], label_visibility="collapsed")
                    elif imps_item[0] == 'V0' or imps_item[0] == 'fracG' or imps_item[0] == 'G_frac':
                        # Show these parameters as a float
                        imps_item[1] = st.number_input(imps_item[0] + '_val', value=imps_item[1], label_visibility="collapsed", format="%f")
                    else:
                        # Show all other parameters in scientific notation e.g. 1e+2
                        imps_item[1] = st.number_input(imps_item[0] + '_val', value=imps_item[1], label_visibility="collapsed", format="%e")
                # Parameter description
                with col_desc_imps:
                    st.text_input(imps_item[0] + '_desc', value=imps_item[2], disabled=True, label_visibility="collapsed")
            st.markdown('<hr>', unsafe_allow_html=True)

        with layer_container_imps.container():
            # Device layer setup        
            st.subheader("Device setup")

            # Show the Ddd layer button
            if st.button('Add a layer'):
                addLayerDialogWrapper(session_path, dev_par, layers, resource_path, zimt_device_parameters, simss_device_parameters)
                
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
                    removeLayerDialogWrapper(dev_par, layers, session_path, zimt_device_parameters, simss_device_parameters)

            st.markdown('<hr>', unsafe_allow_html=True)

    # Section to edit the device parameters
        with container_device_par.container():
            filesDisplay = [zimt_device_parameters]
            filesDisplay.extend(st.session_state['availableLayerFiles'][:-3])

            # Selectbox to choose which layer to edit
            selected_layer = st.selectbox('Select a file to edit', filesDisplay, on_change=save_parameters_local)

            st.markdown('<br>', unsafe_allow_html=True)

            # Build the UI components for the various sections
            for par_section in dev_par[selected_layer]:

                # Skip the first section, this is the description section and is already shown at the top of the page.
                # Skip the layers section, this is already shown in the layer container.
                if not par_section[0] == 'Layers' and not par_section[0] == 'Description':
                    # Initialize expander components for each section
                    if (par_section[0]== 'Optics'):
                        # Do not expand the optics section by default and add a custom description string
                        expand=False
                        section_title = par_section[0] + ' (Optional, use only when calculating the generation profile i.e. genProfile=calc)'
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
