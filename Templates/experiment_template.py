"""Page title/description"""
######### Package Imports #########################################################################

## Import packages here

######### Function Definitions ####################################################################

## Define all functions. 
# Note: everything should be packed into functions and preferably subfunctions. 
# This allows for running the script both standalone and also as part of the The Shell.

def init_func(par1, par2, args):
    """ Example of a a subfunction of the script to perform some preprocessing of data and parameters.

    Parameters
    ----------
    par1 : _type_
        _description_
    par2 : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    # Function logic

    return 

def plot_func(par1, par2, args):
    """Function logic to make plots when running as a standalone script. 
    When running as part of The Shell, plotting functionality is initiated on the result page, 
    to allow for web specific components to be added and form the UI.

    Parameters
    ----------
    par1 : _type_
        _description_
    par2 : _type_
        _description_

    """

    # Plot logic
    # Standard function: utils/plot_functions -> plot_result(...): -- Make a plot for a (sub)set of parameters from a DataFrame

    return

def main_experiment_func(par1, par2, args):
    """Main function of the script. This function should contain all logic to setup and pre/post process the data/parameters and running the simulations, 
    but not anything related to plotting output. This function is called from other scripts/functions to 'perform the actual experiment/simulation'.
    All required input parameters must thus be defined as arguments. 
    
    This function should return either an exit code with message or the process result object with message. 

    Parameters
    ----------
    par1 : _type_
        _description_
    par2 : _type_
        _description_

    Returns
    -------
    CompletedProcess
        Output object of with returncode and console output of the simulation
    string
        Return message to display on the UI, for both success and failed
    List
        When extra result/output files are created (not standard to SIMsalabim) return their filenames in a List. If not, return an empty list
    """
    
    # Simulation logic + data preparation
    # Run SIMsalabim
    # Standard function (with error handling): utils/general -> run_simulation(...) -- Run the SIMsalabim simulation executable with...
    # Perform post data processing/calculations -> Store the results/processed data into a file

    # Create/Process output

    result = message = ''
    filenames = []
    return result, message, filenames


## Running the function as a standalone script
if __name__ == "__main__":
    # Define input parameters
    #   Experiment specific
    #   Simsalabim
    
    # Run the main function
    # result, message, filenames = main_experiment_func()

    # If needed, plot the output
    print('Done')