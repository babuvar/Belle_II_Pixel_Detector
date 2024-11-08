import math as mt
import numpy as np

ringscore = 1.45
mid= mt.floor(10*ringscore) /10

for i in np.arange(mid-0.5, mid+0.5, 0.1):
    print i

