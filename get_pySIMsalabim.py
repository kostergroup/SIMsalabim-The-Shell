import sys, subprocess, shutil, os, requests, zipfile, io
from pathlib import Path

######### Parameter Definitions ###################################################################
cwd = Path.cwd()
folder_name = 'kostergroup-pySIMsalabim-'

###########Function Definitions ###################################################################
def cmd_yes_no_question(question, default = "yes"):
    """_summary_

    Parameters
    ----------
    question : str
        question to ask the user
    default : str, optional
        default answer, by default "yes"

    Returns
    -------
    bool
        whether the default answer is valid or not

    Raises
    ------
    ValueError
        If the default answer is not valid
    """    
    # valid answers (yes/no)
    valid = {'yes' : True, 'y': True, 'ye': True, 'no': False, 'n': False}
    # Set the default answer.
    if default is None:
        prompt = " [y/n] "
    elif default == 'yes':
        prompt = " [Y/n] "
    elif default == 'no':
        prompt = " [y/N] "
    else:
        raise ValueError(f"Invalid default answer: {default}\n")
    
    while True:
        # Capture user input
        sys.stdout.write(question + prompt)
        choice = input()
        # convert the input to lowercase
        choice = choice.lower()
        if default is not None and choice == "":
            # Use default value
            return valid[default]
        elif choice in valid:
            # Use user input
            return valid[choice]
        else:
            # Incorrect input
            sys.stdout.write('Please respond with "y" or "n"\n')

def get_pySIMsalabim_source(cwd, folder_name='kostergroup-pySIMsalabim-',verbose=False):
    """ Get the latest release from the Kostergroup Github

    Parameters
    ----------
    cwd : string
        Current working directory
    folder_name : string, optional
        Name of the folder to download, by default 'kostergroup-pySIMsalabim-'
    verbose : bool, optional
        Print verbose output, by default False

    Returns
    -------
    int

    0 : Success
    2 : Failed
    3 : Failed

    """    
    if verbose:
        print("Getting the latest release from the Kostergroup Github")
    # Get the SIMsalabim source code.
    if os.path.exists(os.path.join(cwd, 'pySIMsalabim')):
    # Pop out dialog box to confirm overwriting
        result = cmd_yes_no_question("Do you want to replace the existing pySIMsalabim folder?")
        if result == True:
            # Remove folder
            shutil.rmtree(os.path.join(cwd, 'pySIMsalabim'))

            # # Get the files from the latest release
            url = 'https://api.github.com/repos/kostergroup/pySIMsalabim/zipball'
            response = requests.get(url)
            # Open the zip file
            z = zipfile.ZipFile(io.BytesIO(response.content))

            # Extract all the files
            z.extractall(path=cwd)

            for dirpath, dirnames, files in os.walk(cwd):
                for dirname in dirnames:
                    if dirname.startswith(folder_name):
                        # Rename folder
                        shutil.move(os.path.join(cwd, dirname, 'pySIMsalabim'), os.path.join(cwd, 'pySIMsalabim'))
                        shutil.rmtree(os.path.join(cwd, dirname))
                        print("\nGot the latest release of pySIMsalabim")
                        return 0
        else:
            print('We keep the current pySIMsalabim version')
            return 0
    else:
        # # Get the files from the latest release
        url = 'https://api.github.com/repos/kostergroup/pySIMsalabim/zipball'
        response = requests.get(url)

        # Open the zip file
        z = zipfile.ZipFile(io.BytesIO(response.content))

        # Extract all the files
        z.extractall(path=cwd)

        for dirpath, dirnames, files in os.walk(cwd):
            for dirname in dirnames:
                if dirname.startswith(folder_name):
                    # print(f"Found a folder named {dirname}")
                    # Rename folder
                    shutil.move(os.path.join(cwd, dirname,'pySIMsalabim'), os.path.join(cwd, 'pySIMsalabim'))
                    shutil.rmtree(os.path.join(cwd, dirname))
                    print("\nGot the latest release of pySIMsalabim")
                    return 0

######### Script ##################################################################################

# Get pySIMsalabim source code
result_pySIMsalabim = get_pySIMsalabim_source(cwd, folder_name)
sys.exit(result_pySIMsalabim)