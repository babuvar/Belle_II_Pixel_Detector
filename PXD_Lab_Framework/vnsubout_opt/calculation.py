#!/usr/bin/python

"""
calculation.py
====================


"""

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl
import numpy as np
#import mapping
import file_utils
#import matrix_operations
import os
import sys
import log_utils

#def getQuality_params(ASICpairData, limit_low=20, limit_high=250):
def getQuality_params(logger, path, module, nGates, nDrains, current_source_ranges, asicpair,
                      bad_pixel_map=None, ped_mask_path=None, limit_low=2, limit_high=254):
    """
    Returns the number of bad pixels, i.e., the number of pixels outside the specified range and also the mean of the pedestal distribution for the ASIC pair.

    :param ASICpairData: row x col
    :type ASICpairData: 2D numpy array
    :param limit_low: defining the lower limit of an 'acceptable pedestal'
    :type limit_low: int
    :param limit_high: defining the upper limit of an 'acceptable pedestal'
    :type limit_high: int
    :return: num_bad_pix
    :rtype: int
    :return: mean
    :rtype: float
    """

    #logger.fine("Performing calculations on DHE %s, asicpair = %i" % (module.dhe,asicpair) )

    rangeData = np.zeros((4 * nGates, 64, len(current_source_ranges)))
    current_source_value = np.zeros(len(current_source_ranges))
    bad_pix_count = np.zeros(len(current_source_ranges))
    #Center-of-gravity of pedestals
    COG_ped = np.zeros(len(current_source_ranges))

    logger.finest("Reading range data for DHE %s, asicpair %i" % (module.dhe, asicpair))
    for index, value in enumerate(current_source_ranges):
        fullname = os.path.join(path, "%srawframe_data_%d.dat" % (module.dhc if module.dhc is not None else "", value))
        #print "fullname = ", fullname
        data = file_utils.read_raw_file(filename=fullname, dhePrefix="PXD:%s" % module.dhe, asicpair=asicpair,
                                        use_header=False)[0]
        ped_mean = np.mean(data, axis=2)
        #ped_noise = np.std(data, axis=2)
        rangeData[:, :, index] = ped_mean

        #print "For module(DHE) = ", module.dhe, ", ascipair = ", asicpair
        #print ped_mean.shape
        pedestal_COG=np.mean(ped_mean)
        num_bad_pix=ped_mean[(ped_mean<limit_low)+(ped_mean>limit_high)].size
        #print "pedestal_COG= ",pedestal_COG, " num_bad_pix= ", num_bad_pix

        current_source_value[index] = value
        bad_pix_count[index] = num_bad_pix
        COG_ped[index] = pedestal_COG

    #Plot ASIC behaviour vs current source values
    module_path = os.path.join(path, module.dhe)
    fullfilename= os.path.join(module_path, "%s_D%i_quality.png" %(module.dhe, asicpair))
    #fig=pl.figure(figsize=(10,10))
    #pl.plot(current_source_value, bad_pix_count, 'ro')
    #pl.show()
    #fig.savefig(fullfilename)
    fig, ax1 = pl.subplots()
    color = 'tab:red'
    ax1.set_xlabel('VnSubOut')
    ax1.set_ylabel('Bad pixel count', color=color)
    ax1.plot(current_source_value, bad_pix_count, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Pedestal center of gravity', color=color)  # we already handled the x-label with ax1
    ax2.plot(current_source_value[:], COG_ped[:], color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    pl.show()
    fig.savefig(fullfilename)


    """
    # we try to get a mask which already exists from the pedestals
    path_mask = os.path.join(ped_mask_path, module.dhe, "pedestal_mask")
    filename_mask = os.path.join(path_mask, "broken_drains.npy")

    # we load the mask if it exists
    if os.path.exists(filename_mask):
        print "filename_mask exists"
        mask_broken_columns = np.load(filename_mask)
        # the mask is for pxd9 consisting of 768x256 pixel, hence we have to split it according to the number of columns
        mask_broken_columns = mask_broken_columns[:, (asicpair-1)*64: asicpair*64]
        # now we check whether a mask already exists, if it is the case we merge the mask to the existing one
        if bad_pixel_map is not None:
            bad_pixel_map = np.logical_or(bad_pixel_map, mask_broken_columns)
        else:
            bad_pixel_map = mask_broken_columns

    else:
        print "filename_mask does not exist"
"""

    #Things to return: rangeData (for plotting), (Numbadpix, COG for each VnSubOut), optimal VnSubOut
    #return rangeData





