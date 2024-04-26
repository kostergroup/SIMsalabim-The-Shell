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
    CV_par_obj['gen_rate'] = CV_par[5][1] 

    for section in dev_par[1:]:
    # Generation profile
        if section[0] == 'Generation and recombination':
            for param in section:
                if param[1] == 'Gen_profile':
                    CV_par_obj['gen_profile'] = param[2]
    # tVG file location
        if section[0] == 'User interface':
            for param in section:
                if param[1] == 'tVG_file':
                    CV_par_obj['tVG_file'] = param[2]
                if param[1] == 'tj_file':
                    CV_par_obj['tj_file'] = param[2]
    
    return CV_par_obj

def read_CV_par_file(session_path, CV_pars_file, CV_pars):
    """When the CV parameter file already exists, use these parameters.

    Parameters
    ----------
    session_path : string
        Path of the simulation folder for this session
    CV_pars_file : string
        Name of the CV parameter file
    CV_pars : List 
        List with the CV parameters to show

    Returns
    -------
    List
        List with updated CV parameters to show
    """
    #ToDo fix setting correct param!
    with open(os.path.join(session_path, CV_pars_file), encoding='utf-8') as fp_CV:
        for line in fp_CV:
            line_element = line.split('=')
            if line_element[0].strip() == 'gen_profile' or line_element[0].strip() == 'tVG_file' or line_element[0].strip() == 'tj_file':
                continue
            elif line_element[0].strip() == 'gen_rate':
                for item in CV_pars:
                    if item[0] == 'gen_rate':
                        item[1] = float(line_element[1].strip())
            elif line_element[0].strip() == 'fstep':
                for item in CV_pars:
                    if item[0] == 'fstep':
                        item[1] = int(line_element[1].strip())
            else:
                for item in CV_pars:
                    if item[0] == line_element[0].strip():
                        item[1] = float(line_element[1].strip())
    fp_CV.close()

    return CV_pars