#!/usr/bin/env python
# coding: utf-8
import file_utils
import numpy as np
import mapping
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import file_utils
import mapping
#np.seterr(divide='ignore', invalid='ignore')

#try gated mode datasets : /Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_GM_o10.dat  /Data/gm_offset_scan/2019_08_09_002/H20rawframe_data_o10.dat



asicpair=1
framenr=10
data_dict = {}
filename = '/Data/current_source_scan/2019_08_15_002/H20rawframe_data_0.dat'
#data_dict[module.dhe] = file_utils.read_raw_file(filename, module.dhe, asicpair=asicpair, frames=framenr, use_header=True, skip_broken_frames=config_ana_dict['skip_broken_frames'])[0]
data_dict['H1011'] = file_utils.read_raw_file(filename, 'H1011', asicpair=asicpair, frames=framenr, use_header=True)[0]
data_dict['H1021'] = file_utils.read_raw_file(filename, 'H1021', asicpair=asicpair, frames=framenr, use_header=True)[0]

data= data_dict['H1011']

drain_mask = np.full(256, fill_value=True, dtype=np.bool)
drain_mask[10:16] = False
total_mask = mapping.matrixToDcd(np.empty((768, 64), dtype=np.bool))
total_mask[:, :] = np.hstack([drain_mask] )[None, :]
total_mask = mapping.dcdToMatrix(total_mask)

#print data.shape[:2]

#data_frame=data[:,:,3]

#data_flat=data_frame.flatten()
#print data_flat.shape

data_real=data_frame[total_mask]
#data_flat=data_real.flatten()
#print data_flat.shape


'''
#Save plot
fig=pl.figure(figsize=(15,15))
pl.subplot(121)
pl.imshow(data[:,:,3]); #pl.colorbar();
pl.subplot(122)
pl.imshow(total_mask); #pl.colorbar();
fig.savefig("compare_%s.png"%asicpair)
'''


'''
#Data files for VnSunOut = 5, 15, 25 (module is H1021)
fullfilename_5 = "/Data/pedestal_scan/2019_04_05_014/H20rawframe_data_5.dat"
pedestals5 = file_utils.read_raw_file(filename=fullfilename_5, dhePrefix="PXD:H1021", asicpair=0, use_header=False)[0]
mapFunc = mapping.mapper("pxd9", "if", fill_value=255)
map_ped5 = mapFunc.raw(pedestals5)
ped5_mean=np.mean(map_ped5,2)
diff5_15=ped15_mean-ped5_mean



#Save plot
fig=pl.figure(figsize=(15,15))
pl.subplot(231)
pl.imshow(ped5_mean); pl.colorbar(); pl.title('ped@vnsubout_5')
pl.subplot(232)
pl.imshow(diff5_15); pl.colorbar(); pl.title('ped@vnsubout_15 - ped@vnsubout_5')
pl.subplot(233)
pl.hist(diff5_15_hist); pl.yscale('log'); pl.title('histogram: ped@vnsubout_15 - ped@vnsubout_5')
pl.subplot(234)
pl.imshow(ped15_mean); pl.colorbar(); pl.title('ped@vnsubout_15')
pl.subplot(235)
pl.imshow(diff15_25); pl.colorbar(); pl.title('ped@vnsubout_25 - ped@vnsubout_15')
pl.subplot(236)
pl.hist(diff15_25_hist); pl.yscale('log'); pl.title('histogram: ped@vnsubout_25 - ped@vnsubout_15')
fig.savefig("plots/pedestal_differences.png")
'''

























