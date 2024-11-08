import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
#from scipy.interpolate import  griddata
from scipy import interpolate
from scipy.ndimage import gaussian_filter
from scipy.interpolate import  Rbf
from matplotlib import cm



## add sensor region
rows=768
#r_start=1; r_end=768
#r_start=241; r_end=270
r_start=200; r_end=350
c_start=6; c_end=245

#reference samples
name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'
#current sample
#name_curr = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-72000_drift-6000_clear-off5000/clusterdb.h5'
#name_curr = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-60000_drift-4000_clear-off5000/clusterdb.h5'
name_curr = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-60000_drift-5000_clear-off3000/clusterdb.h5'

ring_data = tables.open_file(name_ring, mode="r")
ring_map = ring_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
ring_data.close()

#clusterdata = tables.open_file(fullname, mode="r")
## get the hitmap and cluster charge data
#hitmap = clusterdata.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]


#linear sum score
#ring_map = tables.open_file(name_ring, mode="r").root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
'''
flat_map = tables.open_file(name_flat, mode="r").root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
curr_map = tables.open_file(name_curr, mode="r").root.hitmap[r_start-1 : r_end, c_start-1 : c_end]

x=ring_map.flatten()
y=flat_map.flatten()
z=curr_map.flatten()

x_sq=np.sum(np.multiply(x,x))
y_sq=np.sum(np.multiply(y,y))
xy=np.sum(np.multiply(x,y))
zx=np.sum(np.multiply(z,x))
zy=np.sum(np.multiply(z,y))


nr_a=(y_sq*zx) - (xy*zy)
nr_b=(x_sq*zy) - (xy*zx)
dr=(x_sq*y_sq) - (xy*xy)

a = np.true_divide(nr_a,dr)
b = np.true_divide(nr_b,dr)

# z = ax + by => c[dx + (1-d)y]
c=a+b
d=np.true_divide(a,(a+b))

print "ring-like score = ", d
'''

#print ring_map.shape
lim=ring_map.shape[0]

x=np.zeros((lim, 240))
y=np.zeros((lim, 240))

for i in range(30):
    x[i,:]=i
for i in range(240):
    y[:,i]=i



# use RBF
rbf = Rbf(x.flatten(), y.flatten(), ring_map.flatten(), epsilon=2, smooth=1)

ZI = rbf(x, y)

fig=pl.figure(figsize=(15,15))
pl.imshow(ZI, interpolation="none",vmin=0, vmax=np.percentile(ZI, 95));
fig.savefig("rbf.png")
pl.close(fig)





#interpolation
#y=np.arange(768)
#x=np.arange(240)
#func = interpolate.interp2d(x, y, hitmap, kind='cubic')
#func = interpolate.interp2d(x, y, hitmap, kind='linear')
#hitmap_approx = func(x, y)

#other things
#hitmap_smooth=gaussian_filter(hitmap, sigma=5)
#hitmap_smooth=np.divmod(hitmap, 75)[0]



'''
proj = np.mean(hitmap,axis=0)
proj_sqrt = np.sqrt(proj)
mean=np.mean(proj_sqrt)
variance=np.var(proj_sqrt) 
vari=str(variance) 
vari=vari[:8]

fig=pl.figure(figsize=(15,15))
pl.subplot(311)
pl.imshow(hitmap, interpolation="none",vmin=0, vmax=np.percentile(hitmap, 95));  pl.title('Hitmap')
pl.subplot(312)
pl.plot(proj); pl.title('Hitmap : row-projection')
pl.subplot(313)
pl.plot(proj_sqrt); pl.title('sqrt(row-projection),    Variance(FOM) = %s'%vari)
pl.axhline(mean, color='r', linestyle='dashed', linewidth=1)
pl.text(0.7, 0.7,'variance = %s'%variance, fontsize=70)
#pl.text(0.7, 0.7,'variance = %s'%variance)
fig.savefig("algo/hitmap.png")
pl.close(fig)
clusterdata.close()
'''

'''
fig=pl.figure(figsize=(15,15))
pl.subplot(121)
pl.imshow(hitmap, interpolation="none",vmin=0, vmax=np.percentile(hitmap, 95));  pl.title('Hitmap')
pl.subplot(122)
#pl.imshow(hitmap_approx, vmax=np.percentile(hitmap_approx, 95))
pl.imshow(hitmap_smooth, vmax=np.percentile(hitmap_smooth, 95))
fig.savefig("algo/hitmap_1.png")
pl.close(fig)
clusterdata.close()
'''













