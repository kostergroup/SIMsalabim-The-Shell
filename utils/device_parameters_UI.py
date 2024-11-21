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

    st.session_state['LayersFiles'] = retval[0]
    st.session_state['opticsFiles'] = retval[1]
    st.session_state['genProfile'] = retval[2]
    st.session_state['traps_int'] = retval[3]
    st.session_state['traps_bulk'] = retval[4]
    st.session_state['varFile'] = retval[6]
    st.session_state['logFile'] = retval[7]

    if sim == 'simss':
        st.session_state['expJV'] = retval[5]
        st.session_state['JVFile'] = retval[8]
        st.session_state['scParsFile'] = retval[9]
    else:
        st.session_state['tVGFile'] = retval[10]
        st.session_state['tJFile'] = retval[11]

def save_parameters(dev_par, layers, session_path, dev_par_file):
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

