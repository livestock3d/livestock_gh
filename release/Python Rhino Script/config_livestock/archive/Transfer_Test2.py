import sys
path = r'C:\Users\Christian\Desktop\Test_text.txt'

read = open(path, 'r')
lines = read.readlines()
line = []
for l in lines:
    line.append(float(l[:-1]))

#print(line)

x = line[0]
y = x * 2

#sys.stdout = y