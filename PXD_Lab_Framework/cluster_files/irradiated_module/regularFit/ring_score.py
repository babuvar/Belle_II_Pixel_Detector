import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter
import math as mt






#c_start=1; c_end=250
#r_start=1; r_end=768

c_start=10; c_end=240
r_start=20; r_end=750


wafer='W05_OB1'
date='2019_03_21_002'
#date='2018_10_25_007'

name_ring = '/home/bonndaq_pc/tmp_varghese/W05_OB1/source_scan/2019_03_21_002/hv-50000_drift-6000_clear-off3000/data.h5'
name_flat = '/home/bonndaq_pc/tmp_varghese/W05_OB1/source_scan/2019_03_21_002/hv-60000_drift-4000_clear-off5000/data.h5'
#name_ring = '/home/bonndaq_pc/tmp_varghese/W05_OB1/source_scan/2018_10_25_007/hv-62000_drift-4000_clear-off5000/data.h5'
#name_flat = '/home/bonndaq_pc/tmp_varghese/W05_OB1/source_scan/2018_10_25_007/hv-72000_drift-4000_clear-off4000/data.h5'


nrows=(r_end-r_start)+1
ncols=(c_end-c_start)+1

ring_data = tables.open_file(name_ring, mode="r")
ring_map = ring_data.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
ring_data.close()
flat_data = tables.open_file(name_flat, mode="r")
flat_map = flat_data.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
flat_data.close()


#clean up noisy pixels
max_ring=np.zeros(nrows); max_flat=np.zeros(nrows)

for i in range(nrows):
        max_ring[i]=np.percentile(ring_map[i,:], 98)
        max_flat[i]=np.percentile(flat_map[i,:], 98)
        for j in range(ncols):
                    if ring_map[i,j] > max_ring[i]:
                        ring_map[i,j]=0
                    if flat_map[i,j] > max_flat[i]:
                        flat_map[i,j]=0


#np.save('ring_map.npy', ring_map)
#np.save('flat_map.npy', flat_map)




#create plot directories if not existing already
plot_dir=os.path.join('ring_score',wafer,date)
plot_subdir=os.path.join('ring_score',wafer,date,'diffmaps')
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)
if not os.path.exists(plot_subdir):
    os.makedirs(plot_subdir)





#plot reference hitmaps
figu=pl.figure(figsize=(15,15))
pl.subplot(121)
pl.imshow(ring_map, interpolation="none",vmin=0, vmax=np.percentile(ring_map, 95)); pl.title('Reference ring-hitmap')
pl.subplot(122)
pl.imshow(flat_map, interpolation="none",vmin=0, vmax=np.percentile(flat_map, 95)); pl.title('Reference flat-hitmap')
figu.savefig("%s/reference_hitmaps.png"%plot_dir)
pl.close(figu)


input_dir='/home/bonndaq_pc/tmp_varghese/W05_OB1/source_scan/%s'%date

names = {}
for directory in os.listdir(input_dir):
    subdir =  os.path.join(input_dir,directory)
    if os.path.isdir(subdir):
        for filename in os.listdir(subdir):
            fullname = os.path.join(subdir,filename)
            names[directory] = fullname
            



#retain an original copy of the ring and flat maps 
#Otherwise at each iteration, the gaussian blur is applied
#and eventually it will be smoothened out to oblivion
    ring_map_copy = np.copy(ring_map)
    flat_map_copy = np.copy(flat_map)


#results dictionary
results={}

#spread for gaussian blur
gauss_sig=3


for name, fullname in names.items():
    #fig.savefig("plots/%s/hitmap_%s.png" %(wafer,name))

    #Get the original flat and ring maps
    ring_map=ring_map_copy
    flat_map=flat_map_copy

    name_curr=fullname
    curr_data = tables.open_file(name_curr, mode="r")
    curr_map = curr_data.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
    curr_data.close()
    curr_map_copy = np.copy(curr_map)

    #Clean for noisy pixels row-wise
    max_curr=np.zeros(nrows)
    for i in range(nrows):
        max_curr[i]=np.percentile(curr_map[i,:], 98)
        for j in range(ncols):
            if curr_map[i,j] > max_curr[i]:
                curr_map[i,j]=0


    
    #Apply gaussian blur
    ring_map=gaussian_filter(ring_map, sigma=gauss_sig)
    flat_map=gaussian_filter(flat_map, sigma=gauss_sig)
    curr_map=gaussian_filter(curr_map, sigma=gauss_sig)
    

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
    ring_score_full = ring_score
    midval= mt.floor(10*ring_score) /10
    ring_score_s=str(ring_score)
    ring_score_s=ring_score_s[:6]

    
    #vary 'a'
    ran=np.arange(midval-0.5, midval+0.6, 0.1)
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
        fig.savefig("%s/iter_%s_%s.png"%(plot_subdir,name,a))
        pl.close(fig)
    


    fig2=pl.figure(figsize=(15,15))
    pl.subplot(121)
    pl.imshow(curr_map_copy, interpolation="none",vmin=0, vmax=np.percentile(curr_map_copy, 95)); pl.title('%s'%name)
    pl.subplot(122)
    pl.plot(ringness,norm)
    pl.axvline(ring_score, color='r', linestyle='dashed', linewidth=1);  pl.title('Ringness-score : %s'%ring_score_full, color='r')
    pl.xlabel('Multiplicative coefficient'); pl.ylabel('Figure of merit : norm of the difference-hitmap');
    fig2.savefig("%s/score_%s.png"%(plot_dir,name))
    pl.close(fig2)

    
    results[name]=ring_score_full
    print "%s is done"%name


#print "results = ", results

#Save results
np.save('%s/results_%s_%s.npy'%(plot_dir, wafer, date), results)















