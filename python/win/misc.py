__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import xml.etree.ElementTree as ET
import xmltodict

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
        if lookup_key == 'cell':
            cell_results(lookup_dict[lookup_key], result_path, path)
        elif lookup_key == 'layer':
            layer_results(lookup_dict[lookup_key], result_path, path)
        else:
            pass


def cell_results(lookup_list, result_file, folder):
    """Processes cell results"""

    # Initialize
    result_tree = ET.tostring(ET.parse(result_file).getroot())
    results = xmltodict.parse(result_tree)
    results_to_save = {}

    for result in lookup_list:
        results_to_save[str(result)] = []

    # Find results
    for cell in results['result'].keys():

        for result in results['result'][cell]:

            if result == 'layer':
                pass

            else:
                for looking_for in lookup_list:
                    if result == looking_for:
                        results_to_save[str(looking_for)].append(result)
                    else:
                        pass

    # Write files
    for result_name in results_to_save.keys():
        file_path = folder + '/' + result_name + '.csv'
        ls_csv.write_csv(file_path, results_to_save[result_name], dimension=2)


def layer_results(lookup_list, result_file, folder):
    """Processes layer results"""

    result_tree = ET.tostring(ET.parse(result_file).getroot())
    results = xmltodict.parse(result_tree)

    for cell in results['results'].keys():
        pass

#cmf_results(r'C:\Users\Christian\Desktop\test_cmf\test_02')