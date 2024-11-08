#!/usr/bin/env python
# coding: utf-8
import file_utils
import numpy as np
import mapping
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
#np.seterr(divide='ignore', invalid='ignore')



#Data files for VnSunOut = 5, 15, 25 (module is H1021)
fullfilename_5 = "/Data/pedestal_scan/2019_04_25_014/H20rawframe_data_5.dat"

pedestals5 = file_utils.read_raw_file(filename=fullfilename_5, dhePrefix="PXD:H1022", asicpair=0, use_header=False)[0]

'''
mapFunc = mapping.mapper("pxd9", "if", fill_value=255)
map_ped5 = mapFunc.raw(pedestals5)
ped5_mean=np.mean(map_ped5,2)
'''

ped5_mean=np.mean(pedestals5,2)

print ped5_mean.shape
#print "Bad pixel number (@VnSunOut=5) = ",ped5_mean[(ped5_mean<20)+(ped5_mean>250)].size

#broken-drain mask
mask_broken_columns = np.load("/home/bonndaq_pc/tmp_varghese/vnsubout_opt/copy_of_KEK_pedestal_mask/H1022/pedestal_mask/broken_drains.npy")
mask_broken_columns = mask_broken_columns.astype(float)
print mask_broken_columns.shape


fig, ax = pl.subplots(1, 2, figsize=(10,10))

pcm = ax[0].pcolormesh(ped5_mean, cmap='viridis')
fig.colorbar(pcm, ax=ax[0])
pcm = ax[1].pcolormesh(mask_broken_columns, cmap='viridis')
fig.colorbar(pcm, ax=ax[1])

fig.tight_layout()
pl.show()
fig.savefig("test2.png")







