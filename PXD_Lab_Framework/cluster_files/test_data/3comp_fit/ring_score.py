import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter
import math as mt
from scipy import linalg as lng




c_start=10; c_end=240
r_start=20; r_end=750



name_ring = '/Data/source_scan/2020_01_14_002/hv-60000_drift-5000_clear-off2000/data.h5'
name_flat = '/Data/source_scan/2020_01_14_002/hv-66000_drift-5000_clear-off3000/data.h5'
name_grid = '/Data/source_scan/2020_01_14_002/hv-60000_drift-3000_clear-off5000/data.h5'

nrows=(r_end-r_start)+1
ncols=(c_end-c_start)+1

#ring
ring_data = tables.open_file(name_ring, mode="r")
ring_map = ring_data.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
ring_data.close()
#flat
flat_data = tables.open_file(name_flat, mode="r")
flat_map = flat_data.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
flat_data.close()
#grid
grid_data = tables.open_file(name_grid, mode="r")
grid_map = grid_data.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
grid_data.close()


#clean up noisy pixels
max_ring=np.zeros(nrows); max_flat=np.zeros(nrows); max_grid=np.zeros(nrows)

for i in range(nrows):
        max_ring[i]=np.percentile(ring_map[i,:], 98)
        max_flat[i]=np.percentile(flat_map[i,:], 98)
        max_grid[i]=np.percentile(grid_map[i,:], 98)
        for j in range(ncols):
                    if ring_map[i,j] > max_ring[i]:
                        ring_map[i,j]=0
                    if flat_map[i,j] > max_flat[i]:
                        flat_map[i,j]=0
                    if grid_map[i,j] > max_grid[i]:
                        grid_map[i,j]=0






#create plot directories if not existing already
plot_dir=os.path.join('ring_score')
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)





#plot reference hitmaps
figu=pl.figure(figsize=(20,15))
pl.subplot(131)
pl.imshow(ring_map, interpolation="none",vmin=0, vmax=np.percentile(ring_map, 95)); pl.title('Reference ring-hitmap')
pl.subplot(132)
pl.imshow(flat_map, interpolation="none",vmin=0, vmax=np.percentile(flat_map, 95)); pl.title('Reference flat-hitmap')
pl.subplot(133)
pl.imshow(grid_map, interpolation="none",vmin=0, vmax=np.percentile(grid_map, 95)); pl.title('Reference grid-hitmap')
figu.savefig("%s/reference_hitmaps.png"%plot_dir)
pl.close(figu)


input_dir='/Data/source_scan/2020_01_14_002/'

names = {}
for subdir in os.listdir(input_dir):
    fullname = os.path.join(input_dir,subdir,'data.h5')
    if os.path.exists(fullname):
        names[subdir] = fullname





#retain an original copy of the ring and flat maps for plotting
#ring_map_copy = np.copy(ring_map)
#flat_map_copy = np.copy(flat_map)

#spread for gaussian blur
gauss_sig=3

#Apply gaussian blur
ring_map=gaussian_filter(ring_map, sigma=gauss_sig)
flat_map=gaussian_filter(flat_map, sigma=gauss_sig)
grid_map=gaussian_filter(grid_map, sigma=gauss_sig)

#Normalization everything to have int. area same as ring map
ring_full=np.sum(ring_map);
flat_full=np.sum(flat_map); c_flat=np.true_divide(ring_full,flat_full); flat_map=flat_map*c_flat
grid_full=np.sum(grid_map); c_grid=np.true_divide(ring_full,grid_full); grid_map=grid_map*c_grid

#results dictionary
results={}

for name, fullname in names.items():

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
    curr_map=gaussian_filter(curr_map, sigma=gauss_sig)
    

    #normalize
    curr_full=np.sum(curr_map)
    c_curr=np.true_divide(ring_full,curr_full)
    curr_map=curr_map*c_curr


    #------------------------------------------------------------------------------------------------------------------------------
    #Analytical ring-score
    #linear sum score
    
    #x1 -> flat, x2 -> ring, x3 -> grid
    y=curr_map.flatten(); x1=flat_map.flatten(); x2=ring_map.flatten(); x3=grid_map.flatten()

    #Matrix elements
    x1x1=np.sum(np.multiply(x1,x1))
    x1x2=np.sum(np.multiply(x1,x2))
    x1x3=np.sum(np.multiply(x1,x3))
    x2x2=np.sum(np.multiply(x2,x2))
    x2x3=np.sum(np.multiply(x2,x3))
    x3x3=np.sum(np.multiply(x3,x3))
    A = np.array([[x1x1, x1x2, x1x3], [x1x2, x2x2, x2x3], [x1x3,x2x3,x3x3]])
    #Invert A
    A_inv = lng.inv(A)

    #coeffient vector
    x1y=np.sum(np.multiply(x1,y))
    x2y=np.sum(np.multiply(x2,y))
    x3y=np.sum(np.multiply(x3,y))
    B = np.array([x1y, x2y, x3y])

    #Solution Vector
    Sol = A_inv.dot(B)
    #Renormalize Sol
    Sol_unit = Sol / lng.norm(Sol)
    #------------------------------------------------------------------------------------------------------------------------------
    
    #plotting
    fig2=pl.figure(figsize=(7,15))
    pl.imshow(curr_map_copy, interpolation="none",vmin=0, vmax=np.percentile(curr_map_copy, 95)); pl.title('%s'%name); pl.colorbar();
    pl.xlabel('flatness-coeff : %s \n ringness-coeff : %s \n gridness-coeff : %s' %(Sol[0], Sol[1], Sol[2]), color='r');
    fig2.savefig("%s/score_%s.png"%(plot_dir,name))
    pl.close(fig2)
    
    #print'-------------------------------------------------------------'
    #print 'flatness coeff = %s'%Sol[0]
    #print 'ringness coeff = %s'%Sol[1]
    #print 'gridness coeff = %s'%Sol[2]

    results[name]=Sol_unit
    print "%s is done"%name
    #print'-------------------------------------------------------------'


#Save results
np.save('%s/results.npy'%plot_dir, results)














