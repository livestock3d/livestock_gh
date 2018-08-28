import numpy as np
import matplotlib.pyplot as plt

def f(x):
    return np.arccos(abs(x))

x = np.linspace(-1,1,100)
y = f(x)

plt.figure()
plt.plot(x,y)
plt.show()