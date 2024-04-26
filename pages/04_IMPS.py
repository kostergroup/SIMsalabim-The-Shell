"""IMPS Simulations"""
######### Package Imports #########################################################################

import os
import streamlit as st
from utils import device_parameters as utils_devpar
from utils import device_parameters_gen as utils_devpar_gen
from utils import band_diagram as utils_bd
from utils import general as utils_gen
from utils import general_web as utils_gen_web
from utils import imps_func as utils_imps
from Experiments import imps as imps_exp
from datetime import datetime

######### Page configuration ######################################################################

st.set_page_config(layout="wide", page_title="SIMsalabim IMPS",
                   page_icon='./logo/SIMsalabim_logo_HAT.jpg')

# Load custom CSS
utils_gen_web.local_css('./utils/style.css')

# Remove the +/- toggles on number inputs
st.markdown("""<style>
                button.step-up {display: none;}
                button.step-down {display: none;}
                div[data-baseweb] {border-radius: 4px;}
                </style>""",unsafe_allow_html=True)

######### Parameter Initialisation ################################################################

# Only load the contents of the page (also the function definitions!) when a session id has been created including the necessary files and folders. 
# This means the whole page need to be in a conditional statement related related to the session id state variable.
if 'id' not in st.session_state:
    st.error('SIMsalabim simulation has not been initialized yet, return to SIMsalabim page to start a session.')
else:
    # Get Session ID & Folder paths from session states and store them in local variables
    id_session = str(st.session_state['id'])
    resource_path = str(st.session_state['resource_path'])
    zimt_path = str(st.session_state['zimt_path'])
    simss_device_parameters = str(st.session_state['simss_devpar_file'])
    zimt_device_parameters = str(st.session_state['zimt_devpar_file'])
    session_path = os.path.join(str(st.session_state['simulation_path']), id_session)
    imps_pars_file = 'imps_pars.txt'
    
    # default IMPS parameters
    imps_par = [['fmin', 1E-1, 'Hz, Minimum frequency'],
                ['fmax', 5E+06, 'Hz, Maximum frequency'],
                ['fstep', 20, 'Number of frequency steps'],
                ['V0', 0.3, 'V, Applied voltage'],
                ['fracG', 5e-2, 'Fraction to increase the intensity/generation rate with. Sets the size of the initial pertubation'],
                ['gen_rate',1.0, 'Generation rate. Note: When using the option [gen_profile = calc] this is Gfrac, all other cases it is Gehp']]

    # Object to hold device parameters and IMPS specific parameters (with defaults)
    dev_par = [] 
    if os.path.isfile(os.path.join(session_path, imps_pars_file)):
        imps_par = utils_imps.read_imps_par_file(session_path, imps_pars_file, imps_par)

    # UI Containers
    main_container_imps = st.empty()
    container_imps_par = st.empty()
    container_device_par = st.empty()
    bd_container_title = st.empty()
    bd_container_plot = st.empty()

    ######### Function Definitions ####################################################################

    def run_IMPS():
        """Run the IMPS simulation with the saved device parameters. 
        Display an error message (From SIMsalabim or a generic one) when the simulation did not succeed. 
        Save the used file names in global states to use them in the results.
        """
        with st.spinner('SIMulating...'):
            # Store all imps specific parameters into a single object.
            imps_par_obj = utils_imps.read_imps_parameters(imps_par, dev_par)

            # Run the imps script
            result, message = imps_exp.run_IMPS_simu(zimt_device_parameters, session_path, imps_par_obj["tVG_file"], imps_par_obj["fmin"],
                                                               imps_par_obj["fmax"],imps_par_obj["fstep"],imps_par_obj["V0"],
                                                               imps_par_obj["fracG"],imps_par_obj["gen_rate"],imps_par_obj["gen_profile"],True, 
                                                               tj_name=imps_par_obj['tj_file'])
        
        if result == 1:
            # Creating the tVG file for imps failed                
            st.error(message)

            res = 'FAILED'
        else:
            if result == 0 or result == 95:
                # Simulation succeeded, continue with the process
                st.success('Simulation complete. Output can be found in the Simulation results.')
                st.session_state['simulation_results'] = 'IMPS' # Init the results page to display results

                # Save the imps parameters in a file

                if os.path.isfile(os.path.join(session_path, imps_pars_file)):
                     os.remove(os.path.join(os.path.join(session_path, imps_pars_file)))
                with open(os.path.join(session_path, imps_pars_file), 'w') as fp_imps:
                    for key,value in imps_par_obj.items():
                        fp_imps.write('%s = %s\n' % (key, value))

                st.session_state['Exp_object'] = imps_par_obj
                st.session_state['imps_pars'] = imps_pars_file
                st.session_state['freqY_file'] = 'freqY.dat' # Currently a fixed name
        
                # Set the state variable to true to indicate that a new simulation has been run and a new ZIP file with results must be created
                st.session_state['run_simulation'] = True

                # Store the assigned file names from the saved device parameters in session state variables.
                utils_devpar.store_file_names(dev_par,'zimt')

                res = 'SUCCESS'
            else:
                # Simulation failed, show the error message
                st.error(message)

                res = 'FAILED'

        with open(os.path.join('Statistics', 'log_file.txt'), 'a') as f:
            f.write(id_session + ' IMPS ' + res + ' ' + str(datetime.now()) + '\n')


    def save_parameters():
        """Save the current state of the device parameters to the txt file used by the simulation
        """
        # Use this 'layer/inbetween' function to make sure the most recent device parameters are saved
        utils_devpar_gen.save_parameters(dev_par, session_path, zimt_device_parameters)
        utils_gen.exchangeDevPar(session_path, zimt_device_parameters, simss_device_parameters) ## update zimt parameters with simss parameters.

    def save_parameters_BD():
        """Save the device parameters and draw the band diagram.
        """
        save_parameters()
        # Draw the band diagram
        utils_bd.get_param_band_diagram(dev_par)

    def upload_gen_prof_file():
        """Write the generation profile file to the session folder. Update the genProf parameter and save them.

        Returns
        -------
        success
            Display a streamlit success message
        """
        utils_gen.upload_single_file_to_folder(uploaded_file, session_path)

        # Update the Gen_profile name with the name of the just uploaded file.
        for section in dev_par[1:]:
            if section[0] == 'Generation and recombination':
                for item_output_par in section:
                    if 'Gen_profile' in item_output_par[1]:
                        item_output_par[2] = uploaded_file.name
        save_parameters()

        return st.success('File upload complete')

    def upload_trap_level_file():
        """Write the trap level file to the session folder and save it.

        Returns
        -------
        success
            Display a streamlit success message
        """
        utils_gen.upload_single_file_to_folder(uploaded_file, session_path)

        save_parameters()

        return st.success('File upload complete')
    
    def upload_nk_file():
        """ Read and decode the uploaded nk_files and create  files.
        """

        utils_gen.upload_multiple_files_to_folder(uploaded_files, os.path.join(session_path,'Data_nk'))

        save_parameters()

        return st.success('File uploads complete')
    
    def upload_spectrum_file():
        """ Read and decode the uploaded spectrum and create  files.
        """
        utils_gen.upload_multiple_files_to_folder(uploaded_files, os.path.join(session_path,'Data_spectrum',))

        save_parameters()

        return st.success('File upload complete')

    def upload_devpar_file():
        """Write the device parameter file to the session folder. 

        Returns
        -------
        success
            Display a streamlit success message
        """
        utils_gen.upload_single_file_to_folder(uploaded_file, session_path, True, zimt_device_parameters)

        return st.success('Upload device parameters complete')
    
    def create_nk_spectrum_file_array():
        """Create lists containing the names of the available nk and spectrum files.

        Returns
        -------
        List,List
            Lists with nk file names and spectrum file names
        """
        nk_file_list = []
        spectrum_file_list = []
        # Placeholder item when nk/spectrum file is not found
        nk_file_list.append('--none--')
        spectrum_file_list.append('--none--')
        for dirpath, dirnames, filenames in os.walk(os.path.join(session_path,'Data_nk')):
            for filename in filenames:
                nk_file_list.append(os.path.join('Data_nk',filename))
        for dirpath, dirnames, filenames in os.walk(os.path.join(session_path,'Data_spectrum')):
            for filename in filenames:
                spectrum_file_list.append(os.path.join('Data_spectrum',filename))
        return nk_file_list,spectrum_file_list

    def format_func(option):
        """Format function to split a string containing a /

        Parameters
        ----------
        option : string
            To be formatted string

        Returns
        -------
        string
            Last part of formatted string
        """
        filename_split = os.path.split(option)
        return filename_split[1]

    ######### UI layout ###############################################################################

    # Create lists containing the names of available nk and spectrum files. Including user uploaded ones.
    nk_file_list, spectrum_file_list = create_nk_spectrum_file_array()
    # Sort them alphabetically
    nk_file_list.sort(key=str.casefold)
    spectrum_file_list.sort(key=str.casefold)

    with st.sidebar:
        # UI component to upload a generation profile
        chk_genProfile = st.checkbox("Upload generation profile")
        if chk_genProfile:
            file_desc = "Select generation profile"
            uploaded_file = utils_gen_web.upload_file(file_desc, ['=', '@', '0x09', '0x0D'], '', False)
            if uploaded_file != None and uploaded_file != False:
                # File uploaded to memory successfull, enable the button to store the file in the session folder.
                st.button("Upload file", key='gen_prof', on_click=upload_gen_prof_file)
                st.markdown('<hr>', unsafe_allow_html=True)

        # UI component to upload a trap level file
        chk_traplevel = st.checkbox("Upload file with multiple trap levels")
        if chk_traplevel:
            file_desc = "Select file with multiple trap levels"
            uploaded_file = utils_gen_web.upload_file(file_desc, ['=', '@', '0x09', '0x0D'], '', False)
            if uploaded_file != None and uploaded_file != False:
                # File uploaded to memory successfull, enable the button to store the file in the session folder.
                st.button("Upload file", key='multiple_tl', on_click=upload_trap_level_file)
                st.markdown('<hr>', unsafe_allow_html=True)

        # UI component to upload nk files
        chk_nkvalue = st.checkbox("Upload files with n,k values")
        if chk_nkvalue:
            uploaded_files = st.file_uploader("Select files with n,k values",type=['txt'], accept_multiple_files=True, label_visibility='collapsed')
            if uploaded_files != None and uploaded_files != False:
                # File uploaded(s) to memory successfull, enable the button to store the file(s) in the session folder.
                st.button("Upload files", key='multiple_nk', on_click=upload_nk_file)
                st.markdown('<hr>', unsafe_allow_html=True)

        # UI component to upload spectrum files
        chk_spectrum = st.checkbox("Upload files with spectrum values")
        if chk_spectrum:
            uploaded_files = st.file_uploader("Select files with spectrum values",type=['txt'], accept_multiple_files=True, label_visibility='collapsed')
            if uploaded_files != None and uploaded_files != False:
                # File uploaded(s) to memory successfull, enable the button to store the file(s) in the session folder.
                st.button("Upload files", key='spectrum', on_click=upload_spectrum_file)
                st.markdown('<hr>', unsafe_allow_html=True)

        # UI component to upload a device parameter file
        chk_devpar = st.checkbox("Upload device parameters")
        if chk_devpar:
            file_desc = "Select device parameters file to upload"
            uploaded_file = utils_gen_web.upload_file(file_desc, [], '', 'zimt', nk_file_list, spectrum_file_list)
            if uploaded_file != None and uploaded_file != False:
                # File uploaded to memory successfull, enable the button to store the file in the session folder.
                st.button("Upload file", on_click=upload_devpar_file)
                st.markdown('<hr>', unsafe_allow_html=True)

        # Device Parameter buttons
        st.button('Save device parameters', on_click=save_parameters_BD)
        if os.path.isfile(os.path.join(session_path, zimt_device_parameters)):
            with open(os.path.join(session_path, zimt_device_parameters), encoding='utf-8') as fo:
                st.download_button('Download device parameters', fo, file_name=zimt_device_parameters)
                fo.close()

        reset_device_parameters = st.button('Reset device parameters')
        st.button('Run Simulation', on_click=run_IMPS)

    # Load the device_parameters file and create a List object.
    # Check if a session specific file already exists. If True, use this one, else return to the default device_parameters_simss.txt
    dev_par = utils_devpar_gen.load_device_parameters(session_path, zimt_device_parameters, zimt_path)

    # When the reset button is pressed, empty the container and create a List object from the default .txt file. Next, save the default parameters to the parameter file.
    if reset_device_parameters:
        main_container_imps.empty()
        with open(os.path.join(resource_path, zimt_device_parameters), encoding='utf-8') as fd:
            dev_par = utils_devpar_gen.devpar_read_from_txt(fd)
        save_parameters()

    with main_container_imps.container():
        st.title("Intensity Modulated PhotoSpectroscopy (IMPS)")
        st.write("""
            Simulate an IMPS experiment with SIMsalabim. The admittance is calculated at the applied voltage. 
            A small one time pertubation in light intensity at t=0 is introduced, defined as a fraction with which the generation rate is increased. 
            The admittance is calculated using Fourier decomposition, based on the method desrcibed in *S.E. Laux, IEEE Trans. Electron Dev. 32 (10), 2028 (1985)*.
        """)
        with container_imps_par.container():
            st.subheader('IMPS parameters')
            col_par_imps, col_val_imps, col_desc_imps = st.columns([2, 2, 8],)
            for imps_item in imps_par:
                with col_par_imps:
                    st.text_input(imps_item[0], value=imps_item[0], disabled=True, label_visibility="collapsed")

                # Parameter value
                with col_val_imps:
                    if imps_item[0] == 'fstep':
                        # Show these parameters as a float
                        imps_item[1] = st.number_input(imps_item[0] + '_val', value=imps_item[1], label_visibility="collapsed")
                    elif imps_item[0] == 'V0' or imps_item[0] == 'fracG' or imps_item[0] == 'gen_rate':
                        # Show these parameters as a float
                        imps_item[1] = st.number_input(imps_item[0] + '_val', value=imps_item[1], label_visibility="collapsed", format="%f")
                    else:
                        # Show all other parameters in scientific notation e.g. 1e+2
                        imps_item[1] = st.number_input(imps_item[0] + '_val', value=imps_item[1], label_visibility="collapsed", format="%e")
                # Parameter description
                with col_desc_imps:
                    st.text_input(imps_item[0] + '_desc', value=imps_item[2], disabled=True, label_visibility="collapsed")
            st.markdown('<hr>', unsafe_allow_html=True)

        with container_device_par.container():
            st.subheader('Device parameters')
        # Build the UI components for the various sections
            for par_section in dev_par:
                if par_section[0] == 'Description': 
                    # The first section of the page is a 'special' section and must be treated seperately.
                    # The SIMsalabim version number and general remarks to show on top of the page
                    version = [i for i in par_section if i[1].startswith('version:')]
                    st.write("SIMsalabim " + version[0][1])
                    # Reference to the SIMsalabim manual
                    st.write("""For more information about the device parameters or SIMsalabim itself, refer to the
                                    [Manual](https://raw.githubusercontent.com/kostergroup/SIMsalabim/master/Docs/Manual.pdf)""")
                else:
                    # Initialize expander components for each section
                    if (par_section[0]== 'Optics'):
                        # Do not expand the optics section by default and add a custom description string
                        expand=False
                        section_title = par_section[0] + ' (Optional, use only when calculating the generation profile i.e. Gen_profile=calc)'
                    elif (par_section[0]== 'Numerical Parameters' or par_section[0]== 'Voltage range of simulation' or par_section[0]== 'User interface'):
                        # Do not expand these sections by default but use the section name as section title
                        expand = False
                        section_title = par_section[0]
                    else:
                        # Expand all other sections and use the section name as section title
                        expand = True
                        section_title = par_section[0]
                    
                    # Fill the expanders/sections with the parameters
                    with st.expander(section_title, expanded=expand):
                        # Split component into three columns [name, value, description]
                        col_par, col_val, col_desc = st.columns([2, 2, 8],)
                        
                        for item in par_section[1:]:
                            if item[0] == 'comm': # Item is just a comment, do not use column layout for this.
                                st.write(item[1])
                                # Reset the column layout layout to force a break between the parameters to place the comment in the correct position. 
                                # Otherwise all comments will be placed at either the top or bottom of the components 
                                col_par, col_val, col_desc = st.columns([2, 2, 8]) 

                            if item[0] == 'par': # Item contains a parameter, fill all three columns
                                # Parameter name
                                with col_par:
                                    st.text_input(item[1], value=item[1], disabled=True, label_visibility="collapsed")

                                # Parameter value
                                with col_val:
                                    # Handle exceptions/special cases.
                                    if item[1].startswith('nk_'): # nk file name, use a selectbox.
                                        if item[2] not in nk_file_list:
                                            item[2] = '--none--'
                                        item[2] = st.selectbox(item[1] + '_val', options=nk_file_list, format_func=format_func, index=nk_file_list.index(item[2].replace('../','')), label_visibility="collapsed")
                                    elif item[1] == 'spectrum': # spectrum file name, use a selectbox.
                                        if item[2] not in spectrum_file_list:
                                            item[2] = '--none--'
                                        item[2] = st.selectbox(item[1] + '_val', options=spectrum_file_list, format_func=format_func, index=spectrum_file_list.index(item[2].replace('../','')), label_visibility="collapsed")
                                    elif item[1]== 'Pause_at_end':
                                        # This parameter must not be editable and forced to 0, otherwise the program will not exit/complete and hang forever.
                                        item[2] = 0
                                        item[2] = st.text_input(item[1] + '_val', value=item[2], disabled=True, label_visibility="collapsed")
                                    else:
                                        item[2] = st.text_input(item[1] + '_val', value=item[2], label_visibility="collapsed")
                                
                                # Parameter description
                                with col_desc:
                                    st.text_input(item[1] + '_desc', value=item[3], disabled=True, label_visibility="collapsed")
    
    #  Show the SIMsalabim logo in the sidebar
    with st.sidebar:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.image('./logo/SIMsalabim_logo_cut_trans.png')
