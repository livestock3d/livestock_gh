__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import xml.etree.ElementTree as ET
import collections
import subprocess
from shutil import copyfile

# Livestock imports
import gh.ssh as ssh
import gh.geometry as gh_geo
import lib.csv as csv
from comp.component import GHComponent
import gh.misc as gh_misc
from win.templates import pick_template

# Grasshopper imports
import rhinoscriptsyntax as rs

# -------------------------------------------------------------------------------------------------------------------- #
# Livestock Geometry Classes


class LoadMesh(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Filename',
                        'description': 'Directory and file name of mesh',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'Load',
                        'description': 'Activates the component',
                        'access': 'item',
                        'default_value': False}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'Mesh',
                        'description': 'Loaded mesh'},
                    2: {'name': 'MeshData',
                        'description': 'Additional data if any'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 8
        self.description = 'Loads a mesh'
        self.path = None
        self.load = None
        self.checks = [False, False]
        self.mesh = None
        self.data = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, path, load):

        # Gather data
        self.path = path
        self.load = self.add_default_value(load, 1)

        # Run checks
        self.check_inputs()

    def run(self):
        if self.checks and self.load:
            self.mesh = gh_geo.import_obj(self.path)
            self.data = gh_geo.load_mesh_data(self.path)


class SaveMesh(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Mesh',
                        'description': 'Mesh to save',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'Data',
                        'description': 'Additional data if any',
                        'access': 'item',
                        'default_value': None},
                    2: {'name': 'Directory',
                        'description': 'File path to save mesh to',
                        'access': 'item',
                        'default_value': None},
                    3: {'name': 'Filename',
                        'description': 'File name',
                        'access': 'item',
                        'default_value': None},
                    4: {'name': 'Save',
                        'description': 'Activates the component',
                        'access': 'item',
                        'default_value': False}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 7
        self.description = 'Saves a mesh and additional data'
        self.mesh = None
        self.data = None
        self.dir = None
        self.name = None
        self.save = None
        self.checks = [False, False]


    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, mesh, data, dir_, name, save):

        # Gather data
        self.mesh = mesh
        self.data = data
        self.dir = dir_
        self.name = name
        self.save = self.add_default_value(save, 4)

        # Run checks
        self.check_inputs()

    def run(self, doc):
        if self.checks and self.save:
            # Export mesh
            gh_geo.bake_export_delete(self.mesh, self.dir, self.name, '.obj', doc)
            print("Mesh saved to:\n" + self.dir + self.name + '.obj')

            if self.data:
                # Export mesh data
                gh_misc.write_file(self.data, self.dir, self.name + '_Data')
                print('Including ' + self.name + '_Data.txt contianing additional data')
            else:
                print('Without any additional data')
