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
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'#ring
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'#flat

#wafer='W44_IF_2018_03_20_001'; r_start=340; r_end=540
#name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W44_IF_2018_03_20_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W44_IF_2018_03_20_001/hv-72000_drift-4000_clear-off2000/clusterdb.h5'

#wafer='W45_IB_2017_12_04_002'; r_start=300; r_end=500
#name_ring = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W45_IB_2017_12_04_002/hv-60000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W45_IB_2017_12_04_002/hv-68000_drift-5000_clear-off2000/clusterdb.h5'



nrows=(r_end-r_start)+1
ncols=(c_end-c_start)+1





#create plot directories if not existing already
plot_dir=os.path.join('ring_score',wafer)
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)





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

#score_lowlim= 0.9705877904230935
#score_range=1.0 - score_lowlim
#lowest =  1.6236494793930464e-07
#highese =  1.78854256173922e-07
#lowest =  486.11206681940126
#highest =  1263.3914237584538

#var_low=486.11206681940126i
#var_high=1263.3914237584538

var_low = 1.6236494793930464
var_high = 1.78854256173922

const=np.sqrt(var_high-var_low)

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

    
    curr_map=curr_map.astype(float)
    
    #Apply gaussian blur
    curr_map=gaussian_filter(curr_map, sigma=gauss_sig)
    
    '''
    #Row-wise normalization
    for i in range(nrows):
        tot=np.sum(curr_map[i,:])
        curr_map[i,:]=np.true_divide(curr_map[i,:],tot)

    #Column-wise normalization
    for i in range(ncols):
        tot=np.sum(curr_map[:,i])
        curr_map[:,i]=np.true_divide(curr_map[:,i],tot)
    '''
    variance=np.var(curr_map[np.nonzero(curr_map != 0 )])
    #variance=np.var(curr_map)

    #print"ring score = %s"%ring_score
    res_ass.append(variance)
    

    print"%s is done"%name
    
    #results[name]=ring_score_s
    variance=variance * 10000000

    score=np.true_divide(np.sqrt(variance-var_low),const)
    #print "score = ", score

    fig2=pl.figure(figsize=(10,10))
    pl.subplot(121)
    pl.imshow(curr_map_copy, interpolation="none",vmin=0, vmax=np.percentile(curr_map_copy, 95));
    pl.colorbar(); pl.title('%s \n Ringness-score : %s'%(name, score) )
    pl.subplot(122)
    pl.imshow(curr_map); pl.title('Transformed image' )
    fig2.savefig("%s/score_%s.png"%(plot_dir,name))
    pl.close(fig2)


#print res_ass
print "lowest = ", min(res_ass)
print "highest = ",max(res_ass)

#Save results
#np.save('results_%s.npy'%wafer, results)














