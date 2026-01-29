"""Functions for page: Simulation_results"""
######### Package Imports #########################################################################

import matplotlib.pyplot as plt
import streamlit as st
from pySIMsalabim.plots import plot_functions as utils_plot

######### Function Definitions ####################################################################   

def plot_result_JV(data, choice_voltage, plot_funcs, ax, exp, data_exp='', xscale = 'linear', yscale = 'linear'):
    """Make a plot of the JV curve based on the 'JV.dat" file

    Parameters
    ----------
    data : DataFrame
        All output data from the JV.dat file
    choice_voltage : float
        The Vext potential for which the data in Var.dat is shown
    plot_funcs : Any
        Type of plot    # Set figure and axis properti
    ax : axes
        Axes object for the plot
    exp : boolean
        True if experimental JV curve needs to be plotted.
    data_exp : DataFrame
        Optional argument when an experimental JV curve is supplied
    xscale : string, optional
        Scale of the x-axis, by default 'lin'
    yscale : string, optional
        Scale of the y-axis, by default 'lin'

    Returns
    -------
    axes
        Updated Axes object for the plot
    """

    # Remove the +/- toggles on number inputs
    st.markdown("""<style>
        button.step-up {display: none;}
        button.step-down {display: none;}
        div[data-baseweb] {border-radius: 4px;}
        </style>""",unsafe_allow_html=True) 

    # If the yscale is log, we need to take the absolute value of the current to not lose the negative part of the curve. 
    if yscale == 'log':
        data['Jext'] = data['Jext'].abs()
        data['Jext'] = data['Jext'].replace(0, 1e-20) # Avoid log(0) error
        if exp is True:
            data_exp['Jext'] = data_exp['Jext'].abs()
            data_exp['Jext'] = data_exp['Jext'].replace(0, 1e-20) # Avoid log(0) error

    # We only need one label when making the line and scatter plot.
    if plot_funcs == plt.plot:
        plot_funcs(data['Vext'], data['Jext'], label='Simulated')
    else:
        plot_funcs(data['Vext'], data['Jext'])

    # Vertical line to show the selected voltage (Vext)    
    ax.axvline(choice_voltage, color='k', linestyle='--')

    # Configure plot
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.set_xlabel('$V_{ext}$ [V]')
    ax.set_ylabel('$J_{ext}$ [Am$^{-2}$]')
    ax.set_title('Current-voltage characteristic')

    # Add an experimental curve to the plot when needed. Add a legend because we have two different curves.
    if exp is True:
        if plot_funcs == plt.plot:
            plot_funcs(data_exp['Vext'], data_exp['Jext'], label='Experimental')
        else:
            plot_funcs(data_exp['Vext'], data_exp['Jext'])
        ax.legend()

    # Without experimental data, there is no need for a legend. It is just a single JV curve.
    if exp is False:
        legend = ax.legend()
        legend.remove()

    # Indicate the x,y axis
    ax.axhline(y=0, color='gray', linewidth=0.5)
    ax.axvline(x=0, color='gray', linewidth=0.5)

    return ax

def get_nonzero_parameters(pars, data, choice_voltage):
    """Check if a parameter is not equal to zero for a certain voltage. 
    If so, remove it from the options to plot, because it will not show up anyway.

    Parameters
    ----------
    pars : dict
        Dictionary with parameter names and labels
    data : DataFrame
        All output data from the 'Var' file
    choice_voltage : float
        The Vext potential for which to show the data

    Returns
    -------
    dict
        Updtaed dictionary with parameter names and labels
    """
    for par in list(pars.keys()):
        if sum(data[data['Vext'] == choice_voltage][par]) == 0:
            pars.pop(par)
    
    return pars

def create_UI_component_plot(data_org, pars, x_key, xlabel, ylabel, title, plot_no, fig, ax, plot_type,
                             cols, choice_voltage = 0, source_type = '', show_plot_param=True, show_yscale=True, yscale_init=0, xscale_init=0, 
                             show_xscale=False, show_xrange = True, show_yrange = True, xrange_format = "%f", yrange_format = "%e", xrange_val = None, yrange_val = None, weight_key = '', weight_label = '', weight_norm = 'linear', error_x = '', error_y='', show_legend=True,error_fmt='-'):
    """Create a plot for the provided data and place it into a column structure. 
    Add the plot options to the right of the plot when needed. 
    When plotting a 'Var' type file, plot only for the selected voltage

    Parameters
    ----------
    data_org : DataFrame
        Unfiltered data to plot
    pars : dict
        Dict with all potential parameters to plot. Keys represent the names in the dataFrama, values are the corresponding labels
    x_key : string
        Key in the dataframe for the 'x' axis data
    xlabel : string
        Label for the x-axis. Format: parameter [unit]
    ylabel : string
        Label for the y-axis. Format: parameter [unit]
    title : string
        Title of the plot
    plot_no : integer
        Plot number, used as unique identifier
    fig : Figure
        The figure object
    ax : axes
        Axes object for the plot
    plot_type : Any
        Type of plot, e.g. standard plot or scatter
    cols : List
        List with columns to plot figure in (Streamlit specific)
    choice_voltage : float, optional
        The Vext potential for which to show the data. Only relevant when plotting from a 'Var' file
    source_type : string, optional
        From what file type originates the data. Only relevant when equal to 'Var'
    show_plot_param : bool, optional
        Show the multiselectbox to select which parameters to plot, by default True
    show_yscale : bool, optional
        Show a radio toggle to switch between a linear or log y scale, by default true
    yscale_init : int, optional
        Initial scale of the y-axis, used in yscale_options, by default 0
    xscale_init : int, optional
        Initial scale of the x-axis, used in xscale_options, by default 0
    show_xscale : bool, optional
        Show a radio toggle to switch between a linear or log x scale, by default true
    show_xrange : bool, optional
        Show input fields to set the x-range, by default True
    show_yrange : bool, optional
        Show input fields to set the y-range, by default True
    xrange_format : string, optional
        Format of the x-range input fields, by default "%f"
    yrange_format : string, optional
        Format of the y-range input fields, by default "%e"
    xrange_val : List, optional
        Initial values for the x-range input fields, by default [None, None] in which case the min,max values of the data are used as limits
    yrange_val : List, optional
        Initial values for the y-range input fields, by default [None, None] in which case the min,max values of the data are used as limits
    weight_key : string, optional
        Key in the dataframe for the colorbar data, ignored if empty string, by default ''
    weight_label : string, optional
        Label for the colorbar. Format: parameter [unit]
    weight_norm : string, optional
        Scale of the colorbar, 'linear' or 'log', by defailt 'linear'
    error_x : string, optional
        Dataframe key of the column with the error in x, by default ''
    error_y : string, optional
        Dataframe key of the column with the error in y, by default ''
    show_legend : bool, optional
        Toggle between showing the legend in the plot, by default True
    error_fmt : str, optional
        Format of the errorbars, by default '-'

    Returns
    -------
    Figure
        Updated Figure object
    Axes
        Updated Axes object 
    """

    # Remove the +/- toggles on number inputs
    st.markdown("""<style>
        button.step-up {display: none;}
        button.step-down {display: none;}
        div[data-baseweb] {border-radius: 4px;}
        </style>""",unsafe_allow_html=True) 
    
    scale_options = ['linear', 'log']
    error_options = [True, False]

    if source_type == 'Var':
        # Remove parameters that are 'zero' over the full 'x' range
        pars = get_nonzero_parameters(pars, data_org, choice_voltage)
        data = data_org[data_org['Vext'] == choice_voltage] # Plot the data for the chosen voltage
    else:
        data = data_org

    with cols[2]:
        if show_plot_param or show_yscale or show_xscale:
            # Figure options
            st.markdown('<br>', unsafe_allow_html=True)
            st.markdown('<hr>', unsafe_allow_html=True)

        with st.expander('Figure options', expanded=True):
            # Select which parameters to plot
            if show_plot_param:
                options = st.multiselect('Parameters to plot:', list(pars.keys()), list(pars.keys()), key = str(plot_no) + '-par-options')
                st.markdown('<br>', unsafe_allow_html=True)
                st.markdown('<br>', unsafe_allow_html=True)
            else:
                options =  list(pars.keys())

            # Select the y-scale
            if show_yscale:
                st.text('y-scale:')
                yscale = st.radio('y-scale', scale_options, index = yscale_init, key = str(plot_no) + '-y-scale', label_visibility='collapsed',horizontal=True)
            else:
                yscale = scale_options[yscale_init]

            # Select the x-scale
            if show_xscale:
                st.text('x-scale:')
                xscale = st.radio('x-scale', scale_options, index = xscale_init, key = str(plot_no) + '-x-scale', label_visibility='collapsed',horizontal=True)
            else:
                xscale = scale_options[xscale_init]

            # Show the x,y range input fields to rescale the plot
            if show_xrange:
                if xrange_val is None:
                    # Use the min and max values of the selected parameter as limits with a margin of 5% of the range to prevent the data from merging with the axis
                    xlow_init = data[x_key].min()
                    xup_init = data[x_key].max()

                    # Use 5% of the interval
                    x_5p = abs((xup_init - xlow_init) * 0.05)
                    # Subtract this value from the lower limit
                    xlow_init -= x_5p
                    # Add this value to the upper limit
                    xup_init += x_5p

                    # round to two decimals to not display the full float
                    if 'f' in xrange_format:
                        xlow_init = round(xlow_init,2)
                        xup_init = round(xup_init,2)
                else:
                    # Limit values provided by the user as arguments
                    xlow_init = xrange_val[0]
                    xup_init = xrange_val[1]
  
                st.text('Set the x-axis range:')
                col1_x, col2_x, = st.columns([1,1])
                with col1_x:
                    xlow = st.number_input('X-range', value = xlow_init, key = str(plot_no) + '-xrange_low',label_visibility="collapsed", format=xrange_format)
                with col2_x:
                    xup = st.number_input('X-range', value=xup_init, key = str(plot_no) + '-xrange_up',label_visibility="collapsed", format=xrange_format)

            if show_yrange:
                if yrange_val is None:
                    # Get the lowest and highest value of the selected parameters
                    ylow_init = data[options[0]].min()
                    yup_init = data[options[0]].max()
                    for par in options:
                        ylow_init = min(ylow_init, data[par].min())
                        yup_init = max(yup_init, data[par].max())

                    # Use 5% of the interval
                    y_5p = abs((yup_init - ylow_init) * 0.05)
                    # In a log plot, the lower limit should be above zero
                    if yscale == 'log' and ylow_init - y_5p <= 0:
                        ylow_init = min(num for num in data[options[0]] if num > 0) if any(num > 0 for num in data[options[0]]) else 0
                        for par in options:
                            smallest_pos_value = min(num for num in data[par] if num > 0) if any(num > 0 for num in  data[par]) else 1

                            ylow_init = min(ylow_init, smallest_pos_value)
                    else:
                        # Subtract this value from the lower limit
                        ylow_init -= y_5p
                    # Add this value to the upper limit
                    yup_init += y_5p

                st.text('Set the y-axis range:')
                col1_y, col2_y, = st.columns([1,1])
  
                with col1_y:
                    ylow = st.number_input('Y-range', value=ylow_init, key = str(plot_no) + '-yrange_low',label_visibility="collapsed", format=yrange_format)
                with col2_y:
                    yup = st.number_input('Y-range', value=yup_init, key = str(plot_no) + '-yrange_up',label_visibility="collapsed", format=yrange_format)

            # Show the error margin on y1 axis
            if plot_type == plt.errorbar:
                xyerror = st.radio('Show error margins', error_options, index = 0, key = str(1) + '-error_margin')
            else:
                xyerror = error_options[0]

    with cols[1]:
        # Create plot
        fig, ax = plt.subplots()
        if weight_key != '':
            ax,fig = utils_plot.plot_result_colorbar_single( data[x_key],data[options[0]],data[weight_key], ax,fig, xlabel, 
                                                                ylabel, weight_label,weight_norm, title,xscale, yscale,)
        else:
            if xyerror and plot_type == plt.errorbar:
                if error_x == '' and  error_y != '':
                    # Only y errorbar
                    ax = utils_plot.plot_result(data, pars, options, x_key, xlabel, ylabel,xscale, yscale, title, ax, plot_type, y_error=data[error_y],legend=show_legend,error_fmt=error_fmt)
                elif error_x != '' and error_y == '':
                    # only x errorbar
                    ax = utils_plot.plot_result(data, pars, options, x_key, xlabel, ylabel,xscale, yscale, title, ax, plot_type, x_error = data[error_x],legend=show_legend,error_fmt=error_fmt)
                elif error_x != '' and not error_y != '':
                    # both x and y errorbars
                    ax = utils_plot.plot_result(data, pars, options, x_key, xlabel, ylabel,xscale, yscale, title, ax, plot_type, x_error = data[error_x], y_error=data[error_y],legend=show_legend,error_fmt=error_fmt)
                else:
                    # no errorbars
                    ax = utils_plot.plot_result(data, pars, options, x_key, xlabel, ylabel,xscale, yscale, title, ax, plot_type,legend=show_legend,error_fmt=error_fmt)

            else:
                ax = utils_plot.plot_result(data, pars, options, x_key, xlabel, ylabel,xscale, yscale, title, ax, plt.plot,legend=show_legend)
        
        # Set the x,y range, independent of plot type and/or errorbars
        if show_xrange:
            ax.set_xlim(xlow, xup)
        if show_yrange:
            ax.set_ylim(ylow, yup)

        return fig,ax

def create_UI_component_plot_twinx(data_org, pars, selected_1, selected_2, x_key, xlabel, ylabel_1, ylabel_2, title, fig, ax_1, ax_2, 
                             cols, show_plot_param=True, show_yscale_1=True, show_yscale_2 = True, 
                              yscale_init_1 = 0, yscale_init_2 = 0, show_errors=True, yerror_1 = [], yerror_2 = []):
    """_summary_

    Parameters
    ----------
    data_org : DataFrame
        Unfiltered data to plot
    pars : dict
        Dict with all potential parameters to plot. Keys represent the names in the dataFrama, values are the corresponding labels
    selected_1 : List
        Name of selected parameter to plot on the left y-axis
    selected_2 : List
        Name of selected parameter to plot on the right y-axis
    x_key : string
        Key in the dataframe for the 'x' axis data
    xlabel : string
        Label for the x-axis. Format: parameter [unit]
    ylabel_1 : string
        Label for the left y-axis. Format: parameter [unit]
    ylabel_2 : string
        Label for the left y-axis. Format: parameter [unit]
    title : string
        Title of the plot
    fig : Figure
        Figure object
    ax_1 : axes
        Axes object for the plot (left)
    ax_2 : axes
        Axes object for the plot (right)
    cols : List
        List with columns to plot figure in (Streamlit specific)
    show_plot_param : bool, optional
        Show the multiselectbox to select which parameters to plot, by default True
    show_yscale_1 : bool, optional
        Show a radio toggle to switch between a linear or log y scale (left), by default true
    show_yscale_2 : bool, optional
        Show a radio toggle to switch between a linear or log y scale (right), by default true
    yscale_init_1 : int, optional
        Initial scale of the left y-axis, used in yscale_options, by default 0
    yscale_init_2 : int, optional
        Initial scale of the right y-axis, used in yscale_options, by default 0
    show_errors : bool, optional
        Toggle between showing errors, by default True
    yerror_1 : List, optional
        List with error values for the left axis
    yerror_2 : List, optional
        List with error values for the right axis    
    """
    #Only support for impedance plot currently
    
    scale_options = ['linear', 'log']
    error_options = [True, False]

    with cols[2]:
        if show_plot_param or show_yscale_1 or show_yscale_2:
            # Figure options
            st.markdown('<br>', unsafe_allow_html=True)
            st.markdown('<hr>', unsafe_allow_html=True)

        with st.expander('Figure options', expanded=True):
            # Select which parameters to plot
            if show_plot_param:
                options = st.multiselect('Parameters to plot:', list(pars.keys()), list(pars.keys()), key = str(1) + '-par-options' + str(selected_1))
                st.markdown('<br>', unsafe_allow_html=True)
                st.markdown('<br>', unsafe_allow_html=True)
            else:
                options =  list(pars.keys())

            # Show the error margin on y1 axis
            if show_errors:
                st.text('Show error margins::')
                yerror = st.radio('Show error margins', error_options, index = 0, key = str(1) + '-y-error' + str(selected_1), label_visibility='collapsed',horizontal=True)
            else:
                yerror = error_options[1]

            # Select the y1-scale
            if show_yscale_1:
                st.text('y-scale (Left):')
                yscale_1 = st.radio('y-scale (Left)', scale_options, index = yscale_init_1, key = str(1) + '-y1-scale' + str(selected_1), label_visibility='collapsed',horizontal=True)
            else:
                yscale_1 = scale_options[yscale_init_1]

            # Select the y2-scale
            if show_yscale_2:
                st.text('y-scale (Right):')
                yscale_2 = st.radio('y-scale (Right)', scale_options, index = yscale_init_2, key = str(1) + '-y2-scale' + str(selected_1), label_visibility='collapsed',horizontal=True)
            else:
                yscale_2 = scale_options[yscale_init_2]

            # Set the x range
            # Use the min and max values of the selected parameter as limits with a margin of 5% of the range to prevent the data from merging with the axis
            xlow_init = data_org[x_key].min()
            xup_init = data_org[x_key].max()

            # Use 5% of the interval
            x_5p = abs((xup_init - xlow_init) * 0.05)

            # Subtract this value from the lower limit
            # In a log plot, the lower limit should be above zero
            if xlow_init - x_5p <= 0:
                xlow_init = xlow_init
            else:
                # Subtract this value from the lower limit
                xlow_init -= x_5p

            # Add this value to the upper limit
            xup_init += x_5p

            st.text('Set the x-axis range:')
            col1_x, col2_x, = st.columns([1,1])
            with col1_x:
                xlow = st.number_input('X-range', value = xlow_init, key = 'Bode-xrange_low-' + str(selected_1),label_visibility="collapsed", format="%.2e")
            with col2_x:
                xup = st.number_input('X-range', value=xup_init, key = 'Bode-xrange_up-' + str(selected_1),label_visibility="collapsed", format="%.2e")

            # Set the y (Left) range
            # Get the lowest and highest value of the selected parameters
            ylow_init_left = data_org[selected_1].min().iloc[0]
            yup_init_left = data_org[selected_1].max().iloc[0]

            # Use 5% of the interval
            y_5p_left = abs((yup_init_left - ylow_init_left) * 0.05)

            # In a log plot, the lower limit should be above zero
            if yscale_1 == 'log' and ylow_init_left - y_5p_left <= 0:
                ylow_init_left = ylow_init_left
            else:
                # Subtract this value from the lower limit
                ylow_init_left -= y_5p_left
            # Add this value to the upper limit
                yup_init_left += y_5p_left

            st.text('Set the y-axis range (Left):')
            col1_y_left, col2_y_left, = st.columns([1,1])

            with col1_y_left:
                ylow_left = st.number_input('Y-range', value=ylow_init_left, key = 'Bode-left-yrange_low-' + str(selected_1),label_visibility="collapsed", format="%.2e")
            with col2_y_left:
                yup_left = st.number_input('Y-range', value=yup_init_left, key = 'Bode-left-yrange_up-' + str(selected_1),label_visibility="collapsed", format="%.2e")

            # Set the y (Right) range
            # Get the lowest and highest value of the selected parameters
            ylow_init_right = data_org[selected_2].min().iloc[0]
            yup_init_right = data_org[selected_2].max().iloc[0]

            # Use 5% of the interval
            y_5p_right = abs((yup_init_right - ylow_init_right) * 0.05)

            # In a log plot, the lower limit should be above zero
            if yscale_2 == 'log' and ylow_init_right - y_5p_right <= 0:
                ylow_init_right = ylow_init_right
            else:
                # Subtract this value from the lower limit
                ylow_init_right -= y_5p_right
            # Add this value to the upper limit
                yup_init_right += y_5p_right

            st.text('Set the y-axis range (Right):')
            col1_y_right, col2_y_right, = st.columns([1,1])

            with col1_y_right:
                ylow_right = st.number_input('Y-range', value=ylow_init_right, key = 'Bode-right-yrange_low-' + str(selected_2),label_visibility="collapsed", format="%.2e")
            with col2_y_right:
                yup_right = st.number_input('Y-range', value=yup_init_right, key = 'Bode-right-yrange_up-' + str(selected_2),label_visibility="collapsed", format="%.2e")

    with cols[1]:
        # Create plot
        if yerror:
            ax = utils_plot.plot_result_twinx(data_org, pars, selected_1, selected_2, x_key, xlabel, ylabel_1, ylabel_2, 'log', yscale_1, yscale_2, title,ax_1,ax_2, 
                                        plt.errorbar,y_error_1 = yerror_1, y_error_2 = yerror_2)   
        else:
            ax = utils_plot.plot_result_twinx(data_org, pars, selected_1, selected_2, x_key, xlabel, ylabel_1, ylabel_2, 'log', yscale_1, yscale_2, title,ax_1,ax_2, 
                                        plt.plot)
            
        ax.set_xlim(xlow, xup)
        ax_1.set_ylim(ylow_left, yup_left)
        ax_2.set_ylim(ylow_right, yup_right)
            
        st.pyplot(fig, format='png')
