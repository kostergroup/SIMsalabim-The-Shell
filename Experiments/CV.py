"""Perform capacitance simulations"""
######### Package Imports #########################################################################

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import scipy.integrate

from utils import general as utils_gen
from utils import plot_functions_gen as utils_plot_gen

######### Function Definitions ####################################################################

def create_tVG(V_0, V_max, del_V, V_step, G_frac, tVG_name, session_path, freq, ini_timeFactor, timeFactor):
    """Create a tVG file for capacitance experiment. 

    Parameters
    ----------
    V_0 : float
        Initial voltage
    V_max : float
        Maximum voltage
    del_V : float
        Voltage step that is applied directly after t=0
    V_step : float
        Voltage difference, determines at which voltages the capacitance is determined
    G_frac : float
        Fractional light intensity
    tVG_name : string
        Name of the tVG file
    session_path : string
        Path of the simulation folder for this session
    freq : float
        Frequency at which the capacitance-voltage measurement is performed
    ini_timeFactor : float
        Constant defining the size of the initial timestep
    timeFactor : float
        Exponential increase of the timestep, to reduce the amount of timepoints necessary. Use values close to 1.

    Returns
    -------
    string
        A message to indicate the result of the process
    """        

    # Starting line of the tVG file: header + datapoints at time=0. Set the correct header
    tVG_lines = 't Vext G_frac\n'

    # Loop until V reaches V_max, in other words go from Vmin to Vmax with in V_step steps. Add some extra margin on the Vmax to prevent missing the last voltage point due to numerical accuracy.
    while V_0 <= V_max + V_max*1E-5:
        time = 0
        del_t = ini_timeFactor/freq
        tVG_lines += f'{time:.3e} {V_0:.3e} {G_frac:.3e}\n'
        
        # Make the other lines in the tVG file
        while time < 1/freq: #max time: 1/f_min is enough!
            time += del_t
            del_t = del_t * timeFactor
            tVG_lines += f'{time:.3e} {V_0+del_V:.3e} {G_frac:.3e}\n'
    
        V_0 += V_step

    # Write the tVG lines to the tVG file
    with open(os.path.join(session_path,tVG_name), 'w') as file:
        file.write(tVG_lines)

    # tVG file is created, message a success
    msg = 'Success'
    retval = 0

    return retval, msg

def read_tj_file(session_path, tj_file_name='tj.dat'):
    """ Read relevant parameters for capacitance of the tj file

    Parameters
    ----------
    session_path : string
        Path of the simulation folder for this session
    data_tj : dataFrame
        Pandas dataFrame containing the tj output file from ZimT

    Returns
    -------
    DataFrame
        Pandas dataFrame containing among others the time, voltage, current density and numerical error in the current density of the tj_file
    """

    data = pd.read_csv(os.path.join(session_path,tj_file_name), sep=r'\s+')

    return data

def calc_capacitance_forOneVoltage(I, errI, time, VStep, freq):
    """Fourier Decomposition formula which computes the capacitance at frequency freq (Hz) and its complex error
    Based on S.E. Laux, IEEE Trans. Electron Dev. 32 (10), 2028 (1985), eq. 5b
    We integrate from 0 to time[imax] at frequency 1/time[imax]

    Parameters
    ----------
    I : np.array
        Array of currents
    errI : np.array
        Numerical error in calculated currents (output of ZimT)
    time : np.array
        Array with all time positions, from 0 to tmax
    VStep : float
        Voltage step
    imax : integer
        Index of the last timestep/first frequency for which the integrals are calculated

    Returns
    -------
    float
        Capacitance at frequency f: C(f)
    float
        Numerical error in calculated capacitance
    """

    imax = len(I)
    Iinf = I[imax-1] # I at infinite time, i.e. the last one we have.
	
    #prepare array for integrants:
    int2 = np.empty(imax)
    int4 = np.empty(imax)
	
    for i in range(imax):
        cosfac = math.cos(2*math.pi*freq*time[i])
        int2[i] = cosfac*(I[i] - Iinf)	
        int4[i] = cosfac*(I[i] + errI[i] - Iinf - errI[imax-1])	

    #Compute the capacitance:
    cap = scipy.integrate.trapezoid(int2, time)/VStep
	
    #and again, but now with the error added to the current:	
    capErr = scipy.integrate.trapezoid(int4, time)/VStep

    # error is the difference between cap and capPlusErr:
    errC = abs( cap - capErr )

    #now return capacitance, its error and the corresponding frequency:	
    return cap, errC

def calc_capacitance(data, del_V, freq):
    """ Calculate the capacitance over the time range
    
    Parameters
    ----------
    data : dataFrame
        Pandas dataFrame containing the time, voltage, current density and numerical error in the current density of the tj_file
    del_V : float
        Voltage step that is applied directly after t=0
    freq : float
        Frequency at which the capacitance-voltage measurement is performed

    Returns
    -------
    np.array
        Array of the capacitance
    np.array
        Array of the capacitance error
    """
       
    idx_time_zero = data.index[data['t'] == 0] # Find all indices where time is equal to 0
    amountOfVoltagePoints = len(idx_time_zero)
    
    # Prepare array for capacitance & its error:
    cap = np.empty(amountOfVoltagePoints)
    errC = np.empty(amountOfVoltagePoints)

    # Get the capacitance for each voltage step by taking the Fourier Transform over the t & I arrays
    for i in range(amountOfVoltagePoints-1):
        start_idx = idx_time_zero[i]
        end_idx = idx_time_zero[i+1]-1
                
        Jext_subarray = np.array( data.loc[start_idx:end_idx, 'Jext'] )
        errJ_subarray = np.array( data.loc[start_idx:end_idx, 'errJ'] )
        time_subarray = np.array( data.loc[start_idx:end_idx, 't'] )
        
        cap[i], errC[i] = calc_capacitance_forOneVoltage(Jext_subarray, errJ_subarray, time_subarray, del_V, freq)
        
    # Handle the last index from t=0 to tmax_n
    Jext_subarray = np.array( data.loc[idx_time_zero[-1]:, 'Jext'] )
    errJ_subarray = np.array( data.loc[idx_time_zero[-1]:, 'errJ'] )
    time_subarray = np.array( data.loc[idx_time_zero[-1]:, 't'] )
    cap[-1], errC[-1] = calc_capacitance_forOneVoltage(Jext_subarray, errJ_subarray, time_subarray, del_V, freq)
    
    return cap, errC

def store_capacitance_data(session_path, V, cap, errC, output_file='CapVol.dat'):
    """ Save the capacitance & its error in one file called CapVol.dat
    
    Parameters
    ----------
    session_path : string
        working directory for zimt
    V : np.array
        Array of frequencies
    cap : np.array
        Array of the capacitance
    errC : np.array
        Array of the capacitance error
    output_file : string
        Filename where the capacitance data is stored
    """

    with open(os.path.join(session_path,output_file), 'w') as file:
        file.write('V cap errC' + '\n')
        for i in range(len(V)):
            file.write(f'{V[i]:.6e} {cap[i]:.6e} {errC[i]:.6e}' + '\n')

def get_capacitance(data, freq, V_0, V_max, del_V, V_step, session_path, output_file):
    """Calculate the capacitance from the simulation result

    Parameters
    ----------
    data : DataFrame
        DataFrame with the simulation results (tj.dat) file
    freq : float
        Frequency at which the capacitance-voltage measurement is performed
    V_0 : float
        Initial voltage
    V_max : float
        Maximum voltage
    del_V : float
        Voltage step that is applied directly after t=0
    V_step : float
        Voltage difference, determines at which voltages the capacitance is determined
    session_path : string
        working directory for zimt
    output_file : string
        Filename where the capacitance data is stored

    Returns
    -------
    integer,string
        returns -1 (failed) or 1 (success), including a message
    """  

    V = np.linspace(V_0, V_max, num=math.ceil((V_max-V_0)/V_step)+1, endpoint=True)
    cap, errC = calc_capacitance(data, del_V,freq)

    # Write the capacitance results to a file
    store_capacitance_data(session_path, V, cap, errC, output_file)

    # If the capacitance is calculated, message a success
    msg = 'Success'
    retval = 0
    
    return retval, msg

def cap_plot(session_path, output_file, xscale='linear', yscale='linear', plot_type = plt.errorbar):
    """ Plot the capacitance against voltage

    Parameters
    ----------
    session_path : string
        working directory for zimt
    output_file : string
        Filename where the capacitance data is stored
    xscale : string
        Scale of the x-axis. E.g linear or log
    yscale : string
        Scale of the y-axis. E.g linear or log
    plot_type : matplotlib.pyplot
        Type of plot to display
    """
    # Read the data from CapVol-file
    data = pd.read_csv(os.path.join(session_path,output_file), sep=r'\s+')

    # Define the plot parameters
    fig, ax = plt.subplots()
    pars = {'cap' : 'Capacitance' }
    par_x = 'V'
    xlabel = 'Voltage [V]'
    ylabel = 'Capacitance [Fm$^{-2}$]'
    title = 'Capacitance-Voltage'
    
    # Plot with or without errorbars
    if plot_type == plt.errorbar:
        ax = utils_plot_gen.plot_result(data, pars, list(pars.keys()), par_x, xlabel, ylabel, xscale, yscale, title, ax, plot_type, 
                                            [], data['errC'], legend=False)
    else:
        ax = utils_plot_gen.plot_result(data, pars, list(pars.keys()), par_x, xlabel, ylabel, xscale, yscale, title, ax, plot_type, legend=False)

    plt.show()

def plot_capacitance(session_path, output_file='CapVol.dat'):
    """Make a plot of the capacitance

    Parameters
    ----------
    session_path : string
        working directory for zimt
    """

    cap_plot(session_path, output_file)

def run_CV_simu(zimt_device_parameters, session_path, tVG_name, freq, V_min, V_max, del_V, V_step, G_frac, run_mode=False, output_file = 'CapVol.dat', tj_name = 'tj.dat', ini_timeFactor=1e-3, timeFactor=1.02):
    """Create a tVG file and run ZimT with capacitance device parameters

    Parameters
    ----------
    zimt_device_parameters : string
        Name of the zimt device parameters file
    session_path : string
        Working directory for zimt
    tVG_name : string
        Name of the tVG file
    freq : float
        Frequency at which the capacitance-voltage measurement is performed
    V_min : float
        Initial voltage
    V_max : float
        Maximum voltage
    del_V : float
        Voltage step that is applied directly after t=0
    V_step : float
        Voltage difference, determines at which voltages the capacitance is determined
    G_frac : float
        Fractional light intensity
    run_mode : bool, optional
        Indicate whether the script is in 'web' mode (True) or standalone mode (False). Used to control the console output, by default False  
    output_file : string, optional
        Name of the file where the capacitance data is stored, by default CapVol.dat
    tj_name : string, optional
        Name of the tj file where the capacitance data is stored, by default tj.dat
    ini_timeFactor : float, optional
        Constant defining the size of the initial timestep, by default 1e-3
    timeFactor : float, optional
        Exponential increase of the timestep, to reduce the amount of timepoints necessary. Use values close to 1., by default 1.02

    Returns
    -------
    CompletedProcess
        Output object of with returncode and console output of the simulation
    string
        Return message to display on the UI, for both success and failed
    """
   
    # Create tVG
    result, message = create_tVG(V_min, V_max, del_V, V_step, G_frac, tVG_name, session_path, freq, ini_timeFactor, timeFactor)

    # Check if tVG file is created
    if result == 0:
        # In order for zimt to converge, set absolute tolerance of Poisson solver small enough
        tolPois = 10**(math.floor(math.log10(abs(del_V)))-4)

        # Define mandatory options for ZimT to run well with CV:
        CV_args = [{'par':'dev_par_file','val':zimt_device_parameters},
                        {'par':'tVGFile','val':tVG_name},
                        {'par':'tolPois','val':str(tolPois)},
                        {'par':'limitDigits','val':'0'},
                        {'par':'currDiffInt','val':'2'},]
        
        result, message = utils_gen.run_simulation('zimt', CV_args, session_path, run_mode)

        if result.returncode == 0 or result.returncode == 95:
            data = read_tj_file(session_path, tj_file_name=tj_name)

            result, message = get_capacitance(data, freq, V_min, V_max, del_V, V_step, session_path, output_file)
            return result, message

        else:
            return result.returncode, message
        
    return result, message

######### Running the function as a standalone script #############################################
if __name__ == "__main__":
    # Capacitance input parameters    
    freq = 1e4
    V_min = 0.5
    V_max = 1.0
    del_V = 10e-3
    V_step = 0.1    
    G_frac = 0

    # Not user input
    ini_timeFactor = 1e-3 # Initial timestep factor, org 1e-3
    timeFactor = 1.02 # Increase in timestep every step to reduce the amount of datapoints necessary, use value close to 1 as this is best! Org 1.02

    session_path = 'ZimT'
    zimt_device_parameters = 'device_parameters.txt'
    tVG_name = 'tVG.txt'
    tj_name = 'tj.dat'

    # Run Capacitance-Voltage   
    result, message = run_CV_simu(zimt_device_parameters, session_path, tVG_name, freq, V_min, V_max, del_V, V_step, G_frac, run_mode=True, ini_timeFactor=ini_timeFactor, timeFactor=timeFactor)

    # Make the capacitance-voltage plot
    if result == 0 or result == 95:
        plot_capacitance(session_path)
    else:
        print(message)

