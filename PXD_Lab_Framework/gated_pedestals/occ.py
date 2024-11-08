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
ped_mean_ref=np.mean(map_ped_ref, axis=2)
ped_mean_gm=np.mean(map_ped_gm, axis=2)


#Creating artificial zs frames
diff_frames = np.empty(shape=(768, 250, 50))
for i in range(50):
    diff_frames[:,:,i] = map_ped_gm[:,:,i] - ped_mean_ref






##########TESTING##########
'''
#differences w.r.t. reference
ped_mean_diff = ped_mean_gm - ped_mean_ref
#gate-wise projection
ped_diff_row_proj=np.sum(ped_mean_diff, axis=1)
ped_diff_gate_proj=np.sum(ped_diff_row_proj.reshape(-1, 4), axis=1)

#plots
fig_ped=pl.figure(figsize=(15,15))
pl.subplot(131)
#pl.imshow(ped_diff_gate_map); pl.colorbar(); pl.title('pedestal difference')
pl.plot(ped_diff_row_proj); pl.title('row projection')
pl.subplot(132)
pl.plot(ped_diff_gate_proj[180:]); pl.title('gate projection')
pl.subplot(133)
pl.plot(ped_diff_gate_proj[:10]); pl.title('gate projection')
 
fig_ped.savefig("new.png")
'''
##########TESTING##########

















