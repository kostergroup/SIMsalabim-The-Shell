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
    imps_par_obj['gen_rate'] = imps_par[5][1] 


    for section in dev_par[1:]:
    # Generation profile
        if section[0] == 'Generation and recombination':
            for param in section:
                if param[1] == 'Gen_profile':
                    imps_par_obj['gen_profile'] = param[2]
    # tVG file location
        if section[0] == 'User interface':
            for param in section:
                if param[1] == 'tVG_file':
                    imps_par_obj['tVG_file'] = param[2]
                if param[1] == 'tj_file':
                    imps_par_obj['tj_file'] = param[2]
    
    return imps_par_obj

def read_imps_par_file(session_path, imps_pars_file, imps_pars):
    """When the imps parameter file already exists, use these parameters.

    Parameters
    ----------
    session_path : string
        Path of the simulation folder for this session
    imps_pars_file : string
        Name of the imps parameter file
    imps_pars : List 
        List with the imps parameters to show

    Returns
    -------
    List
        List with updated imps parameters to show
    """
    #ToDo fix setting correct param!
    with open(os.path.join(session_path, imps_pars_file), encoding='utf-8') as fp_imp:
        for line in fp_imp:
            line_element = line.split('=')
            if line_element[0].strip() == 'gen_profile' or line_element[0].strip() == 'tVG_file' or line_element[0].strip() == 'tj_file':
                continue
            elif line_element[0].strip() == 'gen_rate':
                for item in imps_pars:
                    if item[0] == 'gen_rate':
                        item[1] = float(line_element[1].strip())
            elif line_element[0].strip() == 'fstep':
                for item in imps_pars:
                    if item[0] == 'fstep':
                        item[1] = int(line_element[1].strip())
            else:
                for item in imps_pars:
                    if item[0] == line_element[0].strip():
                        item[1] = float(line_element[1].strip())
    fp_imp.close()

    return imps_pars