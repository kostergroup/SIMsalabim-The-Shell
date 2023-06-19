"""Draw the energy band diagram"""
######### Package Imports #########################################################################

import matplotlib.pyplot as plt
import streamlit as st

######### Function Definitions ####################################################################

def create_energy_label(x_left, x_right, y, band_type, position, ax):
    """Create and place the label for an energy level (in eV) of a layer

    Parameters
    ----------
    x_left : float
        Left x position of the layer [m]
    x_right : float
        right x position of the layer [m]
    y : float
        Energy of the band [eV]
    band_type : string
        Type of band (CB, VB, Electrode)
    position : float
        Full length of the device
    ax : axes
        Axes object for the plot
    """

    # If the layer covers over 20% of the figure size, move the label to the x middle of the figure. Else align it to the left side of the layer.
    if 'VB' in band_type:
        offset = 0.035
    else:
        offset = -0.01

    if (x_right - x_left) > 0.2*position:
        ax.text((x_left+x_right)/2, y+offset*y, y)
    else:
        ax.text(x_left, y+offset*y, y)


def create_width_label(x_left, x_right, value, y_min, ax, color):
    """ Create the label to displaythe width of a layer on the width bar

    Parameters
    ----------
    x_left : float
        Left x position of the layer [m]
    x_right : float
        right x position of the layer [m]
    value : float
        Width of the layer [m]
    y_max : float
        Lowest energy level of the device [eV]
    ax : axes
        Axes object for the plot
    color : string
        Color of the label
    """
    ax.text((x_left+x_right)/2, y_min-0.7, round(value*1e9), color=color)


def plot_device_widths(ax, y_min, L, LLTL, LRTL, L_original):
    """Plot a width bar below the band energy diagram with the thickness of each layer.

    Parameters
    ----------
    ax : axes
        Axes object for the plot
    y_max : float
        Lowest energy level [eV]
    L : float
        Full width of the device
    LLTL : float
        Width of the Left Transport Layer [m]
    LRTL : float
        Width of the Right Transport Layer
    L_original : List
        List with the layer widths before scaling
    """
    # Horizontal line below the band diagram
    ax.hlines(y_min-0.75, 0, L, color='k')

    # Small vertical line on each layer interface
    ax.vlines([0, LLTL, L-LRTL, L], y_min-0.85, y_min-0.65, color='k')

    # Left Transport Layer
    create_width_label(0, LLTL-0.05*L, L_original[1], y_min, ax, 'k')

    # Active Layer
    create_width_label(LLTL, L-LRTL-0.05*L, L_original[0]-L_original[1]-L_original[2], y_min, ax, 'k')

    # Right Transport Layer
    create_width_label(L-LRTL, L-0.05*L, L_original[2], y_min, ax, 'k')

    # Label for the unit [nm]
    ax.text(1.05*L, y_min-0.7, '[nm]', color='k')


def create_band_energy_diagram(param):
    """Create and plot the band energy diagram for the device based on the input parameters

    Parameters
    ----------
    param : dict
        Dictionary with the relevant parameters from the device parameters file

    Returns
    -------
    Figure
        Figure object with the band energy diagram
    """

    fig, ax = plt.subplots()

    # Read parameters
    L = float(param["L"])
    LLTL = float(param["L_LTL"])
    LRTL = float(param["L_RTL"])
    CB = -float(param["CB"])
    VB = -float(param["VB"])
    WL = -float(param["W_L"])
    WR = -float(param["W_R"])
    CBLTL = -float(param["CB_LTL"])
    CBRTL = -float(param["CB_RTL"])
    VBLTL = -float(param["VB_LTL"])
    VBRTL = -float(param["VB_RTL"])

    # Find the lowest energy to place the horizontal 'width' bar correctly
    E_low = min([CB, VB, WL, WR, CBLTL, CBRTL, VBLTL, VBRTL])

    # Save original vuse the default column layout with a wide column for the header title.alues for width bar
    L_original = [L, LLTL, LRTL]

    # Set a threshold width for bands to remain visible. Threshold is 10% of the total device width. Only when Transport Layer are defined.
    if LLTL != 0 and LRTL != 0:
        if LLTL < 0.1*L:
            LLTL = 0.1*L
        if LRTL < 0.1*L:
            LRTL = 0.1*L
        if (L-LLTL-LRTL) < 0.1*L:
            frac = LLTL/LRTL
            L_diff = 0.1*L-(L-LLTL-LRTL)
            LLTL = LLTL - L_diff*frac
            LRTL = LRTL - L_diff*(1/frac)

    # Left Transport Layer
    if LLTL > 0:
        ax.fill_between([0, LLTL], [CBLTL, CBLTL], y2=[VBLTL, VBLTL], color='#AF312E')
        create_energy_label(0, LLTL, CBLTL, 'CBLTL', L, ax)
        create_energy_label(0, LLTL, VBLTL, 'VBLTL', L, ax)

    # Active Layer
    ax.fill_between([LLTL, L-LRTL], [CB, CB], y2=[VB, VB], color='#C7D5A0')
    create_energy_label(LLTL, L-LRTL, CB, 'CB', L, ax)
    create_energy_label(LLTL, L-LRTL, VB, 'VB', L, ax)

    # Right Transport Layer
    if LRTL > 0:
        ax.fill_between([L-LRTL, L], [CBRTL, CBRTL],y2=[VBRTL, VBRTL], color='#95B2DA')
        create_energy_label(L-LRTL, L, CBRTL, 'CBRTL', L, ax)
        create_energy_label(L-LRTL, L, VBRTL, 'VBRTL', L, ax)

    # Left Electrode
    ax.plot([-0.1*L, 0], [WL, WL], color='k')
    create_energy_label(-0.1*L, 0, WL, 'WL', L, ax)

    # Right Electrode
    ax.plot([L, L+0.1*L], [WR, WR], color='k')
    create_energy_label(L, L+0.1*L, WR, 'WR', L, ax)

    # Hide the figure axis
    ax.axis('off')

    # Add a horizontal bar to the figure width the layer widths
    plot_device_widths(ax, E_low, L, LLTL, LRTL, L_original)

    return fig

def create_UI_band_diagram(fig, msg):
    if msg != '':
        st.error(msg)
    else:
        # Initialize the plot containers again and split into (virtual) columns to position correctly.
        bd_container_title = st.empty()
        bd_container_plot = st.empty()

        # Place the title and close button in the top container
        with bd_container_title:
            col_plot_t_1, col_plot_t_2, col_plot_t_3 = st.columns([3, 4, 4])
            with col_plot_t_2:
                # Title
                st.markdown('''<h3><u>Energy band diagram (eV)</u></h3>''', unsafe_allow_html=True)
            with col_plot_t_3:
                # Close button
                st.button('Close figure', on_click=close_figure)

        # Place the figure in the plot container
        with bd_container_plot:
            col_plot_1, col_plot_2, col_plot_3 = st.columns([3, 4, 4])
            with col_plot_2:
                # Band diagram
                st.pyplot(fig)
            with col_plot_3:
                # Scale disclaimer
                st.markdown('''<em>Note: Band diagram is not to scale</em>''', unsafe_allow_html=True)

def get_param_band_diagram(dev_par, run_mode = True):
    """Create and display the band diagram on the UI based on the relevant parameters from the dict object

    Parameters
    ----------
    dev_par : dict
        Dictionary with all data
    run_mode : boolean
        True if function is called as part of The Shell, False when called directly. 
        Prevents using streamlit components outside of The Shell.
    """
    msg = '' # Init error message string

    # A fixed list of parameters must be supplied to create the band diagram. 
    plot_param = {}
    plot_param_keys = ['L', 'L_LTL', 'L_RTL', 'CB', 'VB', 'W_L', 'W_R', 'CB_LTL', 'CB_RTL', 'VB_LTL', 'VB_RTL']

    # Find the parameter in the main object and assign it to its key in the dict.
    for section in dev_par[1:]:
        for param in section:
            if param[1] in plot_param_keys:
                plot_param[param[1]] = param[2]

    # Band diagram will fail when the width the transport layers exceeds the device width. Early exit when this is the case.
    if float(plot_param['L'])-float(plot_param['L_LTL'])-float(plot_param['L_RTL']) <= 0:
        msg = 'Cannot create band diagram, Width of transport layers (L_LTL + L_RTL) is larger than the device width (L)'
        fig, ax = plt.subplots() # dummy figure object
    else:
        fig = create_band_energy_diagram(plot_param)

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
