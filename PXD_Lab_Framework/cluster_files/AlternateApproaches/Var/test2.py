import numpy as np
import numpy.ma as ma

x = np.array([2, 4, 6, 8])


print"x = ",x
print"mean of x = ", np.mean(x)


print"mean of x(x<7) = ",np.mean( x[np.nonzero(x < 7)] )
