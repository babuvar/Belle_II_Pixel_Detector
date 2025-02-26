import numpy as np
from scipy.interpolate import Rbf
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm

# 2-d tests - setup scattered data
x = np.random.rand(100)*4.0-2.0
y = np.random.rand(100)*4.0-2.0
z = np.exp(-(x-3)**2-y**2)+np.exp(-(x+3)**2-y**2)
ti = np.linspace(-2.0, 2.0, 100)
print "ti = ", ti.shape
XI, YI = np.meshgrid(ti, ti)
print "XI = ", XI

# use RBF
rbf = Rbf(x, y, z, epsilon=2)
ZI = rbf(XI, YI)

# plot the result
plt.subplot(1, 1, 1)
plt.pcolor(XI, YI, ZI, cmap=cm.jet)
plt.scatter(x, y, 100, z, cmap=cm.jet)
plt.title('RBF interpolation - multiquadrics')
plt.xlim(-2, 2)
plt.ylim(-2, 2)
plt.colorbar()
plt.savefig("test2.png")

