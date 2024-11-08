import numpy as np
#from scipy.interpolate import Rbf
#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt
#from matplotlib import cm
from scipy.ndimage import gaussian_filter



#a=np.zeros((21,21))
#a[10,10]=1
#print a
#b=gaussian_filter(a, sigma=1)
#print b[10,10]

#input n : kernel grid size   (3,5,7,9,11...etc)
n=41
r=(n-1)/2
kernel=np.zeros((n,n))
#print kernel


#sig=1
#sig=2
#sig=3
#sig=4
sig=5




#In this case (a,b)=(10,10)
for i in range(n):
    for j in range(n):
        #print(10-r+i,i)
        test=np.zeros((101,101))
        test[50-r+i,50-r+j]=1
        result=gaussian_filter(test, sigma=sig)
        kernel[i,j]=result[50,50]

print kernel
















