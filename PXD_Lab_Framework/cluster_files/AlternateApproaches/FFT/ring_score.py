import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter
from scipy  import fftpack





c_start=6; c_end=245

#wafer='W03_IB_2017_12_04_002'; r_start=240; r_end=440
#name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-70000_drift-4000_clear-off3000/clusterdb.h5'

wafer='W41_IF_2018_03_28_001'; r_start=1; r_end=768
name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'#ring
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'#flat
#name_ring = '/home/bonndaq_pc/tmp_varghese/W05_OB1/source_scan/2019_03_21_002/hv-50000_drift-6000_clear-off3000/data.h5'
#name_ring = '/home/bonndaq_pc/tmp_varghese/W05_OB1/source_scan/2019_03_21_002/hv-60000_drift-4000_clear-off5000/data.h5'

#wafer='W44_IF_2018_03_20_001'; r_start=340; r_end=540
#name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W44_IF_2018_03_20_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W44_IF_2018_03_20_001/hv-72000_drift-4000_clear-off2000/clusterdb.h5'

#wafer='W45_IB_2017_12_04_002'; r_start=300; r_end=500
#name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W45_IB_2017_12_04_002/hv-60000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W45_IB_2017_12_04_002/hv-68000_drift-5000_clear-off2000/clusterdb.h5'

nrows=(r_end-r_start)+1
ncols=(c_end-c_start)+1


ring_data = tables.open_file(name_ring, mode="r")
ring_map = ring_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
#ring_map = ring_data.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
ring_data.close()


#clean up noisy pixels
max_ring=np.zeros(nrows); max_flat=np.zeros(nrows)

for i in range(nrows):
        max_ring[i]=np.percentile(ring_map[i,:], 98)
        for j in range(ncols):
                    if ring_map[i,j] > max_ring[i]:
                        ring_map[i,j]=0



#wafer='W41_IF_2018_03_28_001'


#create plot directories if not existing already
#plot_dir=os.path.join('ring_score',wafer)
#plot_subdir=os.path.join('ring_score',wafer,'diffmaps')
#if not os.path.exists(plot_dir):
#    os.makedirs(plot_dir)
#if not os.path.exists(plot_subdir):
#    os.makedirs(plot_subdir)

#Gaussian blur
ring_map=gaussian_filter(ring_map, sigma=3)
ring_map=gaussian_filter(ring_map, sigma=3)
#ring_map_ffit=np.copy(ring_map)


#FFT
#np.fft.irfft2(ring_map_fft)
ring_map_fft=fftpack.fft2(ring_map)
#ring_map_fft=fftpack.ifft2(ring_map)


#print"ring_map_fft type = ", type(ring_map_fft[3][4])
#print"ring_map_fft shape = ", ring_map_fft.shape


#plot 
from matplotlib.colors import LogNorm

figu=pl.figure(figsize=(30,15))
pl.subplot(151)
pl.imshow(ring_map, interpolation="none",vmin=0, vmax=np.percentile(ring_map, 95)); pl.colorbar(); pl.title('Reference ring-hitmap')
pl.subplot(152)
pl.imshow(ring_map_fft.real, norm=LogNorm()); pl.colorbar(); pl.title('FFT-real')
pl.subplot(153)
pl.imshow(ring_map_fft.imag, norm=LogNorm()); pl.colorbar(); pl.title('FFT-imaginary')
pl.subplot(154)
pl.imshow(np.abs(ring_map_fft), norm=LogNorm()); pl.colorbar(); pl.title('FFT-absolute value')
pl.subplot(155)
pl.imshow(np.angle(ring_map_fft), norm=LogNorm()); pl.colorbar(); pl.title('FFT- phase')
figu.savefig("ringmap.png"); pl.colorbar();

pl.close(figu)




'''
input_dir='/home/bonndaq_pc/tmp_hye/source_scan_opt/%s'%wafer
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
    curr_map = curr_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
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
    ring_score_s=str(ring_score)
    ring_score_s=ring_score_s[:6]



    fig2=pl.figure()
    pl.subplot(121)
    pl.imshow(curr_map_copy, interpolation="none",vmin=0, vmax=np.percentile(curr_map_copy, 95)); pl.title('%s'%name)
    pl.subplot(122)
    pl.plot(ringness,norm)
    pl.axvline(ring_score, color='r', linestyle='dashed', linewidth=1);  pl.title('Ringness-score : %s'%ring_score_s, color='r')
    pl.xlabel('Multiplicative coefficient'); pl.ylabel('Figure of merit : norm of the difference-hitmap');
    fig2.savefig("%s/score_%s.png"%(plot_dir,name))
    pl.close(fig2)

    
    results[name]=ring_score_s


print "results = ", results

#Save results
np.save('results_%s.npy'%wafer, results)
'''














