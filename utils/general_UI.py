"""Functions for general use, WEB only!"""
######### Package Imports #########################################################################

import os, re, shutil, zipfile
import streamlit as st
from datetime import datetime
from subprocess import run, PIPE
from pySIMsalabim.utils import device_parameters as utils_devpar
from utils import device_parameters_UI as utils_devpar_UI
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
        file_name = uploaded_file.name
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

def prepare_results_download(session_path, id_session, sim_type, exp_type):
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
        state the type of experiment run, to collect additional files, must be SS_JV, Transient_JV, Impedance, IMPS, or CV
    """

    if sim_type not in ('simss', 'zimt'):
        st.error('Wrong simulation type provided, must be either "simss" or "zimt"')
        return
        
    elif exp_type not in ('SS_JV', 'Transient_JV', 'Impedance', 'IMPS','CV'):
        st.error('Wrong experiment type provided, must be SS_JV, Transient_JV, Impedance, IMPS, or CV')
        return
    
    tmp_folder_path = os.path.join(session_path, 'tmp')
    # When a previous temp folder already exists remove it first.
    if os.path.exists(tmp_folder_path):
        shutil.rmtree(tmp_folder_path)
    # Create the temp folder inside the session folder
    os.makedirs(tmp_folder_path)

    # The relevant files for the simulation are selected by reading their corresponding session state variable. 
    # If not 'none' the file must be copied to the temp folder to be downloaded.
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


    # Simulation-specific files
    sim_files_map = {
        'simss': ['simss_devpar_file', 'JVFile', 'scParsFile', 'expJV'],
        'zimt': ['zimt_devpar_file', 'tJFile', 'tVGFile']}

    for key in sim_files_map.get(sim_type, []):
        value = state.get(key)
        if value and value != 'none':
            files_to_copy.add(value)

    # Experiment-specific files for ZimT
    if sim_type == 'zimt':
        exp_files_map = {
            'Transient_JV': ['transientPars'],
            'Impedance': ['impedancePars', 'freqZFile'],
            'IMPS': ['IMPSPars', 'freqYFile'],
            'CV': ['CVPars', 'CapVolFile']
        }
        for key in exp_files_map.get(exp_type, []):
            value = state.get(key)
            if value:
                files_to_copy.add(value)

        # Include experimental data if used
        if exp_type == 'Transient_JV' and state["expObject"].get('UseExpData') == 1:
            files_to_copy.update([
                state["expObject"].get('expJV_Vmin_Vmax'),
                state["expObject"].get('expJV_Vmax_Vmin')])

    # Copy main files
    for file in files_to_copy:
        src = os.path.join(session_path, file)
        if os.path.isfile(src):
            shutil.copy(src, tmp_folder_path)

    # When a calculated generation profile is used, retrieve the used nk data and spectrum files as well
    if state['genProfile'] == 'calc':
        for subdir in ['Data_nk', 'Data_spectrum']:
            src_dir = os.path.join(session_path, subdir)
            dst_dir = os.path.join(tmp_folder_path, subdir)
            os.makedirs(dst_dir, exist_ok=True)
            for file in os.listdir(src_dir):
                if os.path.join(subdir, file) in state['opticsFiles']:
                    shutil.copy(os.path.join(src_dir, file), dst_dir)

        # Create the summary and citation file
        utils_sum.create_summary_and_cite(tmp_folder_path, True)
    else:
        utils_sum.create_summary_and_cite(tmp_folder_path, False)

    # Create a ZIP file from the tmp results folder
    shutil.make_archive(f'simulation_results_{id_session}','zip', tmp_folder_path)
    zip_file_name = f'simulation_results_{id_session}.zip'

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


def safe_index(value, options, default=0, strip_prefixes=('../',)):
    """Return a safe index of value in options.
    Attempts (in order): exact match, stripped prefixes, basename match. Returns default when no match is found.

    Parameters
    ----------
    value: str
        the value to look up
    options: list 
        list of option strings
    default: int 
        value to return when not found
    strip_prefixes: tuple 
        prefixes to strip from value before matching

    Returns
    -------
    int
        index of value in options, or default
    """
    try:
        # exact match
        if value in options:
            return options.index(value)
    except Exception:
        # if options is not a sequence or similar error, fall back
        return default

    # try stripping known prefixes
    if isinstance(value, str):
        v = value
        for p in strip_prefixes:
            if v.startswith(p):
                v = v[len(p):]
        if v in options:
            return options.index(v)

    # try basename match
    try:
        basename = os.path.basename(value)
        for i, opt in enumerate(options):
            if os.path.basename(opt) == basename:
                return i
    except Exception:
        pass

    return default


def save_parameters(dev_par, layers, session_path, dev_par_file, exchange_target=None, show_toast=False):
    """Save device parameters and update the other devpar file.

    Parameters
    ----------
    dev_par : List
        Device parameters as a list of nested lists
    layers : List
        List with all layers in the device.
    session_path : string
        Path to the session folder
    dev_par_file : string
        Name of the device parameters file to save
    exchange_target : string, optional
        Name of the paired device parameters file to update, by default None
    show_toast : bool, optional
        Whether to show a toast notification when saving is complete, by default False

    Returns
    -------
    None
    """

    layersAvail = [dev_par_file]
    layersAvail.extend(st.session_state['availableLayerFiles'])
    # Delegate to the existing device-parameters writer
    utils_devpar_UI.write_pars_txt(dev_par, layers, session_path, dev_par_file)

    # Keep the paired device-parameters file in sync when requested
    if exchange_target:
        try:
            exchangeDevPar(session_path, dev_par_file, exchange_target)
        except Exception:
            # Non-fatal; the exchange step is best-effort
            pass

    if show_toast:
        st.toast('Saved device parameters', icon='✔️')

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

def prepare_results(session_path, id_session, sim_type, exp_type):
    """Create a ZIP file with the relevant results.Update the session state variable to show/hide the download button when preparing is complete
    Show a spinner icon, to indicate that the process is running.
    Parameters
    ----------
    session_path : string
        Path to folder with the simulation results
    id_session : string
        Current session id
    sim_type : string
        Type of simulation, either 'simss' or 'zimt'
    """
    # Because this can take sme time show a spinner to indicate that something is being done and the program did not freeze
    with st.spinner('Preparing results...'):
            prepare_results_download(session_path, id_session, sim_type, exp_type) # Will check whether sim_type and exp_type are part of the defined list
    st.session_state['runSimulation'] = False