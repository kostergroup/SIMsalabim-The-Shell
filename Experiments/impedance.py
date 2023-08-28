"""Perform impedance simulations"""
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

def create_tVG(V_0, del_V, G, gen_profile, tVG_name, session_path, f_min=1e-2, f_max=1e6, ini_timeFactor=1e-3, timeFactor=1.02):
    """Create a tVG file for impedance experiments. 

    Parameters
    ----------
    V_0 : float 
        Voltage at t=0
    del_V : float
        Voltage step that is applied after t=0
    G : float
        Amount of suns if gen_profile == 'calc', else amount of generated electron-hole pairs
    gen_profile : string
        Indicator for type of generation profile to set the correct header in the tVG file
    tVG_name : string
        Name of the tVG file
    session_path : string
        Path of the simulation folder for this session
    f_min : float
        Minimum frequency
    f_max : float
        Maximum frequency
    ini_timeFactor : float
        Constant defining the size of the initial timestep
    timeFactor : float
        Exponential increase of the timestep, to reduce the amount of timepoints necessary. Use values close to 1.

    Returns
    -------
    string
        A message to indicate the result of the process
    """

    time = 0
    del_t = ini_timeFactor/f_max

    # Starting line of the tVG file: header + datapoints at time=0. Set the correct header based on the type of generation profile used.
    if gen_profile == 'calc':
        tVG_lines = 't Vext Gfrac\n' + f'{time:.3e} {V_0} {G:.3e}\n'
    else:
        tVG_lines = 't Vext Gehp\n' + f'{time:.3e} {V_0} {G:.3e}\n'

    # Make the other lines in the tVG file
    while time < 1/f_min: #max time: 1/f_min is enough!
        time = time+del_t
        tVG_lines += f'{time:.3e} {V_0+del_V} {G:.3e}\n'
        del_t = del_t * timeFactor # At first, we keep delt constant to its minimum values

    # Write the tVG lines to the tVG file
    with open(os.path.join(session_path,tVG_name), 'w') as file:
        file.write(tVG_lines)

    # tVG file is created, message a success
    msg = 'Success'
    retval = 0

    return retval, msg

def read_tj_file(session_path, tj_file_name='tj.dat'):
    """ Read relevant parameters for impedance of the tj file

    Parameters
    ----------
    session_path : string
        Path of the simulation folder for this session
    data_tj : dataFrame
        Pandas dataFrame containing the tj output file from ZimT

    Returns
    -------
    DataFrame
        Pandas dataFrame containing the time, voltage, current density and numerical error in the current density of the tj_file
    """

    data = pd.read_csv(os.path.join(session_path,tj_file_name), delim_whitespace=True)

    return data

def get_integral_bounds(data, f_min=1e-2, f_max=1e6, f_steps=20):
    """ Determine integral bounds in the time domain, used to compute the conductance and capacitance

    Parameters
    ----------
    data : dataFrame
        Pandas dataFrame containing the time, voltage, current density and numerical error in the current density of the tj_file
    f_min : float
        Minimum frequency
    f_max : float
        Maximum frequency
    f_steps : float
        Frequency steps

    Returns
    -------
    list
        List of array indices that will be used in the plotting
    """

    # Total number of time points
    numTimePoints = len(data['t'])

    # Check which time index corresponds to 1/fmax. We call this istart:
    istart = -1
    for i in range(numTimePoints):
        if math.isclose(data['t'][i], 1/f_max, rel_tol = 2/f_steps): #note: don't use == to compare 2 floating points!
            istart = i

    # Starting time point could not be found.
    if istart == -1:
        msg = 'Could not find a time that corresponds to the highest frequency.'
        return -1, msg
    
    # print('Found istart: ', istart)

    # ifin: last index we should plot, corresponds to time = 1/f_min:
    ifin = numTimePoints - 1

    # isToPlot starts with istart:
    isToPlot = [istart]

    PlotRatio = max(1, round( (ifin-istart)/(math.log10(f_max/f_min) * f_steps)))

    # Incorrect plot ratio
    if PlotRatio < 1:
        msg = 'PlotRatio smaller than 1. It should at least be 1'
        return -1, msg

    # Then add the other indices:
    for i in range(istart+1, ifin-1):
        if (i-istart) % PlotRatio == 0: # note: % is python's modulo operator.
            isToPlot.append(i) # add the index to our array

    # Also include the last index:
    isToPlot.append(ifin)

    # Integral bounds have been determined, return the array with indices and a success message
    msg = 'Success'
    return isToPlot, msg

def calc_impedance_limit_time(I, errI, time, VStep, imax):
    """Fourier Decomposition formula which computes the impedance at frequency freq (Hz) and its complex error
    Based on S.E. Laux, IEEE Trans. Electron Dev. 32 (10), 2028 (1985), eq. 5a, 5b
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
        Frequency belonging to Z(f)
    complex number
        Impedance at frequency f: Z(f)
    complex number
        Numerical error in calculated impedance Z(f)
    """

    freq=1/time[imax] #we obtain the frequency from the time array
    Iinf = I[imax] # I at infinite time, i.e. the last one we have.
	
    #prepare array for integrants:
    int1 = np.empty(imax)
    int2 = np.empty(imax)
    int3 = np.empty(imax)
    int4 = np.empty(imax)
	
    #now we use only part of the time array:
    timeLim = time[0:imax]
	
    for i in range(imax) :
        sinfac = math.sin(2*math.pi*freq*timeLim[i])
        cosfac = math.cos(2*math.pi*freq*timeLim[i])
        int1[i] = sinfac*(I[i] - Iinf)
        int2[i] = cosfac*(I[i] - Iinf)	
        int3[i] = sinfac*(I[i] + errI[i] - Iinf - errI[imax])
        int4[i] = cosfac*(I[i] + errI[i] - Iinf - errI[imax])	

    #now compute the conductance and capacitance:
    cond = (Iinf - I[0] + 2*math.pi*freq*scipy.integrate.trapz(int1, timeLim))/VStep
    cap = scipy.integrate.trapz(int2, timeLim)/VStep
    #convert to impedance:
    Z = 1/(cond + 2J*math.pi*freq*cap)
	
    #and again, but now with the error added to the current:	
    condErr = (Iinf + errI[imax] - I[0] - errI[0] + 2*math.pi*freq*scipy.integrate.trapz(int3, timeLim))/VStep
    capErr = scipy.integrate.trapz(int4, timeLim)/VStep
    #convert to impedance:
    Z2 = 1/(condErr + 2J*math.pi*freq*capErr)
    
    #error is the difference between Z and Z2:
    errZ = Z - Z2
    
    #now return complex impedance, its error and the corresponding frequency:	
    return freq, Z, errZ

def calc_impedance(data, del_V, isToPlot):
    """ Calculate the impedance over the frequency range
    
    Parameters
    ----------
    data : dataFrame
        Pandas dataFrame containing the time, voltage, current density and numerical error in the current density of the tj_file
    del_V : float
        Voltage step
    isToPlot : list
        List of array indices that will be used in the plotting

    Returns
    -------
    np.array
        Array of frequencies
    np.array
        Array of the real component of impedance
    np.array
        Array of the imaginary component of impedance
    np.array
        Array of complex error
    """
    # init the arrays for the impedance and its error:
    numFreqPoints = len(isToPlot)
    freq = np.empty(numFreqPoints)
    ReZ = np.empty(numFreqPoints)
    ImZ = np.empty(numFreqPoints)
    Z = [1 + 1J] * numFreqPoints
    errZ = [1 + 1J] * numFreqPoints

    for i in range(numFreqPoints):
        imax=isToPlot[i]
        freq[i], Z[i], errZ[i] = calc_impedance_limit_time(data['Jext'], data['errJ'], data['t'], del_V, imax)
        # we are only interested in the absolute value of the real and imag components:
        ReZ[i] =(Z[i].real)
        ImZ[i] = (Z[i].imag)
    
    return freq, ReZ, ImZ, errZ

def store_impedance_data(session_path, freq, ReZ, ImZ, errZ, output_file):
    """ Save the frequency, real & imaginary part of the impedance & impedance error in one file called freqZ.dat
    
    Parameters
    ----------
    session_path : string
        working directory for zimt
    freq : np.array
        Array of frequencies
    ReZ : np.array
        Array of the real component of impedance
    ImZ : np.array
        Array of the imaginary component of impedance
    errZ : np.array
        Array of complex error
    """

    with open(os.path.join(session_path,output_file), 'w') as file:
        file.write('freq ReZ ImZ ReErrZ ImErrZ' + '\n')
        for i in range(len(freq)):
            file.write(f'{freq[i]:.6e} {ReZ[i]:.6e} {ImZ[i]:.6e} {abs(errZ[i].real):.6e} {abs(errZ[i].imag):.6e}' + '\n')

    # print('The data of the Impedance Spectroscopy graphs is written to ' + output_file)

def get_impedance(data, f_min, f_max, f_steps, del_V, session_path, output_file):
    """Calculate the impedance from the simulation result

    Parameters
    ----------
    data : DataFrame
        DataFrame with the simulation results (tj.dat) file
    f_min : float
        Minimum frequency
    f_max : float
        Maximum frequency
    f_steps : float
        Frequency step
    del_V : float
        Voltage step
    session_path : string
        working directory for zimt
    output_file : string
        name of the file where the impedance data is stored

    Returns
    -------
    integer,string
        returns -1 (failed) or 1 (success), including a message
    """
    isToPlot, msg = get_integral_bounds(data, f_min, f_max, f_steps)

    if isToPlot != -1:
        # Integral bounds have been determined, continue to calculate the impedance
        freq, ReZ, ImZ, errZ = calc_impedance(data, del_V, isToPlot)

        # Write impedance results to a file
        store_impedance_data(session_path, freq, ReZ, ImZ, errZ, output_file)

        msg = 'Success'
        return 0,msg
    else:
        # Failed to determine integral bounds, exit with the error message
        return -1, msg

def Bode_plot(session_path, output_file, xscale='log', yscale_1='linear', yscale_2='linear', plot_type = plt.errorbar):
    """ Plot the real and imaginary part of the impedance against frequency

    Parameters
    ----------
    session_path : string
        working directory for zimt
    xscale : string
        Scale of the x-axis. E.g linear or log
    yscale_ax1 : string
        Scale of the left y-axis. E.g linear or log
    yscale_ax2 : string
        Scale of the right y-axis. E.g linear or log
    """
    # Read the data from freqZ-file
    data = pd.read_csv(os.path.join(session_path,output_file), delim_whitespace=True)

    # Flip the ImZ data to the first quadrant
    data["ImZ"] = data["ImZ"]*-1

    # Define the plot parameters, two y axis
    pars = {'ReZ' : 'Re Z [Ohm m$^2$]', 'ImZ' : '-Im Z [Ohm m$^2$]' }
    selected_1 = ['ReZ']
    selected_2 = ['ImZ']
    par_x = 'freq'
    xlabel = 'frequency [Hz]'
    ylabel_1 = 'Re Z [Ohm m$^2$]'
    ylabel_2 = '-Im Z [Ohm m$^2$]'
    title = 'Bode plot'

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    utils_plot_gen.plot_result_twinx(data, pars, selected_1, selected_2, par_x, xlabel, ylabel_1, ylabel_2, xscale, yscale_1, yscale_2, title,ax1,ax2, 
                                        plot_type, y_error_1 = data['ReErrZ'], y_error_2 = data['ImErrZ'])
    plt.show()

def Nyquist_plot(session_path, output_file, xscale='linear', yscale='linear', plot_type = plt.errorbar):
    """ Plot the real and imaginary part of the impedance against each other

    Parameters
    ----------
    session_path : string
        working directory for zimt
    xscale : string
        Scale of the x-axis. E.g linear or log
    yscale : string
        Scale of the y-axis. E.g linear or log
    """
    # Read the data from freqZ-file
    data = pd.read_csv(os.path.join(session_path,output_file), delim_whitespace=True)

    # Flip the ImZ data to the first quadrant
    data["ImZ"] = data["ImZ"]*-1

    fig, ax = plt.subplots()
    pars = {'ImZ' : '-Im Z [Ohm m$^2$]'}
    par_x = 'ReZ'
    xlabel = 'Re Z [Ohm m$^2$]'
    ylabel = '-Im Z [Ohm m$^2$]'
    title = 'Nyquist plot'

    # Plot the nyquist plot with or without errorbars
    if plot_type == plt.errorbar:
        ax = utils_plot_gen.plot_result(data, pars, list(pars.keys()), par_x, xlabel, ylabel, xscale, yscale, title, ax, plot_type, 
                                            data['ReErrZ'], data['ImErrZ'], legend=False)
    else:
        ax = utils_plot_gen.plot_result(data, pars, list(pars.keys()), par_x, xlabel, ylabel, xscale, yscale, title, ax, plot_type, legend=False)

    plt.show()

def plot_impedance(session_path, output_file='freqZ.dat'):
    """Make a Bode and Nyquist plot of the impedance

    Parameters
    ----------
    session_path : string
        working directory for zimt
    """
    # Bode plot
    Bode_plot(session_path,output_file)

    #Nyquist plot
    Nyquist_plot(session_path,output_file)


def run_impedance_simu(zimt_device_parameters, session_path, tVG_name, f_min, f_max, f_steps, V_0, del_V, G, gen_profile, run_mode=False, output_file = 'freqZ.dat', tj_name = 'tj.dat'):
    """Create a tVG file and run ZimT with impedance device parameters

    Parameters
    ----------
    zimt_device_parameters : string
        Name of the zimt device parameters file
    session_path : string
        Working directory for zimt
    tVG_name : string
        Name of the tVG file
    f_min : float
        Minimum frequency
    f_max : float
        Maximum frequency
    f_steps : float
        Frequency step
    V_0 : float 
        Voltage at t=0
    del_V : float
        Voltage step
    G : float
        Amount of suns if gen_profile == 'calc', else amount of generated electron-hole pairs
    gen_profile : string
        Indicator for type of generation profile to set the correct header in the tVG file  
    run_mode : bool, optional
        Indicate whether the script is in 'web' mode (True) or standalone mode (False). Used to control the console output, by default False  
    output_file : string, optional
        Name of the file where the impedance data is stored, by default freqZ.dat
    tj_name : string, optional
        Name of the tj file where the impedance data is stored, by default tj.dat
    Returns
    -------
    CompletedProcess
        Output object of with returncode and console output of the simulation
    string
        Return message to display on the UI, for both success and failed
    """
    # Create tVG
    result, message = create_tVG(V_0, del_V, G, gen_profile, tVG_name, session_path, f_min=f_min, f_max=f_max)

    # Check if tVG file is created
    if result == 0:
        # In order for zimt to converge, set absolute tolerance of Poisson solver small enough
        tolPois = 10**(math.floor(math.log10(abs(del_V)))-4)

        # Define mandatory options for ZimT to run well with impedance:
        Impedance_JV_args = [{'par':'dev_par_file','val':zimt_device_parameters},
                             {'par':'tVG_file','val':tVG_name},
                             {'par':'tolPois','val':str(tolPois)},
                             {'par':'LimitDigits','val':'0'},
                             {'par':'CurrDiffInt','val':'2'}]
        
        result, message = utils_gen.run_simulation('zimt', Impedance_JV_args, session_path, run_mode)

        if result.returncode == 0 or result.returncode == 95:
            data = read_tj_file(session_path, tj_file_name=tj_name)

            result, message = get_impedance(data, f_min, f_max, f_steps, del_V, session_path, output_file)
            return result, message

        else:
            return result.returncode, message
        
    return result, message

## Running the function as a standalone script
if __name__ == "__main__":
    # Impedance input parameters
    f_min = 1e-2 # org 1e-2
    f_max = 1e8 # org 1e6
    f_steps = 20 # org 20

    V_0 = 1.0 # Float or 'oc' for the open-circuit voltage
    del_V = 1e-2 # org 1e-2
    # del_V = 1e-2
    # G = 1 * 10**27
    G = 1

    # From device parameters file
    gen_profile = 'calc'

    # Not user input
    ini_timeFactor = 1e-3 # Initial timestep factor, org 1e-3
    timeFactor = 1.02 # Increase in timestep every step to reduce the amount of datapoints necessary, use value close to 1 as this is best! Org 1.02

    # SIMsalabim input parameters
    zimt_device_parameters = 'device_parameters_zimt.txt'
    tVG_name = 'tVG.txt'
    tj_name = 'tj.dat'
    session_path = 'Zimt'

    # Run impedance spectroscopy
    result, message = run_impedance_simu(zimt_device_parameters, session_path, tVG_name,f_min, f_max, f_steps, V_0, del_V, G, gen_profile, run_mode=True)

    # Make the impedance plots
    plot_impedance(session_path)

