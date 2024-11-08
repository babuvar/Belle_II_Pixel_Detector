#!/usr/bin/env python

"""
analysis.py
===========

:authors: Harrison Schreeck

Analyses pedestals

This script load the recorded pedestals and analyses them. This includes creating various plots. The script is
configured via the given analysis.ini file.

Usage:
The script takes all configuration from an ini-file which is given via the -c parameter:
>>> ./analysis.py -c analysis.ini

Config:

[general]
path = latest                       #[REQ]  path to file to be analyzed, this can be latest, newest or nothing to
                                            automatically determine it from .latestpath
subtraction = subtractionfile.npy   #[OPT]  Numpy file that contains pedestals, which will be subtracted from each frame
                                            during the analysis (like an offline pedestal correction). If not given, no
                                            subtraction will be performed

[plots]
mapping = device                    #[REQ]  mapping type, can be: pxd9, hybrid5, electrical, matrix or device (device
                                            will be interpreted as pxd9 or hybrid5, depending on module_type in
                                            measure.ini)
show_plots = False                  #[REQ]  Should the plots be shown on screen or only saved to disk?
plot_frame = False                  #[REQ]  WARNING! This option is not working at the moment, leave it to False!
plot_ped_both_mapping = False       #[REQ]  WARNING! This option is not working at the moment, leave it to False!
plot_noise = False                  #[REQ]  Plot that shows the noise distribution together with a histogram.
plot_pedestals = False              #[REQ]  Plot that shows the pedestal distribution together with a histogram.
plot_pedestals_mult = False         #[REQ]  Plot that shows the pedestal distribution (no mean of frames calculated)
                                            together with a histogram.
plot_everything = False             #[REQ]  Plot pedestal distribution with histogram and noise distribution with given
                                            and electrical mapping

[masking]
do_masking = False                  #[REQ]  Apply noise masking? Unconnected channels are always masked, even if this
                                            option is set to False!
maskthreshold = 2.5                 #[REQ]  Which threshold should be used for masking? Unit is ADU.

[common_mode_correction]
use_cmc = False                     #[REQ]  use offline common mode correction?
cmc_threshold = 5                   #[REQ]  threshold for offline common mode correction
"""

import matplotlib
matplotlib.use('agg')
import log_utils
from argparse import ArgumentParser
import os
import configparser
import elog
import file_utils
import plots
from matplotlib import pyplot as pl
import numpy as np
import mapping
import cm_corr
from epics.ca import create_context, destroy_context
from dhc_utils import get_put_progress
from multiprocessing import Manager
from epics import CAProcess
import raw_data_utils
import config_utils
pl.viridis()


def __submit_elog(credentials, dhc_objects, local_ini, logger, return_dict):
    logger.info("Submitting the elog entries now")
    process_list = []
    for dhc in dhc_objects:
        for dhe in dhc.modules:
            arguments = [credentials, dhe, local_ini, logger, return_dict, dhc_objects]
            process_list.append(CAProcess(target=_submit_single_elog, args=arguments))
    for el in process_list:
        el.start()
    for el in process_list:
        el.join()
    
        
def _submit_single_elog(credentials, dhe, local_ini, logger, return_dict, dhc_objects):
    try:
        if "%spath" % dhe.dhe in return_dict:
            myelog = elog.elog(local_ini, type="Pedestal Analysis", dhe=dhe.dhe, dhc_objects=dhc_objects,
                                username=credentials.getusername(),
                                password=credentials.getpassword())
            myelog.submitEntry(path=return_dict["%spath" % dhe.dhe])
    except Exception as e:
        logger.warning("elog.submitEntry:" + repr(e))


def __getpath(config_ana, tmp):
    if tmp:
        path = "/tmp"
    else:
        # if path is loaded from .latestpath do this with highest priority
        path = config_ana.get("general", "path")
        if path in [None, "", "newest", "latest"]:
            # determine directory of script and read .latestpath file
            latestpathfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".latestpath")
            with open(latestpathfile, "r") as f:
                path = f.read()
    return path


def get_system_info(config_measure, dhc_objects=None):
    """
    The status of the ACMC and 2-Bit DAC offsets is stored in the measure.ini from which we load it here.
    Two dictionaries (key = DHE name, value = list of status) are returned with the information.
    If a list with dhc_objects is given, the same list will be returned at the end. Otherwise this list is created
    based on the information from the measure.ini

    :param config_measure: Path to the measure.ini
    :type  config_measure: string
    :param dhc_objects: List of dhc objects
    :type dhc_objects: list

    :return: List with dhc_objects, Dictionary with the ACMC status, Dictionary withe the Offset status
    :rtype: list, list, list
    """
    if dhc_objects is None:
        dhc_objects = config_utils.get_setup_from_scan_config(config_measure)

    config = config_utils.read_config(config_measure)
    acmc_status_dict = {}
    offset_status_dict = {}
    asicpairs = [1, 2, 3, 4]
    for dhc in dhc_objects:
        for module in dhc.modules:
            acmc_status_dict[module.dhe] = [config.get(module.dhe, "ACMC_DCD%i" % el) for el in asicpairs]
            offset_status_dict[module.dhe] = [config.get(module.dhe, "OFFSET_DHP%i" % el) for el in asicpairs]

    return dhc_objects, acmc_status_dict, offset_status_dict


def mapdata(data, mapping_style, module_type, asicpair=0):
    if mapping_style == "matrix":
        return data
    if mapping_style == "electrical":
        return mapping.matrixToDcd(data)
    mapFunc = mapping.mapper(module_type=mapping_style, module_flavor=module_type, keep_unconnected=True)
    if mapping_style == "pxd9":
        return mapFunc.raw(data, asicpair)
        # return mapping.pxd9_mapping_fast(data, asicpair, module_type)
    if mapping_style == "hybrid5":
        return mapFunc.raw(data)
        # return mapping.hybrid5MatrixToGeoMatrix(data)
    if mapping_style == "emcm":
        return mapFunc.raw(data)
        # return mapping.emcm_mapping(data)


def mapcelldata(data, module_flavor):
    cellmappeddata = np.zeros(data.shape)
    if module_flavor == "ib":
        cellmappeddata = np.flip(data, axis=0)
        cellmappeddata = np.flip(cellmappeddata, axis=1)
    if module_flavor == "of":
        cellmappeddata = np.flip(data, axis=1)
    if module_flavor == "if":
        cellmappeddata = np.flip(data, axis=0)
    if module_flavor == "ob":
        cellmappeddata = data
    return cellmappeddata


def analysis(logger, data, acmc_status, offset_status, gateon_voltages, vnsubin, fullpath,
             user, module, config_ana_dict, return_dict, tmp, useprogresspv):
    create_context()
    asicpair = 0
    asicpairs = [1, 2, 3, 4]

    # Prepare the return dictionary, the 'info' part is filled if something goes wrong ('success' = False)
    return_dict[module.dhe] = {'success': False, 'info': ''}

    # update the progress PV if given, otherwise use dummy function which simply does nothing
    put_progress = get_put_progress(module.dhe, useprogresspv)

    # Create the path
    if fullpath is not None:
        path = fullpath
        try:
            os.makedirs(fullpath)
        except OSError:
            pass
    put_progress(110)

    # remove hits from the data
    data = raw_data_utils.remove_hits(data)

    # Subtract pedestals from data
    if subtraction is not None:
        data = data.astype(np.int16)
        logger.info("Subtracting pedestals from data from file %s" % subtraction)
        subtract = np.load(subtraction)
        data = data - subtract[:, :, None]

    # Apply common mode correction
    cmc_error = False
    non_cmc_data = None
    if config_ana_dict['use_cmc']:
        logger.info("Doing offline common mode correction.")
        non_cmc_data = np.copy(data)
        try:
            if subtraction is None:
                data, CM_all = cm_corr.common_mode_with_ped_corr(data=data, threshold=config_ana_dict['cmc_threshold'],
                                                                 device=config_ana_dict['mapping_style'])
            else:
                data, CM_all = cm_corr.common_mode(data=data, threshold=config_ana_dict['cmc_threshold'])
        except Exception as e:
            logger.warning(e)
            logger.warning("Error with the common mode correction, original data will be use for further analysis: %s",
                           e, exc_info=True)
            cmc_error = True
    else:
        CM_all = None

    # Apply correct mapping
    mapper=mapping.mapper(module_type=config_ana_dict['mapping_style'], module_flavor=module.module_flavor,
                          asicpair=asicpair)
    mapped_data = mapper(data)

    if config_ana_dict['mapping_style'] == "pxd9":
        cell_data = mapcelldata(data=mapped_data, module_flavor=module.module_flavor)

    # Calculate the number of noisy pixel
    noise_array = np.std(data, axis=2)  # noise over all frames
    number_of_noisy_pixel = np.sum(noise_array > config_ana_dict['maskthreshold'])
    put_progress(130)

    # get unconnected channels mask
    if config_ana_dict['mask_unconnected']:
        if module.device_type == "hybrid5":
            # masking Hybrid5:
            logger.info("Masking unconnected Hybrid5 channels.")
            pixel_mask = mapping.mask_hybrid5(rows=data.shape[0], cols=data.shape[1], frames=data.shape[2])
        if module.device_type == "pxd9":
            logger.info("Masking unconnected PXD9 channels")
            pixel_mask = mapping.mask_pxd9(rows=data.shape[0], cols=data.shape[1], frames=data.shape[2])
        pixel_mask = np.ma.make_mask(np.logical_not(pixel_mask))  # Has to be inverted to be a real mask
    else:
        pixel_mask = np.ma.make_mask(np.zeros((data.shape[0], data.shape[1], data.shape[2]), dtype=bool), shrink=False)

    # Apply noise masking or just masking unconnected channels
    if config_ana_dict['do_noise_masking']:
        # mask noisy pixels defined by maskthreshold in analysis.ini
        logger.info("Masking pixels with a noise above %.1f ADU." % config_ana_dict['maskthreshold'])
        # mask is True where noise exceeds limit give by maskthreshold
        noise_mask = noise_array > config_ana_dict['maskthreshold']
        if config_ana_dict['mask_zero_noise_pixel']:
            zero_noise_mask = noise_array == 0
            noise_mask = np.ma.mask_or(noise_mask, zero_noise_mask)

        # Calculate and apply total mask on data
        total_mask = np.ma.mask_or(pixel_mask[:, :, 0], noise_mask)
    else:
        noise_mask = None
        total_mask = pixel_mask[:, :, 0]

    # Module specific masking
    if config_ana_dict['do_module_masking']:
        try:
            modulemask = np.load(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                              "masks/mask%s.npy" % module.module_name))
            total_mask = np.ma.mask_or(total_mask, modulemask)
        except IOError as e:
            logger.fine("Found no mask for %s" % module.module_name)
            pass
    put_progress(140)

    # mask each frame in data
    data = data.astype(float)
    data = np.ma.masked_array(data, mask=np.broadcast_to(total_mask[:, :, None], data.shape)).filled(np.nan)
    # also do it for the non_cmc data!
    # FIXME: Is that good?
    if config_ana_dict['use_cmc'] and not cmc_error:
        non_cmc_data = non_cmc_data.astype(float)
        non_cmc_data = np.ma.masked_array(non_cmc_data,
                                          mask=np.broadcast_to(total_mask[:, :, None], data.shape)).filled(np.nan)

    # Count the number of non-masked pixels (at this step the noisy pixels may have been masked already, therefore I add
    # them here again since I want the total number of 'connected' pixels. If no masking is used, count all pixels.
    if config_ana_dict['mask_unconnected'] and not config_ana_dict['do_noise_masking']:
        total_number_of_pixels = np.count_nonzero(~np.isnan(data[:, :, 0]))
    elif config_ana_dict['mask_unconnected'] and config_ana_dict['do_noise_masking']:
        total_number_of_pixels = np.count_nonzero(~np.isnan(data[:, :, 0])) + number_of_noisy_pixel
    else:
        total_number_of_pixels = data.shape[0] * data.shape[1]

    # make some analysis for each ASIC individually
    # split data for each ASIC if data of all 4 ASICs was recorded!
    data_list = []
    if asicpair == 0:
        data_list = [data[:, ((asic - 1) * 64):(asic * 64)] for asic in asicpairs]
    median_list = []
    std_list = []
    spread_list = []
    underflow_list = []  # technically not an underflow, but number of entries with value '1' (lowest value) !
    overflow_list = []  # technically not an overflow, but number of entries with value '255' (highest value) !
    # TODO: Make useful calculation here!
    if len(data_list) == 0:
        data_list.append(data)
    for el in data_list:
        dummy = el.flatten()
        dummy2 = np.nanmean(el, axis=2).flatten()
        median_list.append(np.nanmedian(dummy))
        std_list.append(np.nanstd(dummy))
        spread_list.append(np.nanmax(dummy) - np.nanmin(dummy))
        # Handle NaNs...
        finiteDummy=dummy2[np.isfinite(dummy2)]
        underflow_list.append(np.count_nonzero(finiteDummy <= 1))
        overflow_list.append(np.count_nonzero(finiteDummy >= 255))
    # find coordinates (ucell, vcell) of pixels that are noisy (over threshold) + over/underflow pixel
    if config_ana_dict['mapping_style'] == "pxd9" and not tmp:
        if len(cell_data.shape) == 3:
            cell_data_mean = np.nanmean(cell_data, axis=2)
        else:
            cell_data_mean = cell_data
        noisy_pixel_u, noisy_pixel_v = np.where(np.std(cell_data, axis=2) > config_ana_dict['maskthreshold'])
        noisy_pixel_list = zip(noisy_pixel_u, noisy_pixel_v)
        overflow_pixel_u, overflow_pixel_v = np.where(cell_data_mean == 255)
        overflow_pixel_list = zip(overflow_pixel_u, overflow_pixel_v)
        underflow_pixel_u, underflow_pixel_v = np.where(cell_data_mean == 1)
        underflow_pixel_list = zip(underflow_pixel_u, underflow_pixel_v)

    # total number of masked pixels
    if module.device_type == 'pxd9':
        if config_ana_dict['mask_unconnected']:
            total_number_of_masked_pixels = len(total_mask[np.where(total_mask == True)]) - 4608
        else:
            total_number_of_masked_pixels = len(total_mask[np.where(total_mask == True)])
    elif module.device_type == 'hybrid5':
        if config_ana_dict['mask_unconnected']:
            total_number_of_masked_pixels = len(total_mask[np.where(total_mask == True)]) - 1024
        else:
            total_number_of_masked_pixels = len(total_mask[np.where(total_mask == True)])

    # create plots
    put_progress(150)
    # use this array to store created figure objects together with an identifier like ("identifier", figureobject)!
    plot_list = []
    pl.close("all")
    perform_plotting(logger, CM_all, acmc_status, cmc_error, data, module.module_name, module.module_flavor,
                     non_cmc_data, offset_status, plot_list, total_mask, gateon_voltages, vnsubin,
                     total_number_of_masked_pixels, config_ana_dict)

    # create results dictionary and store it in results.npy
    put_progress(180)
    if not tmp:
        results = {}
        results["number_of_noisy_pixels"] = number_of_noisy_pixel
        results["total_number_of_pixels"] = total_number_of_pixels
        results["median"] = median_list
        results["std"] = std_list
        results["spread"] = spread_list
        results["underflow"] = underflow_list
        results["overflow"] = overflow_list
        if config_ana_dict['mapping_style'] == "pxd9":
            results["noisy_pixel"] = noisy_pixel_list
            results["overflow_pixel"] = overflow_pixel_list
            results["underflow_pixel"] = underflow_pixel_list
        if config_ana_dict['do_noise_masking']:
            results["totalmask"] = total_mask
            results["noisemask"] = noise_mask
        np.save(os.path.join(path, "results.npy"), results)

    # create analysis.npy with "ready-to-upload" pedestal data (calculate mean!)
    put_progress(190)
    if not tmp:
        # TODO: Decide which pedestals should be written in the two memory blocks!
        analysis = {}
        if asicpair == 0:
            for asic in asicpairs:
                if config_ana_dict['use_cmc'] and cmc_error == 0:
                    with np.warnings.catch_warnings():
                        np.warnings.simplefilter("ignore",category=RuntimeError)
                        upload_data = np.nanmean(non_cmc_data[:, ((asic - 1) * 64):(asic * 64)], axis=2)
                else:
                    with np.warnings.catch_warnings():
                        np.warnings.simplefilter("ignore",category=RuntimeError)
                        upload_data = np.nanmean(data[:, ((asic - 1) * 64):(asic * 64)], axis=2)
                upload_data[np.where(np.isnan(upload_data))] = 255
                analysis['%s:%s:D%s:pedestal_data_%i' % (user, module.dhe, asic, 512)] = upload_data
                analysis['%s:%s:D%s:pedestal_data_%i' % (user, module.dhe, asic, 768)] = upload_data
        else:
            if config_ana_dict['use_cmc'] and cmc_error == 0:
                upload_data = np.nanmean(non_cmc_data, axis=2)
            else:
                upload_data = np.nanmean(data, axis=2)
            upload_data[np.where(np.isnan(upload_data))] = 255
            analysis['%s:%s:D%s:pedestal_data_%i' % (user, module.dhe, asicpair, 512)] = upload_data
            analysis['%s:%s:D%s:pedestal_data_%i' % (user, module.dhe, asicpair, 768)] = upload_data
        np.save(os.path.join(path, "analysis.npy"), analysis)

    # also create txt file for checking by human
    if not tmp:
        txtfile = open(os.path.join(path, "results.txt"), mode="w")
        for key, value in results.iteritems():
            txtfile.write(key + " = " + str(value) + "\n")
        txtfile.close()

    # saving plots to disk
    if not tmp:
        for name, fig in plot_list:
            filename = os.path.join(path, "%s_plot.pdf" % name)
            logger.info("Saving %s plot to %s" % (name, filename))
            fig.savefig(filename)

    # fill the return dictionary, show the plots (if wished) and return
    return_dict["%spath" % module.dhe] = path
    return_dict[module.dhe] = {'success': True, 'info': ''}
    if config_ana_dict['show_plots']:
        logger.info("Showing plots on screen.")
        pl.show()
    put_progress(200)
    destroy_context()


def perform_plotting(logger, CM_all, acmc_status, cmc_error, data, module, module_type, non_cmc_data, offset_status,
                     plot_list, total_mask, gateon_voltages, vnsubin, total_number_of_masked_pixels, c_dict):
    numberofmaskedchannel = total_number_of_masked_pixels
    asicpair = 0
    if c_dict['plot_frame']:
        logger.info("Creating frame plot.")
        plot_list.append(("frame", plots.plot_frame(data=data, asicpair=asicpair, device=c_dict['mapping_style'],
                                                    module=module)))
    if c_dict['plot_ped_both_mapping']:
        logger.info("Creating pedestal plot with both mappings.")
        plot_list.append(("pedestal_both_mappings",
                          plots.plot_ped_both_mapping(data=data, device=c_dict['mapping_style'], module=module,
                                                      module_type=module_type,
                                                      asicpair=asicpair)))
    if c_dict['plot_noise']:
        logger.info("Creating noise plot.")
        plot_list.append(
            ("noise", plots.plot_noise(data=data, device=c_dict['mapping_style'], module=module,
                                       module_type=module_type, asicpair=asicpair, acmc_status=acmc_status,
                                       offset_status=offset_status, gateon_voltages=gateon_voltages, vnsubin=vnsubin,
                                       noise_range='full')))
    if c_dict['plot_pedestals']:
        logger.info("Creating pedestal plot.")
        plot_list.append(
            ("pedestals", plots.plot_pedestals(data=data, device=c_dict['mapping_style'], module=module,
                                               module_type=module_type,
                                               asicpair=asicpair, consecutive=False, acmc_status=acmc_status,
                                               offset_status=offset_status,
                                               gateon_voltages=gateon_voltages, vnsubin=vnsubin,
                                               numberofmaskedchannel=numberofmaskedchannel)))
    if c_dict['plot_pedestals_mult']:
        logger.info("Creating pedestal plot with single frames (no mean calculated).")
        plot_list.append(
            ("pedestals_mult",
             plots.plot_pedestals(data=data, device=c_dict['mapping_style'], module=module, module_type=module_type,
                                  asicpair=asicpair, consecutive=True, acmc_status=acmc_status,
                                  offset_status=offset_status,
                                  gateon_voltages=gateon_voltages, vnsubin=vnsubin,
                                  numberofmaskedchannel=numberofmaskedchannel)))
    if c_dict['plot_everything']:
        logger.info("Creating 'everything' plot.")
        plot_list.append(
            (
                "everything",
                plots.plot_everything(data=data, device=c_dict['mapping_style'], module=module, module_type=module_type,
                                      asicpair=asicpair, consecutive=False)))
    if c_dict['use_cmc'] and not cmc_error:
        try:
            logger.info("Creating Common Mode Comparison plot.")
            cmc_1, cmc_2, cmc_3 = plots.plot_common_mode_data(data=non_cmc_data, device=c_dict['mapping_style'],
                                                              module=module, asicpair=asicpair, module_type=module_type,
                                                              data_corrected=data, all_CMs=CM_all,
                                                              vmax_noise=c_dict['maskthreshold'] * 1.5)
            pl.close(cmc_3)  # Looks like this plot is just empty, so remove it!
            plot_list.append(("cmc_comparison", cmc_1))
            plot_list.append(("cmc_trend", cmc_2))
        except Exception as e:
            logger.warning(e)
            logger.warning("Error with the common mode plotting, no plot will be created: %s", e, exc_info=True)
    if c_dict['do_noise_masking']:
        plot_list.append(("mask",
                          plots.plot_mask(mask=total_mask, device=c_dict['mapping_style'], module=module,
                                          module_type=module_type, asicpair=asicpair)))


def main(logger, local_ini, path=None, tmp=False, noelog=False, dhc_objects=None, elogcredentials=None,
         useprogresspv=False, quietmode=False):
    if tmp or quietmode:
        logger.setLevel(log_utils.SEVERE)
    if tmp:
        noelog = True
        local_ini = "/tmp/analysis.ini.RunPedestalMeasurement"

    logger.info("Start of Pedestal analysis")

    # load required values from ini file
    config_ana = configparser.ConfigParser(delimiters='=')
    config_ana.optionxform = str
    config_ana.read(local_ini)

    # get path
    if path is None:
        path = __getpath(config_ana, tmp)

    # load measure.ini from data path!
    config_measure = configparser.ConfigParser(delimiters='=')
    config_measure.optionxform = str
    if tmp:
        config_measure_filename = os.path.join(path, "measure.ini.RunPedestalMeasurement")
    else:
        config_measure_filename = os.path.join(path, "measure.ini")
    config_measure.read(config_measure_filename)

    # load values from measure.ini
    user = config_measure.get("general", "user")
    asicpair = 0
    framenr = config_measure.getint("general", "framenr")
    useDHC = config_measure.getboolean("general", "useDHC")

    # Load information about the system from the measure.ini including ACMC and 2-Bit DAC Offset status
    dhc_objects, acmc_status_dict, offset_status_dict = get_system_info(config_measure_filename, dhc_objects)

    # load values from analysis.ini and store them in a dictionary!
    config_ana_dict = __get_config_ana_dict(config_ana)

    # deal with elog credentials
    if not noelog and not tmp:
        elog_auth = config_utils.get_elog_authentification_method()
        if elogcredentials is not None:
            credentials = elogcredentials
        elif elog_auth == "credentials":
            credentials = elog.credentials(noinput=False)
        elif elog_auth == "sshtunnel":
            credentials = elog.credentials(noinput=True)
        else:
            logger.exception('No valid elog authentification method specified in master.setup.ini! '
                             'Aborting measurement now!')
            return -1

    # load information from PV dump
    no_pvdump = False
    try:
        pvdump = np.load(os.path.join(path, "PVdump-prescan.npy")).item()
    except IOError as e:
        no_pvdump = True

    # Get voltage and vnsubin from the PV dump
    gateon_voltages_dict = {}
    vnsubin_dict = {}
    for dhc in dhc_objects:
        for module in dhc.modules:
            if no_pvdump:
                gateon_voltages_dict[module.dhe] = None
                vnsubin_dict[module.dhe] = None
            else:
                gateon_voltages_dict[module.dhe] = [pvdump['%s:%s:gate-on%i:VOLT:req' %
                                                           (user, "P%s" % module.dhe[1:], i + 1)][0] for i in range(3)]
                vnsubin_dict[module.dhe] = [pvdump['%s:%s:R%i:dacvnsubin:VALUE:set' %
                                                   (user, module.dhe, i + 1)][0] for i in range(4)]

    # optional parameters
    global subtraction
    subtraction = config_ana.get("general", "subtraction", fallback=None)

    # if mapping is set to 'device', use the mapping that is correct for this module this is now always 'pxd9'
    # (not 'electrical' or 'matrix')
    if config_ana_dict['mapping_style'] == "device":
        config_ana_dict['mapping_style'] = 'pxd9'
    logger.info("Using %s mapping." % config_ana_dict['mapping_style'])

    # ---------------Do calculation/analysis of pedestal data here------------------------------------------------------
    manager = Manager()
    return_dict = manager.dict()
    process_list = []
    mydict = {}  # dictionary, that will be returned at the end (after the analysis is complete)
    for dhc in dhc_objects:
        data_dict = {}
        for module in dhc.modules:
            try:
                if useDHC:
                    filename = os.path.join(path, "%srawframe_data.dat" % dhc.name)
                else:
                    filename = os.path.join(path, "rawframe_data.dat")
                data_dict[module.dhe] = \
                    file_utils.read_raw_file(filename, module.dhe,
                                             asicpair=asicpair,
                                             frames=framenr,
                                             use_header=True,
                                             skip_broken_frames=config_ana_dict['skip_broken_frames'])[0]
            except IOError as e:
                data_dict[module.dhe] = None
                logger.warning("No data for DHE %s (DHC %s)" % (module.dhe, dhc.name))
                logger.warning("Error: %s" % repr(e))
                mydict[module.dhe] = {'success': False}
            if data_dict[module.dhe] is not None:
                analysispath = os.path.join(path, module.dhe)
                arguments = [logger, data_dict[module.dhe], acmc_status_dict[module.dhe], offset_status_dict[module.dhe],
                             gateon_voltages_dict[module.dhe], vnsubin_dict[module.dhe], analysispath,
                             user, module, config_ana_dict, return_dict, tmp, useprogresspv]
                process_list.append(CAProcess(target=analysis, args=arguments))
    for el in process_list:
        el.start()
    for el in process_list:
        el.join()

    # Submit all the elog entries
    if not tmp and not noelog:
        __submit_elog(credentials, dhc_objects, local_ini, logger, return_dict)

    # cleanup the return dictionary and return it! ;)
    analysis_files = []
    for dhc in dhc_objects:
        for module in dhc.modules:
            if "%spath" % module.dhe in return_dict:
                analysis_files.append(os.path.join(return_dict["%spath" % module.dhe], 'analysis.npy'))
            if module.dhe in return_dict:
                mydict[module.dhe] = return_dict[module.dhe]
    mydict['analysis.npy'] = analysis_files
    return mydict


def __get_config_ana_dict(config_ana):
    """
    Helper function which returns a dictionary containing parameters from the analysis.ini file

    :param config_ana: config object of the analysis.ini
    :return: config dictionary
    """
    config_ana_dict = {}
    config_ana_dict['mapping_style'] = config_ana.get("plots", "mapping")  # pxd9, hybrid5, electrical, matrix, device
    config_ana_dict['show_plots'] = config_ana.getboolean("plots", "show_plots")
    config_ana_dict['plot_frame'] = config_ana.getboolean("plots", "plot_frame")
    config_ana_dict['plot_ped_both_mapping'] = config_ana.getboolean("plots", "plot_ped_both_mapping")
    config_ana_dict['plot_noise'] = config_ana.getboolean("plots", "plot_noise")
    config_ana_dict['plot_pedestals'] = config_ana.getboolean("plots", "plot_pedestals")
    config_ana_dict['plot_pedestals_mult'] = config_ana.getboolean("plots", "plot_pedestals_mult")
    config_ana_dict['plot_everything'] = config_ana.getboolean("plots", "plot_everything")
    config_ana_dict['mask_unconnected'] = config_ana.getboolean("masking", "mask_unconnected")
    config_ana_dict['do_noise_masking'] = config_ana.getboolean("masking", "do_noise_masking")
    config_ana_dict['mask_zero_noise_pixel'] = config_ana.getboolean("masking", "mask_zero_noise_pixel", fallback=False)
    config_ana_dict['do_module_masking'] = config_ana.getboolean("masking", "do_module_masking", fallback=False)
    config_ana_dict['maskthreshold'] = config_ana.getfloat("masking", "maskthreshold")
    config_ana_dict['use_cmc'] = config_ana.getboolean("common_mode_correction", "use_cmc")
    config_ana_dict['cmc_threshold'] = config_ana.getint("common_mode_correction", "cmc_threshold")
    config_ana_dict['skip_broken_frames'] = config_ana.getboolean("general", "skip_broken_frames", fallback=False)
    return config_ana_dict


if __name__ == "__main__":
    # get inifile from command line argument (if not supplied: default=analysis.ini)
    parser = ArgumentParser(description='Analyse Pedestals')
    parser.add_argument('-c', '--local_ini', dest='local_ini',
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis.ini"))
    parser.add_argument('-tmp', '--temporary', action='store_true', dest='temporary', default=False,
                        help="If this flag is set, no elog entry will be created, the logging is turned off, and the "
                             "data is stored in /tmp/. In addition no PVDump is created. This is useful to speed up "
                             "the measurement.")
    parser.add_argument('-n', '--no-elog', action='store_true', dest='noelog', default=False,
                        help='Option to disable the elog logging feature. In contrast to the \'-tmp\' flag, plots are '
                             'still saved at the location specified in the *.ini file and not in /tmp/.')
    parser.add_argument('--quiet', action='store_true', dest='quietmode', default=False,
                        help='Option to set the loglevel to severe. If enabled only errors will be shown.')
    args = parser.parse_args()
    local_ini = args.local_ini.decode('utf-8')

    # initialize logger and start the elog entry
    logger = log_utils.get_pxd_main_logger(application_name="pedestal/analysis", no_remote=True)

    main(logger, local_ini, tmp=args.temporary, noelog=args.noelog, quietmode=args.quietmode)
