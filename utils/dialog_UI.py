import streamlit as st
import shutil, os
from utils import general_UI as utils_gen_UI
from utils import upload_UI as utils_upload_UI
from utils import device_parameters_UI as utils_devpar_UI

def uploadFileDialog(session_path, dev_par, layers, device_parameters_current, device_parameters_alt, simtype):
    """
    Dialog window to upload a file and process it according to the type of file uploaded.
    
    Parameters
    ----------
    session_path: str
        path to the current simulation session
    dev_par: dict 
        current device parameters
    layers: list    
        current layer parameter file names
    device_parameters_current: str 
        name of the device parameter file required for the current simulation (simss or zimt)
    device_parameters_alt: str 
        name of the other device parameter file to keep in sync (simss or zimt)

    Returns
    -------
    dev_par: dict
        updated device parameters after upload
    layers: list
        updated layer parameter file names after upload
    """
    # Select the type of file the user wants to upload. A fixed list of options based on SIMsalabim v5.11
    allFilesUploaded = True # Boolean to disable submit button in case of uploading simulation setup

    st.write('Which type of file do you want to upload?')
    if simtype == 'Steady State JV':
        # Need to include a single experimental JV file
        uploadOptions = ['Experimental JV', 'Generation profile', 'Trap distribution','n,k values', 'Spectrum', 'Simulation setup', 'Layer parameters']
    elif simtype == 'Transient JV':
        # Need to include multiple experimental JV files
        uploadOptions = ['Experimental JVs', 'Generation profile', 'Trap distribution','n,k values', 'Spectrum', 'Simulation setup', 'Layer parameters']
    else:
        uploadOptions = ['Generation profile', 'Trap distribution','n,k values', 'Spectrum', 'Simulation setup', 'Layer parameters']

    # UI selectbox for the type of file to upload
    uploadChoice = st.selectbox('File to upload', options=uploadOptions, label_visibility='collapsed')
    st.markdown('<hr>', unsafe_allow_html=True)

    # Show the actual file uploader. Some file types have special requirements.
    fileDesc = f'Select {uploadChoice}:'
    if (uploadChoice == 'Experimental JV') or (uploadChoice == 'Generation profile') or(uploadChoice == 'Trap distribution') or(uploadChoice == 'Spectrum'):
        uploadedFile = utils_gen_UI.upload_file(fileDesc, ['=', '@', '0x09', '0x0D'], '', False)
    elif uploadChoice == 'Experimental JVs':
        uploadedFiles = st.file_uploader("Select experimental current voltage characteristics",type=['txt'], accept_multiple_files=True, label_visibility='visible')
    elif uploadChoice == 'n,k values':
        # Special to allow multiple files to be uploaded.
        uploadedFile = None
        uploadedFiles = st.file_uploader("Select one or more files with n,k values",type=['txt'], accept_multiple_files=True, label_visibility='visible')
    elif uploadChoice == 'Simulation setup':
        st.warning('Note: You can only upload a Simulation setup file in combination with the associated layer parameter files!')
        # Implement checks on devpar files
        uploadedFile = st.file_uploader(fileDesc, type=['txt'], accept_multiple_files=False, label_visibility='visible')
        if (uploadedFile != None and uploadedFile != False):
            data = uploadedFile.getvalue().decode('utf-8')
            tmp_layers = utils_devpar_UI.getLayersFromSetup(data)
            
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
            if uploadChoice == 'Experimental JV':
                utils_upload_UI.upload_exp_jv_file(uploadedFile, session_path, dev_par, layers, device_parameters_current, device_parameters_alt )
            elif uploadChoice == 'Experimental JVs':
                    utils_upload_UI.upload_expJV_files(uploadedFiles,session_path, dev_par, layers, device_parameters_current, device_parameters_alt)
            elif uploadChoice == 'Generation profile':
                utils_upload_UI.upload_gen_prof_file(uploadedFile, session_path, dev_par, layers, device_parameters_current, device_parameters_alt )
            elif uploadChoice == 'Trap distribution':
                utils_upload_UI.upload_trap_level_file(uploadedFile, session_path, dev_par, layers, device_parameters_current, device_parameters_alt )
            elif uploadChoice == 'n,k values':
                utils_upload_UI.upload_nk_file(uploadedFiles, session_path, dev_par, layers, device_parameters_current, device_parameters_alt )
            elif uploadChoice == 'Spectrum':
                utils_upload_UI.upload_spectrum_file(uploadedFile, session_path, dev_par, layers, device_parameters_current, device_parameters_alt )
            elif uploadChoice == 'Simulation setup':
                # Update the available files list to check whether a new file name has been added with the upload
                for item in layerNames:
                    if not item in st.session_state['availableLayerFiles']:
                        st.session_state['availableLayerFiles'].insert(-3,item)
                utils_upload_UI.upload_devpar_file(uploadedFile, uploadedFiles, session_path,device_parameters_current)
            elif uploadChoice == 'Layer parameters':
                utils_upload_UI.upload_layer_file(uploadedFile, session_path)
                if not uploadedFile.name in st.session_state['availableLayerFiles']:
                    st.session_state['availableLayerFiles'].insert(-3,uploadedFile.name)

        # Rerun the script to process all the changes
        st.rerun()
    return dev_par, layers

def addLayerDialog(session_path, dev_par, layers, resource_path, device_parameters_current, device_parameters_alt):
    """
    Dialog window to add a new layer to the device.

    Parameters
    ----------
    session_path: str
        path to the current simulation session
    dev_par: dict 
        current device parameters
    layers: list    
        current layer parameter file names
    resource_path: str
        path to the resource folder with standard files
    device_parameters_current: str 
        name of the device parameter file required for the current simulation (simss or zimt)
    device_parameters_alt: str 
        name of the other device parameter file to keep in sync (simss or zimt)
    
    Returns
    -------
    dev_par: dict
        updated device parameters after adding the layer
    layers: list
        updated layer parameter file names after adding the layer
    """

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
        for section in dev_par[device_parameters_current]:
            if section[0] == 'Layers':
                section.append(new_layer)

        # Save the files
        utils_gen_UI.save_parameters(dev_par, layers, session_path, device_parameters_current, device_parameters_alt)

        # Rerun UI to update the displayed layers
        st.rerun()
    
    return dev_par, layers

def removeLayerDialog(dev_par, layers, session_path, device_parameters_current, device_parameters_alt):
    """
    Dialog window to remove a layer from the device.

    Parameters
    ----------
    dev_par: dict 
        current device parameters
    layers: list
        current layer parameter file names
    session_path: str
        path to the current simulation session
    device_parameters_current: str 
        name of the device parameter file required for the current simulation (simss or zimt)
    device_parameters_alt: str 
        name of the other device parameter file to keep in sync (simss or zimt)

    Returns
    -------
    dev_par: dict
        updated device parameters after removing the layer
    layers: list
        updated layer parameter file names after removing the layer
    """

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
        for section in dev_par[device_parameters_current]:
            if section[0] == 'Layers':
                removeIndex = section.index(layerRemoved)
                section.remove(layerRemoved)
                for i in range(len(section)):
                    # Reorder dev par object
                    if i>=removeIndex:
                        section[i][1] = f'l{i}'
                        section[i][3] = f'parameter file for layer {i}'

        # Save the files
        utils_gen_UI.save_parameters(dev_par, layers, session_path, device_parameters_current, device_parameters_alt)

        # Rerun UI to update the displayed layers
        st.rerun()
    
    return dev_par, layers
