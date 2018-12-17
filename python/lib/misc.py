__author__ = "Christian Kongsgaard"
__license__ = "GNU GPLv3 "

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
from System import Array
import os
import math

# Livestock imports


# Grasshopper imports
import scriptcontext as sc
from Grasshopper import DataTree as Tree
from Grasshopper.Kernel.Data import GH_Path as Path


# -------------------------------------------------------------------------------------------------------------------- #
# Functions and Classes


def tree_to_list(tree_input):
    """Returns a list representation of a Grasshopper DataTree"""

    tree = []
    for i in range(tree_input.BranchCount):
        branch = tree_input.Branch(i)

        b_list = []

        for item in branch:
            b_list.append(item)

        tree.append(b_list)

    return tree


def list_to_tree(input_, none_and_holes=True, source=[0]):
    """
    | Transforms nestings of lists or tuples to a Grasshopper DataTree
    | `Source`__

    __ https://gist.github.com/piac/ef91ac83cb5ee92a1294
    """

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
    """Pass a class from one Grasshopper component to another."""

    def __init__(self, pyClass, name):
        self.c = pyClass
        self.n = name

    def __repr__(self):
        return "Livestock." + self.n


def write_file(text, path, name, file_type='txt'):
    """
    Writes a text file.

    :param text: Text to write.
    :param path: Directory to save it to.
    :param name: File name.
    :param file_type: File extension.
    """

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


def decompose_ladybug_location(_location):
    """
    Decompose a Ladybug Tools location in to a tuple.

    :param _location: Ladybug Location.
    :type _location: str
    :return: Tuple with location values.
    :rtype: tuple
    """

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
    """
    Collects the python.exe path from a sticky.

    :return: The python path.
    :rtype: str
    """

    py = str(sc.sticky["PythonExe"])

    return py


def hour_to_date(hour_of_the_year):
    """
    Transform a hour of the year into a string datetime on the format DD MMM HH:mm

    :param hour_of_the_year: Hour of the year
    :type hour_of_the_year: int
    :return: Datetime on format DD MMM HH:mm
    :rtype: str
    """

    #TODO - Make better code

    month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    number_of_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
    number_of_hours = [24 * days
                       for days in number_of_days]

    if hour_of_the_year % 8760 == 0:
        return str(31) + ' ' + 'DEC' + ' 24:00'

    for h in range(len(number_of_hours) - 1):
        if hour_of_the_year <= number_of_hours[h + 1]:
            month = month_list[h]
            break
    try:
        month
    except:
        month = month_list[h]  # for the last hour of the year

    if (hour_of_the_year) % 24 == 0:
        day = int((hour_of_the_year - number_of_hours[h]) / 24)
        time = str(24) + ':00'

    else:
        day = int((hour_of_the_year - number_of_hours[h]) / 24) + 1
        minutes = str(int(round((hour_of_the_year - math.floor(hour_of_the_year)) * 60)))

        if len(minutes) == 1:
            minutes = '0' + minutes

        time = str(int(hour_of_the_year % 24)) + ':' + minutes

    return str(day) + ' ' + str(month) + ' ' + str(time)