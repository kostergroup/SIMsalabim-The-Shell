"""Functions for processing the device parameters"""
######### Package Imports #########################################################################

import os, random
import streamlit as st

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
            if not line.startswith('*') and not line.startswith('\n') and not line == '':
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
            if not line.startswith('*') and not line.startswith('\n') and not line == '':
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
            if item_par[0].startswith('nk_'):
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

def store_file_names(dev_par, sim):
    """Read the relevant file names from the device parameters and store the file name in a session state. 
        This way the correct and relevant files can be retrieved and used in the results. Make a distinction between simss and zimt.

    Parameters
    ----------
    dev_par : List
        Nested List object containing all device parameters
    sim : string
        Store files for either SimSS or ZimT
    """
    for section in dev_par[1:]:
        # Generation profile
        if section[0] == 'Generation and recombination':
            for param in section:
                if param[1] == 'Gen_profile':
                    if param[2] != 'none' and param[2] != 'calc':
                        st.session_state['genProf'] = param[2]
                    elif param[2] == 'calc':
                        st.session_state['genProf'] = 'calc'
                    else:
                        st.session_state['genProf'] = 'none'
        
        # Traps
        if section[0] == 'Trapping':
            for param in section:
                if param[1] == 'BulkTrapFile':
                    if param[2] != 'none':
                        st.session_state['traps_bulk'] = param[2]
                    else:
                        st.session_state['traps_bulk'] = 'none'
                if param[1] == 'IntTrapFile':
                    if param[2] != 'none':
                        st.session_state['traps_int'] = param[2]
                    else:
                        st.session_state['traps_int'] = 'none'

        # Files in USer Interface section
        if section[0] == 'User interface':
            for param in section:
                if param[1] == 'Var_file':
                    st.session_state['Var_file'] = param[2]
                if param[1] == 'log_file':
                    st.session_state['log_file'] = param[2]
                if sim == 'simss':
                    if param[1] == 'UseExpData':
                        if param[2] != '1':
                            expjv_id = False
                            st.session_state['expJV'] = 'none'
                        else:
                            expjv_id = True
                    if param[1] == 'ExpJV' and expjv_id is True:
                        st.session_state['expJV'] = param[2]
                    if param[1] == 'JV_file':
                        st.session_state['JV_file'] = param[2]
                    if param[1] == 'scPars_file':
                        st.session_state['scPars_file'] = param[2]
                if sim == 'zimt':
                    if param[1] == 'tVG_file':
                        st.session_state['tVG_file'] = param[2]
                    if param[1] == 'tj_file':
                        st.session_state['tj_file'] = param[2]

    # When the generation profile has been calculated, store the names of the nk and spectrum files.
    if st.session_state['genProf'] == 'calc':
        st.session_state['optics_files'] = []
        specfile = ''
        for section in dev_par[1:]:
            if section[0] == 'Optics':
                for param in section:
                    if param[1].startswith('nk_'):
                        st.session_state['optics_files'].append(param[2])
                    elif param[1]=='spectrum':
                        specfile = param[2]
            if section[0] == 'Transport layers':
                for param in section:
                    if param[1].startswith('nk_'):
                        st.session_state['optics_files'].append(param[2])
        st.session_state['optics_files'].append(specfile)


