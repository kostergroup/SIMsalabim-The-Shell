"""Functions for processing the device parameters"""
######### Package Imports #########################################################################

import os, random
import streamlit as st
from pySIMsalabim.utils import device_parameters as utils_devpar

######### Function Definitions ####################################################################

def verify_devpar_file(data_devpar, check_devpar, nk_file_list, spectrum_file_list):
    """Verify the uploaded device parameters file. Compare it with the standard device parameter file. If it does not match, reject the upload.
    
    Parameters
    ----------
    data_devpar : List
        List object with all parameters and comments.
    check_devpar : string
        Indicate which type of device parameters file needs to be checked, simss or zimt
    nk_file_list : List
        List with the available nk files
    spectrum_file_list : List
        List with the available spectrum files       
    Returns
    -------
    integer
        0 if file is valid. 1 if file is invalid
    string
        Message which, when file is invalid, states the reason including line numbers
    """   

    res_path = st.session_state['resource_path'] # Path to default device parameters
    line_min = []
    line_min_default = []
    valid_upload = 1
    msg = ''
    potLayers = [f'l{i}' for i in range(1,1000)] # List with all possible layer names


    ## Store the uploaded file with a random id in a temporary directory. 
    tmp_id = random.randint(0, int(1e10))
    destination_file_devpar = open('Simulations/tmp/devpar_' + str(tmp_id) + '.txt', "w", encoding='utf-8')
    destination_file_devpar.write(data_devpar)
    destination_file_devpar.close()

    # Read the uploaded file line by line. Keep a record of the line number to eventually create a clear error message.
    with open('Simulations/tmp/devpar_' + str(tmp_id) + '.txt', encoding='utf-8') as fpp:
        count = 1
        for line in fpp:
            line = line.strip()
            # Empty lines and lines containing comments must be ignored

            line_split = line.split('=')

            if not line.startswith('*') and not line.startswith('\n') and not line == '' and not (line_split[0].strip() in potLayers):
                line_min.append([line, count])
            count += 1

    # File content has been stored in an object. Remove the tmp file.
    for item_dir_list in os.listdir('Simulations/tmp'):
        if str(tmp_id) in item_dir_list:
            os.remove('Simulations/tmp/devpar_' + str(tmp_id) + '.txt')

    if check_devpar == 'simss':
        std_par_file = os.path.join(res_path, st.session_state['simss_devpar_file'])
    elif check_devpar == 'zimt':
        std_par_file = os.path.join(res_path, st.session_state['zimt_devpar_file'])
    else:
        valid_upload = 1
        msg = 'Something went wrong, upload failed'
        return valid_upload, msg

    # Open and read the standard device parameters file
    with open(std_par_file, encoding='utf-8') as fp:
        count = 1
        for line in fp:
            line = line.strip()
            # Empty lines and lines containing comments must be ignored

            line_split = line.split('=')
            if not line.startswith('*') and not line.startswith('\n') and not line == '' and not (line_split[0].strip() in potLayers):
                line_min_default.append([line, count])
            count += 1
    
    # Loop simultaneously over both Lists and check whether each entry matches. If not, return an error message with the relevant lines.
    for a, b in zip(line_min, line_min_default):
        a_par = a[0].split('=')
        b_par = b[0].split('=')

        if len(a[0]) < 2:
            valid_upload = 1
            msg = ('Upload failed, file not formatted correctly.\n\n Line ' + str(a[1]) + ': " ' + a + '" is not according to the format.')
            return valid_upload, msg
        elif a_par[0] != b_par[0]:
            valid_upload = 1
            msg = ('Upload failed, expected parameter: "' + b_par[0] + '" (line ' + str(b[1]) + ') and received parameter "' + a_par[0] + '" (line ' + str(a[1]) + ')')
            return valid_upload, msg
        else:
            valid_upload = 0

    if valid_upload == 0:
        # Extra check, verify whether the nk/spectrum files exist
        for item in line_min:
            item_par = item[0].split('=')
            if item_par[0].startswith('nk'):
                # Found a nk_file
                item_par_split = item_par[1].split('*')
                if item_par_split[0].strip() not in nk_file_list and item_par_split[0].strip() != 'none':
                    # Check if the file is in the list or labelled as none
                    if msg == '':
                        msg = [item_par_split[0].strip()]
                    else:
                        msg.append(item_par_split[0].strip())
                    valid_upload = 2
            elif item_par[0].startswith('spectrum'):
                # Found the spectrum
                item_par_split = item_par[1].split('*')
                if item_par_split[0].strip() not in spectrum_file_list and item_par_split[0].strip() != 'none':
                    # Check if the file is in the list or labelled as none
                    if msg == '':
                        msg = [item_par_split[0].strip()]
                    else:
                        msg.append(item_par_split[0].strip())
                    valid_upload = 2
        
        if valid_upload == 2:
            # One or more files were not found, a list of the missing files is returned in the message.
            msg = ['Warning, File(s) not found. \n These files will be replaced by --none--. If you want to calculate the generation profile, select files from the list or upload them.\n'] + msg

    return valid_upload, msg

def store_file_names(dev_par, sim, dev_par_name, layers):
    """Read the relevant file names from the device parameters and store the file name in a session state. 
        This way the correct and relevant files can be retrieved and used in the results. Make a distinction between simss and zimt.

    Parameters
    ----------
    dev_par : List
        Nested List object containing all device parameters
    sim : string
        Store files for either SimSS or ZimT
    dev_par_name : string
        Name of the device parameter file
    layers : List
        List with all the layers in the device
    """

    retval = utils_devpar.store_file_names(dev_par, sim, dev_par_name, layers, run_mode=True)

    # Common session state keys # Index 5 must be skipped as this is the expJV file!
    shared_keys = ['LayersFiles', 'opticsFiles', 'genProfile', 'traps_int', 'traps_bulk', None, 'varFile', 'logFile']
    for key, value in zip(shared_keys, retval):
        if key is not None:
            st.session_state[key] = value

    # Handle Simulation-specific keys
    if sim == 'simss':
        sim_keys = ['expJV', 'JVFile', 'scParsFile']
        sim_indices = [5, 8, 9]
    else:  # zimt
        sim_keys = ['tVGFile', 'tJFile']
        sim_indices = [10, 11]

    for key, idx in zip(sim_keys, sim_indices):
        st.session_state[key] = retval[idx]

def write_pars_txt(dev_par, layers, session_path, dev_par_file):
    """Write device parameters to the txt file.

    Parameters
    ----------
    dev_par : List
        List object with all parameters and comments.
    layers : List
        List with all the layers in the device
    session_path : string
        Folder path of the current simulation session
    defv_par_file : string
        name of the device parameters file
    """
    # Write the device parameter List object to a txt string.
    i = 0 # Index for the different layers, 0 is always the simulation setup file
    # First check what the most recent names of the layers are from the UI. Update the names in the dev_par object first
    for layer in layers:
        for section in dev_par[dev_par_file]:
            if section[0] == 'Layers':
                for param in section[1:]:
                    if param[1] == layer[1]:
                        param[2] = layer[2]
                        
    for layer in layers:
        par_file = utils_devpar.devpar_write_to_txt(dev_par[layer[2]])
        # Check if the layer is the simulation setup file or a layer file and set the name accordingly
        if layer[1]=='setup':
            file_name = dev_par_file
        else:
            file_name = layer[2]
        # Open the device_parameters file (in the id folder) and write content of par_file to it.

        with open(os.path.join(session_path, file_name), 'w', encoding='utf-8') as fp_device_parameters:
            fp_device_parameters.write(par_file)
            fp_device_parameters.close()
        i+=1

def getLayersFromSetup(data):
    """Retrieve the layers from the setup file

    Parameters
    ----------
    data : string
        Content of the setup file

    Returns
    -------
    List
        List with all the layers
    """
    # Write the uploaded file to a tmp file. This is necessary to read the file line by line.
    tmp_id = random.randint(0, int(1e10))
    destination_file_devpar = open('Simulations/tmp/devpar_' + str(tmp_id) + '.txt', "w", encoding='utf-8')
    destination_file_devpar.write(data)
    destination_file_devpar.close()

    # Read the uploaded file line by line. Keep a record of the line number to eventually create a clear error message.
    with open('Simulations/tmp/devpar_' + str(tmp_id) + '.txt', encoding='utf-8') as fp:
        tmp_devpar = utils_devpar.devpar_read_from_txt(fp)

    # File content has been stored in an object. Remove the tmp file.
    for item_dir_list in os.listdir('Simulations/tmp'):
        if str(tmp_id) in item_dir_list:
            os.remove('Simulations/tmp/devpar_' + str(tmp_id) + '.txt')
    
    # Extract the layers from the tmp object
    tmp_layers = []
    for section in tmp_devpar:
        if section[0] == 'Layers':
            for param in section[1:]:
                tmp_layers.append(param[2])
    
    return tmp_layers

def create_nk_spectrum_file_array(session_path):
    """Create lists containing the names of the available nk and spectrum files.

    Parameters
    ----------
    session_path : string
        Path of the current simulation session

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

def read_exp_parameters(exp_par, dev_par_list, param_keys, extract_keys):
    """Read the parameters from the device parameters needed for the experiments and return them as a dictionary.

    Parameters
    ----------
    exp_par : dict
        Dictionary with the experiment specific parameters
    dev_par_list : List
        Nested List object containing all device parameters
    param_keys : List
        List with the names of the required experiment specific parameters
    extract_keys : List
        List with the names of the parameters to extract from the "User interface" section

    Returns
    -------
    dict
        Dictionary with all experiment specific parameters
    """
    # Construct dictionary with parameters
    exp_par_obj = {name: row[1] for row, name in zip(exp_par, param_keys)}

    # Find the "User interface" section
    ui_section = next((section for section in dev_par_list if section[0] == "User interface"), [])

    # # Extract parameters and update
    exp_par_obj.update({name: value for _, name, value,_ in ui_section[1:] if name in extract_keys})

    return exp_par_obj

def read_exp_file(session_path, expParsFile, expPars, skip_keys={},int_keys={},string_keys={}):
    """ Read the experiment parameter file and update the experiment parameters object. 
    Interpret the parameters as float, unless specified different.

    Parameters
    ----------
    session_path : string
        Path of the current simulation session
    expParsFile : string
        Name of the experiment parameter file
    expPars : List
        Nested List object containing all experiment specific parameters
    skip_keys : set, optional
        Set with the names of parameters to skip when reading the file, by default {}
    int_keys : set, optional
        Set with the names of parameters to interpret as integers, by default {}
    string_keys : set, optional
        Set with the names of parameters to interpret as strings, by default {}

    Returns
    -------
    List
        Updated nested List object containing all experiment specific parameters
    """
    # Build a lookup dictionary
    lookup_dict = {item[0]: item for item in expPars}

    with open(os.path.join(session_path, expParsFile), encoding="utf-8") as fp:
        for line in fp:
            if "=" not in line:
                continue  # ignore lines that do not contain a parameter

            key, value = line.split("=", 1)
            key = key.strip()

            if key in skip_keys:
                continue # Skip the ignored paraemters

            if key not in lookup_dict:
                continue  # Skip unknown parameters

            # Convert typed values
            value = value.strip()

            # Convert typed values
            value = value.strip()
            if key in int_keys: # integers
                parsed = int(value)
            elif key in string_keys: # strings
                parsed = value
            else: # floats
                parsed = float(value)

            lookup_dict[key][1] = parsed

    return expPars