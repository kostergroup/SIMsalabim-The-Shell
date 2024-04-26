"""SIMsalabim The Shell"""
######### Package Imports #########################################################################

import os, shutil
from datetime import datetime, timezone
import streamlit as st
from utils import general_web as utils_gen_web

######### Page configuration ######################################################################

st.set_page_config(layout="wide", page_title="SIMsalabim - The Shell", page_icon='./logo/SIMsalabim_logo_HAT.jpg')

# Load custom CSS.
utils_gen_web.local_css('./utils/style.css')

######### Parameter Initialisation ################################################################

version_theshell = '1.09' # The Shell version
version_simsalabim = '4.56' # SIMsalabim version

# Folder name where simulations are executed and data is stored
simulation_path = 'Simulations'
# Folder name where the simulation resources are located, like standard device parameters or files with nk values or spectra
resource_path = 'Resources'

# Main executable/Resource paths and default device parameter file names. 
# Note: we do not use the device parameters from the standard SimSS/ZimT folder, 
# but the renamed files in the Resources folder, to avoid issues with similar file names.
simss_path = os.path.join('SIMsalabim', 'SimSS')
simss_devpar_file = 'device_parameters_simss.txt'
zimt_path = os.path.join('SIMsalabim', 'ZimT')
zimt_devpar_file = 'device_parameters_zimt.txt'

# Create and assign paths to a reusable session state. 
# Note: When changing the name of the key of a session state, process the changed name in all occurences of the session state key
st.session_state.key = 'SIMsalabim_version'
st.session_state.key = 'TheShell_version'
st.session_state.key = 'simulation_path'
st.session_state.key = 'simss_path'
st.session_state.key = 'simss_devpar_file'
st.session_state.key = 'zimt_path'
st.session_state.key = 'zimt_devpar_file'
st.session_state.key = 'simulation_results'

st.session_state['SIMsalabim_version'] = version_simsalabim
st.session_state['TheShell_version'] = version_theshell
st.session_state['simulation_path'] = simulation_path
st.session_state['resource_path'] = resource_path
st.session_state['simss_path'] = simss_path
st.session_state['zimt_path'] = zimt_path
st.session_state['simss_devpar_file'] = simss_devpar_file
st.session_state['zimt_devpar_file'] = zimt_devpar_file
st.session_state['simulation_results'] = '' # Empty string, because it depends on the session id which is not fixed.

# Initialise session states for output/input file names.
# Note: When changing the name of the key of a session state, process the changed name in all occurences of the session state key
st.session_state.key = 'expJV'
st.session_state.key = 'genProf'
st.session_state.key = 'traps_bulk'
st.session_state.key = 'traps_int'
st.session_state.key = 'JV_file'
st.session_state.key = 'Var_file'
st.session_state.key = 'scPars_file'
st.session_state.key = 'log_file'
st.session_state.key = 'optics_files'
st.session_state.key = 'tj_file'
st.session_state.key = 'tVG_file'
st.session_state.key = 'hyst_pars'
st.session_state.key = 'hyst_rms_error'
st.session_state.key = 'impedance_pars'
st.session_state.key = 'Exp_object'
st.session_state.key = 'freqZ_file'
st.session_state.key = 'imps_pars'
st.session_state.key = 'freqY_file'
st.session_state.key = 'CV_pars'
st.session_state.key = 'CapVol_file'

st.session_state.key = 'run_simulation'

# Check if the user already has an id. If not, create it for the user to identify input/output files. Currently UTC timestamp is used as an identifier.
if 'id' not in st.session_state:
    # Create an id based on the utc timestamp and store it in a state
    id_user = int(datetime.now(timezone.utc).timestamp()*1e6)
    st.session_state.key = 'id'
    st.session_state['id'] = id_user

    st.experimental_set_query_params(session=id_user)

    session_path = os.path.join(simulation_path, str(st.session_state['id']))

    # If session folder does not exist yet, create it
    if not os.path.exists(session_path):
        os.makedirs(session_path)

    # Copy the content of the Resource folder to the session folder. Also copy SimSS and ZimT executable from the SIMsalabim folder.
    shutil.copytree(resource_path,session_path,dirs_exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(simss_path):
        for filename in filenames:
            if filename == 'simss':
                shutil.copy(os.path.join(simss_path, filename), session_path)

        for dirpath, dirnames, filenames in os.walk(zimt_path):
            for filename in filenames:
                if filename == 'zimt':
                    shutil.copy(os.path.join(zimt_path, filename), session_path)

######### Function Definitions ####################################################################

######### UI ######################################################################################
# st.warning('''PLACEHOLDER''')

st.title("SIMsalabim - The Shell")

st.text('The Shell v' + version_theshell + ' | ' + 'SIMsalabim v' + version_simsalabim)

st.write('An easy-to-use web interface for open source SIMsalabim drift-diffusion simulation package.')

#st.warning('''Note! The Shell will be down temporarly on PLACEHOLDER due to maintenance. ''')

st.warning('''Note: The Shell does not support all features and functionality that SIMsalabim has to offer. 
To use all functionality, download and run the SIMsalabim project on your machine as described in the 
[SIMsalabim Project readme](https://github.com/kostergroup/SIMsalabim). 
For a full overview of the functionality of SIMsalabim, refer to the 
[SIMsalabim manual](https://raw.githubusercontent.com/kostergroup/SIMsalabim/master/Docs/Manual.pdf).''')

st.write('''Currently supported functionality in The Shell is:
- Define your device via the device parameters on a template or upload your own device parameters.
- Use optics (based on the Transfermatrix method) to calculate a generation profile
- Upload and use an experimental JV curve
- Upload and use a generation profile
- Upload and use a definition of multiple trap levels
- Plot, analyze and download the simulation results
- Simulate a JV hysteresis experiment and compare it to an experimental JV curve
- Simulate an impedance spectroscopy experiment
- Simulate an IMPS experiment
- Simulate a capacitance-voltage experiment
''')
st.text(' ')

st.write('To cite this work and SIMsalabim refer to the open-source version of the code published as:')

st.info('M. Koopmans, V.M. Le Corre, and L.J.A. Koster, SIMsalabim: An open-source drift-diffusion simulator for semiconductor devices, J. Open Source Softw. 7, 3727 (2022).')

st.write('The paper can be viewed [here](https://joss.theoj.org/papers/10.21105/joss.03727)')

st.text('''

Copyright Ⓒ 2023 - 2024 | S. Heester, F.D. Elhorst, Dr. M. Koopmans, Dr. V.M. Le Corre and Prof. Dr. L.J.A. Koster, University of Groningen.
''')
        
#  Show the SIMsalabim logo in the sidebar
with st.sidebar:
    st.image('./logo/SIMsalabim_logo_cut_trans.png')
