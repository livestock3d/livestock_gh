# Imports
from livestock.hydrology import run_model
# Run CMF Model
run_model(r'C:\Users\ocni\PycharmProjects\livestock_gh\grasshopper\tests\test_data\CMF_Slope_v0\cmf')
# Announce that template finished and create out file
print('Finished with template')
file_obj = open('out.txt', 'w')
file_obj.close()