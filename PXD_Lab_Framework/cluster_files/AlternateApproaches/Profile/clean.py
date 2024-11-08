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
import numpy.ma as ma
np.seterr(divide='ignore', invalid='ignore')

#from ROOT import  gROOT, TCanvas, TH2F, TH1F, TGraph2D, gStyle, gPad, RooFormulaVar, RooRealVar, RooDataHist, RooArgSet, RooArgList, RooFit, RooChebychev, RooFitResult, RooLinkedList, RooCmdArg, RooAbsPdf
#from ROOT import  TFile

#hfile = TFile( 'py-hsimple.root', 'RECREATE', 'Demo ROOT file with histograms' )

c_start=6; c_end=245
r_start=1; r_end=768

#wafer='W03_IB_2017_12_04_002';
#name_ring = '/Data2/source_scan_samples/W03_IB_2017_12_04_002/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W03_IB_2017_12_04_002/hv-70000_drift-4000_clear-off3000/clusterdb.h5'

wafer='W41_IF_2018_03_28_001'; 
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'#ring
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'#flat

#wafer='W44_IF_2018_03_20_001'; 
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


onelist=[('hv-66000_drift-6000_clear-off5000', '/Data2/source_scan_samples/%s/hv-66000_drift-6000_clear-off5000/clusterdb.h5'%wafer)]


#for name, fullname in names.items():
for name, fullname in onelist:


    
    name_curr=fullname
    curr_data = tables.open_file(name_curr, mode="r")
    curr_map = curr_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
    curr_data.close()
    curr_map=curr_map.astype(float)
    ratio= np.zeros((nrows,ncols))
    



    #Clean for noisy pixels row-wise
    for i in range(nrows):
        for j in range(ncols):
            lit_map = curr_map[i-3:i+4,j-3:j+4]
            lit_map=lit_map.flatten()
            lit_sum= np.sum(lit_map) - curr_map[i,j]
            mean = np.divide(lit_sum, float(lit_map.size - 1))
            #print(curr_map[i,j], mean)
            ratio[i,j] = np.divide(curr_map[i,j], mean)
            #print("ratio = ",ratio[i,j])
            #print("-------------------------------------------")

    ratio = ratio[~np.isnan(ratio)]

    fig=pl.figure(figsize=(25,10))
    pl.subplot(121)
    pl.hist(ratio.flatten(), bins=100); pl.yscale('log')
    pl.subplot(122)
    pl.hist(ratio.flatten(), bins=100);
    fig.savefig("ratio.png")
    pl.close(fig)




            











