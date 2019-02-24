__author__ = "Christian Kongsgaard"
__license__ = "GNU GPLv3"


# -------------------------------------------------------------------------------------------------------------------- #
# Functions and Classes

def read_csv(path_and_file, header=True):
    data = []

    with open(path_and_file, 'r') as file_obj:
        for l in file_obj.readlines():
            line = l[:-1].split(",")
            data.append(line)

    if header:
        header = data[0]
        data = data[1:]

        return header, data
    else:
        return data


def write_csv(path_and_file, data, header=None, dimension=1):
    with open(path_and_file, 'w') as file_obj:

        if header:
            header_str = ','.join(header)
            file_obj.write(header_str + '\n')

        if dimension == 1:
            for i in range(0, len(data)):
                file_obj.write(str(data[i]) + '\n')

        elif dimension == 2:
            for i in range(0, len(data)):
                file_obj.write(','.join([str(s) for s in data[i]]) + '\n')
        else:
            raise ValueError('dimension must be 1 or 2. Dimension given was:' + str(dimension))
