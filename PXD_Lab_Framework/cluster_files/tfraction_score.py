import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os
#from scipy.ndimage import gaussian_filter
from ROOT import  gROOT, TCanvas, TH2F, TObjArray, TFractionFitter
import ROOT

gROOT.SetBatch(True)


## add sensor region
rows=768
r_start=1; r_end=768
#r_start=241; r_end=270
#r_start=200; r_end=350
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


#clean up noisy pixels and fill histograms
hitmap_flat = TH2F( 'hitmap_flat', 'hitmap_flat', 240, -0.01, 239.99, 768, -0.01, 767.99 )
hitmap_ring = TH2F( 'hitmap_ring', 'hitmap_ring', 240, -0.01, 239.99, 768, -0.01, 767.99 )

fmax_ring=np.zeros(768); fmax_flat=np.zeros(768)
for i in range(768):
    fmax_ring[i] = np.percentile(ring_map[i,:], 98); fmax_flat[i] = np.percentile(flat_map[i,:], 98)
    for j in range(240):
        if ring_map[i,j] < fmax_ring[i]:
            hitmap_ring.Fill(j,i,ring_map[i,j])
        if flat_map[i,j] < fmax_flat[i]:
            hitmap_flat.Fill(j,i,flat_map[i,j])



wafer='W41_IF_2018_03_28_001'


#create plot directories if not existing already
plot_dir=os.path.join('ring_score_tfrac',wafer)
#plot_subdir=os.path.join('ring_score_tfrac',wafer,'diffmaps')
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)
#if not os.path.exists(plot_subdir):
    #os.makedirs(plot_subdir)

#plot reference histograms
c1 = TCanvas( 'c1', 'c1')
c1.Divide(2,1)
c1.cd(1)
hitmap_ring.Draw('colz')
c1.cd(2)
hitmap_flat.Draw('colz')
c1.Update()
c1.SaveAs('ring_score_tfrac/%s/hitmap_refs_th2f.png'%wafer) 
c1.Close()


template = TObjArray(2)
template.Add(hitmap_ring)
template.Add(hitmap_flat)



input_dir='/home/bonndaq_pc/tmp_hye/source_scan_opt/%s'%wafer
names = {}
for directory in os.listdir(input_dir):
    subdir =  os.path.join(input_dir,directory)
    if os.path.isdir(subdir):
        for filename in os.listdir(subdir):
            fullname = os.path.join(subdir,filename)
            names[directory] = fullname


hitmap_curr = TH2F( 'hitmap_curr', 'hitmap_curr', 240, -0.01, 239.99, 768, -0.01, 767.99 )

for name, fullname in names.items():

    #Get the sample
    name_curr=fullname
    curr_data = tables.open_file(name_curr, mode="r")
    curr_map = curr_data.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
    curr_data.close()


    #hitmap_curr = TH2F( 'hitmap_curr', 'hitmap_curr', 240, -0.01, 239.99, 768, -0.01, 767.99 )
    hitmap_curr.Reset("ICESM")
    fmax_curr = np.zeros(768)
    for i in range(768):
        fmax_curr[i] = np.percentile(curr_map[i,:], 98)
        for j in range(240):
            if curr_map[i,j] < fmax_curr[i]:
                hitmap_curr.Fill(j,i,curr_map[i,j])


    fit = TFractionFitter(hitmap_curr, template)
    status = fit.Fit()
    
    #weights and errors
    w1= ROOT.Double(0); w1_err=ROOT.Double(0)
    w2= ROOT.Double(0); w2_err=ROOT.Double(0)
    fit.GetResult(0, w1, w1_err)
    fit.GetResult(1, w2, w2_err)

    c2 = TCanvas( 'c2', 'c')
    c2.cd()
    hitmap_curr.Draw('colz')
    hitmap_curr.SetTitle('w1 = %s +/= %s , w2 = %s +/- %s '%(w1,w1_err,w2,w2_err))
    c2.Update()
    c2.SaveAs('%s/hitmap_%s_th2f.png'%(plot_dir,name))
    c2.Close()
















