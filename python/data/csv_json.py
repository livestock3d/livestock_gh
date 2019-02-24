__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import json
from lib.livestock_csv import read_csv

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


p1 = r'C:\Users\ocni\PycharmProjects\livestock_gh\python\data\retention_curves.csv'
p2 = r'C:\Users\ocni\PycharmProjects\livestock_gh\python\data\syntheticDeciduous.csv'
p3 = r'C:\Users\ocni\PycharmProjects\livestock_gh\python\data\vegetation_data.csv'


def retention(p):
    a = read_csv(p)
    #print(a)

    b = []
    for lst in a[1]:
        sub = []
        for elem in lst:
            try:
                sub.append(float(elem))
            except ValueError:
                sub.append(elem)
        b.append(sub)

    data = {}
    data['units'] = a[0]
    data['data'] = b

    print(data)
    with open(p[:-3]+'json', 'w') as file:
        pass
        json.dump(data, file)


retention(p3)