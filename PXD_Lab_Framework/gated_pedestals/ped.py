#!/usr/bin/env python
# coding: utf-8
import file_utils
import numpy as np
import mapping
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
#np.seterr(divide='ignore', invalid='ignore')

#try gated mode datasets : /Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_GM_o0.dat  /Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_o0.dat



#Data files for VnSunOut = 5, 15, 25 (module is H1021)
filename_gm  = "/Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_GM_o0.dat"
filename_ref = "/Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_o0.dat"

ped_gm  = file_utils.read_raw_file(filename=filename_gm, dhePrefix="PXD:H1021", asicpair=0, use_header=False)[0]
ped_ref = file_utils.read_raw_file(filename=filename_ref, dhePrefix="PXD:H1021", asicpair=0, use_header=False)[0]

mapFunc = mapping.mapper("pxd9", "if", fill_value=255)

map_ped_gm = mapFunc.raw(ped_gm)
map_ped_ref = mapFunc.raw(ped_ref)


#mean pedestals
ped_mean_gm=np.mean(map_ped_gm, axis=2)
ped_mean_ref=np.mean(map_ped_ref, axis=2)

#pedestal noise
ped_noise_gm=np.std(map_ped_gm, axis =2)
ped_noise_ref=np.std(map_ped_ref, axis =2)

#differences w.r.t. reference
ped_mean_diff = ped_mean_gm - ped_mean_ref
ped_noise_diff = ped_noise_gm - ped_noise_ref

#hiatograms of differences
ped_mean_diff_hist = ped_mean_diff.flatten()
ped_noise_diff_hist = ped_noise_diff.flatten()

#full pedestal difference with frame information
ped_diff_full = map_ped_gm - map_ped_ref



#plots
'''
fig_ped=pl.figure(figsize=(15,15))
pl.subplot(121)
pl.imshow(ped_mean_ref); pl.colorbar(); pl.title('pedestals without GM')
pl.subplot(122)
pl.imshow(ped_mean_gm); pl.colorbar(); pl.title('pedestals with GM')
fig_ped.savefig("pedestals.png")

fig_ped_diff=pl.figure(figsize=(15,15))
pl.subplot(121)
pl.imshow(ped_mean_diff); pl.colorbar(); pl.title('Pedestal difference: with GM - without GM')
pl.subplot(122)
pl.hist(ped_mean_diff_hist); pl.yscale('log'); pl.title('Histogram of pedestal differences')
fig_ped_diff.savefig("pedestal_differences.png")

fig_noi=pl.figure(figsize=(15,15))
pl.subplot(121)
pl.imshow(ped_noise_ref); pl.colorbar(); pl.title('noise without GM')
pl.subplot(122)
pl.imshow(ped_noise_gm); pl.colorbar(); pl.title('noise with GM')
fig_noi.savefig("noise.png")

fig_noi_diff=pl.figure(figsize=(15,15))
pl.subplot(121)
pl.imshow(ped_noise_ref); pl.colorbar(); pl.title('Noise  difference: with GM - without GM')
pl.subplot(122)
pl.hist(ped_noise_diff_hist); pl.yscale('log'); pl.title('Histogram of noise differences')
fig_noi_diff.savefig("noise_differences.png")



fig_drainped_proj=pl.figure(figsize=(15,15))
for i  in range(250):
    pl.plot(ped_mean_diff[:,i])
pl.ylim(-60, 60)
#pl.xlim(300,760)
#pl.xlim(600,700)
pl.xlim(660,690)
fig_drainped_proj.set_figwidth(30)
fig_drainped_proj.savefig("pedestal_drain_projections.png")


fig_drainnoi_proj=pl.figure(figsize=(15,15))
for i  in range(250):
    #pl.plot(ped_noise_diff[:,i])
    pl.plot(ped_noise_gm[:,i])
pl.ylim(0, 15)
pl.xlim(660,760)
fig_drainnoi_proj.set_figwidth(30)
fig_drainnoi_proj.savefig("noise_drain_projections.png")


#projections of pedestal-differences and gm-noise together
fig_proj_tog=pl.figure(figsize=(15,15))
pl.subplot(211)
for i  in range(250):
    pl.plot(ped_mean_diff[:,i])
pl.ylim(-60, 60)
pl.xlim(660,770)
pl.subplot(212)
for i  in range(250):
    pl.plot(ped_noise_gm[:,i])
pl.ylim(0, 20)
pl.xlim(660,770)
fig_proj_tog.set_figwidth(30)
fig_proj_tog.set_figheight(20)
fig_proj_tog.savefig("ped_noise_together.png")



odd=[]
even=[]

for i in range(250):
    if(i%2==1):
        odd.append(i)
    else:
        even.append(i)

#time-evolution of row-685 pixels
fig_ped_diff_full=pl.figure(figsize=(15,15))
#for i  in range(250):
#for i  in range(64):
#for i in odd:
for i in even:
    pl.plot(ped_diff_full[685,i,:])
pl.ylim(0, 40)
#pl.xlim(300,760)
#pl.xlim(600,700)
#pl.xlim(660,690)
fig_ped_diff_full.set_figwidth(20)
fig_ped_diff_full.savefig("time_evolution_row685.png")



#Correlations with mean: How well do row-wise jumps(falls) for drain lines correlate with each-other? : ped_mean_gm
corr=np.zeros(250)
ref = ped_mean_diff[:,125] # reference: drain line 121
for i  in range(250): #looping over drain-lines
    corr[i]=np.corrcoef(ref,ped_mean_diff[:,i])[0][1]
fig_corr=pl.figure(figsize=(15,15))
pl.hist(corr);  pl.title('GM - correlations')
fig_corr.savefig("gm_corr.png")


#Correlations looking at all frames seperately
corr=np.zeros((250,50))
ref = ped_diff_full[:,125,:] # reference: drain line 126
for frame  in range(50):#loop over frames
    for i  in range(250): #looping over drain-lines
        corr[i][frame]=np.corrcoef(ref[:,frame],ped_diff_full[:,i,frame])[0][1]
fig_corr=pl.figure(figsize=(15,15))
pl.hist(corr.flatten());  pl.title('Full GM - correlations')
fig_corr.savefig("gm_corr_full.png")
'''

#Correcting for row-wise averaged noise (row CMC)
#row-wise correction
row_avg_ped_diff=np.mean(ped_mean_diff,axis=1)
ped_mean_diff_corr= ped_mean_diff - row_avg_ped_diff[:,None]
#gate-wise correction
gate_avg_ped_diff=np.mean(row_avg_ped_diff.reshape(-1, 4), axis=1)
gate_avg_ped_diff = np.repeat(gate_avg_ped_diff, 4)
ped_mean_diff_corr2= ped_mean_diff - gate_avg_ped_diff[:,None]
#plotting
fig_row_cmc=pl.figure(figsize=(15,15))
pl.subplot(311)
for i  in range(250):
#for i  in range(63):
    pl.plot(ped_mean_diff[:,i])
#pl.ylim(-60, 60)
pl.xlim(660,720)
#pl.xlim(660,690)
pl.plot(row_avg_ped_diff, 'ko-')
pl.plot(gate_avg_ped_diff, 'ro-')
#pl.plot(row_avg_ped_diff, 
pl.subplot(312)
for i  in range(250):
#for i  in range(63):
    pl.plot(ped_mean_diff_corr[:,i])
#pl.ylim(-60, 60)
pl.xlim(660,720)
#pl.xlim(660,690)
pl.subplot(313)
for i  in range(250):
#for i  in range(63):
    pl.plot(ped_mean_diff_corr2[:,i])
#pl.ylim(-60, 60)
pl.xlim(660,720)
#pl.xlim(660,690)
fig_row_cmc.set_figwidth(30)
fig_row_cmc.set_figheight(30)
#fig_row_cmc.savefig("cmc_corrected_ped_diff_zoom.png")
fig_row_cmc.savefig("cmc_corrected_ped_diff.png")















