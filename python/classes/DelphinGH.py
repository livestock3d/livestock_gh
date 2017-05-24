__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
#Functions and Classes


class DelphinMaterials:

    def __init__(self):
        self.matDir = r'C:\Program Files (x86)\IBK\Delphin 5.8\DB_material_data'
        self.matList = []

    def refreshList(self):
        from os import listdir
        from os.path import isfile, join
        self.matList = []
        for f in listdir(self.matDir):
            if isfile:
                f = f[:-3]
                self.matList.append((f.split('_')[0],int(f.split('_')[1])))

def rgbToHex(r,g,b):
    def clamp(x):
        return max(0, min(x, 255))

    return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))