import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter
from scipy.ndimage import spline_filter
from scipy  import fftpack





c_start=6; c_end=245

#wafer='W03_IB_2017_12_04_002'; r_start=240; r_end=440
#name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-70000_drift-4000_clear-off3000/clusterdb.h5'

wafer='W41_IF_2018_03_28_001'; r_start=1; r_end=768
name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'#ring
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'#flat


nrows=(r_end-r_start)+1
ncols=(c_end-c_start)+1


ring_data = tables.open_file(name_ring, mode="r")
ring_map = ring_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
ring_data.close()

'''
#clean up noisy pixels
max_ring=np.zeros(nrows); max_flat=np.zeros(nrows)
for i in range(nrows):
        max_ring[i]=np.percentile(ring_map[i,:], 98)
        for j in range(ncols):
                    if ring_map[i,j] > max_ring[i]:
                        ring_map[i,j]=0
'''


#Gaussian blur
#ring_map=gaussian_filter(ring_map, sigma=3)

#spline filter
ring_map=spline_filter(ring_map)



    
fig2=pl.figure(figsize=(10,10))
pl.imshow(ring_map, interpolation="none"); pl.colorbar(); 
fig2.savefig("spline_filter.png")
pl.close(fig2)















