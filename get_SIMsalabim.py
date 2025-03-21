import sys, subprocess, shutil
from packaging import version
from pathlib import Path
import pySIMsalabim.install as utils_install

######### Parameter Definitions ###################################################################
cwd = Path.cwd()
folder_name = 'kostergroup-SIMsalabim-'
min_fpc_version = '3.2.0'

###########Function Definitions ###################################################################
def get_pySIMsalabim_source(cwd, folder_name='kostergroup-SIMsalabim-',verbose=False):
    """ Get the latest release from the Kostergroup Github
    
    Parameters
    ----------
    cwd : Path
        Current working directory
    folder_name : str, optional
        Folder name for the download, by default 'kostergroup-SIMsalabim-'
    verbose : bool, optional
        Print verbose output, by default False

    Returns
    -------
    int
        Return code
        0 : Success
        1 : Success
        2 : Failed
        3 : Failed
    """

    # Check if fpc installed
    if verbose:
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
            if verbose:
                print(f'Free Pascal Compiler (fpc) is installed with version >= {min_fpc_version}\n')

            result_fpc = utils_install.use_SIMsalabim_source(cwd, folder_name)
            return result_fpc
        else: 
            # fpc version requirement not met
            print(f'Installed Free Pascal Compiler (fpc) version is {fpc_version}, but must be at least 3.2.0\n')
            result = utils_install.cmd_yes_no_question("Do you want to continue with the pre-compiled binaries (y) or abort and update the Free Pascal Compiler (n)", 'no')
            if result is True:
                # download assets
                print("\ndownload assets")

                result_assets = utils_install.get_SIMsalabim_assets(cwd)
                return result_assets
            elif result is False:
                # return and exit
                return 3
    else:
        # fpc is not installed.
        print("Free Pascal Compiler is not installed.\n")
        result = utils_install.cmd_yes_no_question("Do you want to continue with the pre-compiled binaries (y) or abort and install the Free Pascal Compiler (n)", 'no')
        if result is True:
            # download assets
            print("\ndownload assets")

            result_assets = utils_install.get_SIMsalabim_assets(cwd)
            return result_assets
        elif result is False:
            # return and exit
            return 3

######### Script ##################################################################################

if __name__ == "__main__":
    # Get SIMsalabim source code
    result_SIMsalabim = get_pySIMsalabim_source(cwd, folder_name)
    sys.exit(result_SIMsalabim)
