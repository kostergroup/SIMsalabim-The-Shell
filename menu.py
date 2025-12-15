# Menu definition for the SIMsalabim - The Shell application 
import streamlit as st

def menu():
    # Show the full navigation pane for the simualtion run / experiments pages
    if not st.session_state['pagename'] == 'Simulation results':
        st.sidebar.page_link("SIMsalabim.py", label="SIMsalabim")
        st.sidebar.page_link("pages/Steady_State_JV.py", label="Steady State JV & EQE")
        st.sidebar.page_link("pages/Transient_JV.py", label="Transient JV")
        st.sidebar.page_link("pages/Impedance.py", label="Impedance")
        st.sidebar.page_link("pages/IMPS.py", label="IMPS")
        st.sidebar.page_link("pages/CV.py", label="CV")
        st.sidebar.page_link("pages/Simulation_results.py", label="Simulation results")
        st.sidebar.page_link("pages/Getting_help.py", label="Getting help")
    else: 
        # Show a single return button when on the simulation results page
        if st.session_state['def_pagename'] == 'SIMsalabim':
            st.sidebar.page_link("SIMsalabim.py", label="Back to SIMsalabim")
        else:
            st.sidebar.page_link(f"pages/{st.session_state['def_pagename'].replace(' ','_')}.py", label=f"Back to {st.session_state['def_pagename']}")

    st.sidebar.markdown('---')