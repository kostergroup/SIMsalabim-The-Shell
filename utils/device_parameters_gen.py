"""Functions for processing the device parameters"""
######### Package Imports #########################################################################

import os, shutil, random

######### Function Definitions ####################################################################

def load_device_parameters(session_path, dev_par_file_name, default_path=os.path.join('SIMsalabim', 'ZimT'), reset = False, availLayers = []):
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
    reset : boolean
        If True, the default device parameters are copied to the session folder
    availLayers : List
        List with all the available layer files

    Returns
    -------
    List
        List with nested lists for all parameters in all sections.
    List
        List with all the layers
    """
    dev_par = {}
    # Check if the session specific device parameter file exists. If not, copy the default file to the session folder.
    if not os.path.isfile(os.path.join(session_path, dev_par_file_name)) or (reset == True):
        shutil.copy(os.path.join(default_path, dev_par_file_name), session_path) # The simulation_setup_file
        file_list = os.listdir(default_path)
        for file in file_list:
            if (file.endswith('_parameters.txt')):
                shutil.copy(os.path.join(default_path, file), session_path) # The layer files

    # Read the simulation_setup file and store all lines in a list
    with open(os.path.join(session_path, dev_par_file_name), encoding='utf-8') as fp:
        # First check how many layers are defined.
        layersSection = False
        layers = [['par', 'setup',dev_par_file_name,dev_par_file_name]] # Initialize the simulation setup file. This is identified by key 'setup'

        for line in fp:
            # Read all lines from the file
            if line.startswith('**'):
            # Left adjusted comment
                comm_line = line.replace('*', '').strip()
                if ('Layers' in comm_line):  # Found section with the layer files
                    layersSection = True
                else:
                    layersSection = False
            else:
                    # Line is either a parameter or leftover comment.
                par_line = line.split('*')
                if '=' in par_line[0]:  # Line contains a parameter
                    par_split = par_line[0].split('=')
                    par = ['par', par_split[0].strip(), par_split[1].strip(),par_line[1].strip()] # The element with index 2 contains the actual file name!
                    if layersSection: # If the line is in the layer section, it contains the name of a layer file, thus add it to the Layers list
                        layers.append(par) # Add sublist to the layers list 
        fp.close()

    # Read each layer file and append it as a sublist in the main dev_par list
    for layer in layers:
        with open(os.path.join(session_path, layer[2]), encoding='utf-8') as fp:
            dev_par[f'{layer[2]}'] = devpar_read_from_txt(fp)
            fp.close()
    
    # Now load the layer files that are not in the simulation_setup but have been defined or created before
    devLayerList = []
    for layer in layers:
        devLayerList.append(layer[2])

    extraLayers = []
    for layer in availLayers:
        if layer not in devLayerList:
            extraLayers.append(layer)

    # Read each extra layer file and append it as a sublist in the main dev_par list
    for layer in extraLayers:
        with open(os.path.join(session_path, layer), encoding='utf-8') as fp:
            dev_par[f'{layer}'] = devpar_read_from_txt(fp)
            fp.close()
    return dev_par, layers

def devpar_read_from_txt(fp):
    """Read the opened .txt file line by line and store all in a List.

    Parameters
    ----------
    fp : TextIOWrapper
        filepointer to the opened .txt file.

    Returns
    -------
    List
        List with nested lists for all parameters in all sections.
    """
    index = 0
    # Reserve the first element of the list for the top/header description
    dev_par_object = [['Description']]

    # All possible section headers
    section_list = ['General', 'Layers', 'Contacts', 'Optics', 'Numerical Parameters', 'Voltage range of simulation', 'User interface','Mobilities', 'Interface-layer-to-right', 'Ions', 'Generation and recombination', 'Bulk trapping']
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
    for layer in layers:
        par_file = devpar_write_to_txt(dev_par[layer[2]])
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
        tmp_devpar = devpar_read_from_txt(fp)

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