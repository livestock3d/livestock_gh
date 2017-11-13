__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import xml.etree.ElementTree as ET
import xmltodict
import numpy as np

# Livestock imports
import lib.csv as ls_csv

# -------------------------------------------------------------------------------------------------------------------- #
# Livestock Windows Misc Functions


def cmf_results(path):
    files = os.listdir(path)
    result_path = None
    lookup_path = None

    for f in files:
        if f.startswith('results'):
            result_path = path + '/' + f
        elif f.startswith('result_lookup'):
            lookup_path = path + '/' + f
        else:
            pass

    # Read look up file
    file_obj = open(lookup_path, 'r')
    line = file_obj.readline()
    lookup_dict = eval(line)

    for lookup_key in lookup_dict.keys():
        if lookup_key.startswith('cell'):
            cell_results(lookup_dict[lookup_key], result_path, path)
        elif lookup_key.startswith('layer'):
            layer_results(lookup_dict[lookup_key], result_path, path)
        else:
            pass


def cell_results(looking_for, result_file, folder):
    """Processes cell results"""

    # Initialize
    result_tree = ET.tostring(ET.parse(result_file).getroot())
    results = xmltodict.parse(result_tree)
    results_to_save = []

    # Find results
    for cell in results['result'].keys():
        if looking_for == 'evapotranspiration':
            evapo = np.array(eval(results['result'][cell]['evaporation']))
            transp = np.array(eval(results['result'][cell]['transpiration']))
            evapotransp = evapo + transp
            results_to_save.append(list(evapotransp))

        else:
            for result in results['result'][cell]:
                if result.startswith('layer'):
                    pass

                else:
                    if result == looking_for:
                        if result == 'heat_flux':
                            # Covert heat flux from MJ/(m2*day) to W/m2h
                            flux_MJ = np.array(eval(results['result'][cell][str(result)]))
                            flux_Wm2 = flux_MJ/0.0864
                            results_to_save.append(list(flux_Wm2))
                        else:
                            results_to_save.append(results['result'][cell][str(result)][1:-1])
                    else:
                        pass

    # Write files
    file_path = folder + '/' + looking_for + '.csv'
    ls_csv.write_csv(file_path, results_to_save, dimension=1)


def layer_results(lookup_list, result_file, folder):
    """Processes layer results"""

    result_tree = ET.tostring(ET.parse(result_file).getroot())
    results = xmltodict.parse(result_tree)

    for cell in results['results'].keys():
        pass
