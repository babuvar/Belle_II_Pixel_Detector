import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter
from scipy  import fftpack
from matplotlib.colors import  LogNorm




c_start=6; c_end=245

#wafer='W03_IB_2017_12_04_002'; r_start=240; r_end=440
#name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-70000_drift-4000_clear-off3000/clusterdb.h5'

wafer='W41_IF_2018_03_28_001'; r_start=1; r_end=768
name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'#ring
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'#flat

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
ring_data.close()


#clean up noisy pixels
max_ring=np.zeros(nrows); max_flat=np.zeros(nrows)

for i in range(nrows):
        max_ring[i]=np.percentile(ring_map[i,:], 98)
        for j in range(ncols):
                    if ring_map[i,j] > max_ring[i]:
                        ring_map[i,j]=0





'''
#create plot directories if not existing already
plot_dir=os.path.join('ring_score',wafer)
plot_subdir=os.path.join('ring_score',wafer,'diffmaps')
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)
if not os.path.exists(plot_subdir):
    os.makedirs(plot_subdir)
'''

ring_map=ring_map.astype(float)

#Gaussian blur
ring_map=gaussian_filter(ring_map, sigma=3)



#Row-wise normalization
for i in range(nrows):
    tot=np.sum(ring_map[i,:])
    ring_map[i,:]=np.true_divide(ring_map[i,:],tot)



#Column-wise normalization
for i in range(ncols):
    tot=np.sum(ring_map[:,i])
    ring_map[:,i]=np.true_divide(ring_map[:,i],tot)


gradmap = np.gradient(ring_map, 5)


grad_abs=np.zeros((768,240))
grad_phase=np.zeros((768,240))


for i in range(768):
    for j in range(240):
        grad_abs[i][j]=np.sqrt((gradmap[0][i][j]*gradmap[0][i][j])+(gradmap[1][i][j]*gradmap[1][i][j]))
        grad_phase[i][j]=np.arctan(gradmap[1][i][j]/gradmap[0][i][j])
#FFT
fftmap=fftpack.fft2(ring_map)


#plot
fig=pl.figure(figsize=(15,15))
pl.subplot(141)
pl.imshow(ring_map); pl.colorbar(); pl.title('Hitmap')
pl.subplot(142)
pl.imshow(grad_abs); pl.colorbar(); pl.title('Gradient modulus')
pl.subplot(143)
pl.imshow(grad_phase); pl.colorbar(); pl.title('Gradient phase')
pl.subplot(144)
pl.imshow(np.abs(fftmap), norm=LogNorm()); pl.colorbar(); pl.title('FFT')
fig.savefig("plot.png")
pl.close(fig)

#plot
fig=pl.figure(figsize=(4,8))
pl.imshow(grad_abs, interpolation="none");
fig.savefig("grad.png")
pl.close(fig)

'''


input_dir='/Data2/source_scan_samples/%s'%wafer
names = {}
for directory in os.listdir(input_dir):
    subdir =  os.path.join(input_dir,directory)
    if os.path.isdir(subdir):
        for filename in os.listdir(subdir):
            fullname = os.path.join(subdir,filename)
            names[directory] = fullname


#results dictionary
results={}

#spread for gaussian blur
gauss_sig=3

res_ass=[]

score_lowlim= 0.9705877904230935
score_range=1.0 - score_lowlim

for name, fullname in names.items():

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
    curr_map=gaussian_filter(curr_map, sigma=gauss_sig)
    

    #normalize
    ring_full=np.sum(ring_map)
    curr_full=np.sum(curr_map)
    c_curr=np.true_divide(ring_full,curr_full)
    curr_map=curr_map*c_curr


    #Correlation
    #linear sum score
    rm=ring_map.flatten()
    cm=curr_map.flatten()

    ring_score=np.corrcoef(rm,cm)[0][1]
    ring_score=(ring_score - score_lowlim) / score_range
    
    #print"ring score = %s"%ring_score
    #res_ass.append(ring_score)
    
    fig2=pl.figure(figsize=(10,10))
    pl.imshow(curr_map_copy, interpolation="none",vmin=0, vmax=np.percentile(curr_map_copy, 95)); pl.colorbar(); pl.title('%s \n Flatness-score : %s'%(name, ring_score) )
    fig2.savefig("%s/score_%s.png"%(plot_dir,name))
    pl.close(fig2)

    print"%s is done"%name
    
    #results[name]=ring_score_s


#print res_ass
#print "lowest = ", min(res_ass)


#Save results
#np.save('results_%s.npy'%wafer, results)


'''











