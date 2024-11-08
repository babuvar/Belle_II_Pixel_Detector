#import ROOT
from ROOT import gROOT, TCanvas, TH2F, TH1F, TGraph2D, gStyle
import numpy as np
import matplotlib as mpl
#mpl.use('Agg')
from matplotlib import pyplot as pl
from mpl_toolkits.mplot3d import Axes3D


date='2018_10_25_007'; hv=np.array([60000, 62000, 64000, 66000, 68000, 70000]); ring_score=np.zeros((6,3,4))


score_data = np.load('results.npy').item()



drift=np.array([3000, 4000, 5000])
clear_off=np.array([2000, 3000, 4000, 5000])


#Histograms
nbinsx=hv.size; x_low=hv[0] - 1000; x_high=hv[hv.size-1] + 1000
nbinsy=clear_off.size; y_low=clear_off[0] - 500; y_high=clear_off[clear_off.size-1] + 500


h1 = TH2F('h1','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h1.SetTitle("Drift = %s mV; High-voltage (mV); Clear-off (mV); Ring-score"%drift[0]);
h2 = TH2F('h2','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h2.SetTitle("Drift = %s mV; High-voltage (mV); Clear-off (mV); Ring-score"%drift[1]);
h3 = TH2F('h3','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h3.SetTitle("Drift = %s mV; High-voltage (mV); Clear-off (mV); Ring-score"%drift[2]);


ring_score[:,:,:]=-999


for key,val in score_data.items():
    hv_val=float(key[3:8]); drift_val=float(key[15:19]); clear_off_val = float(key[29:34])
    ring_score[np.where(hv == hv_val),np.where(drift == drift_val),np.where(clear_off == clear_off_val)]=val



gStyle.SetNumberContours(999)
gStyle.SetOptStat(0)


#plots

c1 = TCanvas('c1','',200, 10, 1200, 900 ); c1.Divide(2,2)

for i in range(hv.size):
    for j in range(4):
        if ring_score[i,0,j] > -5:
            h1.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,0,j]) )
        if ring_score[i,1,j] > -5:
            h2.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,1,j]) )
        if ring_score[i,2,j] > -5:
            h3.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,2,j]) )




c1.cd(1); h1.Draw("colz");
c1.cd(2); h2.Draw("colz");
c1.cd(3); h3.Draw("colz");


c1.SaveAs('VoltageMap.png')



raw_input()












