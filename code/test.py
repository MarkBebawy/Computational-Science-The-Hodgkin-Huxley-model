import numpy as np
import matplotlib.pyplot as plt
from tools import rk4

def f(t,x):
  return x

t, y = rk4(f, 0 , [1], 0.001, 5000)
plt.plot(t,y[:,0])
plt.plot(t, np.exp(t))
plt.show()