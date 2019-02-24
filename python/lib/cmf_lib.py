__author__ = "Christian Kongsgaard"
__license__ = "GNU GPLv3"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import datetime
import json
from collections import OrderedDict


# Livestock imports

# Grasshopper imports

# -------------------------------------------------------------------------------------------------------------------- #
# CMF Component Functions


def load_retention_curve(soil_index, properties_dict={}):
    """
    | Loads the retention curve data and converts it into a order dict.
    | If any property is to be overwritten it is also done in this function.

    """

    data_path = os.getenv('APPDATA') + r'\McNeel\Rhinoceros\5.0\scripts\livestock\data'

    with open(os.path.join(data_path, 'retention_curves.json')) as file:
        file_data = json.load(file)

    data = file_data['data']
    soil_index = int(soil_index)

    properties = OrderedDict([
        ('type', data[soil_index][0]),
        ('k_sat', data[soil_index][1]),
        ('phi', data[soil_index][2]),
        ('alpha', data[soil_index][3]),
        ('n', data[soil_index][4]),
        ('m', data[soil_index][5]),
        ('l', data[soil_index][6])
    ])

    # Set modified properties
    for key in properties_dict.keys():
        if properties_dict[key]:
            properties[key] = properties_dict[key]

    return properties


def load_surface_cover(surface_index, properties_dict={}):
    """
    | Loads the surface cover data and converts it into a order dict.
    | If any property is to be overwritten it is also done in this function.

    """

    data_path = os.getenv('APPDATA') + r'\McNeel\Rhinoceros\5.0\scripts\livestock\data'
    surface_index = int(surface_index)

    if surface_index != 7:
        with open(os.path.join(data_path, 'vegetation_data.json')) as file:
            file_data = json.load(file)

        data = file_data['data']
        properties = OrderedDict([
            ('name', data[surface_index][0]),
            ('height', data[surface_index][1]),
            ('lai', data[surface_index][2]),
            ('albedo', data[surface_index][3]),
            ('canopy_closure', data[surface_index][4]),
            ('canopy_par', data[surface_index][5]),
            ('canopy_capacity', data[surface_index][6]),
            ('stomatal_res', data[surface_index][7]),
            ('root_depth', data[surface_index][8]),
            ('root_fraction', data[surface_index][9]),
            ('leaf_width', data[surface_index][10]),
        ])

    elif surface_index == 7:
        with open(os.path.join(data_path, 'synthetic_deciduous.json')) as file:
            file_data = json.load(file)
        data = file_data['data']

        if properties_dict['height']:
            height = properties_dict['height']
        else:
            height = 5

        properties = compute_tree(height, data)

    else:
        raise ValueError('Surface Index was out of bound! It should be less than or equal to 7. '
                         'Given value was: ' + str(surface_index))

    # Set modified properties
    for key in properties_dict.keys():
        if properties_dict[key]:
            properties[key] = properties_dict[key]

    return properties


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


def retention_curve_units():
    units = OrderedDict([
        ('K_sat', 'm/day'),
        ('Phi', 'm3/m3'),
        ('Alpha', '1/cm'),
        ('N', '-'),
        ('M', '-'),
        ('L', '-')
    ])
    return units


def vegetation_units():
    units = OrderedDict([
        ('Height', 'm'),
        ('LeafAreaIndex', '-'),
        ('Albedo', '-'),
        ('CanopyClosure', '-'),
        ('CanopyPARExtinction', '-'),
        ('CanopyCapacityLAI', '-'),
        ('StomatalResistance', 's/m'),
        ('RootDepth', 'm'),
        ('FractionRootDepth', '-'),
        ('LeafWidth', 'm')
    ])
    return units


def compute_tree(height, tree_data):
    """Selects the correct tree property. It computes the property information and stores it as a ordered dict."""

    tree = OrderedDict(
        [('name', 'Deciduous Tree - ' + str(height) + 'm'),
         ('height', height),
         ('lai', tree_data[0][2] * height + tree_data[1][2]),
         ('albedo', tree_data[0][3] * height + tree_data[1][3]),
         ('canopy_closure', tree_data[2][4]),
         ('canopy_par', tree_data[2][5]),
         ('canopy_capacity', tree_data[0][6] * height + tree_data[1][6]),
         ('stomatal_res', tree_data[0][7] * height + tree_data[1][7]),
         ('root_depth', tree_data[2][8]),
         ('root_fraction', tree_data[2][9]),
         ('leaf_width', 0.05)
         ])

    return tree
