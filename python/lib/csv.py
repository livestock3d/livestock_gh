__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
#Functions and Classes

def read_csv(pathAndFile, header=True):

    data = []

    file_obj = open(pathAndFile,'r')
    for l in file_obj.readlines():
        line = l[:-1].split(",")
        data.append(line)
    file_obj.close()

    if header:
        header = data[0]
        data = data[1:]

        return header, data
    else:
        return data

def write_csv(pathAndFile, data, header=None, dimension=1):
    file_obj = open(pathAndFile, 'w')

    if header:
        header_str = ','.join(header)
        file_obj.write(header_str + '\n')

    if dimension == 1:
        for i in range(0,len(data)):
                file_obj.write(str(data[i]) + '\n')

    elif dimension == 2:
        for i in range(0,len(data)):
                file_obj.write(','.join([str(s) for s in data[i]]) + '\n')
    else:
        raise ValueError('dimension must be 1 or 2. Dimension given was:'+str(dimension))

    file_obj.close()

def add_column():
    return None

def add_row():
    return None