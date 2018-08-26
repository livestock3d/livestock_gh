__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# ---------------------------------------------------------------------------- #
# Imports

# Module imports

# Livestock imports
import livestock.lib.geometry as gh_geo
from livestock.components.component import GHComponent
from livestock.components import component
import livestock.lib.misc as gh_misc

# Grasshopper imports

# ---------------------------------------------------------------------------- #
# Livestock Geometry Classes


class LoadMesh(GHComponent):
    """A component class that loads an .obj file onto the Grasshopper canvas"""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('required'),

                    1: {'name': 'Filename',
                        'description': 'Directory and file name of mesh',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'Load',
                        'description': 'Activates the component',
                        'access': 'item',
                        'default_value': False}}

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'Mesh',
                        'description': 'Loaded mesh'},
                    2: {'name': 'MeshData',
                        'description': 'Additional data if any'}}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 8
        self.description = 'Loads a mesh'
        self.checks = [False, False]

        # Data Parameters
        self.path = None
        self.load = None
        self.mesh = None
        self.data = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, path, load):
        """
        Gathers the inputs and checks them.

        :param path: Path where the mesh is saved.
        :param load: Load the mesh or not
        """

        # Gather data
        self.path = path
        self.load = self.add_default_value(load, 2)

        # Run checks
        self.check_inputs()

    def run(self):
        """
        In case all the checks have passed and Load is True the component runs.
        It loads the .obj file and its data if there is any.
        """

        if self.checks and self.load:
            self.mesh = gh_geo.import_obj(self.path)
            self.data = gh_geo.load_mesh_data(self.path)


class SaveMesh(GHComponent):

    """A component class that saves a Grasshopper mesh to an .obj file"""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('required'),

                    1: {'name': 'Mesh',
                        'description': 'Mesh to save',
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
                        'default_value': False},

                    5: component.inputs('optional'),

                    6: {'name': 'Data',
                        'description': 'Additional data if any',
                        'access': 'item',
                        'default_value': None},
                    }

        def outputs():
            return {0: component.outputs('readme')}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 7
        self.description = 'Saves a mesh and additional data'
        self.checks = [False, False]

        # Data Parameters
        self.mesh = None
        self.data = None
        self.dir = None
        self.name = None
        self.save = None

    def check_inputs(self):
        """Checks inputs and raises a warning if an input is not the correct type."""

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, mesh, dir_, name, save, data):
        """
        Gathers the inputs and checks them.

        :param mesh: Mesh that should be saved.
        :param data: Mesh data that should be saved.
        :param dir_: Directory where the files should be saved.
        :param name: Name for mesh.
        :param save: Whether to save or not.
        """

        # Gather data
        self.mesh = mesh
        self.data = data
        self.dir = dir_
        self.name = name
        self.save = self.add_default_value(save, 4)

        # Run checks
        self.check_inputs()

    def run(self, doc):
        """
        In case all the checks have passed and save is True the component runs.
        It saves the .obj file and its data if there is any.
        """

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
