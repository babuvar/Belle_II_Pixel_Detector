import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
from scipy.ndimage import gaussian_filter
from scipy  import fftpack
from matplotlib.colors import  LogNorm
from scipy.stats import kurtosis, skew

#from ROOT import  gROOT, TCanvas, TH2F, TH1F, TGraph2D, gStyle, gPad, RooFormulaVar, RooRealVar, RooDataHist, RooArgSet, RooArgList, RooFit, RooChebychev, RooFitResult, RooLinkedList, RooCmdArg, RooAbsPdf
#from ROOT import  TFile

#hfile = TFile( 'py-hsimple.root', 'RECREATE', 'Demo ROOT file with histograms' )

c_start=6; c_end=245
r_start=1; r_end=768

#wafer='W03_IB_2017_12_04_002';
#name_ring = '/Data2/source_scan_samples/W03_IB_2017_12_04_002/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-70000_drift-4000_clear-off3000/clusterdb.h5'

#wafer='W41_IF_2018_03_28_001'; 
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'#ring
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'#flat

wafer='W44_IF_2018_03_20_001'; 
#name_ring = '/Data2/source_scan_samples/W44_IF_2018_03_20_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W44_IF_2018_03_20_001/hv-72000_drift-4000_clear-off2000/clusterdb.h5'

#wafer='W45_IB_2017_12_04_002'; 
#name_ring = '/Data2/source_scan_samples/W45_IB_2017_12_04_002/hv-60000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W45_IB_2017_12_04_002/hv-68000_drift-5000_clear-off2000/clusterdb.h5'


nrows=(r_end-r_start)+1
ncols=(c_end-c_start)+1

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
    #curr_map=gaussian_filter(curr_map, sigma=3)
    profile = np.copy(curr_map)
    
    #Row-wise normalization
    for i in range(nrows):
        tot=np.sum(curr_map[i,:])
        curr_map[i,:]=np.true_divide(curr_map[i,:],tot)
        nonz=np.count_nonzero(curr_map_copy[i,:])
        curr_map[i,:]= curr_map[i,:]*nonz

    #Column-wise normalization
    for i in range(ncols):
         tot=np.sum(curr_map[:,i])
         curr_map[:,i]=np.true_divide(curr_map[:,i],tot)
         nonz=np.count_nonzero(curr_map_copy[:,i])
         curr_map[:,i]= curr_map[:,i]*nonz

    #Apply gaussian blur
    curr_map=gaussian_filter(curr_map, sigma=3)
    profile = gaussian_filter(profile, sigma=3)



    #renormalize
    curr_mean=np.mean(curr_map)
    eff_map=np.true_divide(curr_map,curr_mean)
    eff_map_cp=np.copy(eff_map)

    #Get the profile map ring_profile
    for  i in range(nrows):
        for j in range(ncols):
            profile[i,j] = profile[i,j] / eff_map[i,j]

    #1 - Eff
    eff_map=np.subtract(1,eff_map)

    #Weighted residuals
    residual = eff_map * profile


    res_hist=residual.flatten()
    ku=kurtosis(res_hist)
    sk=skew(res_hist)
    bimo_coeff = ( (sk*sk) + 1) / ku
    std=np.std(res_hist)
    
    
    fig2=pl.figure(figsize=(25,10))
    pl.subplot(151)
    pl.imshow(curr_map_copy, interpolation="none", vmin=0, vmax=np.percentile(curr_map_copy, 95)); pl.colorbar();
    pl.subplot(152)
    pl.imshow(eff_map_cp, interpolation="none"); pl.colorbar();
    pl.subplot(153)
    pl.imshow( profile, interpolation="none"); pl.colorbar();
    pl.subplot(154)
    pl.imshow(residual, interpolation="none"); pl.colorbar(); pl.title('Weighted residual-map' )
    pl.subplot(155)
    pl.hist(res_hist, range=[-50, 50], bins=100); pl.title('score = %s'%std )
    fig2.savefig("histos/hist_%s.png"%name)
    pl.close(fig2)

    print"%s is done"%name














