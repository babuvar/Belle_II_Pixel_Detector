import numpy as np
from scipy.ndimage import gaussian_filter

results={}


sigs=[1,2,3,4,5]

for sig in sigs:
    n=(8*sig)+1
    r=(n-1)/2
    kernel=np.zeros((n,n))

    #In this case (a,b)=(50,50)
    for i in range(n):
        for j in range(n):
            #print(10-r+i,i)
            test=np.zeros((101,101))
            test[50-r+i,50-r+j]=1
            result=gaussian_filter(test, sigma=sig)
            kernel[i,j]=result[50,50]

    #string='sigma_%s'%sig
    results['sigma_%s'%sig]=kernel


np.save('kernels.npy', results)
















