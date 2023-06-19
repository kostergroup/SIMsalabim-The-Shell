"""Perform JV hysteresis simulations"""
######### Package Imports #########################################################################

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import general as utils_gen
from utils import plot_functions_gen as utils_plot_gen

######### Function Definitions ####################################################################

def build_tVG_arrays(t,tmax, V,G, scan_speed, V1, V2, Genrate, sign):
    """Build the Arrays for voltage and Generation rate for a hysteresis experiment.

    Parameters
    ----------
    t : array
        Array with all time positions, from 0 to tmax
    tmax : float
        Last time point
    V : array
        Array to store voltages
    G : array
        Array to store generation rate
    scan_speed : float
        Voltage scan speed [V/s]
    V1 : float
        Left voltage boundary
    V2 : float
        Right voltage boundary
    Genrate : float
        Generation rate
    sign : integer
        Indicator to swap the sign for either s forward-backward or s backward-forward scan

    Returns
    -------
    array,array
        Filled V, G arrays
    """
    for i in t:
        if i < tmax:
            # First  voltage sweep
            V.append(sign*scan_speed*i + V1)
        else: 
            # Second voltage sweep
            V.append(-sign*scan_speed*(i-tmax) + V2)
        # Append the generation rate
        G.append(Genrate)
    return V,G

def create_tVG(Vmin,Vmax,scan_speed, direction, steps, gen_profile, gen_rate, tVG_name, session_path):
    """Create a tVG file for hysteresis experiments. 

    Parameters
    ----------
    Vmin : float 
        Left voltage boundary
    Vmax : float
        Right voltage boundary
    scan_speed : float
        Voltage scan speed [V/s]
    direction : integer
        Perform a forward-backward (1) or backward-forward scan (-1). 
    steps : integer
        Number of time steps
    gen_profile : string
        Indicator for type of generation profile to set the correct header in the tVG file
    gen_rate : float
        Generation rate
    tVG_name : string
        Name of the tVG file

    Returns
    -------
    string
        A message to indicate the result of the process
    """
    V,G = [],[]

    # Determine max time point
    tmax = abs((Vmax - Vmin)/scan_speed)

    # Create two arrays for both time sweeps
    t_min_to_max = np.linspace(0,tmax,int(steps/2))
    t_max_to_min = np.linspace(tmax,2*tmax,int(steps/2))

    t_max_to_min = np.delete(t_max_to_min,[0]) # remove double entry
    t = np.append(t_min_to_max,t_max_to_min)

    # Create V,G arrays for both sweep directions
    if direction == 1:
        # forward -> backward
        V,G = build_tVG_arrays(t, tmax, V,G, scan_speed, Vmin, Vmax, gen_rate, direction)
    elif direction == -1:
        # backward -> forward
        V,G = build_tVG_arrays(t, tmax, V,G, scan_speed, Vmax, Vmin, gen_rate, direction)
    else:
        # Illegal value for direction given
        msg = 'Incorrect scan direction, choose either 1 for a forward - backward scan or -1 for a backward - forward scan'
        retval = 1
        return retval, msg
   
    # Set the correct header for the tVG file based on the gen_profile parameter
    if gen_profile == 'calc':
        tVG_header = ['t','Vext','Gfrac']
    else :
        tVG_header = ['t','Vext','Gehp']

    # Combine t,V,G arrays into a DataFrame
    tVG = pd.DataFrame(np.stack([t,np.asarray(V),np.asarray(G)]).T,columns=tVG_header)

    # Create tVG file
    tVG.to_csv(os.path.join(session_path,tVG_name),sep=' ',index=False,float_format='%.3e')

    # tVG file is created, msg a success
    msg = 'Success'
    retval = 0
    return retval, msg

def plot_hysteresis_JV():
    """Plot the hysteresis JV curve
    """
    # Read the data from tj-file
    data_tj = pd.read_csv(os.path.join(session_path,'tj.dat'), delim_whitespace=True)
    
    fig, ax = plt.subplots()
    pars = {'Jext' : '$J_{ext}$'}
    par_x = 'Vext'
    xlabel = '$V_{ext}$ [V]'
    ylabel = 'Current density [Am$^{-2}$]'
    yscale = 'linear'
    title = 'JV curve'
    plot_type = plt.plot
    ax = utils_plot_gen.plot_result(data_tj, pars, list(pars.keys()), par_x, xlabel, ylabel, yscale, title, ax, plot_type)
    plt.show()


def Hysteresis_JV(zimt_device_parameters, session_path,Vmin, Vmax, scan_speed, direction, steps, gen_profile, gen_rate, file_name, run_mode=False):
    """Create a tVG file and perform a JV hysteresis experiment.

    Parameters
    ----------
    zimt_device_parameters : string
        name of the zimt device parmaeters file
    session_path : string
        working directory for zimt
    VVmin : float 
        Left voltage boundary
    Vmax : float
        Right voltage boundary
    scan_speed : float
        Voltage scan speed [V/s]
    direction : integer
        Perform a forward-backward (1) or backward-forward scan (-1). 
    steps : integer
        Number of time steps
    gen_profile : string
        Device Parameter | Indicator for type of generation profile to set the correct header in the tVG file
    gen_rate : float
        Device Parameter | Generation rate
    file_name : string
        Device Parameter | Name of the tVG file
    run_mode : bool, optional
        indicate whether the script is in 'web' mode (True) or standalone mode (False). Used to control the console output, by default False

    Returns
    -------
    CompletedProcess
        Output object of with returncode and console output of the simulation
    string
        Return message to display on the UI, for both success and failed
    """
    # Create tVG
    result, message = create_tVG(Vmin, Vmax, scan_speed, direction, steps, gen_profile, gen_rate, file_name, session_path)

    if result == 0:
        # tVG file created
        Hysteresis_JV_args = [{'par':'dev_par_file','val':zimt_device_parameters}]
        result, message = utils_gen.run_simulation('zimt', Hysteresis_JV_args, session_path, run_mode)

    return result, message

## Running the function as a standalone script
if __name__ == "__main__":
    # Hysteresis input parameters
    Vmin = 0
    Vmax = 1.15
    scan_speed = 5e-1
    gen_rate = 1
    gen_profile = 'calc'
    steps = 1e3
    file_name = 'tVG.txt'
    direction = 1

    # SIMsalabim input parameters
    zimt_device_parameters = os.path.join('device_parameters_zimt.txt')
    session_path = 'tmp_zimt'

    result, message = Hysteresis_JV(zimt_device_parameters, session_path, Vmin, Vmax, scan_speed, direction, steps, gen_profile, gen_rate, file_name)
    
    plot_hysteresis_JV()
