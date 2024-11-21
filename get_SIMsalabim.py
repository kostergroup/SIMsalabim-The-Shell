import sys, subprocess, shutil, os, requests, zipfile, io
from packaging import version
from pathlib import Path
import pySIMsalabim.install as utils_install

######### Parameter Definitions ###################################################################
cwd = Path.cwd()
folder_name = 'kostergroup-SIMsalabim-'
min_fpc_version = '3.2.0'

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

        result_fpc = utils_install.use_SIMsalabim_source(cwd, folder_name)
        sys.exit(result_fpc)
    else: 
        # fpc version requirement not met
        print(f'Installed Free Pascal Compiler (fpc) version is {fpc_version}, but must be at least 3.2.0\n')
        result = utils_install.cmd_yes_no_question("Do you want to continue with the pre-compiled binaries (y) or abort and update the Free Pascal Compiler (n) (recommended)", 'no')
        if result is True:
            # download assets
            print("\ndownload assets")

            # Get pySIMsalabim source code
            result_pySIMsalabim = get_pySIMsalabim_source(cwd, folder_name)

            result_assets = utils_install.get_SIMsalabim_assets(cwd)
            sys.exit(result_assets)
        elif result is False:
            # return and exit
            sys.exit(3)
else:
    # fpc is not installed.
    print("Free Pascal Compiler is not installed.\n")
    result = utils_install.cmd_yes_no_question("Do you want to continue with the pre-compiled binaries (y) or abort and install the Free Pascal Compiler (n) (recommended)", 'no')
    if result is True:
        # download assets
        print("\ndownload assets")

        # Get pySIMsalabim source code
        result_pySIMsalabim = get_pySIMsalabim_source(cwd, folder_name)

        result_assets = utils_install.get_SIMsalabim_assets(cwd)
        sys.exit(result_assets)
    elif result is False:
        # return and exit
        sys.exit(3)
