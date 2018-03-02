# Imports
from pathlib import Path
home_user = str(Path.home())
from livestock_linux.lib_cmf import CMFModel
# Run CMF Model
folder = home_user + '/livestock/ssh'
result_path = folder + '/results.xml'
model = CMFModel(folder)
model.run_model(result_path)
# Announce that template finished and create out file
print('Finished with template')
file_obj = open('out.txt', 'w')
file_obj.close()