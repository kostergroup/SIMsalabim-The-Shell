import sys
import os
import subprocess
import shutil
import json,requests,zipfile,io
from packaging import version
from pathlib import Path

######### Parameter Definitions ###################################################################
cwd = Path.cwd()
folder_name = 'kostergroup-SIMsalabim-'
min_fpc_version = '3.2.0'

######### Function Definitions ####################################################################
def cmd_yes_no_question(question, default = "yes"):
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

def clear_current_working_directory(cwd, folder_name):
    # Clear the current working directory
    for dirpath, dirnames, files in os.walk(cwd):
        for dirname in dirnames:
            if dirname.startswith(folder_name):
                result = cmd_yes_no_question(f"Are you sure you want to overwrite the {dirname} folder?")
                if result == True:
                    shutil.rmtree(os.path.join(cwd,dirname))
                    print(f"Found and removed a folder named {dirname}")
                    return True
                elif result is False:
                    print(f"Not allowed to write into folder {dirname}")
                    return False
            else:
                # print(f"No folder found named SIMsalabim, continue.")
                return True

def get_SIMsalabim_source(cwd, folder_name):
    print("Getting the latest release from the Kostergroup Github")
    # Get the SIMsalabim source code.
    if os.path.exists(os.path.join(cwd, 'SIMsalabim')):
    # Pop out dialog box to confirm overwriting
        result = cmd_yes_no_question("Are you sure you want to overwrite the 'SIMsalabim' folder?")
        if result == True:
            # Remove folder
            shutil.rmtree(os.path.join(cwd, 'SIMsalabim'))

            # # Get the files from the latest release
            url = 'https://api.github.com/repos/kostergroup/SIMsalabim/zipball'
            response = requests.get(url)

            # Open the zip file
            z = zipfile.ZipFile(io.BytesIO(response.content))

            # Extract all the files
            z.extractall(path=cwd)

            for dirpath, dirnames, files in os.walk(cwd):
                for dirname in dirnames:
                    if dirname.startswith(folder_name):
                        # Rename folder
                        shutil.move(os.path.join(cwd, dirname), os.path.join(cwd, 'SIMsalabim'))
                        print("Got the latest release of SIMSalabim")
                        return 0
        else:
            print('We keep the current SIMsalabim version')
            return 0
    else:
        # # Get the files from the latest release
        url = 'https://api.github.com/repos/kostergroup/SIMsalabim/zipball'
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
                    shutil.move(os.path.join(cwd, dirname), os.path.join(cwd, 'SIMsalabim'))
                    print("Got the latest release of SIMSalabim")
                    return 0

def get_SIMsalabim_assets(cwd):
    print("Getting the latest compiled binaries from the Kostergroup Github")
    # Get the assets from the latest release
    url = "https://api.github.com/repos/kostergroup/SIMsalabim/releases/latest"
    response = requests.get(url)
    data = json.loads(response.text)

    for asset in data["assets"]:
        download_url = asset["browser_download_url"]
        filename = asset["name"]
        response = requests.get(download_url)
        open(os.path.join(cwd,filename), "wb").write(response.content)

    for dirpath, dirnames, files in os.walk(cwd):

        for filename in files:
            if filename.startswith('simss') and os.path.exists(os.path.join(cwd, filename)):
                print(f"Found a folder named {filename}")
                # Rename folder
                shutil.move(os.path.join(cwd, filename), os.path.join(cwd, 'SIMsalabim','SimSS',filename))
            elif filename.startswith('zimt') and os.path.exists(os.path.join(cwd, filename)):
                print(f"Found a folder named {filename}")
                # Rename folder
                shutil.move(os.path.join(cwd, filename), os.path.join(cwd, 'SIMsalabim','ZimT',filename))
            else:
                pass
    return 1

def use_SIMsalabim_source(cwd, folder_name):
    # Clear the working directory. TEMP disabled
    # result = clear_current_working_directory(cwd, folder_name)
    result = True
    if result == True:
        result_get = get_SIMsalabim_source(cwd, folder_name)
        return result_get
    elif result == False:
        print('Script terminated manually')
        return 3
    else: 
        print('Failed')
        return 2

######### Script ##################################################################################

# Check if fpc installed
print("Checking for Free Pascal Compiler (fpc) package")
if shutil.which("fpc") is not None:
    # fpc is installed, check the version and print to stdout.
    result = subprocess.run(["fpc", "-iV"], stdout=subprocess.PIPE, text=True)
    fpc_version = result.stdout

    # remove possible newline character
    if '\n' in fpc_version:
        fpc_version = fpc_version.strip('\n')

    # fpc version must be larger than min_fpc_version
    if version.parse(fpc_version) > version.parse(min_fpc_version):
        print(f'Free Pascal Compiler (fpc) is installed with version >= {min_fpc_version}\n')
        result_fpc = use_SIMsalabim_source(cwd, folder_name)
        sys.exit(result_fpc)
    else: 
        # fpc version requirement not met
        print(f'Installed Free Pascal Compiler (fpc) version is {fpc_version}, but must be at least 3.2.0\n')
        result = cmd_yes_no_question("Do you want to continue with the pre-compiled binaries (y) or abort and update the Free Pascal Compiler (n) (recommended)", 'no')
        if result is True:
            # download assets
            print("\ndownload assets")
            result_assets = get_SIMsalabim_assets(cwd)
            sys.exit(result_assets)
        elif result is False:
            # return and exit
            sys.exit(3)
else:
    # fpc is not installed.
    print("Free Pascal Compiler is not installed.\n")
    result = cmd_yes_no_question("Do you want to continue with the pre-compiled binaries (y) or abort and install the Free Pascal Compiler (n) (recommended)", 'no')
    if result is True:
        # download assets
        print("\ndownload assets")
        result_assets = get_SIMsalabim_assets(cwd)
        sys.exit(result_assets)
    elif result is False:
        # return and exit
        sys.exit(3)
