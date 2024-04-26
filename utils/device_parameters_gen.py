"""Functions for processing the device parameters"""
######### Package Imports #########################################################################

import os, shutil

######### Function Definitions ####################################################################

def load_device_parameters(session_path, dev_par_file_name, default_path=os.path.join('SIMsalabim', 'ZimT')):
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
