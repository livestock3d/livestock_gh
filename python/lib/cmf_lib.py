__author__ = "Christian Kongsgaard"
__license__ = "GNU GPLv3"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import collections
import os
import datetime
import json

# Livestock imports
import livestock.lib.livestock_csv as csv


# Grasshopper imports


# -------------------------------------------------------------------------------------------------------------------- #
# CMF Component Functions

def load_csv(data_path):
    """Loads a csv file with the retention curve data."""

    units, data = csv.read_csv(data_path)

    return units, data


def load_retention_curve(soil_index, properties_dict={}):
    """
    | Loads the retention curve data and converts it into a order dict.
    | If any property is to be overwritten it is also done in this function.

    """
    data_path = os.getenv('APPDATA') + \
                r'\McNeel\Rhinoceros\5.0\scripts\livestock\data\retention_curves.csv'

    units, data = load_csv(data_path)
    property = collections.OrderedDict([('type', str(data[soil_index][0])),
                                        ('k_sat', float(data[soil_index][1])),
                                        ('phi', float(data[soil_index][2])),
                                        ('alpha', float(data[soil_index][3])),
                                        ('n', float(data[soil_index][4])),
                                        ('m', float(data[soil_index][5])),
                                        ('l', float(data[soil_index][6]))
                                        ])

    # Set modified properties
    for key in properties_dict.keys():
        if properties_dict[key]:
            property[key] = properties_dict[key]

    return property


def load_surface_cover(surface_index, properties_dict={}):
    """
    | Loads the surface cover data and converts it into a order dict.
    | If any property is to be overwritten it is also done in this function.

    """

    data_path = os.getenv('APPDATA') + \
                r'\McNeel\Rhinoceros\5.0\scripts\livestock\data\vegetation_data.csv'
    units, data = load_csv(data_path)
    property_ = collections.OrderedDict([('name',
                                          str(data[surface_index][0])),
                                         ('height',
                                          float(data[surface_index][1])),
                                         ('lai',
                                          float(data[surface_index][2])),
                                         ('albedo',
                                          float(data[surface_index][3])),
                                         ('canopy_closure',
                                          float(data[surface_index][4])),
                                         ('canopy_par',
                                          float(data[surface_index][5])),
                                         ('canopy_capacity',
                                          float(data[surface_index][6])),
                                         ('stomatal_res',
                                          float(data[surface_index][7])),
                                         ('root_depth',
                                          float(data[surface_index][8])),
                                         ('root_fraction',
                                          float(data[surface_index][9])),
                                         ('leaf_width',
                                          float(data[surface_index][10])),
                                         ])

    # Set modified properties
    for key in properties_dict.keys():
        if properties_dict[key]:
            property_[key] = properties_dict[key]

    return property_


def default_solver_settings(modified_settings=dict()):
    settings = {'analysis_length': (24, 'h'),
                'time_step': (1, 'h'),
                'tolerance': 10 ** -8,
                'start_time': {'day': 1,
                               'month': 1,
                               'year': datetime.datetime.now().year}
                }

    # Set modified settings
    for key in modified_settings.keys():
        if modified_settings[key]:
            settings[key] = modified_settings[key]

    return settings


def default_outputs():
    output_dict = {'cell': ['surface_water_volume', ],
                   'layer': ['volume', ]}

    return output_dict


def load_cmf_result_file(file_path, result_type):
    with open(file_path, 'r') as json_file:
        result_data = json.load(json_file)

    if result_type == 'evapotranspiration':
        raise NotImplementedError('Load %i results is not '
                                  'implemented yet' % result_type)

    elif result_type == 'surface_water_volume':
        processed_result = []

        for index in range(len(result_data.keys())):
            cell = 'cell_' + str(index)
            processed_result.append(result_data[cell]['surface_water_volume'])

    elif result_type == 'surface_water_flux':
        raise NotImplementedError('Load %i results is not '
                                  'implemented yet' % result_type)

    elif result_type == 'heat_flux':
        raise NotImplementedError('Load %i results is not '
                                  'implemented yet' % result_type)

    elif result_type == 'volumetric_flux':
        raise NotImplementedError('Load %i results is not '
                                  'implemented yet' % result_type)

    elif result_type == 'potential':
        raise NotImplementedError('Load %i results is not '
                                  'implemented yet' % result_type)

    elif result_type == 'theta':
        raise NotImplementedError('Load %i results is not '
                                  'implemented yet' % result_type)

    elif result_type == 'volume':
        processed_result = []

        for cell in result_data.keys():
            layer_result = []
            for layer in result_data[cell]:
                if layer.startswith('layer'):
                    layer_result.append(result_data[cell][layer]['volume'])

            processed_result.append(layer_result)

    elif result_type == 'wetness':
        raise NotImplementedError('Load %i results is not '
                                  'implemented yet' % result_type)

    else:
        raise KeyError('Unknown result: %i to load.' % result_type)

    return processed_result
