"""Impedance Simulations"""
######### Package Imports #########################################################################

import os, shutil
import streamlit as st
from utils import device_parameters as utils_devpar
from utils import device_parameters_gen as utils_devpar_gen
from utils import band_diagram as utils_bd
from utils import general as utils_gen
from utils import general_web as utils_gen_web
from utils import impedance_func as utils_impedance
from Experiments import impedance as impedance_exp
from datetime import datetime 
from menu import menu

######### Page configuration ######################################################################

st.set_page_config(layout="wide", page_title="SIMsalabim Impedance",
                   page_icon='./logo/SIMsalabim_logo_HAT.jpg')

# Load custom CSS
utils_gen_web.local_css('./utils/style.css')

# Session states for page navigation
st.session_state['pagename'] = 'Impedance'
st.session_state['def_pagename'] = 'Impedance'

# Remove the +/- toggles on number inputs
st.markdown("""<style>
                button.step-up {display: none;}
                button.step-down {display: none;}
                div[data-baseweb] {border-radius: 4px;}
                </style>""",unsafe_allow_html=True)

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
    impedance_pars_file = 'impedance_pars.txt'
    
    # default impedance parameters
    impedance_par = [['fmin', 1E-1, 'Hz, Minimum frequency'],
                     ['fmax', 1E+06, 'Hz, Maximum frequency'],
                     ['fstep', 20, 'Number of frequency steps'],
                     ['V0', 0.6, 'V, Applied voltage'],
                     ['delV', 1e-2, 'V, Voltage step size. Keep this around 1 - 10 mV.'],
                     ['G_frac',1.0, 'Fractional Generation rate']]

    # Object to hold device parameters and impedance specific parameters (with defaults)
    dev_par = {}
    if os.path.isfile(os.path.join(session_path, impedance_pars_file)):
        impedance_par = utils_impedance.read_impedance_par_file(session_path, impedance_pars_file, impedance_par)

    # UI Containers
    main_container_impedance = st.empty()
    container_impedance_par = st.empty()
    layer_container_impedance = st.empty()
    container_device_par = st.empty()
    bd_container_title = st.empty()
    bd_container_plot = st.empty()

    ######### Function Definitions ####################################################################

    def run_Impedance():
        """Run the Impedance simulation with the saved device parameters. 
        Display an error message (From SIMsalabim or a generic one) when the simulation did not succeed. 
        Save the used file names in global states to use them in the results.
        """
        with st.toast('Simulation started'):
            # Store all impedance specific parameters into a single object.
            impedance_par_obj = utils_impedance.read_impedance_parameters(impedance_par, dev_par[zimt_device_parameters])

            # Run the impedance script
            result, message = impedance_exp.run_impedance_simu(zimt_device_parameters, session_path, impedance_par_obj["tVGFile"], impedance_par_obj["fmin"],
                                                               impedance_par_obj["fmax"],impedance_par_obj["fstep"],impedance_par_obj["V0"],
                                                               impedance_par_obj["delV"],impedance_par_obj["G_frac"],True, tj_name=impedance_par_obj['tJFile'])
        
        if result == 1:
            # Creating the tVG file for the impedance failed                
            st.error(message)
            res = 'FAILED'
        else:
            if result == 0 or result == 95:
                # Simulation succeeded, continue with the process
                st.success('Simulation complete. Output can be found in the Simulation results.')
                st.session_state['simulation_results'] = 'Impedance' # Init the results page to display Steady State results

                # Save the impedance parameters in a file

                if os.path.isfile(os.path.join(session_path, impedance_pars_file)):
                     os.remove(os.path.join(os.path.join(session_path, impedance_pars_file)))
                with open(os.path.join(session_path, impedance_pars_file), 'w') as fp_impedance:
                    for key,value in impedance_par_obj.items():
                        fp_impedance.write('%s = %s\n' % (key, value))

                st.session_state['expObject'] = impedance_par_obj
                st.session_state['impedancePars'] = impedance_pars_file
                st.session_state['freqZFile'] = 'freqZ.dat' # Currently a fixed name

                # Set the state variable to true to indicate that a new simulation has been run and a new ZIP file with results must be created
                st.session_state['runSimulation'] = True
                # Store the assigned file names from the saved device parameters in session state variables.
                utils_devpar.store_file_names(dev_par, 'zimt', zimt_device_parameters, layers)

                res = 'SUCCESS'

            else:
                # Simulation failed, show the error message
                st.error(message)

                res = 'ERROR'

        # Log the simulation result in the log file
        with open(os.path.join('Statistics', 'log_file.txt'), 'a') as f:
            f.write(id_session + ' Impedance ' + res + ' ' + str(datetime.now()) + '\n')

    def save_parameters(show_toast = False):
        """Save the current state of the device parameters to the txt file used by the simulation scripts.

        Parameters
        ----------
        show_toast : bool, optional
            Show a quick message that the simualtion completed with success, by default False
        """
        # Use this 'layer/inbetween' function to make sure the most recent device parameters are saved
        layersAvail = [zimt_device_parameters]
        layersAvail.extend(st.session_state['availableLayerFiles'])
        utils_devpar_gen.save_parameters(dev_par, layers, session_path, zimt_device_parameters)
        utils_gen.exchangeDevPar(session_path, zimt_device_parameters, simss_device_parameters) ## update simss parameters with zimt parameters.

        if show_toast:
            st.toast('Saved device parameters', icon="✔️")

    def save_parameters_BD():
        """Save the device parameters and draw the band diagram.
        """
        save_parameters(show_toast=True)
        # Draw the band diagram
        utils_bd.get_param_band_diagram(dev_par, layers, zimt_device_parameters)

    def upload_gen_prof_file(uploaded_file):
        """Write the generation profile file to the session folder. Update the genProfile parameter and save them.

        Parameters
        ----------
        uploaded_file : file
            The uploaded file to be saved

        Returns
        -------
        success
            Display a streamlit success message
        """
        utils_gen.upload_single_file_to_folder(uploaded_file, session_path)

        # Update the Gen_profile name with the name of the just uploaded file.
        for section in dev_par[zimt_device_parameters][1:]:
            if section[0] == 'Optics':
                for item_output_par in section:
                    if 'genProfile' in item_output_par[1]:
                        item_output_par[2] = uploaded_file.name
        save_parameters()

        return st.success('File upload complete')

    def upload_trap_level_file(uploaded_file):
        """Write the trap level file to the session folder and save it. Append the file to the trapFiles list.

        Parameters
        ----------
        uploaded_file : file
            The uploaded file to be saved

        Returns
        -------
        success
            Display a streamlit success message
        """
        utils_gen.upload_single_file_to_folder(uploaded_file, session_path)
        st.session_state['trapFiles'].append(uploaded_file.name)
        save_parameters()

        return st.success('File upload complete')


    def upload_nk_file(uploaded_files):
        """ Read and decode the uploaded nk_files and create  files.

        Parameters
        ----------
        uploaded_files : files
            The uploaded files to be saved

        Returns
        -------
        success
            Display a streamlit success message
        """
        utils_gen.upload_multiple_files_to_folder(uploaded_files, os.path.join(session_path,'Data_nk'))

        save_parameters()

        return st.success('File uploads complete')
    
    def upload_spectrum_file(uploaded_file):
        """ Read and decode the uploaded spectrum and create  files.

        Parameters
        ----------
        uploaded_file : file
            The uploaded file to be saved

        Returns
        -------
        success
            Display a streamlit success message
        """
        utils_gen.upload_single_file_to_folder(uploaded_file, os.path.join(session_path,'Data_spectrum',))

        save_parameters()

        return st.success('File upload complete')
        
    def upload_devpar_file(uploaded_file, uploaded_files):
        """Write the simualtion seetup file to the session folder. 

        Parameters
        ----------
        uploaded_file : file
            The uploaded simualtion setup file to be saved

        uploaded_file : file
            The uploaded layer files to be saved

        Returns
        -------
        success
            Display a streamlit success message
        """
        uploaded_file.name = zimt_device_parameters
        utils_gen.upload_single_file_to_folder(uploaded_file, session_path)
        utils_gen.upload_multiple_files_to_folder(uploaded_files, session_path)

        return st.success('Upload device parameters complete')

    def upload_layer_file(uploaded_file):
        """Write the layer parameter file to the session folder. 

        Parameters
        ----------
        uploaded_file : file
            The uploaded file to be saved

        Returns
        -------
        success
            Display a streamlit success message
        """
        utils_gen.upload_single_file_to_folder(uploaded_file, session_path)

        return st.success('Upload device parameters complete')
    
    def create_nk_spectrum_file_array():
        """Create lists containing the names of the available nk and spectrum files.

        Returns
        -------
        List,List
            Lists with nk file names and spectrum file names
        """
        nk_file_list = []
        spectrum_file_list = []
        # Placeholder item when nk/spectrum file is not found
        nk_file_list.append('--none--')
        spectrum_file_list.append('--none--')
        for dirpath, dirnames, filenames in os.walk(os.path.join(session_path,'Data_nk')):
            for filename in filenames:
                nk_file_list.append(os.path.join('Data_nk',filename))
        for dirpath, dirnames, filenames in os.walk(os.path.join(session_path,'Data_spectrum')):
            for filename in filenames:
                spectrum_file_list.append(os.path.join('Data_spectrum',filename))
        return nk_file_list,spectrum_file_list

    def format_func(option):
        """Format function to split a string containing a /

        Parameters
        ----------
        option : string
            To be formatted string

        Returns
        -------
        string
            Last part of formatted string
        """
        filename_split = os.path.split(option)
        return filename_split[1]

    # Dialog window definitions. Placed within each page file due to the decorator.

    # Dialog window to upload a file.
    @st.experimental_dialog("Upload a file")
    def uploadFileDialog():
        # Select the type of file the user wants to upload. A fixed list of options based on SIMsalabim v5.11
        allFilesUploaded = True # Boolean to disable submit button in case of uploading simulation setup

        st.write('Which type of file do you want to upload?')
        uploadOptions = ['Generation profile', 'Trap distribution','n,k values', 'Spectrum', 'Simulation setup', 'Layer parameters']
        uploadChoice = st.selectbox('File to upload', options=uploadOptions, label_visibility='collapsed')
        st.markdown('<hr>', unsafe_allow_html=True)

        # Show the actual file uploader. Some file types have special requirements.
        fileDesc = f'Select {uploadChoice}:'
        if (uploadChoice == 'Generation profile') or(uploadChoice == 'Trap distribution') or(uploadChoice == 'Spectrum'):
            uploadedFile = utils_gen_web.upload_file(fileDesc, ['=', '@', '0x09', '0x0D'], '', False)
        elif uploadChoice == 'n,k values':
            # Special to allow multiple files to be uploaded.
            uploadedFiles = st.file_uploader("Select one or more files with n,k values",type=['txt'], accept_multiple_files=True, label_visibility='visible')
        elif uploadChoice == 'Simulation setup':
            st.warning('Note: You can only upload a Simulation setup file in combination with the associated layer parameter files!')
            # Implement checks on devpar files
            uploadedFile = st.file_uploader(fileDesc, type=['txt'], accept_multiple_files=False, label_visibility='visible')
            if (uploadedFile != None and uploadedFile != False):
                data = uploadedFile.getvalue().decode('utf-8')
                tmp_layers = utils_devpar_gen.getLayersFromSetup(data)
                
                uploadedFiles = st.file_uploader("Select all the layer parameter files associated with the simulation setup",type=['txt'], accept_multiple_files=True, label_visibility='visible')
                layerNames = []
                for item in uploadedFiles:
                    layerNames.append(item.name)

                allFilesUploaded = all(item in layerNames for item in tmp_layers) # Check if all the required parameter files have been uploaded
                if not allFilesUploaded:
                    # List the names of the missing files
                    st.write('Missing layer parameter files:')
                    for item in tmp_layers:
                        if not item in layerNames:
                            st.write(item)
                            
        elif uploadChoice == 'Layer parameters':
            uploadedFile = st.file_uploader(fileDesc, type=['txt'], accept_multiple_files=False, label_visibility='visible')
            if (uploadedFile != None and uploadedFile != False):
                if uploadedFile.name in st.session_state['availableLayerFiles']:
                    st.warning('A layer parameter file with this name already exists, it will be overwritten. Consider changing the name of the to be uploaded file if you want to keep both files.')

        if st.button("Submit", disabled = not allFilesUploaded):
            # Depending on the type of uploaded file, call the corresponding function to process the upload
            if (uploadedFile != None and uploadedFile != False) or (uploadedFiles != None and uploadedFiles != False):
                if uploadChoice == 'Generation profile':
                    upload_gen_prof_file(uploadedFile)
                elif uploadChoice == 'Trap distribution':
                    upload_trap_level_file(uploadedFile)
                elif uploadChoice == 'n,k values':
                    upload_nk_file(uploadedFiles)
                elif uploadChoice == 'Spectrum':
                    upload_spectrum_file(uploadedFile)
                elif uploadChoice == 'Simulation setup':
                    # Update the available files list to check whether a new file name has been added with the upload
                    for item in layerNames:
                        if not item in st.session_state['availableLayerFiles']:
                            st.session_state['availableLayerFiles'].insert(-3,item)
                    upload_devpar_file(uploadedFile,uploadedFiles)
                elif uploadChoice == 'Layer parameters':
                    upload_layer_file(uploadedFile)
                    if not uploadedFile.name in st.session_state['availableLayerFiles']:
                        st.session_state['availableLayerFiles'].insert(-3,uploadedFile.name)

            # Rerun the script to process all the changes
            st.rerun()

    # Dialog window to add a new layer to the device
    @st.experimental_dialog("Add a layer")
    def addLayerDialog():
        st.write(f"Add a new layer to the device")
        # We need two columns, one for the labels, one for the values. Only the layer configuration is selectable, the other values are fixed.
        col_par, col_val = st.columns([1,1],)
        with col_par:
            st.text_input("Layer_index", value="Layer index", disabled=True, label_visibility="collapsed")
            st.text_input("Layer_name", value="layer_name", disabled=True, label_visibility="collapsed")
            st.text_input("Layer_configuration", value="layer_config", disabled=True, label_visibility="collapsed")
        with col_val:
            layer_index_val = st.text_input("Layer_index_val", value=str(len(layers)),disabled=True, label_visibility="collapsed")
            layer_name_val = st.text_input("Layer_name_val", value=f'l{layer_index_val}', disabled=True, label_visibility="collapsed")
            # Add the default layer files to the list to have them as a selection option
            layers_default =  ['PVSK','ETL','HTL'] # Store these files not here but init them somewhere else or read them from the resource folder (However these must be manually related!!)

            layers_options = st.session_state['availableLayerFiles']

            # layers_ext = [x[2] for x in layers] + layers_default # Create a single list from the existing layers and the default layers to choose from
            layer_config_val = st.selectbox("Layer_configuration_val", options=layers_options,format_func=lambda x: x, label_visibility="collapsed")
        if layer_config_val in layers_default:
            disableCreateNew = True # We must create a new layer parameter file, as a default file cannot be reused.
        else:
            disableCreateNew = False

        chk_createNew = st.checkbox("Create new layer parameter file?", value=True, disabled=disableCreateNew)

        if st.button("Submit"):
            if chk_createNew:
                # We need to create a new file.
                updatedFileName = f'L{layer_index_val}_parameters.txt'
                # If we add a defualt layer, copy the default layer parameters to the session folder and rename it to the new layer index.
                if layer_config_val in layers_default: # We are duplicating a default file. Copy the default file to the session folder with the new name.
                    if layer_config_val == 'PVSK':
                        def_idx = 2
                    elif layer_config_val == 'ETL':
                        def_idx = 3
                    elif layer_config_val == 'HTL':
                        def_idx = 1
                    layer_config_val = f'L{def_idx}_parameters.txt'
                    shutil.copy(os.path.join(resource_path, layer_config_val), os.path.join(session_path,updatedFileName))
                else:
                    # Duplicate an existing layer file and rename to the new layer index
                    fileList = os.listdir(session_path)
                    if updatedFileName not in fileList:
                        shutil.copy(os.path.join(session_path, f'{layer_config_val}'), os.path.join(session_path,updatedFileName))
                    else:
                    # The file already exsisted in some situation before. Add a subindex to differentiate
                        i=1
                        while os.path.isfile(os.path.join(session_path,f'L{layer_index_val}_parameters_{i}.txt')):
                            i+=1
                        else:
                            shutil.copy(os.path.join(session_path, f'{layer_config_val}'), os.path.join(session_path,f'L{layer_index_val}_parameters_{i}.txt'))
                            updatedFileName = f'L{layer_index_val}_parameters_{i}.txt'
                # Add the just created file name to the list of available layer parameter files
                st.session_state['availableLayerFiles'].insert(-3,updatedFileName)

                # Append to the currently used layers list to display on the UI
                new_layer = ['par',layer_name_val, updatedFileName, f'parameter file for layer {layer_index_val}']
                dev_par[updatedFileName]= dev_par[layer_config_val] # Append the layer parameters to the dev_par object

            else:
                # Creating a new layer using an existing layer definition. We only need to add it to the currently used layers list
                new_layer = ['par',layer_name_val, layer_config_val, f'parameter file for layer {layer_index_val}']

            layers.append(new_layer)
            # Update the simulation_setup file with the new layer
            for section in dev_par[zimt_device_parameters]:
                if section[0] == 'Layers':
                    section.append(new_layer)

            # Save the files
            save_parameters()

            # Rerun UI to update the displayed layers
            st.rerun()

    # Dialog window to remove a layer from the device
    @st.experimental_dialog("Remove a layer")
    def removeLayerDialog():
        st.write(f"Remove a layer from the device")
        # Have a selectbox with which layer to remove
        col_par, col_val = st.columns([1,1],)
        with col_par:
            layerRemoved = st.selectbox('Select a layer to remove', layers[1:], format_func=lambda x: x[1], label_visibility="collapsed")
        with col_val:
            st.text_input('Layer_index_val', value=layerRemoved[2], disabled=True, label_visibility="collapsed")
        # As we need to keep consecutive indices for the layers, warn the user.
        st.warning('Note: Removing a layer cannot be reversed! After removal, the remaining layers will be reordered to retain consecutive layer indices. ')
        if st.button("Submit"):
            # Remove the layer from all relevant list and objects
            removeIndex = layers.index(layerRemoved)
            layers.remove(layerRemoved)
            for i in range(len(layers)):
                # Reorder layers list
                if i>=removeIndex:
                    layers[i][1] = f'l{i}'
                    layers[i][3] = f'parameter file for layer {i}'
            
            # Update the simulation_setup file with the new layer
            for section in dev_par[zimt_device_parameters]:
                if section[0] == 'Layers':
                    removeIndex = section.index(layerRemoved)
                    section.remove(layerRemoved)
                    for i in range(len(section)):
                        # Reorder dev par object
                        if i>=removeIndex:
                            section[i][1] = f'l{i}'
                            section[i][3] = f'parameter file for layer {i}'

            # Save the files
            save_parameters()

            # Rerun UI to update the displayed layers
            st.rerun()

    ######### UI layout ###############################################################################

    # Create lists containing the names of available nk and spectrum files. Including user uploaded ones.
    nk_file_list, spectrum_file_list = create_nk_spectrum_file_array()
    # Sort them alphabetically
    nk_file_list.sort(key=str.casefold)
    spectrum_file_list.sort(key=str.casefold)

    # Load the device_parameters file and create a List object.
    dev_par, layers = utils_devpar_gen.load_device_parameters(session_path, zimt_device_parameters, zimt_path, availLayers = st.session_state['availableLayerFiles'][:-3])

    with st.sidebar:
        # Show custom menu
        menu()
        # Open a dialog window to upload a file
        if st.button('Upload a file'):
            uploadFileDialog()

        # Device Parameter button to save, download or reset a file
        st.button('Save device parameters', on_click=save_parameters_BD)

        # Prepare a ZIP archive to download the device parameters
        zip_filename = utils_gen.create_zip(session_path, layers)

        # Show a button to download the ZIP archive
        with open(zip_filename, 'rb') as fp:
            btn = st.download_button(label='Download device parameters', data = fp, file_name = os.path.basename(zip_filename), mime='application/zip')

        # Reset the device parameters to the default values.
        reset_device_parameters = st.button('Reset device parameters')
        st.button('Run Simulation', on_click=run_Impedance)

    # When the reset button is pressed, empty the container and create a List object from the default .txt file. Next, save the default parameters to the parameter file.
    if reset_device_parameters:
        main_container_impedance.empty()
        dev_par, layers = utils_devpar_gen.load_device_parameters(session_path, zimt_device_parameters, resource_path, True, availLayers=st.session_state['availableLayerFiles'][:-3])
        save_parameters()

    with main_container_impedance.container():
    # Start building the UI for the actual page
        st.title("Impedance spectroscopy")
        st.write("""
            Simulate an impedance spectroscopy experiment with SIMsalabim (ZimT). The impedance is calculated at the applied voltage. 
            A small one time pertubation at t=0 is introduced at this voltage, defined by the voltage step size. 
            The impedance is calculated using Fourier decomposition, based on the method desrcibed in *S.E. Laux, IEEE Trans. Electron Dev. 32 (10), 2028 (1985)*.
        """)

        for par_section in dev_par[zimt_device_parameters]: # ToDo check if correct
            if par_section[0] == 'Description': 
                # The first section of the page is a 'special' section and must be treated seperately.
                # The SIMsalabim version number and general remarks to show on top of the page
                version = [i for i in par_section if i[1].startswith('version:')]
                st.write("SIMsalabim " + version[0][1])
                # Reference to the SIMsalabim manual
                st.write("""For more information about the device parameters or SIMsalabim itself, refer to the
                                [Manual](https://raw.githubusercontent.com/kostergroup/SIMsalabim/master/Docs/Manual.pdf)""")
                
        with container_impedance_par.container():
            st.subheader('Impedance parameters')
            col_par_impedance, col_val_impedance, col_desc_impedance = st.columns([2, 2, 8],)
            for impedance_item in impedance_par:
                with col_par_impedance:
                    st.text_input(impedance_item[0], value=impedance_item[0], disabled=True, label_visibility="collapsed")

                # Parameter value
                with col_val_impedance:
                    if impedance_item[0] == 'fstep':
                        # Show these parameters as a float
                        impedance_item[1] = st.number_input(impedance_item[0] + '_val', value=impedance_item[1], label_visibility="collapsed")
                    elif impedance_item[0] == 'V0' or impedance_item[0] == 'delV' or impedance_item[0] == 'G_frac':
                        # Show these parameters as a float
                        impedance_item[1] = st.number_input(impedance_item[0] + '_val', value=impedance_item[1], label_visibility="collapsed", format="%f")
                    else:
                        # Show all other parameters in scientific notation e.g. 1e+2
                        impedance_item[1] = st.number_input(impedance_item[0] + '_val', value=impedance_item[1], label_visibility="collapsed", format="%e")
                # Parameter description
                with col_desc_impedance:
                    st.text_input(impedance_item[0] + '_desc', value=impedance_item[2], disabled=True, label_visibility="collapsed")
            st.markdown('<hr>', unsafe_allow_html=True)

        with layer_container_impedance.container():
            # Device layer setup        
            st.subheader("Device setup")

            # Show the Ddd layer button
            if st.button('Add a layer'):
                addLayerDialog()
                
            # Display the layers
            for layer in layers:
                if not layer[1] == 'setup':
                    col_par, col_val, col_desc = st.columns([2, 4, 8]) 
                    with col_par:
                        st.text_input(layer[1], value=layer[1], key=layer[1], disabled=True, label_visibility="collapsed")
                    with col_val:
                        # create a list with the layer names to choose from
                        layer_names = st.session_state['availableLayerFiles'][:-3]
                        selected_layer = layer_names.index(layer[2])
                        st.selectbox(layer[2],key=layer[1] + ' ' + layer[2], options=layer_names,index = selected_layer,format_func=lambda x: x, label_visibility="collapsed")
                    with col_desc:
                        st.text_input(layer[3], value=layer[3],key=layer[1] + ' ' + layer[3], disabled=True, label_visibility="collapsed")

            # Show the remove layer button. Only when more than 1 layer is present!
            if len(layers) >2:
                if st.button('Remove a layer'):
                    removeLayerDialog()

            st.markdown('<hr>', unsafe_allow_html=True)

    # Section to edit the device parameters
        with container_device_par.container():
            filesDisplay = [zimt_device_parameters]
            filesDisplay.extend(st.session_state['availableLayerFiles'][:-3])

            selected_layer = st.selectbox('Select a file to edit', filesDisplay, on_change=save_parameters)

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
                                        item[2] = st.selectbox(selected_layer + item[1] + '_val', options=nk_file_list, format_func=format_func, index=nk_file_list.index(item[2].replace('../','')), label_visibility="collapsed")
                                    elif item[1] == 'spectrum': # spectrum file name, use a selectbox.
                                        if item[2] not in spectrum_file_list:
                                            item[2] = '--none--'
                                        item[2] = st.selectbox(selected_layer + item[1] + '_val', options=spectrum_file_list, format_func=format_func, index=spectrum_file_list.index(item[2].replace('../','')), label_visibility="collapsed")
                                    elif item[1]== 'pauseAtEnd':
                                        # This parameter must not be editable and forced to 0, otherwise the program will not exit/complete and hang forever.
                                        item[2] = 0
                                        item[2] = st.text_input(selected_layer + item[1] + '_val', value=item[2], disabled=True, label_visibility="collapsed")
                                    elif (item[1] == 'intTrapFile') or (item[1] == 'bulkTrapFile'):
                                        # This could be uploaded trap files,so display a list of available ones. 
                                        if item[2] not in st.session_state['trapFiles']:
                                            # Value from file is not recognized, replace with none
                                            st.toast(f'Could not find file "{item[2]}" for parameter {item[1]} and has been set to none. If you want to use this file, please upload it using the "Upload trap distribution" option and associate it with the {item[1]} parameter.')
                                            item[2] == 'none'
                                        item[2] = st.selectbox(selected_layer + item[1]+ '_val', options=st.session_state['trapFiles'], index=st.session_state['trapFiles'].index(item[2]), label_visibility="collapsed")
                                    else:
                                        item[2] = st.text_input(selected_layer + item[1] + '_val', value=item[2], label_visibility="collapsed")
                                
                                # Parameter description
                                with col_desc:
                                    st.text_input(item[1] + '_desc', value=item[3], disabled=True, label_visibility="collapsed")
            
    #  Show the SIMsalabim logo in the sidebar
    with st.sidebar:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.image('./logo/SIMsalabim_logo_cut_trans.png')
