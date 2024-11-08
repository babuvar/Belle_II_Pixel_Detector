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


onelist=[('hv-66000_drift-6000_clear-off5000', '/Data2/source_scan_samples/%s/hv-66000_drift-6000_clear-off5000/clusterdb.h5'%wafer)]

nrows2=nrows
ncols2=ncols

for name, fullname in names.items():
#for name, fullname in onelist:


    nrows=nrows2
    ncols=ncols2
    
    name_curr=fullname
    curr_data = tables.open_file(name_curr, mode="r")
    curr_map = curr_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
    curr_data.close()
    curr_map_copy = np.copy(curr_map)

    #Trim rows
    takerows=[]
    for i in range(nrows):
        nonz=float(np.count_nonzero(curr_map[i,:]))
        size = float(curr_map[i,:].size)
        frac_dead = (size-nonz) / size
        if frac_dead < 0.05:
            takerows.append(i)
    curr_map=np.take(curr_map, takerows, axis=0)


    #Trim cols
    takecols=[]
    for i in range(ncols):
        nonz=float(np.count_nonzero(curr_map[:,i]))
        size = float(curr_map[:,i].size)
        frac_dead = (size-nonz) / size
        if frac_dead < 0.05:
            takecols.append(i)
    curr_map=np.take(curr_map, takecols, axis=1)

    
    #modify after trimming
    nrows=curr_map.shape[0]; ncols=curr_map.shape[1]
    curr_map=curr_map.astype(float)
    

    #Clean out noisy pixels 
    for i in range(nrows):
        for j in range(ncols):
            lit_map = curr_map[i-3:i+4,j-3:j+4]
            lit_map=lit_map.flatten()
            lit_sum= np.sum(lit_map) - curr_map[i,j]
            mean = np.divide(lit_sum, float(lit_map.size - 1))
            ratio = np.divide(curr_map[i,j], mean)
            if ratio > 5:
                curr_map[i,j] = 0

    #Zero map for ignoring pixels in later calculations
    zero_map=np.copy(curr_map)
    

    #curr_map=ma.masked_where(curr_map == 0, curr_map)


    #Row-projection (240)
    r_proj = np.zeros(ncols)
    r_proj.astype(float)
    for i in range(ncols):
        r_proj[i] = np.sum(curr_map[:,i])
        nonz = np.count_nonzero(curr_map[:,i])
        r_proj[i] = r_proj[i] / nonz
    r_max = np.max(r_proj)
    r_proj = np.divide(r_proj, r_max)
    #r_proj=gaussian_filter(r_proj, sigma=8)

    #Column-wise normalization (768)
    c_proj = np.zeros(nrows)
    c_proj.astype(float)
    for i in range(nrows):
        c_proj[i] = np.sum(curr_map[i,:])
        nonz = np.count_nonzero(curr_map[i,:])
        c_proj[i] = c_proj[i] / nonz
    c_max = np.max(c_proj)
    c_proj = np.divide(c_proj, c_max)
    #c_proj=gaussian_filter(c_proj, sigma=8)

    #profile map
    profile =np.zeros((nrows,ncols))
    for i in range(nrows):
        for j in range(ncols):
            profile[i,j] = c_proj[i]*r_proj[j]

    #Apply gaussian blur on hitmap
    #curr_map=curr_map.astype(float)
    blur_map=gaussian_filter(curr_map, sigma=3)


    #renormalize
    prof_sum = np.sum(profile)
    curr_sum = np.sum(curr_map)
    const = prof_sum / curr_sum
    profile = np.true_divide(profile, const)


    #Residual map
    diff_map =np.zeros((nrows,ncols))
    for i in range(nrows):
        for j in range(ncols):
            if zero_map[i,j] == 0:
                diff_map[i,j] = 0
            else:
                diff_map[i,j] = blur_map[i,j] - profile[i,j]

    #normalize
    diff_map = np.true_divide(diff_map,curr_sum)

    #std.dev and variance
    #Ignore dead pixels in calculation
    diff_hist=diff_map.flatten()
    zero_hist=zero_map.flatten()
    diff_hist=diff_hist[np.nonzero(zero_hist)]
    #Moments
    std = np.std(diff_hist)
    var = np.var(diff_hist)

    
    fig2=pl.figure(figsize=(25,10))
    #pl.subplot(161)
    #pl.plot(r_proj)
    #pl.subplot(162)
    #pl.plot(c_proj)
    pl.subplot(151)
    pl.imshow(curr_map_copy, interpolation="none", vmin=0, vmax=np.percentile(curr_map_copy, 95)); pl.colorbar();
    pl.subplot(152)
    pl.imshow(blur_map, interpolation="none"); pl.colorbar();
    pl.subplot(153)
    pl.imshow(profile, interpolation="none"); pl.colorbar();
    pl.subplot(154)
    pl.imshow(diff_map, interpolation="none"); pl.colorbar();
    pl.subplot(155)
    pl.hist(diff_hist, bins=100 ); pl.title('std = %s'%std)
    fig2.savefig("histos/hist_%s.png"%name)
    pl.close(fig2)
    
    print("%s is done"%name)












