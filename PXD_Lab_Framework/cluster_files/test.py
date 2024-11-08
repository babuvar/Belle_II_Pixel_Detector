import numpy as np


x = np.array([1,2])
y = np.array([3,5])
#print "norm = ", np.linalg.norm(x)

print "product = ",np.multiply(x,y)
print "norm of product = ", np.sum(np.multiply(x,y))
print np.sum(np.multiply(x,x))
