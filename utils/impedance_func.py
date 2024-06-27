""" Functions specific for impedance spectroscopy simulations"""
######### Package Imports #########################################################################

import os

######### Function Definitions ####################################################################    

def read_impedance_parameters(impedance_par, dev_par):
    """Store all impedance related parameters into a single dictionary

    Parameters
    ----------
    impedance_par : List
        List with impedance specific parmaters
    dev_par : List
        List with the device parameters

    Returns
    -------
    dict
        Dictionary with impedance related parameters
    """
    impedance_par_obj = {}
    impedance_par_obj['fmin'] = impedance_par[0][1] 
    impedance_par_obj['fmax'] = impedance_par[1][1] 
    impedance_par_obj['fstep'] = impedance_par[2][1] 
    impedance_par_obj['V0'] = impedance_par[3][1] 
    impedance_par_obj['delV'] = impedance_par[4][1]
    impedance_par_obj['G_frac'] = impedance_par[5][1] 


    for section in dev_par[1:]:
    # tVG file location
        if section[0] == 'User interface':
            for param in section:
                if param[1] == 'tVGFile':
                    impedance_par_obj['tVGFile'] = param[2]
                if param[1] == 'tJFile':
                    impedance_par_obj['tJFile'] = param[2]
    
    return impedance_par_obj

def read_impedance_par_file(session_path, impedanceParsFile, impedancePars):
    """When the impedance parameter file already exists, use these parameters.

    Parameters
    ----------
    session_path : string
        Path of the simulation folder for this session
    impedanceParsFile : string
        Name of the impedance parameter file
    impedancePars : List 
        List with the impedance parameters to show

    Returns
    -------
    List
        List with updated impedance parameters to show
    """
    #ToDo fix setting correct param!
    with open(os.path.join(session_path, impedanceParsFile), encoding='utf-8') as fp_imp:
        for line in fp_imp:
            line_element = line.split('=')
            if line_element[0].strip() == 'tVGFile' or line_element[0].strip() == 'tJFile':
                continue
            elif line_element[0].strip() == 'G_frac':
                for item in impedancePars:
                    if item[0] == 'G_frac':
                        item[1] = float(line_element[1].strip())
            elif line_element[0].strip() == 'fstep':
                for item in impedancePars:
                    if item[0] == 'fstep':
                        item[1] = int(line_element[1].strip())
            else:
                for item in impedancePars:
                    if item[0] == line_element[0].strip():
                        item[1] = float(line_element[1].strip())
    fp_imp.close()

    return impedancePars