"""Draw the energy band diagram"""
######### Package Imports #########################################################################
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

plt.rcParams.update({'font.size': 24})

######### Constants ################################################################################

MIN_VISIBLE_WIDTH = 0.09 # Minimum visible fraction of device width. If the layer thickness is less than 9% of the full device thickness, rescale to 9% to remain visible.
TOP_OFFSET = 0.11   # Top offset of the labels to not overlap with the layers
BOT_OFFSET = -0.40 # Bottom offset of the labels to not overlap with the layers
ELEC_LABEL_OFFSET = 15e-9 # Side offset for the anode/cathode label to not overlap with the energy level bar
WIDTH_LABEL_OFFSET = 2.0  # Downward offset of the width label, as it needs to be placed below the actual band layers and width bar
BOUNDARY_BAR_OFFSET = 1.4 # Downward offset of the width bar, as it needs to be placed below the actual band ayers


######### Function Definitions ####################################################################

def get_section(block, section_name):
    """Return the section from a nested parameter block.
    
    Parameters
    ----------
    block : list
        The parameter block as a list of lists.
    section_name : str
        The name of the section to retrieve.
    
    Returns
    -------
    list or Nones
        The section as a list of lists, or None if not found.
    """
    return next((s for s in block if s[0] == section_name), None)


def get_param(section, param_name, cast=float):
    """Return the value of a parameter within a section.
    
    Parameters
    ----------
    section : list
        The section as a list of parameter lists.
    param_name : str
        The name of the parameter to retrieve.
    cast : type, optional
        The type to cast the parameter value to (default is float).

    Returns
    -------
    value or None
        The parameter value cast to the specified type, or None if not found.
    """
    if section is None:
        return None
    for p in section:
        if p[1] == param_name:
            return cast(p[2])
    return None


def create_width_label(x_left, x_right, correction, value, y_min, ax, color):
    """ Create a label for the layer width and add it to the ax.

    Parameters
    ----------
    x_left : float
        Left x-coordinate of the layer.
    x_right : float
        Right x-coordinate of the layer.
    correction : float
        Correction to center the label.
    value : float
        Width value in meters.
    y_min : float
        Minimum y-coordinate for label placement.
    ax : matplotlib.axes.Axes
        The axes to plot on.
    color : str
        Color of the label text.

    Returns
    -------
    None
    """
    ax.text((x_left + x_right) / 2 - correction,
            y_min - WIDTH_LABEL_OFFSET,
            f"{value * 1e9:.0f}",
            color=color)


def plot_device_widths(ax, y_min, L, L_original):
    """ Plot the device width bar.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to plot on.
    y_min : float
        Minimum y-coordinate for label placement.
    L : list of float
        List of layer widths (possibly adjusted for visibility).
    L_original : list of float
        List of original layer widths.

    Returns
    -------
    None

    """
    # Get the full device length for scaling
    boundaries = np.cumsum([0] + L)
    L_total = boundaries[-1]

    # Draw the width bar
    ax.hlines(y_min - BOUNDARY_BAR_OFFSET, 0, L_total, color='k')

    # Draw layer boundaries and width labels
    for i, (x_left, x_right) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        ax.vlines(x_left, y_min - 1.2, y_min - 1.6, color='k')
        create_width_label(x_left, x_right, 0.02 * L_total,
                           L_original[i], y_min, ax, 'k')

    # Draw rightmost boundary and unit label
    ax.vlines(L_total, y_min - 1.2, y_min - 1.6, color='k')
    ax.text(1.04 * L_total, y_min - 2.2, "[nm]", color='k')


def create_energy_label(x_left, x_right, L_total, y, band_type, ax, vert_pos):
    """ Create an energy label for the band diagram and add it to the ax.

    Parameters
    ----------
    x_left : float
        Left x-coordinate of the layer.
    x_right : float
        Right x-coordinate of the layer.
    L_total : float
        Total device length.
    y : float
        Energy level in eV.
    band_type : str
        Type of band ('CB', 'VB', 'WL', 'WR').
    ax : matplotlib.axes.Axes
        The axes to plot on.
    vert_pos : str
        Vertical position of the label ('top' or 'bot').

    Returns
    -------
    None
    """
    # Determine vertical offset and horizontal alignment
    offset = TOP_OFFSET if vert_pos == 'top' else BOT_OFFSET
    width = x_right - x_left

    # Determine horizontal position and alignment of the text based on band type and width
    if width > 0.2 * L_total:
        x = (x_left + x_right) / 2 + 0.01 * L_total
        ha = 'center'
    elif 'WR' in band_type:
        x = x_right
        ha = 'right'
    else:
        x = x_left + 0.01 * L_total
        ha = 'left'

    ax.text(x, y + offset, f"{y}", ha=ha)


def get_work_function_sfb(layer, dev_par, dev_par_name):
    """ Calculate the work function using.

    Parameters
    ----------
    layer : list
        The layer parameter block as a list of lists.
    dev_par : list
        The list of nested lists with the device parameters.
    dev_par_name : str
        The name of the device parameter file.
    
    Returns
    -------
    float
        The calculated work function in eV.
    """
    q = 1.6022e-19 # Elementary charge in C
    k = 1.3807e-23 # Boltzmann constant in J/K

    # Extract necessary parameters from the device parameters
    gen_section = get_section(dev_par[dev_par_name], "General")
    T = get_param(gen_section, "T")

    layer_section = get_section(dev_par[layer[2]], "General")
    E_c = get_param(layer_section, "E_c")
    E_v = get_param(layer_section, "E_v")
    N_c = get_param(layer_section, "N_c")
    N_D = get_param(layer_section, "N_D")
    N_A = get_param(layer_section, "N_A")

    net = N_A - N_D

    # Calculate the work function based on doping type
    if net > 0:
        WF = E_v - (k * T / q) * np.log(N_c / net)
    elif net < 0:
        WF = E_c + (k * T / q) * np.log(-N_c / net)
    else:
        WF = (E_c + E_v) / 2

    return round(WF, 2)


def get_param_band_diagram(dev_par, layers, dev_par_name, run_mode=True):
    """ Construct and display the energy band diagram.

    Parameters
    ----------
    dev_par : list
        The device parameters as a list of nested lists.
    layers : list 
        The list of layers,
    dev_par_name : str
        The name of the device parameter file.
    run_mode : bool, optional
        Whether to run in UI mode (default is True).

    Returns
    -------
    matplotlib.figure.Figure 
        The band diagram figure
    """
    msg = ""
    
    # Extract electrode parameters
    contacts = get_section(dev_par[dev_par_name], "Contacts")
    leftElec = get_param(contacts, "leftElec", int)

    # Left electrode WF
    WL_raw = get_param(contacts, "W_L", str)
    W_L = -get_work_function_sfb(layers[1], dev_par, dev_par_name) if WL_raw == "sfb" else -float(WL_raw)

    # Right electrode WF
    WR_raw = get_param(contacts, "W_R", str)
    W_R = -get_work_function_sfb(layers[-1], dev_par, dev_par_name) if WR_raw == "sfb" else -float(WR_raw)

    # Get layer widths and energy levels
    L = []
    E_c = []
    E_v = []

    for layer in layers[1:]:
        sec = get_section(dev_par[layer[2]], "General")
        L.append(get_param(sec, "L"))
        E_c.append(-get_param(sec, "E_c"))
        E_v.append(-get_param(sec, "E_v"))

    # Copy original widths and get the total width
    L_real = L.copy()
    L = np.array(L, dtype=float)
    L_total_original = L.sum()

    # Expand thin layers to minimum visible fraction
    L = np.maximum(L, MIN_VISIBLE_WIDTH * L_total_original)
    boundaries = np.cumsum([0] + list(L))
    L_total = boundaries[-1]

    # Create the diagram
    fig, ax = plt.subplots(figsize=(15, 5))

    E_high = max(E_v) # Upper limit for the energy scale

    # Create a custom color map, to account for N layers. Repeats every 20 instances
    color_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    colors = (color_list * ((len(L) // len(color_list)) + 1))[:len(L)]
    
    # Ploit layers
    for i, (x_left, x_right) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        ax.fill_between([x_left, x_right], [E_c[i], E_c[i]],
                        y2=[E_v[i], E_v[i]], color=colors[i])

        create_energy_label(x_left, x_right, L_total, E_c[i], 'CB', ax, 'top')
        create_energy_label(x_left, x_right, L_total, E_v[i], 'VB', ax, 'bot')

    # Plot electrodes
    W_L_pos, W_R_pos = ('top', 'bot') if W_L > W_R else ('bot', 'top')
    Label_left, Label_right = ('Cathode', 'Anode') if leftElec == -1 else ('Anode', 'Cathode')

    # Left electrode
    ax.plot([-0.06 * L_total, 0], [W_L, W_L], color='k')
    create_energy_label(-0.12 * L_total, 0, L_total, W_L, 'WL', ax, W_L_pos)
    ax.text(-ELEC_LABEL_OFFSET, E_high - 1.52, Label_left, ha='right', style='italic')

    # Right electrode
    ax.plot([L_total, L_total + 0.06 * L_total], [W_R, W_R], color='k')
    create_energy_label(L_total, L_total + 0.12 * L_total, L_total, W_R, 'WR', ax, W_R_pos)
    ax.text(L_total + ELEC_LABEL_OFFSET, E_high - 1.52, Label_right, ha='left', style='italic')

    ax.axis('off')

    # Width bar
    plot_device_widths(ax, E_high, L.tolist(), L_real)

    # UI wrapper
    if run_mode:
        create_UI_band_diagram(fig, msg)
    else:
        return msg if msg else fig


def create_UI_band_diagram(fig, msg):
    """ Create a Streamlit UI element to display the band diagram.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The band diagram figure.
    msg : str
        An optional error message to display instead of the figure.
    
    Returns
    -------
    Nones
    """
    if msg:
        # Something went wrong, display the error message
        st.error(msg)
        return

    container_title = st.empty()
    container_plot = st.empty()

    # Above the band diagram display the title and close button
    with container_title:
        c1, c2, c3 = st.columns([2, 4, 2])
        with c2:
            st.markdown("<h3><u>Energy band diagram [eV]</u></h3>", unsafe_allow_html=True)
        with c3:
            st.button("Close figure", on_click=close_figure)

    # Display the band diagram itself
    with container_plot:
        _, c2, c3 = st.columns([2, 4, 2])
        with c2:
            st.pyplot(fig)
        with c3:
            st.markdown("<em>Note: Band diagram is not to scale</em>", unsafe_allow_html=True)


def close_figure():
    pass
