"""Functions for processing the device parameters"""
######### Package Imports #########################################################################

import os, random, shutil
import streamlit as st

######### Function Definitions ####################################################################

def load_device_parameters(session_path, dev_par_file_name, default_path):
    """Load the device_parameters file and create a List object. Check if a session specific file already exists. 
    If True, use this one, else return to the default device_parameters

    Parameters
    ----------
    session_path : string
        Folder path of the current simulation session
    dev_par_file_name : string
        Name of the device parameters file
    default_path : string
        Path name where the default/standard device parameters file is located

    Returns
    -------
    List
        List with nested lists for all parameters in all sections.
    """
    if os.path.isfile(os.path.join(session_path, dev_par_file_name)):
        # Session specific parameter file
        with open(os.path.join(session_path, dev_par_file_name), encoding='utf-8') as fp:
            dev_par = devpar_read_from_txt(fp)
            fp.close()
    else:
        # Default parameter file, so copy it from the default folder.
        shutil.copy(os.path.join(default_path, dev_par_file_name), session_path)
        with open(default_path+dev_par_file_name, encoding='utf-8') as fp:
            dev_par = devpar_read_from_txt(fp)
            fp.close()

    return dev_par

def devpar_read_from_txt(fp):
    """Read the opened .txt file line by line and store all in the dev_par_object.

    Parameters
    ----------
    fp : TextIOWrapper
        filepointer to the opened .txt file.

    Returns
    -------
    List
        List with nested lists for all parameters in all sections.
    """
# Note:List object format (basic layout) Identical structure for all sections
#
# [
#     [
#         'Description',
#         ['comm', {comment1}],
#         ['comm', {comment2}],
#             ...
#     ],
#     [   'General',
#         ['par', {parameter_general_name1}, {parameter_general_value1}, {parameter_general_description1}],
#         ['par', {parameter_general_name2}, {parameter_general_value2}, {parameter_general_description2}],
#         ['comm', {comment_general_1}],
#         ...
#     ],
#     [   'Mobilities',
#         ...
#     ],
#     ...
# ]

    index = 0

    # Reserve the first element of the list for the top/header description
    dev_par_object = [['Description']]

    # All possible section headers
    section_list = ['General', 'Mobilities', 'Optics', 'Contacts', 'Transport layers', 'Ions', 'Generation and recombination',
                    'Trapping', 'Numerical Parameters', 'Voltage range of simulation', 'User interface']

    for line in fp:
        # Read all lines from the file
        if line.startswith('**'):
        # Left adjusted comment
            comm_line = line.replace('*', '').strip()
            if (comm_line in section_list):  # Does the line match a section name
                # New section, add element to the main list
                dev_par_object.append([comm_line])
                index += 1
            else:
                # A left-adjusted comment, add with 'comm' flag to current element
                dev_par_object[index].append(['comm', comm_line])
        elif line.strip() == '':
        # Empty line, ignore and do not add to dev_par_object
            continue
        else:
        # Line is either a parameter or leftover comment.
            par_line = line.split('*')
            if '=' in par_line[0]:  # Line contains a parameter
                par_split = par_line[0].split('=')
                par = ['par', par_split[0].strip(), par_split[1].strip(),par_line[1].strip()]
                dev_par_object[index].append(par)
            else:
                # leftover (*) comment. Add to the description of the last added parameter
                dev_par_object[index][-1][3] = dev_par_object[index][-1][3] + \
                    "*" + par_line[1].strip()
                
    return dev_par_object

def devpar_write_to_txt(dev_par_object):
    """Convert the List object into a single string. Formatted to the device_parameter definition

    Parameters
    ----------
    dev_par_object : List
        List object with all parameters and comments.

    Returns
    -------
    string
        Formatted string for the txt file
    """
    par_file = []  # Initialize List to hold all lines
    lmax = 0  # Max width of 'parameter = value' section, initialise with 0
    section_length_max = 84 # Number of characters in the section title

    # Description and Version
    for item in dev_par_object[0][1:]:
        # First element of the main object contains the top description lines. Skip very first element (Title).
        desc_line = "** " + item[1] + '\n'
        par_file.append(desc_line)

    # Determine max width of the 'parameter = value' section of the txt file to align properly.
    for sect_item in dev_par_object[1:]:
        # Loop over all sections
        for par_item in sect_item[1:]:
            # Loop over all parameters
            if par_item[0] == 'par':
                # Only real parameter entries need to be considered, characterised by the first list element being 'par'
                temp_string = par_item[1] + ' = ' + par_item[2]
                if len(temp_string) > lmax:
                    # Update maxlength if length of 'par = val' combination exceeds it.
                    lmax = len(temp_string)
    # Add 1 to max length to allow for a empty space between 'par=val' and description.
    lmax = lmax + 1

    # Read every entry of the Parameter List object and create a formatted line (string) for it. Append to string List par_file.
    for sect_element in dev_par_object[1:]:
        # Loop over all sections. Exclude the first (Description Title) element.

        ## Section
        # Start with a new line before each section name. Section title must be of format **title************...
        par_file.append('\n')
        sec_title = "**" + sect_element[0]
        sec_title_length = len(sec_title)
        sec_title = sec_title + "*" * \
            (section_length_max-sec_title_length) + '\n'
        par_file.append(sec_title)

        ## Parameters
        for par_element in sect_element:
            #  Loop over all elements in the section list, both parameters ('par') and comments ('comm')
            if par_element[0] == 'comm':
                # Create string for a left-justified comment and append to string List.
                par_line = '** ' + par_element[1] + '\n'
                par_file.append(par_line)
            elif par_element[0] == 'par':
                # Create string for a parameter. Format is par = val
                par_line = par_element[1] + ' = ' + par_element[2]
                par_line_length = len(par_line)
                # The string is filled with blank spaces until the max length is reached
                par_line = par_line + ' '*(lmax - par_line_length)
                # The description can be a multi-line description. The multiple lines are seperated by a '*'
                if '*' in par_element[3]:
                    # MultiLine description. Split it and first append the par=val line as normal
                    temp_desc = par_element[3].split('*')
                    par_line = par_line + '* ' + temp_desc[0] + '\n'
                    par_file.append(par_line)
                    for temp_desc_element in temp_desc[1:]:
                        #  For every extra comment line, fill left part of the line with empty characters and add comment/description as normal.
                        par_line = ' '*lmax + '* ' + temp_desc_element + '\n'
                        par_file.append(par_line)
                else:
                    # Single Line description. Add 'par=val' and comment/description together, seperated by a '*'
                    par_line = par_line + '* ' + par_element[3] + '\n'
                    par_file.append(par_line)

    # Join all individual strings/lines together
    par_file = ''.join(par_file)

    return par_file

def save_parameters(dev_par, session_path, dev_par_file):
    """Write device parameters to the txt file.

    Parameters
    ----------
    dev_par : List
        List object with all parameters and comments.
    session_path : string
        Folder path of the current simulation session
    defv_par_file : string
        name of the device parameters file
    """
    # Write the device parameter List object to a txt string.
    par_file = devpar_write_to_txt(dev_par)

    # Open the device_parameters file (in the id folder) and write content of par_file to it.
    with open(os.path.join(session_path, dev_par_file), 'w', encoding='utf-8') as fp_device_parameters:
        fp_device_parameters.write(par_file)
        fp_device_parameters.close()

def verify_devpar_file(data_devpar):
    """Verify the uploaded device parameters file. Compare it with the standard device parameter file. If it does not match, reject the upload.
    
    Parameters
    ----------
    data_devpar : List
        List object with all parameters and comments.

    Returns
    -------
    integer
        0 if file is valid. 1 if file is invalid
    string
        Message which, when file is invalid, states the reason including line numbers
    """   

    simss_path = st.session_state['resource_path'] # Path to default simss device parameters
    line_min = []
    line_min_default = []
    valid_upload = 1
    msg = ''

    ## Store the uploaded file with a random id in a temporary directory. 
    tmp_id = random.randint(0, 1e10)
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

    # Open and read the standard device parameters file
    with open(os.path.join(simss_path, st.session_state['simss_devpar_file']), encoding='utf-8') as fp:
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


