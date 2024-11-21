"""Functions for general use, WEB only!"""
######### Package Imports #########################################################################

import os, re, shutil, zipfile
import streamlit as st
from datetime import datetime
from werkzeug.utils import secure_filename
from subprocess import run, PIPE
from pySIMsalabim.utils import device_parameters as utils_devpar
from utils import summary_and_citation as utils_sum

######### Function Definitions ####################################################################

def local_css(file_name):
    """Load a custom CSS file and add it to the application

    Parameters
    ----------
    file_name : string
        path to the CSS file
    """

    with open(file_name, encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def upload_file(file_desc, ill_chars, pattern, check_devpar='', nk_file_list = [], spectrum_file_list= []):
    """Upload a txt file to the Simulation folder

    Parameters
    ----------
    file_desc : string
        Text to show on upload button
    ill_chars : List
        List of illegal characters in the file. Characters as strings
    pattern : string
        Regex expression which each line must match
    check_devpar : Boolean, optional
        Check a simss or zimt file when uploading a device parameters file, by default ''
    nk_file_list : List, optional
        List with the available nk files, by default []
    spectrum_file_list : List, optional
        List with the available spectrum files, by default []

    Returns
    -------
    UploadedFile | Boolean
        When upload is succesfull (in memory), return the uploaded object. If failed, return False
    """
    # File upload component. Only accept txt files and one file at a time. 
    uploaded_file = st.file_uploader(file_desc, type=['txt'], accept_multiple_files=False, label_visibility='visible')
    if uploaded_file is not None:
        data = uploaded_file.getvalue().decode('utf-8')
        # Basic validation of the uploaded file:
        # - Illegal characters
        # - File pattern
        # - Filename length
        chk_chars = 0
        msg_chars = ''
        chk_pattern = 0
        msg_pattern = ''
        chk_filename = 0
        msg_filename = ''
        chk_devpar_file = 0
        msg_devpar = ''

        # Illegal characters
        if len(ill_chars) > 0:
            for ill_char in ill_chars:
                if ill_char in data:
                    chk_chars = 1
                    msg_chars = "Illegal characters " + ill_char + " used. \n"

        # File pattern
        if pattern != '':
            data = data.splitlines()
            pattern_re = re.compile(pattern)
            for line in data[1:]:
                if not pattern_re.match(line):
                    chk_pattern = 1
                    msg_pattern = 'File content does not meet the required pattern. \n'

        # Filename lengthand secure the filename.
        file_name = secure_filename(uploaded_file.name)
        if len(file_name) > 50:
            print('filename too long. Max 50 characters')
            chk_filename = 1
            msg_filename = 'Filename is too long. Max 50 characters'

        if check_devpar == 'simss' or check_devpar == 'zimt':  # Check if a device parameters file has the correct structure. Only when uploading a device parameters file.
            chk_devpar_file, msg_devpar = utils_devpar.verify_devpar_file(data, check_devpar, nk_file_list, spectrum_file_list)

        if chk_chars + chk_pattern + chk_filename == 0:
            if chk_devpar_file ==1:
                # Error found in the devpar file, do not continue with uplaoding the file
                st.error(msg_devpar)
                st.markdown('<hr>', unsafe_allow_html=True)
                return False
            elif chk_devpar_file == 2:
                # Cannot find the nk/spectrum files from the uplaoded device parameter file. Continue the upload but show a warning
                msg_devpar_2 = msg_devpar[0]
                for msg in msg_devpar[1:]:
                    # Files not found have been stored into a List
                    msg_devpar_2 = msg_devpar_2 + '- ' + msg + '\n'
                st.warning(msg_devpar_2)
                return uploaded_file
            else:
                # All checks passed, allow upload
                return uploaded_file
        else:
            # One or more of the standard checks failed. Do not allow upload and show error message
            st.error(msg_chars + msg_pattern + msg_filename)
            st.markdown('<hr>', unsafe_allow_html=True)
            return False

def prepare_results_download(session_path, id_session, sim_type, exp_type=''):
    """Gather all the relevant files for the simulation and store them into a tmp directory to ZIP them. 
    Whether a file is needed is determined btVG.txtased on the state parameter, which has been set when running a simulation.

    Parameters
    ----------
    session_path : string
        File path of the current simulation, including id
    id_session : string
        session id, to create a unique name for the ZIP archive
    sim_type : string
        which simulation has been run, either 'simss' or 'zimt'
    exp_type : str, optional
        state the type of experiment run, to collect additional files, by default ''
    """
    # When a previous temp folder already exists remove it first.
    if os.path.exists(os.path.join(session_path, 'tmp')):
        shutil.rmtree(os.path.join(session_path, 'tmp'))

    # Create the temp folder inside the session folder
    os.makedirs(os.path.join(session_path, 'tmp'))

    # The relevant files for the simulation are selected by reading their corresponding session state variable. 
    # If not 'none' the file must be copied to the temp folder to be downloaded. # Can probably be done in s smarter/faster way?
    target_path = os.path.join(session_path, 'tmp')
    state = st.session_state

    # Files to copy based on conditions
    files_to_copy = {
        state['varFile'], 
        state['logFile'], 
        *state['traps_bulk'], 
        *state['traps_int'], 
        *state['LayersFiles']
    }

    # Only applicable when uploaded generation profile has been used
    if state['genProfile'] not in {'none', 'calc'}:
        files_to_copy.add(state['genProfile'])

    # SimSS specific files
    if sim_type == 'simss':
        files_to_copy.update({
            state['simss_devpar_file'], 
            state['JVFile'], 
            state['scParsFile']
        })
        if state['expJV'] != 'none':
            files_to_copy.add(state['expJV'])

    # ZimT specific files (including experiments)
    if sim_type == 'zimt':
        files_to_copy.update({
            state['zimt_devpar_file'], 
            state['tJFile'], 
            state['tVGFile']
        })
        if exp_type == 'hysteresis':
            files_to_copy.add(state['hystPars'])
            if state["expObject"]['UseExpData'] == 1:
                files_to_copy.update({
                    state["expObject"]['expJV_Vmin_Vmax'], 
                    state["expObject"]['expJV_Vmax_Vmin']
                })
        if exp_type == 'impedance':
            files_to_copy.update({
                state['impedancePars'], 
                state['freqZFile']
            })
        if exp_type == 'imps':
            files_to_copy.update({
                state['IMPSPars'], 
                state['freqYFile']
            })
        if exp_type == 'CV':
            files_to_copy.update({
                state['CVPars'], 
                state['CapVolFile']
            })

    # Walk through the directory and copy files
    for dirpath, dirnames, files in os.walk(session_path):
        for file in files:
            if file in files_to_copy:
                shutil.copy(os.path.join(session_path, file), target_path)

    # When a calculated generation profile is used, retrieve the used nk data and spectrum files as well
    if st.session_state['genProfile'] == 'calc':
        # Create sub-directories to store the files
        os.makedirs(os.path.join(session_path,'tmp','Data_nk'))
        os.makedirs(os.path.join(session_path,'tmp','Data_spectrum'))

        # nk files
        for dirpath, dirnames, files in os.walk(os.path.join(session_path, 'Data_nk')):
            for file in files:
                if os.path.join('Data_nk',file) in st.session_state['opticsFiles']:
                    shutil.copy(os.path.join(session_path, 'Data_nk', file),os.path.join(session_path,'tmp','Data_nk'))

        # spectrum file
        for dirpath, dirnames, files in os.walk(os.path.join(session_path, 'Data_spectrum')):
            for file in files:
                if os.path.join('Data_spectrum',file) in st.session_state['opticsFiles']:
                    shutil.copy(os.path.join(session_path, 'Data_spectrum', file),os.path.join(session_path,'tmp','Data_spectrum'))


    # Create the summary and citation file
    if st.session_state['genProfile'] == 'calc':
        utils_sum.create_summary_and_cite(os.path.join(session_path,'tmp'),True)
    else:
        utils_sum.create_summary_and_cite(os.path.join(session_path,'tmp'),False)

    # Create a ZIP file from the tmp results folder
    shutil.make_archive('simulation_results_' + id_session, 'zip', os.path.join(session_path, 'tmp'))
    zip_file_name = 'simulation_results_' + id_session + '.zip'

    # If the ZIP archive already exists for this id in the Simulations folder, remove it first.
    if os.path.isfile(os.path.join('Simulations', zip_file_name)):
        os.remove(os.path.join('Simulations', zip_file_name))

    # Copy the ZIP file to the 'main' simulations folder
    shutil.move(zip_file_name, 'Simulations/')

def exchangeDevPar(session_path, source , target):
    """Exchanges the device parameters (SimSS, ZimT) of source to target using the exchangeDevPar executable.

    Parameters
    ----------
    session_path : string
        path to the current session folder, where device parameter files are located
    source : string
        source file name
    target : string
        target file name

    Returns
    -------
    integer
        the returncode of the exchangedevpar executable
    """   
    
    result = run(['./exchangeDevPar', source, target], cwd=session_path, stdout=PIPE, check=False)
    return result.returncode

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

def create_zip(session_path, layers):
    """ Create a ZIP archive from a list of filenames

    Parameters
    ----------
    session_path : string
        path to the current session folder, where device parameter files are located
    layers : List
        List with all filenames/paths to be zipped, to be extracted from the layer object

    Returns
    -------
    string
        Filename of the ZIP archive
    """

    # Read all the file names to be zipped
    files = []
    for layer in layers:
        # Check if a layer file is already added, as they can be reused for different layers. If so, there is no need in including it twice in the ZIP archive
        if not os.path.join(session_path,layer[2]) in files:
            files.append(os.path.join(session_path,layer[2]))

    # Fixed name for the ZIP archive
    zip_filename = os.path.join(session_path, 'Device_parameters.zip')

    # Store the current date & time for the archive
    current_datetime = datetime.now().timetuple()[:6]

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        dir_name = 'Device_parameters' #Name of the subfolder in ZIP archive
        # get the current date and time to set the correct modified date for the subfolder, would otherwise be 01-01-1970 00:00
        info = zipfile.ZipInfo(f'{dir_name}/')
        info.date_time = current_datetime
        zipf.writestr(info, '')

        for file in files:
            zipf.write(file, arcname=os.path.join(dir_name,os.path.basename(file)))

    return zip_filename