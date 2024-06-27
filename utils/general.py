"""Functions for general use"""
######### Package Imports #########################################################################

import os, zipfile
from subprocess import run, PIPE
from datetime import datetime

######### Function Definitions ####################################################################

def fatal_error_message(errorcode):
    """When a 'standard Pascal' fatal error occurs, add the standard error message

    Parameters
    ----------
    errorcode : int
        the error code
    """
    message = ''
    if errorcode == 106:
        message = 'Invalid numeric format: Reported when a non-numeric value is read from a text file'
    elif errorcode == 200:
        message = 'Division by zero: The application attempted to divide a number by zero.'
    elif errorcode == 201:
        message = 'Range check error.'
    elif errorcode == 202:
        message = 'Stack overflow error: This error is only reported when stack checking is enabled.'
    elif errorcode == 205:
        message = 'Floating point overflow.'
    elif errorcode == 206:
        message = 'Floating point underflow.'
    else:
        message = 'A fatal error occured.'
    return message

def construct_cmd(type, cmd_pars):
    """Construct a single string to use as command to run a SIMsalabim executable

    Parameters
    ----------
    type : string
        Which program to run: simss or zimt
    cmd_pars : List
        List with parameters to add to the simss/zimt cmd line. Each parameter is a dict with par,val keys. 
        Note: when relevant the first entry must be the deviceparameters file with a key: dev_par_file

    Returns
    -------
    string
        Constructed string to run as cmd
    """
    # Start with the executable name
    cmd_line = './' + type

    # Check whether a device parameters file has been defined
    for i in cmd_pars:
        # When specified, the device parameter file must be placed first, as is required by SIMsalabim
        if i['par'] == 'dev_par_file':
            args_single = ' ' + i['val']
            cmd_line = cmd_line + args_single
            # After the dev_par_file key had been found once, stop the loop. If more than one dev_par_file is specified, the rest are ignored.
            break

    # Add the parameters
    for i in cmd_pars:
        if i['par'] != 'dev_par_file':
            # Add each parameter as " -par_name par_value"
            args_single = ' -' +i['par'] + ' ' + i['val']
            cmd_line = cmd_line + args_single

    return cmd_line

def run_simulation(type, cmd_pars, session_path, run_mode = False):
    """Run the SIMsalabim simulation executable with the chosen device parameters. 
        Return the complete result object of the process accompanied by a message with information, 
        in case of both success and failure.

    Parameters
    ----------
    type : string
        Which type of simulation to run: simss or zimt
    cmd_pars : List
        List with parameters to add to the simss/zimt cmd line. Each parameter is a dict with par,val keys. 
        Note: when relevant the first entry must be the deviceparameters file with a key: dev_par_file
    session_path : string
        File path of the simss or zimt executable 
    run_mode : boolean
        True if function is called as part of The Shell, False when called directly. 
        Prevents using streamlit components outside of The Shell.

    Returns
    -------
    CompletedProcess
        Output object of with returncode and console output of the simulation
    string
        Return message to display on the UI, for both success and failed
    """
    # Construct the command to run the executable
    cmd_line = construct_cmd(type, cmd_pars)

    if run_mode:
        result = run([cmd_line], cwd=session_path, stdout=PIPE, check=False, shell=True)
    

        # Check the results of the process using the returncodes and console output
        if result.returncode != 0 and result.returncode != 95 and result.returncode != 3:
            # SIMsalabim raised an error, stop the program and return the error message on the UI.
            startMessage = False
            message = ''
            result_decode = result.stdout.decode('utf-8')

            if result.returncode >= 100:
                # A fatal (numerical) error occurred. Return errorcode and a standard error message.
                message = fatal_error_message(result.returncode)
            else:
                # Simsalabim raised an error. Read the console output for the details / error messaging. 
                # All linetypes after 'Program will be terminated, press enter.' are considered part of the error message
                for line_console in result_decode.split('\n'):
                    if startMessage is True:
                        # The actual error message. Since the error message can be multi-line, append each line.
                        message = message + line_console + '\n'
                    if 'Program will be terminated.' in line_console:
                        # Last 'regular' line of the console output. The next line is from the error message.
                        startMessage = True

            # Show the message as an error on the screen. Do not continue to the simulation results page.
            message = 'Simulation raised an error with Errorcode: ' + str(result.returncode) + '\n\n' + message
        else:
            # SIMsalabim simulation succeeded
            if result.returncode == 95:
                # In case of errorcode 95, failures during the simulations were encountered but the simulation did not halt. Show 'error' messages on the UI.
                startMessage = False
                message = ''
                result_decode = result.stdout.decode('utf-8')
                for line_console in result_decode.split('\n'):
                    if startMessage is True:
                        # The actual error message. Since the error message can be multi-line, append each line.
                        message = message + line_console + '\n'
                    if 'Program will be terminated.' in line_console:
                        # Last 'regular' line of the console output. The next line is from the error message.
                        startMessage = True

                # Show the message as a success on the screen
                message = 'Simulation completed but raised errorcode: ' + str(result.returncode) + '\n\n' + 'The simulation finished but at least 1 point did not converge. \n\n' + message
            elif result.returncode == 3:
                # Special case, should not occur in the web version.
                # When the program exits as a success but no simulation has been run, e.g. in the case of the autotidy functionality. 
                message = 'Action completed'
            else:
                # Simulation completed as expected.
                message = 'Simulation complete. Output can be found in the Simulation results.'
    else:
        result = run([cmd_line], cwd=session_path, check=False, shell=True)
        message = ''
        
    return result, message

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
