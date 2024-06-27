""" Functions specific for CV simulations"""
######### Package Imports #########################################################################

import os

######### Function Definitions ####################################################################    

def read_CV_parameters(CV_par, dev_par):
    """Store all CV related parameters into a single dictionary

    Parameters
    ----------
    CV_par : List
        List with CV specific parmaters
    dev_par : List
        List with the device parameters

    Returns
    -------
    dict
        Dictionary with CV related parameters
    """
    CV_par_obj = {}
    CV_par_obj['freq'] = CV_par[0][1] 
    CV_par_obj['Vmin'] = CV_par[1][1] 
    CV_par_obj['Vmax'] = CV_par[2][1] 
    CV_par_obj['delV'] = CV_par[3][1] 
    CV_par_obj['Vstep'] = CV_par[4][1]
    CV_par_obj['G_frac'] = CV_par[5][1] 

    for section in dev_par[1:]:
    # tVG file location
        if section[0] == 'User interface':
            for param in section:
                if param[1] == 'tVGFile':
                    CV_par_obj['tVGFile'] = param[2]
                if param[1] == 'tJFile':
                    CV_par_obj['tJFile'] = param[2]
    
    return CV_par_obj

def read_CV_par_file(session_path, CVParsFile, CVPars):
    """When the CV parameter file already exists, use these parameters.

    Parameters
    ----------
    session_path : string
        Path of the simulation folder for this session
    CVParsFile : string
        Name of the CV parameter file
    CVPars : List 
        List with the CV parameters to show

    Returns
    -------
    List
        List with updated CV parameters to show
    """
    #ToDo fix setting correct param!
    with open(os.path.join(session_path, CVParsFile), encoding='utf-8') as fp_CV:
        for line in fp_CV:
            line_element = line.split('=')
            if line_element[0].strip() == 'tVGFile' or line_element[0].strip() == 'tJFile':
                continue
            elif line_element[0].strip() == 'G_frac':
                for item in CVPars:
                    if item[0] == 'G_frac':
                        item[1] = float(line_element[1].strip())
            elif line_element[0].strip() == 'fstep':
                for item in CVPars:
                    if item[0] == 'fstep':
                        item[1] = int(line_element[1].strip())
            else:
                for item in CVPars:
                    if item[0] == line_element[0].strip():
                        item[1] = float(line_element[1].strip())
    fp_CV.close()

    return CVPars