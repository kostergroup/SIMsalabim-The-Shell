""" Functions specific for IMPS simulations"""
######### Package Imports #########################################################################

import os

######### Function Definitions ####################################################################    

def read_imps_parameters(imps_par, dev_par):
    """Store all imps related parameters into a single dictionary

    Parameters
    ----------
    imps_par : List
        List with imps specific parmaters
    dev_par : List
        List with the device parameters

    Returns
    -------
    dict
        Dictionary with imps related parameters
    """
    imps_par_obj = {}
    imps_par_obj['fmin'] = imps_par[0][1] 
    imps_par_obj['fmax'] = imps_par[1][1] 
    imps_par_obj['fstep'] = imps_par[2][1] 
    imps_par_obj['V0'] = imps_par[3][1] 
    imps_par_obj['fracG'] = imps_par[4][1]
    imps_par_obj['G_frac'] = imps_par[5][1] 


    for section in dev_par[1:]:
    # tVG file location
        if section[0] == 'User interface':
            for param in section:
                if param[1] == 'tVGFile':
                    imps_par_obj['tVGFile'] = param[2]
                if param[1] == 'tJFile':
                    imps_par_obj['tJFile'] = param[2]
    
    return imps_par_obj

def read_imps_par_file(session_path, IMPSParsFile, IMPSPars):
    """When the imps parameter file already exists, use these parameters.

    Parameters
    ----------
    session_path : string
        Path of the simulation folder for this session
    IMPSParsFile : string
        Name of the imps parameter file
    IMPSPars : List 
        List with the imps parameters to show

    Returns
    -------
    List
        List with updated imps parameters to show
    """
    #ToDo fix setting correct param!
    with open(os.path.join(session_path, IMPSParsFile), encoding='utf-8') as fp_imp:
        for line in fp_imp:
            line_element = line.split('=')
            if line_element[0].strip() == 'tVGFile' or line_element[0].strip() == 'tJFile':
                continue
            elif line_element[0].strip() == 'G_frac':
                for item in IMPSPars:
                    if item[0] == 'G_frac':
                        item[1] = float(line_element[1].strip())
            elif line_element[0].strip() == 'fstep':
                for item in IMPSPars:
                    if item[0] == 'fstep':
                        item[1] = int(line_element[1].strip())
            else:
                for item in IMPSPars:
                    if item[0] == line_element[0].strip():
                        item[1] = float(line_element[1].strip())
    fp_imp.close()

    return IMPSPars