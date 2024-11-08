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
#name_curr = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-68000_drift-6000_clear-off4000/clusterdb.h5'


ring_data = tables.open_file(name_ring, mode="r")
ring_map = ring_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
ring_data.close()
flat_data = tables.open_file(name_flat, mode="r")
flat_map = flat_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
flat_data.close()

#plot reference hitmaps
figu=pl.figure()
pl.subplot(121)
pl.imshow(ring_map, interpolation="none",vmin=0, vmax=np.percentile(ring_map, 95)); pl.title('Reference ring-hitmap')
pl.subplot(122)
pl.imshow(flat_map, interpolation="none",vmin=0, vmax=np.percentile(flat_map, 95)); pl.title('Reference flat-hitmap')
figu.savefig("ring_score/reference_hitmaps.png")
pl.close(figu)

wafer='W41_IF_2018_03_28_001'


'''
plot_dir=os.path.join('plots',wafer)
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

input_dir='/home/bonndaq_pc/tmp_hye/source_scan_opt/%s'%wafer
names = {}
for directory in os.listdir(input_dir):
    subdir =  os.path.join(input_dir,directory)
    if os.path.isdir(subdir):
        for filename in os.listdir(subdir):
            fullname = os.path.join(subdir,filename)
            names[directory] = fullname

for name, fullname in names.items():
    clusterdata = tables.open_file(fullname, mode="r")
    ## get the hitmap and cluster charge data
    hitmap = clusterdata.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
    fig=pl.figure(figsize=(15,15))
    pl.imshow(hitmap, interpolation="none",vmin=0, vmax=np.percentile(hitmap, 95)); pl.colorbar(); pl.title('Hitmap')
    #pl.imshow(hitmap, interpolation="none", origin="lower", aspect="auto", vmin=0, vmax=np.percentile(hitmap, 95))
    fig.savefig("plots/%s/hitmap_%s.png" %(wafer,name))
    pl.close(fig)
    clusterdata.close()
'''



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

#Analytical ring-score
 #linear sum score
x=ring_map.flatten()
y=flat_map.flatten()
z=curr_map.flatten()

x_sq=np.sum(np.multiply(x,x))
y_sq=np.sum(np.multiply(y,y))
xy=np.sum(np.multiply(x,y))
zx=np.sum(np.multiply(z,x))
zy=np.sum(np.multiply(z,y))

ring_score = np.true_divide(zx - xy -zy + y_sq, x_sq - (2*xy) + y_sq)
ring_score_s=str(ring_score)
ring_score_s=ring_score_s[:6]


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
    pl.imshow(curr_map, interpolation="none",vmin=0, vmax=np.percentile(curr_map, 95)); pl.title('Measured hitmap')
    pl.subplot(132)
    pl.imshow(calc_map, interpolation="none",vmin=0, vmax=np.percentile(calc_map, 95)); pl.title('Calculated hitmap; coeff = %s' %a)
    pl.subplot(133)
    pl.imshow(diff_map, interpolation="none",vmin=np.percentile(diff_map, 5), vmax=np.percentile(diff_map, 95)); pl.colorbar(); pl.title('Difference: calculated - measured hitmap')
    fig.savefig("ring_score/lin_sum_%s.png"%a)
    pl.close(fig)



fig2=pl.figure()
pl.subplot(121)
pl.imshow(curr_map, interpolation="none",vmin=0, vmax=np.percentile(curr_map, 95)); pl.title('Measured hitmap')
pl.subplot(122)
pl.plot(ringness,norm)
pl.axvline(ring_score, color='r', linestyle='dashed', linewidth=1);  pl.title('Ringness-score : %s'%ring_score_s, color='r')
pl.xlabel('Multiplicative coefficient'); pl.ylabel('Figure of merit : norm of the difference-hitmap');
fig2.savefig("ring_score/lin_sum_fom.png")
pl.close(fig)





















