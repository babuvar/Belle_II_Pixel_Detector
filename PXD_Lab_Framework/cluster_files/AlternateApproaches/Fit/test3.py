import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter
from scipy  import fftpack
from matplotlib.colors import  LogNorm
#from ROOT import  gROOT, TCanvas, TH2F, TH1F, TGraph2D, gStyle, gPad, RooFormulaVar, RooRealVar, RooDataHist, RooArgSet, RooArgList, RooFit, RooChebychev, RooFitResult, RooLinkedList, RooCmdArg, RooAbsPdf
#from ROOT import  TFile

#hfile = TFile( 'py-hsimple.root', 'RECREATE', 'Demo ROOT file with histograms' )

c_start=6; c_end=245
r_start=1; r_end=768

#wafer='W03_IB_2017_12_04_002'; r_start=240; r_end=440
#name_ring = '/Data2/source_scan_samples/W03_IB_2017_12_04_002/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-70000_drift-4000_clear-off3000/clusterdb.h5'

wafer='W41_IF_2018_03_28_001'; r_start=1; r_end=768
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'#ring
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'#flat

#wafer='W44_IF_2018_03_20_001'; r_start=340; r_end=540
#name_ring = '/Data2/source_scan_samples/W44_IF_2018_03_20_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W44_IF_2018_03_20_001/hv-72000_drift-4000_clear-off2000/clusterdb.h5'

#wafer='W45_IB_2017_12_04_002'; r_start=300; r_end=500
#name_ring = '/Data2/source_scan_samples/W45_IB_2017_12_04_002/hv-60000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W45_IB_2017_12_04_002/hv-68000_drift-5000_clear-off2000/clusterdb.h5'


nrows=(r_end-r_start)+1
ncols=(c_end-c_start)+1



ring_map=np.zeros((nrows, ncols))


#ring_data = tables.open_file(name_ring, mode="r")
#ring_map = ring_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
#ring_data.close()

input_dir='/Data2/source_scan_samples/%s'%wafer
names = {}
for directory in os.listdir(input_dir):
    subdir =  os.path.join(input_dir,directory)
    if os.path.isdir(subdir):
        for filename in os.listdir(subdir):
            fullname = os.path.join(subdir,filename)
            names[directory] = fullname


for name, fullname in names.items():
    name_curr=fullname
    curr_data = tables.open_file(name_curr, mode="r")
    curr_map = curr_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
    curr_data.close()
    ring_map=ring_map+curr_map
    #print "%s is done"%name







#clean up noisy pixels
max_ring=np.zeros(nrows); max_flat=np.zeros(nrows)

for i in range(nrows):
        max_ring[i]=np.percentile(ring_map[i,:], 98)
        for j in range(ncols):
                    if ring_map[i,j] > max_ring[i]:
                        ring_map[i,j]=0



#gStyle.SetOptStat(0)


#create plot directories if not existing already
plot_dir=os.path.join('ring_score',wafer)
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

ring_map=ring_map.astype(float)



#Gaussian blur
ring_map=gaussian_filter(ring_map, sigma=3)

ring_full=np.sum(ring_map)

ring_profile = np.copy(ring_map)


#Row-wise normalization
for i in range(nrows):
    tot=np.sum(ring_map[i,:])
    ring_map[i,:]=np.true_divide(ring_map[i,:],tot)



#Column-wise normalization
for i in range(ncols):
    tot=np.sum(ring_map[:,i])
    ring_map[:,i]=np.true_divide(ring_map[:,i],tot)


#renormalize
#ring_mean=np.mean(ring_map)
ring_mean=np.max(ring_map)
ring_map=np.true_divide(ring_map,ring_mean)


#Get the profile map ring_profile
for  i in range(nrows):
    for j in range(ncols):
        ring_profile[i,j] = ring_profile[i,j] / ring_map[i,j]


#plot
fig=pl.figure(figsize=(15,15))
pl.subplot(121)
#pl.imshow(ring_map[350:500,50:200]); pl.colorbar(); pl.title('Efficiency-rings')
pl.imshow(ring_map); pl.colorbar(); pl.title('Efficiency-rings')
pl.subplot(122)
pl.imshow(ring_profile); pl.colorbar(); pl.title('Hitmap-profile')
fig.savefig("plot.png")
pl.close(fig)


#Renaming
eff=np.subtract(1.0, ring_map)




print "its done"





#results dictionary
results={}

#spread for gaussian blur
gauss_sig=3

res_ass=[]


for name, fullname in names.items():

    #A locally normalized profile map
    prof=np.copy(ring_map)


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
    curr_map=curr_map.astype(float)
    curr_map=gaussian_filter(curr_map, sigma=gauss_sig)
    

    #normalize
    prof_full=np.sum(prof)
    curr_full=np.sum(curr_map)
    c_prof=np.true_divide(curr_full,prof_full)
    prof=prof*c_prof


    #Ring score
    diffmap = curr_map - prof
    deviation = np.std(diffmap)
    mean = np.mean(diffmap)

    
    
    fig2=pl.figure(figsize=(10,10))
    pl.imshow(curr_map_copy, interpolation="none",vmin=0, vmax=np.percentile(curr_map_copy, 95)); pl.colorbar(); pl.title('%s \n deviation : %s , mean = %s'%(name, deviation, mean) )
    fig2.savefig("%s/score_%s.png"%(plot_dir,name))
    pl.close(fig2)

    print"%s is done"%name
    
    #results[name]=ring_score_s


#print res_ass
#print "lowest = ", min(res_ass)


#Save results
#np.save('results_%s.npy'%wafer, results)














