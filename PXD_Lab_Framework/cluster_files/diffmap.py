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
c_start=6; c_end=245

#reference samples
name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'


ring_data = tables.open_file(name_ring, mode="r")
ring_map = ring_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
ring_data.close()
flat_data = tables.open_file(name_flat, mode="r")
flat_map = flat_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
flat_data.close()

#np.save('ring_map.npy', ring_map)
#np.save('flat_map.npy', flat_map)

#clean up noisy pixels
max_ring=np.zeros(768); max_flat=np.zeros(768)

for i in range(768):
        max_ring[i]=np.percentile(ring_map[i,:], 98)
        max_flat[i]=np.percentile(flat_map[i,:], 98)
        for j in range(240):
                    if ring_map[i,j] > max_ring[i]:
                        ring_map[i,j]=0
                    if flat_map[i,j] > max_flat[i]:
                        flat_map[i,j]=0

#do stuff
gauss_sig=3
#Apply gaussian blur
#ring_map=gaussian_filter(ring_map, sigma=gauss_sig)
#flat_map=gaussian_filter(flat_map, sigma=gauss_sig)
#normalize
ring_full=np.sum(ring_map)
flat_full=np.sum(flat_map)
const=np.true_divide(ring_full,flat_full)
flat_map=flat_map*const
diff_map=ring_map - flat_map

print 'diff_map = ', diff_map.shape
print 'flat_map = ', flat_map.shape
print 'ring_map = ', ring_map.shape


#np.save('ring_blur_map.npy', ring_map)
#np.save('flat_blur_map.npy', flat_map)
#np.save('diff_blur_map.npy', diff_map)

np.save('diff_map.npy', diff_map) #diffmap without blur

















