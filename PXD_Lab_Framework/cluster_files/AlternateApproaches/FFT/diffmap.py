import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LogNorm
from scipy import fftpack



## add sensor region
rows=768
r_start=1; r_end=768
c_start=6; c_end=245

#reference samples
name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
name_flat = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'


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
ring_map=gaussian_filter(ring_map, sigma=gauss_sig)
flat_map=gaussian_filter(flat_map, sigma=gauss_sig)


#normalize
ring_full=np.sum(ring_map)
flat_full=np.sum(flat_map)
const=np.true_divide(ring_full,flat_full)
flat_map=flat_map*const


diff_map=ring_map - flat_map

#FFT
diff_fft=fftpack.fft2(diff_map)

diff_fft2= diff_fft.copy()
diff_fft2[50:199,:]=0
diff_fft2[:,50:717]=0

diff_new = fftpack.ifft2(diff_fft2).real


figu=pl.figure(figsize=(30,15))
pl.subplot(121)
pl.imshow(diff_map); pl.colorbar(); pl.title('diffmap')
pl.subplot(122)
pl.imshow(diff_new); pl.colorbar(); pl.title('diffmap (fft-denoised)')
figu.savefig("fft.png")
pl.close(figu)


#plot
'''
figu=pl.figure(figsize=(30,15))
pl.subplot(151)
pl.imshow(diff_map); pl.colorbar(); pl.title('Reference ring      -hitmap')
pl.subplot(152)
pl.imshow(ring_map_fft.real[:20,:20]); pl.colorbar(); pl.title('FFT-real')
pl.subplot(153)
pl.imshow(ring_map_fft.imag[:20,:20]); pl.colorbar(); pl.title('FFT-imaginary')
pl.subplot(154)
pl.imshow(np.abs(ring_map_fft[:20,:20])); pl.colorbar(); pl.title('FFT-absolute value')
pl.subplot(155)
pl.imshow(np.angle(ring_map_fft[:20,:20])); pl.colorbar(); pl.title('FFT- phase')
figu.savefig("diffmap.png");
pl.close(figu)
'''


'''
figu=pl.figure(figsize=(30,15))

pl.subplot(131)
pl.imshow(diff_map); pl.colorbar(); pl.title('Reference ring-hitmap')
pl.subplot(132)
pl.imshow(np.abs(ring_map_fft), norm=LogNorm()); pl.colorbar(); pl.title('FFT-absolute value')
pl.subplot(133)
pl.imshow(np.abs(ring_map_fft[:20,:20])); pl.colorbar(); pl.title('FFT-absolute value')

figu.savefig("diffmap.png");pl.close(figu)
'''




























