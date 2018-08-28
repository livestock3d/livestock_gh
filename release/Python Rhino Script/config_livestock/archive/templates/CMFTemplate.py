__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
# Imports
import sys
sys.path.insert(0, r'C:\livestock\python\classes')
import LivestockGH as ls
from CMFClasses import *
import os

#----------------------------------------------------------------------------------------------------------------------#
# Functions



weatherDic, treeDic, groundDic, mesh = load_cmf_files(path)


model = CMFModel()
model.run_model(weatherDic, treeDic, groundDic)




