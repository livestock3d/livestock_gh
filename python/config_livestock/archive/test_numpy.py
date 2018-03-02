import numpy as np

"""
a = np.array([[1,2,3],[4,5,6]])
b = np.array([1,2,3])
c = b.T
d = a.T
e = np.append(c,b)
print('a')
print(a)
print(a.shape)
print('\nb')
print(b)
print(b.shape)
print('\nc')
print(c)
print(c.shape)
print('\nd')
print(d)
print(d.shape)
print('\ne')
print(e)
print(e.shape)



a = np.array([1.97889260451, 1.96107872327, -0.996134022872])
b = [np.array([1.97889260451, 1.96107872327, -0.996134022872]), np.array([2.03892119726,2.02110727628,-0.996134022872]),np.array([1.97889260451,1.96107872327,-0.996134022872])]

for d in b:
    c = np.allclose(a, d)
    print(c)
"""

p0 = np.array([0,0,0])
p1 = np.array([3,0,0])
p2 = np.array([1.5,2,2])
p3 = np.array([0,0,0.2])
p4 = np.array([3,0,0.2])
p5 = np.array([1.5,2,0.2])

def lls(p0,p1,p2,p3):
    x1, y1, z1 = p0
    x2, y2, z2 = p1
    x3, y3, z3 = p2
    x4, y4, z4 = p3
    #px = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
    #py = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
    pz = ((x1*z2-z1*x2)*(z3-z4)-(z1-z2)*(x3*z4-z3*x4))/((x1-x2)*(z3-z4)-(z1-z2)*(x3-x4))
    print(pz)



def lineIntersection(p1,p2,p3,p4):
    v1 = (p2-p1)
    v2 = (p4-p3)

    cv12 = np.cross(v1,v2)
    cpv = np.cross((p1-p3),v2)
    t = np.linalg.norm(cpv)/np.linalg.norm(cv12)
    return p1+a*v1
