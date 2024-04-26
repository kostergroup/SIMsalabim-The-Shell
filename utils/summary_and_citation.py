import os
import streamlit as st
from utils.ref_optics import nk_ref_dict, spectrum_ref_dict

# Fixed references
SIMsalabim_cite = 'M. Koopmans, V.M. Le Corre, and L.J.A. Koster, SIMsalabim: An open-source drift-diffusion simulator for semiconductor devices, J. Open Source Softw. 7, 3727 (2022).'
fourier_decomp_cite = 'S.E. Laux, IEEE Trans. Electron Dev. 32 (10), 2028 (1985)'

# File name
summary_file_name = 'SUMMARY_AND_HOW_TO_CITE.txt'

def create_summary_and_cite(session_path, used_optics):
    """Create a file with a summary of the simulation, including the relevant files, description of the experiments and citations.

    Parameters
    ----------
    session_path : string
        path to the session folder
    used_optics : boolean
        Indicate whether the transfer matrix script has been used.
    """
    # Create the file
    fp = open(os.path.join(session_path, summary_file_name),'w')

    # SIMsalabim and The Shell version + repository
    fp.write('SIMsalabim drift-diffusion simulations\n\n')
    fp.write('SIMsalabim version: ' + st.session_state['SIMsalabim_version'] + '\n')
    fp.write('Source code available at: https://github.com/kostergroup/SIMsalabim\n')
    fp.write('The Shell version: ' + st.session_state['TheShell_version'] + '\n')
    fp.write('Source code available at: https://github.com/kostergroup/SIMsalabim-The-Shell\n')
    fp.write('\n')

    # Used SimSS or ZimT
    if st.session_state['simulation_results'] == 'Steady State JV':
        progName = 'SimSS'
    else:
        progName = 'ZimT'
    fp.write('SIMsalabim program: ' + progName + '\n\n')

    # List all included files (input and output) in the session folder
    fp.write('Included files:\n')
    for filename in os.listdir(session_path):
        if os.path.isfile(os.path.join(session_path, filename)) and not filename == summary_file_name:
            fp.write('- ' + filename + '\n')

    fp.write('\n')

    # When the transfer matrix script has been used, list the nk and spectrum files as well
    if used_optics:
        fp.write('nk/spectrum_files (Used to calculate the generation profile)\n')
        for dirpath, dirnames, filenames in os.walk(os.path.join(session_path,'Data_nk')):
            for filename in filenames:
                fp.write('- ' + filename + '\n')
        for dirpath, dirnames, filenames in os.walk(os.path.join(session_path,'Data_spectrum')):
            for filename in filenames:
                fp.write('- ' + filename + '\n')
        fp.write('\n')
    
    # Which simulation has been run
    fp.write('Simulation type: ' + st.session_state['simulation_results'] + '\n')
    # Create a custom description for this simulation. This also described how to 'reproduce' the simulation
    desc = create_description(st.session_state['simulation_results'])
    fp.write(desc + '\n')

    # Write the important experiment specific parameters (not for Steady State JV)
    if not st.session_state['simulation_results'] == 'Steady State JV':
        if st.session_state['simulation_results'] == 'Hysteresis JV':
            # Hysteresis JV
            fp.write(st.session_state['simulation_results'] + ' variables are stored in hyst_pars.txt\n')
            if st.session_state["Exp_object"]['UseExpData'] == 0:
                fp.write(f'Voltage range: {st.session_state["Exp_object"]["Vmin"]:.3f} to {st.session_state["Exp_object"]["Vmax"]:.3f} V\n')
            else:
                fp.write(f'Experimental JV data used. Files:\n')
                fp.write(f'- {st.session_state["Exp_object"]["expJV_Vmin_Vmax"]}\n')
                fp.write(f'- {st.session_state["Exp_object"]["expJV_Vmax_Vmin"]}\n')

            fp.write(f'Scan speed: {st.session_state["Exp_object"]["scan_speed"]:.3E} V/s\n')
            fp.write(f'direction: {st.session_state["Exp_object"]["direction"]} (Voltage sweep order, 1 for [ Vmin-Vmax | Vmax-Vmin ], -1 for [ Vmax-Vmin | Vmin-Vmax ])\n')
            if used_optics:
                fp.write(f'Generation rate: {st.session_state["Exp_object"]["gen_rate"]:.3E} (Fraction of the light intensity/generation rate)\n')
            else:
                 fp.write(f'Generation rate: {st.session_state["Exp_object"]["gen_rate"]:.3f} m^-3 s^-1\n')
            fp.write('\n')
        elif st.session_state['simulation_results'] == 'Impedance':
            # Impedance
            fp.write(st.session_state['simulation_results'] + ' variables are stored in impedance_pars.txt\n')
            fp.write(f'Frequency range: {st.session_state["Exp_object"]["fmin"]:.2E} to {st.session_state["Exp_object"]["fmax"]:.2E} Hz\n')
            fp.write(f'Applied Voltage: {st.session_state["Exp_object"]["V0"]:.3f} V\n')
            fp.write(f'Voltage step size: {st.session_state["Exp_object"]["delV"]:f} V\n')
            if used_optics:
                fp.write(f'Generation rate: {st.session_state["Exp_object"]["gen_rate"]:.3E} (Fraction of the light intensity/generation rate)\n')
            else:
                 fp.write(f'Generation rate: {st.session_state["Exp_object"]["gen_rate"]:.3f} m^-3 s^-1\n')
            fp.write('\n')
        elif st.session_state['simulation_results'] == 'IMPS':
            # IMPS
            fp.write(st.session_state['simulation_results'] + ' variables are stored in imps_pars.txt\n')
            fp.write(f'Frequency range: {st.session_state["Exp_object"]["fmin"]:.2E} to {st.session_state["Exp_object"]["fmax"]:.2E} Hz\n')
            fp.write(f'Applied Voltage: {st.session_state["Exp_object"]["V0"]:.3f} V\n')
            fp.write(f'Fraction generation rate: {st.session_state["Exp_object"]["fracG"]:f} (Fraction to increase the intensity/generation rate with. Sets the size of the initial pertubation)\n')
            if used_optics:
                fp.write(f'Generation rate: {st.session_state["Exp_object"]["gen_rate"]:.3E} (Fraction of the light intensity/generation rate)\n')
            else:
                 fp.write(f'Generation rate: {st.session_state["Exp_object"]["gen_rate"]:.3f} m^-3 s^-1\n')
            fp.write('\n')
        elif st.session_state['simulation_results'] == 'CV':
            # IMPS
            fp.write(st.session_state['simulation_results'] + ' variables are stored in CV_pars.txt\n')
            fp.write(f'Frequency at which CV is performed: {st.session_state["Exp_object"]["freq"]:.2E}\n')
            fp.write(f'Voltage range: {st.session_state["Exp_object"]["Vmin"]:.3f} to {st.session_state["Exp_object"]["Vmax"]:.3f} V\n')
            if used_optics:
                fp.write(f'Generation rate: {st.session_state["Exp_object"]["gen_rate"]:.3E} (Fraction of the light intensity/generation rate)\n')
            else:
                 fp.write(f'Generation rate: {st.session_state["Exp_object"]["gen_rate"]:.3f} m^-3 s^-1\n')
            fp.write('\n')

    # Citation
    fp.write('HOW TO CITE:\n\n')
    # SIMsalabim
    fp.write('* SIMsalabim: \n')
    fp.write(SIMsalabim_cite)
    fp.write('\n\n')

    # In case of impedance or IMPS, cite the Laux (1985) paper
    if st.session_state['simulation_results'] == 'Impedance' or st.session_state['simulation_results'] == 'IMPS':
        fp.write('* Fourier Decomposition (' + st.session_state['simulation_results'] +')\n')
        fp.write(fourier_decomp_cite + '\n\n')

    # When the transfer matrix method has been used, provide references to the used nk and spectrum files. 
    # If the reference is not known, e.g. when the user uploads a file, indicate that no reference has been provided
    if used_optics:
        for dirpath, dirnames, filenames in os.walk(os.path.join(session_path,'Data_nk')):
                # nk files
                for filename in filenames:
                    file_name = os.path.splitext(filename)
                    file_ref = get_reference(file_name[0], nk_ref_dict)
                    fp.write('* ' + file_name[0] + ': ' + file_ref + '\n')
        for dirpath, dirnames, filenames in os.walk(os.path.join(session_path,'Data_spectrum')):
                # spectrum files
                for filename in filenames:
                    file_name = os.path.splitext(filename)
                    file_ref = get_reference(file_name[0], spectrum_ref_dict)
                    fp.write('* ' + file_name[0] + ': ' + file_ref + '\n')
    
    # Close the file
    fp.close()

def create_description(type):
    """Return a custom description for the performed simulation/experiment

    Parameters
    ----------
    type : string
        Name of the simulation/experiment performed. Taken from the state parameter 'simulation_results'
    """
    if type == 'Hysteresis JV':
        # Hysteresis JV
        desc = '''
Simulate a JV hysteresis experiment with SIMsalabim.
Create a linear (forward and backward) sweep across the voltages specified by Vmin (low voltage) and Vmax (high voltage) over time using the voltage scan speed. 
The voltage sweep order is specified via the direction, either  1 for forward | backward [ Vmin-Vmax | Vmax-Vmin ] or -1 for backward-forward[ Vmax-Vmin | Vmin-Vmax ]
        '''
    elif type == 'Impedance':
        # Impedance
        desc = '''
Simulate an impedance spectroscopy experiment with SIMsalabim. 
The impedance is calculated at the applied voltage. A small one time pertubation at t=0 is introduced at this voltage, defined by the voltage step size. 
The time step of the pertubation is 0.1% of 1/fmax. The time profile is not linear, but the timestep increases by 2% every time point to reduce the number of (unnecessary) datapoints. 
The light intensity (generation rate) is kept constant. The impedance is calculated using Fourier decomposition, based on the method desrcibed in S.E. Laux, IEEE Trans. Electron Dev. 32 (10), 2028 (1985). 
Note, we do not integrate from t=0 to infinity, but only from t=0 to the time corresponding to the lowest frequency, i.e. 1/fmin. The integral is calculated using the trapezoidal rule. 
The results (stored in freqZ.dat) consists of the real and imaginary part (including error margins) of the impedance as a function of the frequency.
        '''
    elif type == 'IMPS':
        # IMPS
        desc = '''
Simulate an Intensity Modulated PhotoSpectroscopy (IMPS) experiment with SIMsalabim. 
The impedance is calculated at the applied voltage. A small one time pertubation in light intensity at t=0 is introduced at this voltage, defined as a fraction with which the generation rate is increased.  
The time step of the pertubation is 0.1% of 1/fmax. The time profile is not linear, but the timestep increases by 2% every time point to reduce the number of (unnecessary) datapoints. 
The applied voltage is kept constant. The admittance is calculated using Fourier decomposition, based on the method desrcibed in S.E. Laux, IEEE Trans. Electron Dev. 32 (10), 2028 (1985). 
Note, we do not integrate from t=0 to infinity, but only from t=0 to the time corresponding to the lowest frequency, i.e. 1/fmin. The integral is calculated using the trapezoidal rule. 
The results (stored in freqY.dat) consists of the real and imaginary part (including error margins) of the admittance as a function of the frequency.
        '''
    else:
        desc = ''
    return(desc)

def get_reference(file_name, ref_dict):
    """Retrieve the reference for a nk or spectrum file from the provided nk/spectrum files. If the reference cannot be found, put a missing statement.

    Parameters
    ----------
    file_name : string
        name of the file (without extension)
    ref_dict : dict
        Dictionary holding the references

    Returns
    -------
    string
        the reference
    """
    if file_name in ref_dict:
        return ref_dict[file_name]
    else:
        return '-No reference provided-'
