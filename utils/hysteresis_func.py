""" Functions specific for JV hysteresis simulations"""
######### Package Imports #########################################################################

import os

######### Function Definitions ####################################################################    
def read_hysteresis_parameters(hyst_par, dev_par):
    """Store all hysteresis related parameters into a single dictionary

    Parameters
    ----------
    hyst_par : List
        List with hysteresis specific parmaters
    dev_par : List
        List with the device parameters

    Returns
    -------
    dict
        Dictionary with hysteresis related parameters
    """
    hyst_par_obj = {}
    hyst_par_obj['scan_speed'] = hyst_par[0][1] 
    hyst_par_obj['direction'] = hyst_par[1][1] 
    hyst_par_obj['G_frac'] = hyst_par[2][1] 
    hyst_par_obj['UseExpData'] = hyst_par[3][1] 
    hyst_par_obj['Vmin'] = hyst_par[4][1] 
    hyst_par_obj['Vmax'] = hyst_par[5][1] 
    hyst_par_obj['steps'] = hyst_par[6][1]
    hyst_par_obj['expJV_Vmin_Vmax'] = hyst_par[7][1] 
    hyst_par_obj['expJV_Vmax_Vmin'] = hyst_par[8][1] 
    
    for section in dev_par[1:]:
    # tVG file location
        if section[0] == 'User interface':
            for param in section:
                if param[1] == 'tVGFile':
                    hyst_par_obj['tVGFile'] = param[2]
    
    return hyst_par_obj

def read_hyst_par_file(session_path, hystParsFile, hystPars):
    """When the hysteresis parameter file already exists, use these parameters.

    Parameters
    ----------
    session_path : string
        Path of the simulation folder for this session
    hystParsFile : string
        Name of the hysteresis parameter file
    hystPars : List 
        List with the hysteresis parameters to show

    Returns
    -------
    _type_
        _description_
    """
    #ToDo fix setting correct param!
    with open(os.path.join(session_path, hystParsFile), encoding='utf-8') as fp_hyst:
        for line in fp_hyst:
            line_element = line.split('=')
            if line_element[0].strip() == 'tVGFile':
                continue
            elif line_element[0].strip() == 'G_frac':
                for item in hystPars:
                    if item[0] == 'G_frac':
                        item[1] = float(line_element[1].strip())
            elif line_element[0].strip() == 'direction' or line_element[0].strip() == 'steps' or line_element[0].strip() == 'UseExpData':
                for item in hystPars:
                    if item[0] == line_element[0].strip():
                        item[1] = int(line_element[1].strip())
            elif line_element[0].strip() == 'expJV_Vmin_Vmax' or line_element[0].strip() == 'expJV_Vmax_Vmin':
                for item in hystPars:
                    if item[0] == line_element[0].strip():
                        item[1] = line_element[1].strip()
            else:
                for item in hystPars:
                    if item[0] == line_element[0].strip():
                        item[1] = float(line_element[1].strip())
    fp_hyst.close()

    return hystPars