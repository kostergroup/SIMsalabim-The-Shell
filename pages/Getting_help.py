"""Getting Help for SIMsalabim"""
######### Package Imports #########################################################################

import streamlit as st
from utils import general_web as utils_gen_web
from menu import menu

######### Page configuration ######################################################################

st.set_page_config(layout="wide", page_title="SIMsalabim Help",
                   page_icon='./logo/SIMsalabim_logo_HAT.jpg')

# Load custom CSS
utils_gen_web.local_css('./utils/style.css')

# Session states for page navigation
st.session_state['pagename'] = 'Getting help'
st.session_state['def_pagename'] = 'Getting help'

######### Parameter Initialisation ################################################################

######### Function Definitions ####################################################################

######### UI ######################################################################################

st.subheader('SIMsalabim project')
st.write("For more information on the SIMsalabim project and how to run it locally, visit the [projects Github page](https://github.com/kostergroup/SIMsalabim).")
st.subheader('Manual')
st.write('''A detailed description of the functionality and possibilities of SIMsalabim can be found in the [SIMsalabim manual](https://raw.githubusercontent.com/kostergroup/SIMsalabim/master/Docs/Manual.pdf). This includes among other things:
- Included physics in SIMsalabim
- Description of all device parameters
- Preparing input files, for example expirmental JV curves
- Understanding the output of SIMsalabim''')
st.subheader("Slack community")
st.write("To keep up to date with the latest developments of SIMsalabim and interact with the community, join our SIMsalabim Slack channel by sending an email to l.j.a.koster(at)rug.nl")

# ToDo: QA or FAQ document

#  Show the SIMsalabim logo in the sidebar
with st.sidebar:
    with st.sidebar:
        # Show custom menu
        menu()
    st.image('./logo/SIMsalabim_logo_cut_trans.png')