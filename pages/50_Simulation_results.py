"""Simulation Results routing/navigation page"""
######### Package Imports #########################################################################

import os
import streamlit as st
from utils import general_web as utils_gen_web
from results_pages import result_Steady_State as result_simss
from results_pages import result_Hysteresis_JV as result_hyst
from results_pages import result_Impedance as result_imp
from results_pages import result_IMPS as result_imps
from results_pages import result_CV as result_CV


######### Page configuration ######################################################################

st.set_page_config(layout="wide", page_title="SIMsalabim simulation results", page_icon='./logo/SIMsalabim_logo_HAT.jpg')

# Load custom CSS.
utils_gen_web.local_css('./utils/style.css')

######### Parameter Initialisation ################################################################

if 'id' not in st.session_state:
    st.error('SIMsalabim simulation has not been initialized yet, return to SIMsalabim page to start a session.')
else:
    id_session = str(st.session_state['id'])
    session_path = os.path.join('Simulations', id_session)

    # This page acts as a navigation/routing page for the simulation results. 
    # To display the correct results page, read the session state identifier 'simulation_results', 
    # which has been filled with the correct value after running a (successfull) simulation.
    # The UI and functionality of a specific page is packaged into a single function, located in the 'results_pages' folder. 
    # The content is retrieved by making a call to that function with the session id. 
    if st.session_state['simulation_results'] == 'Steady State JV':
        # Steady State (SimSS) results
        result_simss.show_results_Steady_State(session_path, id_session)
    elif st.session_state['simulation_results'] == 'Hysteresis JV':
        # Hysteresis JV results
        result_hyst.show_results_Hysteresis_JV(session_path, id_session)
    elif st.session_state['simulation_results'] == 'Impedance':
        # Impedance results
        result_imp.show_results_impedance(session_path, id_session)
    elif st.session_state['simulation_results'] == 'IMPS':
        # IMPS results
        result_imps.show_results_imps(session_path, id_session)
    elif st.session_state['simulation_results'] == 'CV':
        # CV results
        result_CV.show_results_CV(session_path, id_session)
    else:
        # No simulation has been run successfully, thus nothing to display.
        st.error('No results to display, no simulation has been run yet.')

######### Function Definitions ####################################################################

######### UI ######################################################################################
