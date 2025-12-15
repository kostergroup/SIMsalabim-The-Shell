import streamlit as st
import utils.general_UI as utils_gen_UI
import os

def upload_single_file_to_folder(uploaded_file, session_path, is_dev_par = False, dev_par_name = ''):
    """ Read and decode the uploaded file and write to a file in the session folder.

    Parameters
    ----------
    uploaded_file : UploadedFile
        Object with the contents of the uploaded file
    session_path : string
        Path of the simulation folder for this session
    is_dev_par : boolean
        True when a  device parameters file is uploaded
    dev_par_name : string
        Fixed name of the device parameters file

    Returns
    -------
    None
    """
    # Decode the uploaded file (utf-8)
    data = uploaded_file.getvalue().decode('utf-8')

    # Setup the write directory. When a device parameters file is uplaoded, use the fixed/pre-set name, otherwise use the name of the uploaded file.
    if is_dev_par == True:
        target_path = os.path.join(session_path, dev_par_name)
    else:
        target_path = os.path.join(session_path, uploaded_file.name)

    # Write the contents of the uploaded file to a file in the SimSS folder
    destination_file = open(target_path, "w", encoding='utf-8')
    destination_file.write(data)
    destination_file.close()

def upload_multiple_files_to_folder(uploaded_files, session_path):
    """ Read and decode the uploaded file and write to a file in the session folder.

    Parameters
    ----------
    uploaded_files : List
        List object with each element being the contents of a uploaded file
    session_path : string
        Path of the simulation folder for this session
    
    Returns
    -------
    None
    """
            
    for i in range(len(uploaded_files)):
        # Decode the uploaded file (utf-8)
        data = uploaded_files[i].getvalue().decode('utf-8')

        # Setup the write directory
        target_path = os.path.join(session_path, uploaded_files[i].name)

        # Write the contents of the uploaded file to a file in the SimSS folder
        destination_file_nk = open(target_path, "w", encoding='utf-8')
        destination_file_nk.write(data)
        destination_file_nk.close()

def upload_exp_jv_file(uploaded_file, session_path, dev_par, layers, device_parameters_current, device_parameters_alt ):
    """Write the experimental JV file to the session folder. Update the expJV parameters and save them.

    Parameters
    ----------
    uploaded_file : file
        The uploaded file to be saved
    session_path : str
        The path to the session folder
    dev_par : list
        The device parameters as a list of nested lists
    layers : List
        List with all layers in the device.
    device_parameters_current : str
        The name of the current device parameters file
    device_parameters_alt : str
        The name of the other device parameters file

    Returns
    -------
    success
        Display a streamlit success message
    """
    upload_single_file_to_folder(uploaded_file, session_path)

    # Update the UseExpData to 1 and change the ExpJV file name to the name of the just uploaded file.
    for section in dev_par[device_parameters_current][1:]:
        if section[0] == 'User interface':
            for item_output_par in section:
                if 'useExpData' in item_output_par[1]:
                    item_output_par[2] = '1'
                if 'expJV' in item_output_par[1]:
                    item_output_par[2] = uploaded_file.name

    utils_gen_UI.save_parameters(dev_par, layers, session_path, device_parameters_current, device_parameters_alt)

    return st.success('File upload complete')

def upload_expJV_files(uploaded_files,session_path,dev_par,layers,device_parameters_current, device_parameters_alt):
    """ Read and decode the uploaded exp JVs and create files.

    Parameters
    ----------
    uploaded_files : files
        The uploaded files to be saved
    session_path : str
        The path to the session folder
    dev_par : list
        The device parameters as a list of nested lists
    layers : List
        List with all layers in the device.
    device_parameters_current : str
        The name of the current device parameters file
    device_parameters_alt : str
        The name of the other device parameters file

    Returns
    -------
    success
        Display a streamlit success message
    """
    utils_gen_UI.upload_multiple_files_to_folder(uploaded_files, os.path.join(session_path))

    utils_gen_UI.save_parameters(dev_par, layers, session_path, device_parameters_current, device_parameters_alt)

    return st.success('File upload complete')

def upload_gen_prof_file(uploaded_file, session_path, dev_par, layers, device_parameters_current, device_parameters_alt ):
    """Write the generation profile file to the session folder. Update the genProfile parameter and save them.

    Parameters
    ----------
    uploaded_file : file
        The uploaded file to be saved
    session_path : str
        The path to the session folder
    dev_par : list
        The device parameters as a list of nested lists
    layers : List
        List with all layers in the device.
    device_parameters_current : str
        The name of the current device parameters file
    device_parameters_alt : str
        The name of the other device parameters file

    Returns
    -------
    success
        Display a streamlit success message
    """
    upload_single_file_to_folder(uploaded_file, session_path)

    # Update the Gen_profile name with the name of the just uploaded file.
    for section in dev_par[device_parameters_current][1:]:
        if section[0] == 'Optics':
            for item_output_par in section:
                if 'genProfile' in item_output_par[1]:
                    item_output_par[2] = uploaded_file.name
    utils_gen_UI.save_parameters(dev_par, layers, session_path, device_parameters_current, device_parameters_alt)

    return st.success('File upload complete')

def upload_trap_level_file(uploaded_file, session_path, dev_par, layers, device_parameters_current, device_parameters_alt ):
    """Write the trap level file to the session folder and save it. Append the file to the trapFiles list.

    Parameters
    ----------
    uploaded_file : file
        The uploaded file to be saved
    session_path : str
        The path to the session folder
    dev_par : list
        The device parameters as a list of nested lists
    layers : List
        List with all layers in the device.
    device_parameters_current : str
        The name of the current device parameters file
    device_parameters_alt : str
        The name of the other device parameters file

    Returns
    -------
    success
        Display a streamlit success message
    """
    upload_single_file_to_folder(uploaded_file, session_path)
    st.session_state['trapFiles'].append(uploaded_file.name)
    utils_gen_UI.save_parameters(dev_par, layers, session_path, device_parameters_current, device_parameters_alt)

    return st.success('File upload complete')

def upload_nk_file(uploaded_files, session_path, dev_par, layers, device_parameters_current, device_parameters_alt ):
    """ Read and decode the uploaded nk_files and create  files.

    Parameters
    ----------
    uploaded_files : files
        The uploaded files to be saved
    session_path : str
        The path to the session folder
    dev_par : list
        The device parameters as a list of nested lists
    layers : List
        List with all layers in the device.
    device_parameters_current : str
        The name of the current device parameters file
    device_parameters_alt : str
        The name of the other device parameters file

    Returns
    -------
    success
        Display a streamlit success message
    """
    upload_multiple_files_to_folder(uploaded_files, os.path.join(session_path,'Data_nk'))

    utils_gen_UI.save_parameters(dev_par, layers, session_path, device_parameters_current, device_parameters_alt)

    return st.success('File uploads complete')

def upload_spectrum_file(uploaded_file, session_path, dev_par, layers, device_parameters_current, device_parameters_alt ):
    """ Read and decode the uploaded spectrum and create  files.

    Parameters
    ----------
    uploaded_file : file
        The uploaded file to be saved
    session_path : str
        The path to the session folder
    dev_par : list
        The device parameters as a list of nested lists
    layers : List
        List with all layers in the device.
    device_parameters_current : str
        The name of the current device parameters file
    device_parameters_alt : str
        The name of the other device parameters file

    Returns
    -------
    success
        Display a streamlit success message
    """
    upload_single_file_to_folder(uploaded_file, os.path.join(session_path,'Data_spectrum',))

    utils_gen_UI.save_parameters(dev_par, layers, session_path, device_parameters_current, device_parameters_alt)

    return st.success('File upload complete')

def upload_devpar_file(uploaded_file, uploaded_files, session_path, device_parameters):
    """Write the simualtion seetup file to the session folder. 

    Parameters
    ----------
    uploaded_file : file
        The uploaded simualtion setup file to be saved
    uploaded_files : files
        The uploaded layer parameter files to be saved
    session_path : str
        The path to the session folder
    device_parameters : str
        The name of the device parameters file

    Returns
    -------
    success
        Display a streamlit success message
    """
    uploaded_file.name = device_parameters
    upload_single_file_to_folder(uploaded_file, session_path)
    upload_multiple_files_to_folder(uploaded_files, session_path)

    return st.success('Upload device parameters complete')

def upload_layer_file(uploaded_file, session_path):
    """Write the layer parameter file to the session folder. 

    Parameters
    ----------
    uploaded_file : file
        The uploaded file to be saved
    session_path : str
        The path to the session folder

    Returns
    -------
    success
        Display a streamlit success message
    """
    upload_single_file_to_folder(uploaded_file, session_path)

    return st.success('Upload device parameters complete')