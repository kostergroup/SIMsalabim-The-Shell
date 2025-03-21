"""Draw the energy band diagram"""
######### Package Imports #########################################################################

import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

plt.rcParams.update({'font.size': 24}) # Set font size larger for the band diagram for readability

######### Function Definitions ####################################################################

def create_width_label(x_left, x_right, x_corr, value, y_min, ax, color):
    """ Create the label to display the width of a layer on the width bar

    Parameters
    ----------
    x_left : float
        Left x position of the layer [m]
    x_right : float
        right x position of the layer [m]
    x_corr : float
        Correction factor to place the label in the middle of the layer
    value : float
        Width of the layer [m]
    y_max : float
        Lowest energy level of the device [eV]
    ax : axes
        Axes object for the plot
    color : string
        Color of the label
    """
    ax.text((x_left+x_right)/2-x_corr, y_min-2.0, round(value*1e9), color=color)


def plot_device_widths(ax, y_min, L, L_original):
    """Plot a width bar below the band energy diagram with the thickness of each layer.

    Parameters
    ----------
    ax : axes
        Axes object for the plot
    y_max : float
        Lowest energy level [eV]
    L : float
        Full width of the device [m]
    L_original : List
        List with the layer widths before scaling
    """
    # Horizontal line below the band diagram 
    ax.hlines(y_min-1.4, 0, sum(L), color='k')

    # Add a small vertical line at each boundary/interface between two layers and add a label with the width of the layer
    for i in range(len(L)):
        ax.vlines(sum(L[:i]), y_min-1.2, y_min-1.6, color='k')
        create_width_label(sum(L[:i]), sum(L[:i+1]), 0.02*sum(L), L_original[i], y_min, ax, 'k')
    
    # Add the vertical line at the right most side 
    ax.vlines(sum(L), y_min-1.2, y_min-1.6, color='k')

    # Add label with unit of [nm] to the end of the horizontal label
    ax.text(1.04*sum(L), y_min-2.2, '[nm]', color='k')


def create_energy_label(x_left, x_right, L, y, band_type, position, ax, vert_pos='top'):
    """Create and place the label for an energy level (in eV) of a layer

    Parameters
    ----------
    x_left : float
        Left x position of the layer [m]
    x_right : float
        right x position of the layer [m]
    L : float
        Full width of the device [m]
    y : float
        Energy of the band [eV]
    band_type : string
        Type of band (CB, VB, Electrode)
    position : float
        Full length of the device
    ax : axes
        Axes object for the plot
    """

    # Offset of the labels to not overlap with the layers
    if vert_pos == 'top':
        offset = 0.11
    else:
        offset = -0.4

    # If the layer covers over 20% of the figure size, move the label to the x middle of the figure. Else align it to the left side of the layer.
    if (x_right - x_left) > 0.2*position:
        ax.text((x_left+x_right)/2 + 0.01*L, y+offset, y)
    elif 'WR' in band_type:
        # In case of the right WF, we must align the text to the right of the label
        ax.text(x_right, y+offset, y, horizontalalignment='right')
    else:
        ax.text(x_left+ 0.01*L, y+offset, y)

def create_UI_band_diagram(fig, msg):
    """Create the UI for the band diagram

    Parameters
    ----------
    fig : figure
        Figure object for the band diagram
    msg : string
        Error message to display
    """
    if msg != '':
        st.error(msg)
    else:
        # Initialize the plot containers again and split into (virtual) columns to position correctly.
        bd_container_title = st.empty()
        bd_container_plot = st.empty()

        # Place the title and close button in the top container
        with bd_container_title:
            col_plot_t_1, col_plot_t_2, col_plot_t_3 = st.columns([2, 4, 2])
            with col_plot_t_2:
                # Title
                st.markdown('''<h3><u>Energy band diagram [eV]</u></h3>''', unsafe_allow_html=True)
            with col_plot_t_3:
                # Close button
                st.button('Close figure', on_click=close_figure)

        # Place the figure in the plot container
        with bd_container_plot:
            col_plot_1, col_plot_2, col_plot_3 = st.columns([2, 4, 2])
            with col_plot_2:
                # Band diagram
                st.pyplot(fig)
            with col_plot_3:
                # Scale disclaimer
                st.markdown('''<em>Note: Band diagram is not to scale</em>''', unsafe_allow_html=True)

def get_WF_sfb(layer, dev_par, dev_par_name):
    """Calculate the work function of an electrode for a semi-lat band based on the net doping of the layer

    Parameters
    ----------
    layer : List
        List with the layer data
    dev_par : dict
        Dictionary with all data
    dev_par_name : string
        Name of the device parameter file

    Returns
    -------
    float
        Work function of the electrode [eV]
    """

    # Constants
    q = 1.6022e-19  	#[C] elementary charge
    k = 1.3807e-23;     #[J/K] Boltzmann's constant

    # Get the temperature
    for section in dev_par[dev_par_name]:
        if section[0] == 'General':
            for param in section:
                if 'T' in param[1]:
                    T = float(param[2])
    
    # Get the relevant parameters from the layer file
    for section in dev_par[layer[2]]:
        if section[0] == 'General':
            for param in section:
                if 'E_c' in param[1]:
                    E_c = float(param[2])
                elif 'E_v' in param[1]:
                    E_v = float(param[2])
                elif 'N_c' in param[1]:
                    N_c = float(param[2])
                elif 'N_D' in param[1]:
                    N_D = float(param[2])
                elif 'N_A' in param[1]:
                    N_A = float(param[2])
    

    netDoping = N_A - N_D
    
    if netDoping > 0: # effectively p-doped
        WF = E_v - k*T/q * np.log(N_c/netDoping)
    elif netDoping < 0: # effectively n-doped
        WF = E_c + k*T/q * np.log(-N_c/netDoping)
    else: # intrinsic or fully compensated
        WF = (E_c + E_v)/2
    
    WF = round(WF,2) # Round to 2 decimal places to prevent long float in fig

    return WF
                
def get_param_band_diagram(dev_par, layers, dev_par_name, run_mode = True):
    """Create and display the band diagram on the UI based on the relevant parameters from the dict object

    Parameters
    ----------
    dev_par : dict
        Dictionary with all data
    layers : List
        List with all the layers in the device
    dev_par_name : string
        Name of the device parameter file
    run_mode : boolean
        True if function is called as part of The Shell, False when called directly. 
        Prevents using streamlit components outside of The Shell.
    """
    msg = '' # Init error message string

    # Init arrays for thicknesses and energy levels
    L = []
    E_c = []
    E_v = []

    # Get the work functions of the electrodes
    for section in dev_par[dev_par_name]:
        if section[0] == 'Contacts':
            for param in section:
                if 'leftElec' in param[1]:
                    # Is the left electrode cathode (-1) or anode (1)? Used to ad the correct label to the band diagram
                    leftElec = int(param[2])
                elif 'W_L' in param[1]:
                    # semi-flat band, calculate from net doping at electrode
                    if 'sfb' in param[2]:
                        W_L = -get_WF_sfb(layers[1],dev_par,dev_par_name)
                    else:
                        W_L = -float(param[2])

                elif 'W_R' in param[1]:
                    if 'sfb' in param[2]:
                        # semi-flat band, calculate from net doping at electrode
                        W_R = -get_WF_sfb(layers[-1],dev_par,dev_par_name)
                    else:
                        W_R = -float(param[2])

    # Get the thicknesses and energy levels from the respective layer files
    for layer in layers[1:]:
        for section in dev_par[layer[2]]:
            if section[0] == 'General':
                for param in section:
                    if param[1] in 'L':
                        L.append(float(param[2]))
                    elif param[1] in 'E_c':
                        E_c.append(-float(param[2]))
                    elif param[1] in 'E_v':
                        E_v.append(-float(param[2]))

    
    # Create a figure where the band diagram will be plotted
    # Each element from the array is a layer in the device
    fig, ax = plt.subplots(figsize = (15,5))

    E_high = max(E_v) # To properly place the horizontal width bar
    L_total = sum(L) # Total thickness of the device

    L_real = L.copy() # Create a backup of the widths before adjusting for plotting, used for creating the width labels

    # Create acolor list with 25 standard colors. 
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    # Create and plot a color block to indicate the bands of a layer
    for i in range(len(L)):
        # If the layer thickness is less than 9% of the full device thickness, rescale to 9% to remain visible.
        if L[i] < 0.09*L_total:
            L[i] = 0.09*L_total

        ax.fill_between([sum(L[:i]), sum(L[:i+1])], [E_c[i], E_c[i]], y2=[E_v[i], E_v[i]], color=colors[i])
        create_energy_label(sum(L[:i]), sum(L[:i+1]),sum(L), E_c[i], 'CB', L_total, ax, 'top')
        create_energy_label(sum(L[:i]), sum(L[:i+1]),sum(L), E_v[i], 'VB', L_total, ax, 'bot')
    
    L_total = sum(L) # update with the corrected values

    # Based on the alignment of W_R/W_L set the proper position of the labels
    if W_L > W_R:
        W_L_pos = 'top'
        W_R_pos = 'bot'
    else:
        W_L_pos = 'bot'
        W_R_pos = 'top'   

    Label_left_elec = 'Cathode' if leftElec == -1 else 'Anode'
    Label_right_elec = 'Cathode' if leftElec == 1 else 'Anode'

    # Left Electrode
    ax.plot([-0.06*L_total, 0], [W_L, W_L], color='k') # Horizontal line
    create_energy_label(-0.12*L_total, 0, sum(L), W_L, 'WL', L_total, ax, W_L_pos) # Value label
    ax.text(-15E-9, E_high-1.52, Label_left_elec,horizontalalignment='right',style='italic' ) # Cathode/Anode label

    # Right Electrode
    ax.plot([L_total, L_total+0.06*L_total], [W_R, W_R], color='k')# Horizontal line
    create_energy_label(L_total, L_total+0.12*L_total, sum(L), W_R, 'WR', L_total, ax, W_R_pos) # Value label
    ax.text(sum(L)+15E-9, E_high-1.52, Label_right_elec,horizontalalignment='left',style='italic' ) # Cathode/Anode label

    # Hide the figure axis
    ax.axis('off')

    # Add a horizontal bar to the figure width the layer widths for an arbitray number of layers
    plot_device_widths(ax, E_high, L, L_real)

    if run_mode:
        # Using The Shell, plot the band diagram on the UI
        create_UI_band_diagram(fig, msg)
    else:
        # Standalone function call, return either the figure or error message
        if msg != '':
            # Error encountered, return message
            return msg
        else:
            return fig

def close_figure():
    """Close the band diagram manually.
    """
    # Dummy function to close the band diagram containers
