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

#wafer='W41_IF_2018_03_28_001'; r_start=1; r_end=768
name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'#ring
#name_ring = '/Data2/source_scan_samples/W41_IF_2018_03_28_001/hv-72000_drift-4000_clear-off4000/clusterdb.h5'#flat

#wafer='W44_IF_2018_03_20_001'; #r_start=340; r_end=540
#name_ring = '/Data2/source_scan_samples/W44_IF_2018_03_20_001/hv-62000_drift-4000_clear-off5000/clusterdb.h5'
#name_flat = '/home/bonndaq_pc/tmp_hye/source_scan_opt/W44_IF_2018_03_20_001/hv-72000_drift-4000_clear-off2000/clusterdb.h5'

#wafer='W45_IB_2017_12_04_002'; r_start=300; r_end=500
#name_ring = '/Data2/source_scan_samples/W45_IB_2017_12_04_002/hv-60000_drift-4000_clear-off5000/clusterdb.h5'
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



#gStyle.SetOptStat(0)


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

ring_full=np.sum(ring_map)

ring_profile = np.copy(ring_map)
copy = np.copy(ring_map)

#Row-wise normalization
for i in range(nrows):
    tot=np.sum(ring_map[i,:])
    ring_map[i,:]=np.true_divide(ring_map[i,:],tot)



#Column-wise normalization
for i in range(ncols):
    tot=np.sum(ring_map[:,i])
    ring_map[:,i]=np.true_divide(ring_map[:,i],tot)


#renormalize
ring_mean=np.max(ring_map)
#c_ring=np.true_divide(ring_full,ring_fullnow)
ring_map=np.true_divide(ring_map,ring_mean)


#Get the profile map ring_profile
for  i in range(nrows):
    for j in range(ncols):
        ring_profile[i,j] = ring_profile[i,j] / ring_map[i,j]


#plot
fig=pl.figure(figsize=(15,15))
pl.subplot(131)
pl.imshow(copy); pl.colorbar();
pl.subplot(132)
#pl.imshow(ring_map[350:500,50:200]); pl.colorbar(); pl.title('Efficiency-rings')
pl.imshow(ring_map); pl.colorbar(); pl.title('Efficiency-rings')
pl.subplot(133)
pl.imshow(ring_profile); pl.colorbar(); pl.title('Hitmap-profile')
fig.savefig("plot.png")
pl.close(fig)





#ringmap = TH2F( 'ringmap', 'ringmap', 240, -0.01, 239.99, 768, -0.01, 767.99 )
#for i in range(768):
#    for j in range(240):
#        ringmap.Fill(float(j),float(i),ring_map[i,j])



#Fitting

#drow = RooRealVar("drow","drow",0,240);
#dcol = RooRealVar("dcol","dcol",0,768);

#importing to RooDataHist

#map2d = RooDataHist("map2d","map2d", RooArgList(RooArgSet(drow,dcol)), ringmap);

#map2d = RooDataHist("map2d","map2d", RooArgSet('drow','dcol'), ringmap, 1)
#map2d = RooFit.Import(ringmap)


#radial function
#circle offset
#x0 = RooRealVar("x0","x0",-10000,10000);
#y0 = RooRealVar("y0","y0",-10000,10000);
#rad = RooFormulaVar("rad","sqrt( ((drow-x0)*(drow-x0)) + ((dcol-y0)*(dcol-y0)) )",RooArgList(drow,dcol,x0,y0));

#5th order chebyshev
#p1 = RooRealVar("p1","p1",0.0,-1.0,1.0);
#p2 = RooRealVar("p2","p2",0.0,-1.0,1.0);
#p3 = RooRealVar("p3","p3",0.0,-1.0,1.0);
#p4 = RooRealVar("p4","p4",0.0,-1.0,1.0);
#p5 = RooRealVar("p5","p5",0.0,-1.0,1.0);
#radPol = RooChebychev("radPol", "radPol", rad, RooArgList(p1,p2,p3,p4,p5));
#radPol = RooChebychev("radPol", "radPol", rad, RooArgList(p1,p2));

#result = RooFitResult(map2d, RooFit.Save(True) )
#result = radPol.fitTo(map2d, RooFit.Extended(1), RooFit.Range("fitRange"), RooFit.SumCoefRange("fitRange"), RooFit.NumCPU(1), RooFit.Verbose(0), RooFit.PrintLevel(-1), RooFit.Save(True) )

#x0.setConstant(0)
#y0.setConstant(0)
#p1.setConstant(0)
#p2.setConstant(0)
#p3.setConstant(0)
#p4.setConstant(0)
#p5.setConstant(0)

#print "map2d type is ", type(map2d)
#print "radPol type is ", type(radPol)


#arglist = RooLinkedList(0)
#saveArg = RooFit.Save()
#arglist.add(saveArg)
#radPol.chi2FitTo(map2d, arglist)

#hfile.Write()


print "its done"





#c1 = TCanvas('c1','',200, 10, 500, 1200 );
#c1.cd(); ringmap.Draw("colz"); gPad.SetLeftMargin(0.15); gPad.SetRightMargin(0.15);
#c1.SaveAs('hitmap.png')


#raw_input()

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











