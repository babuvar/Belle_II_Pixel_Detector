#!/usr/bin/python

"""
offsetCalculation.py
====================

Functions which are required to calculate the offset pattern
"""


from matplotlib import pyplot as pl
import numpy as np
#from file_utils import read_DHP02_raw_file
#from dcd_waveform.dcd_waveform_scan import dhePrefix
import mapping
import file_utils
import matrix_operations
import os
import sys
import re


def getOffsets_for_mean(calibrationData, minPedData, mean, maxGoodValue):
    """
    Rreturns the offsets moving the pedestal distribution closest to given mean, but above minPedData, if IPDAC is fixed

    :param calibrationData: row x col x IPDAC x OffsetDAC
    :type calibrationData: 4D numpy array
    :param minPedData: the minimum size, the pedestals should have, before beeing out of dynamic range numpy Array (row x col)
    :type minPedData: 2D numpy array
    :param mean: to be close to
    :type mean: int
    :param maxGoodValue: maximum value which is acceptable
    :type maxGoodValue: int
    :return: offsets (row x col)  (int, 0-3)
    :rtype: 2D numpy array
    """
    # convert the rangeMap (minPedData) into a four dimensional object
    minPedData = minPedData.reshape(minPedData.shape[0], minPedData.shape[1], 1)
    # calculate the difference between the calibration data (row, col, ipdac, pattern) and the mean value
    dist = calibrationData - mean
    # sort out values which are below the rangeMap (20)
    dist[calibrationData[:,:,:,0] < minPedData,0] = -500.3
    dist[calibrationData[:,:,:,1] < minPedData,1] = -500.2
    dist[calibrationData[:,:,:,2] < minPedData,2] = -500.1
    dist[calibrationData[:,:,:,3] < minPedData,3] = -500.0
    # sort out values which are above the maxGoodValue (210)
    dist[calibrationData[:,:,:,0]  > maxGoodValue,0] = 1000.0
    dist[calibrationData[:,:,:,1]  > maxGoodValue,1] = 1000.1
    dist[calibrationData[:,:,:,2]  > maxGoodValue,2] = 1000.2
    dist[calibrationData[:,:,:,3]  > maxGoodValue,3] = 1000.3

    # get the absolut value
    dist = np.absolute(dist)
    # get the minimum of the distance along the offsets (0, 1, 2, 3)
    offsets = np.argmin(dist, axis=3)
    return offsets


def expectedPedestals(calibrationData, offsetMap):
    """
    Returns the best guess pedestals if this ipdac and offsetMap are used

    :param calibrationData: (row x col x IPDAC x OffsetDAC)
    :type calibrationData: 4D numpy array
    :param offsetMap: (row x col)  (int, 0-3)
    :type offsetMap: 2D numpy array
    :return: pedestals (row x col) (float)
    :rtype: 2D numpy array
    """
    index = 4 * np.arange(offsetMap.size) + offsetMap.reshape(-1)
    pedestals = calibrationData.reshape(-1)[index]
    return pedestals.reshape(offsetMap.shape)


def qualityGuess(pedestalMap, minPedData, maxGoodValue, badPixelMap,percentiles=[0.2, 99.8],verbose=False):
    """
    Returns the quality of the pedestal distribution (small is good)

    :param pedestalMap:  Pedestals
    :type pedestalMap: 2D numpy array (row x col) (dtype=float)
    :param minPedData: the minimum size, the pedestals should have, before being out of dynamic range numpy Array (row x col)
    :type minPedData: 2D numpy array (row x col)
    :param maxGoodValue: maximum value which is acceptable
    :type maxGoodValue: int
    :param bad PixelMap: map of known bad pixel
    :return: ???
    """
    # same size as badPixelMap => fill everything with True
    # badPixelMap is a numpy array, it is True for bad pixel.
    bad_pixel_before_scan=np.count_nonzero(badPixelMap)
    goodPixelMap = np.logical_not(badPixelMap)
    # number of pixels which are above the maxGoodValue
    badhighpixel = np.count_nonzero(pedestalMap[goodPixelMap] > maxGoodValue)
    # number of pixels which are below the minPedData
    badlowpixel = np.count_nonzero(pedestalMap[goodPixelMap] < minPedData[goodPixelMap])
    # get percentiles 0.05 and 0.95 quantile
    low, high = np.percentile(pedestalMap[goodPixelMap], percentiles)
    if verbose:
        print "Summary:\nlow border:", low, "\nhigh border:", high,"\nbad pixel (low)",badlowpixel,
        print "\nbad pixel (high)",badhighpixel,"\nmasked:",bad_pixel_before_scan
    #variance=np.std(pedestalMap[goodPixelMap])
    #print  round(20*(high-low)+ badhighpixel+0.3*badlowpixel,0), badhighpixel,badlowpixel,round(high,2),round(low,2),round(variance,2)
    #return 20 * (high - low) + badhighpixel + 0.3 * badlowpixel
    return 4 * (high - low) + high/10. + badhighpixel + 0.5 * badlowpixel


def getDynamicRange(rangeData):
    """
    Create 2 numpy arrays with the shape of the range Data (row, col, current_source), where current_source is vnsubin, vnsubout ...
    One array is filled with 30. The other one is filled with False

    :param rangeData: Data of ranges (row, col, current_source)
    :type rangeData: 3D numpy array
    :returns: See description
    :rtype: 2x 2D numpy arrays
    """
    return np.zeros((rangeData.shape[0], rangeData.shape[1])) + 10, \
           np.zeros((rangeData.shape[0], rangeData.shape[1]), dtype=np.bool)


def calculateOffsets(calibrationData, rangeData, bad_pixel_map=None):
    """
    Calculates the Offset values and the IPDAC value

    :param calibrationData: (row x col x IPDAC x OffsetDAC)
    :type calibrationData: 4D numpy array
    :param rangeData: Data of ranges (row, col, current_source)
    :type rangeData: 3D numpy array

    :return: IPDAC-value, Offsets (2D numpy array), expected Pedestals (2D numpy array), quality Map (2D numpy array)
    """
    rangeMap, badPixelMap = getDynamicRange(rangeData)
    if bad_pixel_map is not None:
        badPixelMap=np.logical_or(badPixelMap,bad_pixel_map)
    maxGoodValue = 210
    qualityMap = np.zeros((calibrationData.shape[2], 220))
    for mean in range(220):
        if mean % 50 == 0:
            print "mean", mean
        offsetValues = getOffsets_for_mean(calibrationData, rangeMap, mean, maxGoodValue)
        expPed = expectedPedestals(calibrationData, offsetValues)
        for ipdac in range(calibrationData.shape[2]):
            #print "ipdac",ipdac
            #qualityMap[ipdac, mean] = 219 - mean + qualityGuess(expPed[:, :, ipdac],
            qualityMap[ipdac, mean] = qualityGuess(expPed[:, :, ipdac],
                                                                rangeMap,
                                                                maxGoodValue,
                                                                badPixelMap)

    minipdac = np.argmin(np.amin(qualityMap, 1), 0)
    minmean = np.argmin(qualityMap[minipdac, :], 0)
    print "best mean:", minmean, "best IPDAC:", minipdac
    offsetValues = getOffsets_for_mean(calibrationData, rangeMap, minmean, maxGoodValue)
    expPed = expectedPedestals(calibrationData, offsetValues)
    qualityGuess(expPed[:, :, minipdac], rangeMap, maxGoodValue, badPixelMap,verbose=True)
    return minipdac, offsetValues[:, :, minipdac], expPed[:, :, minipdac], qualityMap


def getOffsets_new(logger, path, module, nGates, nDrains, current_source_ranges, ipdac_ranges, asicpair,
                   bad_pixel_map=None, ped_mask_path=None):
    """
    This function reads the offsets calibration data and the range data and caluclates the offsets

    :param logger: logger object
    :type logger: log_utils._java_logger_adapter
    :param path: path where calibration data and range data are stored
    :type path: string
    :param module: module object
    :type module: devices.Device
    :param nGates: number of Gates, should be equal to the matrix size
    :type nGates: int
    :param nDrains: number of Drains, should be equal to the matrix size
    :type nDrains: int
    :param current_source_ranges: Curren source values
    :type current_source_ranges: list of int
    :param ipdac_ranges: IPDAC values
    :type ipdac_ranges: list of int
    :param asicpair: asicpair (not required for zero suppressed data)
    :type asicpair: int
    :param bad_pixel_map:
    :type bad_pixel_map:
    """

    # (rows, columns, ipdac-values, offsetpattern)
    # we analyze each asicpair individually => only 64 columns
    # when we read the function (in pedestals_from_zp_slices then
    # we read the entire matrix, i.e. four asicpairs => hence we
    # need to specify the correct number of columns and rows
    calibrationData = np.zeros((4 * nGates, 64, len(ipdac_ranges), 4))
    rangeData = np.zeros((4 * nGates, 64, len(current_source_ranges)))
    #calibrationData = np.zeros((4 * nGates, nDrains/4, len(ipdac_ranges), 4))
    #rangeData = np.zeros((4 * nGates, nDrains/4, len(current_source_ranges)))
    logger.finest("Reading range data for DHE %s, asicpair %i" % (module.dhe, asicpair))
    for index, value in enumerate(current_source_ranges):
        fullname = os.path.join(path, "%srangeData_%03d.dat" % (module.dhc if module.dhc is not None else "", value))
        #FIXME
        # only works for memory dumps
        #data = file_utils.read_raw_file(dhePrefix=dhePrefix, filename=fullname, asicpair=asicpair)[0]
        #rangeData[:, :, index] = np.mean(data, axis=2)
        #print "nGates*4", nGates*4
        #print "nDrains/4", nDrains/4
        #print "asicpair", asicpair
        #ped_mean, ped_noise = matrix_operations.pedestals_from_zp_slices(filename=fullname,
        #                                                                 dhePrefix=dhePrefix,
        #                                                                 rows=nGates*4,
        #                                                                 columns=nDrains/4,
        #                                                                 asicpair=asicpair)
        data = file_utils.read_raw_file(filename=fullname, dhePrefix="PXD:%s" % module.dhe, asicpair=asicpair,
                                        use_header=False)[0]
        ped_mean = np.mean(data, axis=2)
        ped_noise = np.mean(data, axis=2)
        # row, col, vnsubin
        rangeData[:, :, index] = ped_mean

    for pattern in range(4):
        for i, ipdacVal in enumerate(ipdac_ranges):
            if pattern == 0 and i > 0:
                fullname = os.path.join(path,
                                        "%soffsetData_%01d_%03d.dat" % (module.dhc if module.dhc is not None else "",
                                                                        pattern, ipdac_ranges[0]))
            else:
                fullname = os.path.join(path,
                                        "%soffsetData_%01d_%03d.dat" % (module.dhc if module.dhc is not None else "",
                                                                        pattern, ipdacVal))
            #FIXME
            # only works for memory dumps
            #data = file_utils.read_raw_file(dhePrefix=dhePrefix, filename=fullname, asicpair=asicpair)[0]
            #calibrationData[:, :, value, offset] = np.mean(data, axis=2)
            #ped_mean, ped_noise = matrix_operations.pedestals_from_zp_slices(filename=fullname,
            #                                                                 dhePrefix=dhePrefix,
            #                                                                 rows=nGates*4,
            #                                                                 columns=nDrains/4,
            #                                                                 asicpair=asicpair)

            data = file_utils.read_raw_file(filename=fullname, dhePrefix="PXD:%s" % module.dhe, asicpair=asicpair,
                                            use_header=False)[0]
            ped_mean = np.mean(data, axis=2)
            ped_noise = np.mean(data, axis=2)
            # row, col, ipDacVal, pattern
            calibrationData[:, :, i, pattern] = ped_mean

    # we try to get a mask which already exists from the pedestals
    path_mask = os.path.join(ped_mask_path, module.dhe, "pedestal_mask")
    filename_mask = os.path.join(path_mask, "broken_drains.npy")
    # we load the mask if it exists

    if os.path.exists(filename_mask):
        mask_broken_columns = np.load(filename_mask)
        # the mask is for pxd9 consisting of 768x256 pixel, hence we have to split it according to the number of columns
        mask_broken_columns = mask_broken_columns[:, (asicpair-1)*64: asicpair*64]
        # now we check whether a mask already exists, if it is the case we merge the mask to the existing one
        if bad_pixel_map is not None:
            bad_pixel_map = np.logical_or(bad_pixel_map, mask_broken_columns)
        # otherwise this (mask of broken columns) will be our new mask
        else:
            bad_pixel_map = mask_broken_columns

    ipdac_index, offsetMatrixFormat, expPedestals, quality = calculateOffsets(calibrationData, rangeData,
                                                                              bad_pixel_map=bad_pixel_map)
    return ipdac_ranges[ipdac_index], offsetMatrixFormat, expPedestals, quality, calibrationData



