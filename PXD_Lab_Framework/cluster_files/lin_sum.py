import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter



## add sensor region
rows=768
r_start=1; r_end=768
#r_start=241; r_end=270
#r_start=200; r_end=350
c_start=6; c_end=245

#reference samples
name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'
#current sample
#name_curr = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-72000_drift-6000_clear-off5000/clusterdb.h5'
#name_curr = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-60000_drift-4000_clear-off5000/clusterdb.h5'
#name_curr = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-60000_drift-5000_clear-off3000/clusterdb.h5'
name_curr = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-68000_drift-6000_clear-off4000/clusterdb.h5'


ring_data = tables.open_file(name_ring, mode="r")
ring_map = ring_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
ring_data.close()
flat_data = tables.open_file(name_flat, mode="r")
flat_map = flat_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
flat_data.close()
curr_data = tables.open_file(name_curr, mode="r")
curr_map = curr_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
curr_data.close()

ring_map=gaussian_filter(ring_map, sigma=5)
flat_map=gaussian_filter(flat_map, sigma=5)
curr_map=gaussian_filter(curr_map, sigma=5)


#normalize
ring_full=np.sum(ring_map)
flat_full=np.sum(flat_map)
curr_full=np.sum(curr_map)
c_flat=np.true_divide(ring_full,flat_full)
c_curr=np.true_divide(ring_full,curr_full)
flat_map=flat_map*c_flat
curr_map=curr_map*c_curr

norm=np.zeros(11)
ringness=np.zeros(11)

#vary 'a'
ran=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
#for a in ran:
for i in range(11):
    a=ran[i]
    calc_map=(a*ring_map)+((1-a)*flat_map)
    diff_map=calc_map - curr_map
    nor=np.linalg.norm(diff_map)
    norm[i]=nor
    ringness[i]=a

    fig=pl.figure(figsize=(15,15))
    pl.subplot(131)
    pl.imshow(curr_map, interpolation="none",vmin=0, vmax=np.percentile(ring_map, 95));
    pl.subplot(132)
    pl.imshow(calc_map, interpolation="none",vmin=0, vmax=np.percentile(flat_map, 95));
    pl.subplot(133)
    pl.imshow(diff_map, interpolation="none",vmin=0, vmax=np.percentile(diff_map, 95)); pl.colorbar()
    fig.savefig("lin_sum_%s.png"%a)
    pl.close(fig)


fig2=pl.figure()
pl.plot(ringness,norm)
fig2.savefig("lin_sum_fom.png")
pl.close(fig)









#linear sum score
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













