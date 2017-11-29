__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
from System import Array
import os
from itertools import chain
from xml.dom import minidom
import xml.etree.ElementTree as ET
# Livestock imports


# Grasshopper imports
import scriptcontext as sc
from Grasshopper import DataTree as Tree
from Grasshopper.Kernel.Data import GH_Path as Path


# -------------------------------------------------------------------------------------------------------------------- #
# Functions and Classes


def tree_to_list(input_, retrieve_base=lambda x: x[0]):
    """Returns a list representation of a Grasshopper DataTree"""

    def extend_at(path_, index, simple_input, rest_list):
        target = path[index]

        if len(rest_list) <= target:
            rest_list.extend([None] * (target-len(rest_list) + 1))
        if index == path.Length - 1:
            rest_list[target] = list(simple_input)
        else:
            if rest_list[target] is None:
                rest_list[target] = []
            extend_at(path_, index + 1, simple_input, rest_list[target])

    all_ = []
    for i in range(input_.BranchCount):
        path = input_.Path(i)
        extend_at(path, 0, input_.Branch(path), all_)

    return retrieve_base(all_)


def list_to_tree(input_, none_and_holes=True, source=[0]):
    """Transforms nestings of lists or tuples to a Grasshopper DataTree"""

    def proc(input_, tree, track):
        path = Path(Array[int](track))
        if len(input_) == 0 and none_and_holes:
            tree.EnsurePath(path)
            return
        for i, item in enumerate(input_):
            if hasattr(item, '__iter__'):  # if list or tuple
                track.append(i)
                proc(item, tree, track)
                track.pop()
            else:
                if none_and_holes:
                    tree.Insert(item, path, i)
                elif item is not None:
                    tree.Add(item, path)

    if input is not None:
        t = Tree[object]()
        proc(input_, t, source[:])
        return t


class PassClass:
    def __init__(self, pyClass, name):
        self.c = pyClass
        self.n = name

    def __repr__(self):
        return "Livestock." + self.n


def write_file(text, path, name, file_type='txt'):

    # Make file path name with extension
    file_path = os.path.join(path, name + "." + str(file_type))

    # Open file
    file_write = open(file_path, "w")

    # Write text data to file
    # If integer
    if isinstance(text, int):
        file_write.write(str(text))

    # If string
    elif isinstance(text, str):
        file_write.write(text)

    else:
        i = 0
        while i < len(text):
            if i == len(text) - 1:
                file_write.write(str(text[i]))
            else:
                file_write.write(str(text[i]) + "\n")
            i += 1

    # Close file
    file_write.close()


def flatten_list(l):
    """Ladybug - flattenList"""

    return list(chain.from_iterable(l))


def decompose_ladybug_location(_location):
    location_str = _location.split('\n')
    new_loc_str = ""

    # clean the idf file
    for line in location_str:
        if '!' in line:
            line = line.split('!')[0]
            new_loc_str = new_loc_str + line.replace(" ", "")
        else:
            new_loc_str = new_loc_str + line

        new_loc_str = new_loc_str.replace(';', "")

    site, location_name, latitude, longitude, time_zone, elevation = new_loc_str.split(',')

    latitude, longitude, time_zone, elevation = float(latitude), float(longitude), float(time_zone), float(elevation)

    return location_name, latitude, longitude, time_zone, elevation


def get_python_exe():
    py = str(sc.sticky["PythonExe"])

    return py
