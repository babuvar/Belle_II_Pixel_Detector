#import ROOT
from ROOT import gROOT, TCanvas, TH2F, TH1F, TGraph2D, gStyle, TColor
import numpy as np
import matplotlib as mpl
#mpl.use('Agg')
from matplotlib import pyplot as pl
from mpl_toolkits.mplot3d import Axes3D


date='2018_10_25_007'; hv=np.array([60000, 62000, 64000, 66000, 68000, 70000]); ring_score=np.zeros((6,3,4,3))


score_data = np.load('results.npy').item()



drift=np.array([3000, 4000, 5000])
clear_off=np.array([2000, 3000, 4000, 5000])


#Histograms
nbinsx=hv.size; x_low=hv[0] - 1000; x_high=hv[hv.size-1] + 1000
nbinsy=clear_off.size; y_low=clear_off[0] - 500; y_high=clear_off[clear_off.size-1] + 500

#flatness-histograms
h1 = TH2F('h1','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h1.SetTitle("Flatness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Flatness-coeff"%drift[0]);
h2 = TH2F('h2','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h2.SetTitle("Flatness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Flatness-coeff"%drift[1]);
h3 = TH2F('h3','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h3.SetTitle("Flatness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Flatness-coeff"%drift[2]);

#ringness-histograms
h4 = TH2F('h4','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h4.SetTitle("Ringness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Ringness-coeff"%drift[0]);
h5 = TH2F('h5','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h5.SetTitle("Ringness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Ringness-coeff"%drift[1]);
h6 = TH2F('h6','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h6.SetTitle("Ringness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Ringness-coeff"%drift[2]);

#gridness-histograms
h7 = TH2F('h7','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h7.SetTitle("Gridness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Gridness-coeff"%drift[0]);
h8 = TH2F('h8','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h8.SetTitle("Gridness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Gridness-coeff"%drift[1]);
h9 = TH2F('h9','',nbinsx,x_low,x_high,nbinsy,y_low,y_high); h9.SetTitle("Gridness@Drift = %s mV; High-voltage (mV); Clear-off (mV); Gridness-coeff"%drift[2]);





for key,val in score_data.items():
    hv_val=float(key[3:8]); drift_val=float(key[15:19]); clear_off_val = float(key[29:34])
    ring_score[np.where(hv == hv_val),np.where(drift == drift_val),np.where(clear_off == clear_off_val),:]=val



#gStyle.SetNumberContours(999)

gStyle.SetOptStat(0)
gStyle.SetPalette(106)
TColor.InvertPalette()

#plots


for i in range(hv.size):
    for j in range(4):
        h1.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,0,j,0]) )
        h2.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,1,j,0]) )
        h3.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,2,j,0]) )

        h4.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,0,j,1]) )
        h5.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,1,j,1]) )
        h6.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,2,j,1]) )

        h7.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,0,j,2]) )
        h8.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,0,j,2]) )
        h9.Fill( float(hv[i]), float(clear_off[j]), float(ring_score[i,0,j,2]) )


c1 = TCanvas('c1','',200, 10, 1200, 900 ); c1.Divide(2,2)
c1.cd(1); h1.Draw("colz"); c1.cd(2); h2.Draw("colz"); c1.cd(3); h3.Draw("colz");
c1.SaveAs('VoltageMap_flatness.png')

c2 = TCanvas('c2','',200, 10, 1200, 900 ); c2.Divide(2,2)
c2.cd(1); h4.Draw("colz"); c2.cd(2); h5.Draw("colz"); c2.cd(3); h6.Draw("colz");
c2.SaveAs('VoltageMap_ringness.png')

c3 = TCanvas('c3','',200, 10, 1200, 900 ); c3.Divide(2,2)
c3.cd(1); h7.Draw("colz"); c3.cd(2); h8.Draw("colz"); c3.cd(3); h9.Draw("colz");
c3.SaveAs('VoltageMap_gridness.png')


raw_input()











