#!/usr/bin/env python

"""
analysis.py
===========

This script caculates the optimal VnSubOut value using calibration data.

>>> ./analysis.py -c my_inifile.ini


**Config**::

    [general]
    path = latest                       #[OPT] path in which data will be analyzed
    use_multiprocessing = True|False    #[REQ] if the analysis for multiple asicpairs in performed in parallel
"""

import matplotlib as mpl
mpl.use('agg')
import sys
import os
import argparse
import config_utils
import epics_utils
import mapping
import configparser
import numpy as np
import calculation as calc
from matplotlib import pyplot as pl
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import plots
import multiprocessing
from matplotlib.backends.backend_pdf import PdfPages
import log_utils
import elog
import shutil
from epics import CAProcess
from multiprocessing import Manager


def __submit_elog(credentials, dhc_objects, local_ini, logger, noelog, return_dict):
    """

    :param credentials:
    :param dhc_objects:
    :param local_ini:
    :param logger:
    :param noelog:
    :param return_dict:
    :return:
    """
    if not noelog:
        logger.info("Submitting the elog entries now")
        try:
            for dhc in dhc_objects:
                for module in dhc.modules:
                    if "%spath" % module.dhe in return_dict:
                        myelog = elog.elog(local_ini, type="Offsets Calibration Analysis", dhe=module.dhe,
                                           dhc_objects=dhc_objects,
                                           username=credentials.getusername(),
                                           password=credentials.getpassword())
                        myelog.submitEntry(path=return_dict["%spath" % module.dhe])
        except Exception as e:
            logger.warning("elog.submitEntry:" + repr(e))
            raise e



def analysis(logger, module, path, analysispath, current_source_ranges, return_dict, ped_mask_path=None):
    """
    Analysis function which is called for each module. Calculates the optimal offsets and stores the analyisi results
    together with the plots.

    :param logger: logger object
    :type logger: log_utils._java_logger_adapter
    :param module: module object
    :type module: devices.Device
    :param path: path to the data
    :type path: string
    :param analysispath: path where the analysis results for the given module will be saved
    :type analysispath: string
    :param current_source_ranges: list of recorded current source values
    :type current_source_ranges: list of int
    :param return_dict: dictionary that will be filled with information relevant for this analysis like success/failure
    :type return_dict: multiprocessing.Manager.dict

    :return:
    """
    # Create the analysispath
    if not os.path.isdir(analysispath):
        os.makedirs(analysispath)

    #print "Performing analysis for module-",module,", DHE-",module.dhe

    # Prepare the return dictionary, the 'info' part is filled if something goes wrong ('success' = False)
    return_dict[module.dhe] = {'success': False, 'info': ''}

    # TODO: we have to remove this, it is ALWAYS 'PXD'
    user = 'PXD'

    if module.device_type == "hybrid5":
        asicpairs = [1]
        nGates = 16
        nDrains = 128
        user_badPixelMap = np.full((4 * nGates, 64), False, dtype=np.bool)
        user_badPixelMap[:, :16] = True
        user_badPixelMap[:, 48:] = True
    elif module.device_type == "pxd9":
        asicpairs = [1, 2, 3, 4]
        nGates = 192
        nDrains = 1024
        # we calculate for each asicpair individually
        # hence we have 64 rows
        user_badPixelMap = np.full((4 * nGates, 64), False, dtype=np.bool)
        user_badPixelMap = mapping.matrixToDcd(user_badPixelMap)
        user_badPixelMap[:, 10: 16] = True
        user_badPixelMap = mapping.dcdToMatrix(user_badPixelMap)
    else:
        logger.severe("ERROR: unknown device:", module.device_type)
        sys.exit(1)

    # lists
    #ipdac_dict = multiprocessing.Manager().dict()
    #offsetMatrixFormat_dict = multiprocessing.Manager().dict()
    expPedestals_dict = multiprocessing.Manager().dict()
    quality_dict = multiprocessing.Manager().dict()
    calibrationData_dict = multiprocessing.Manager().dict()

    logger.fine("Performing analysis for module - %s ,DHE - %s" % (module, module.dhe))
    successful_asicpairs = multiprocessing.Manager().list()
    asic_proceses = []
    for asicpair in asicpairs:
        rangeData= analysis_asic(analysispath, asicpair, calibrationData_dict, current_source_ranges,
                                 logger, module, nDrains, nGates, path, quality_dict, successful_asicpairs, 
                                 user_badPixelMap, ped_mask_path)
        #rangeData=asic_proceses.append(CAProcess(target=analysis_asic,
                                       #args=(analysispath, asicpair, calibrationData_dict, current_source_ranges,
                                             #logger, module, nDrains, nGates, path, quality_dict, successful_asicpairs,
                                             #user_badPixelMap, ped_mask_path)))
    [p.start() for p in asic_proceses]
    [p.join() for p in asic_proceses]

    # save to disk; create dictionary with entries
    """
    PVdump = np.load(os.path.join(path, "PVdump-prescan.npy")).item()
    analysis = {}
    for asicpair in successful_asicpairs:

        # we get the vnsubin and ipdaddin and put it into analysis .npy (although they are not related to analysis)
        # such that we can perform the upload.py and save the configuration to DB

        pv_name_vnsubin = epics_utils.pvname_dcd(epics_utils.pvname(user, module.dhe), asicpair, "dacvnsubin:VALUE:set")
        analysis[pv_name_vnsubin] = PVdump[pv_name_vnsubin][0]

    np.save(os.path.join(analysispath, "analysis.npy"), analysis)
    """

    # fill the return dictionary, show the plots (if wished) and return
    return_dict["%spath" % module.dhe] = os.path.join(path, module.dhe)
    return_dict[module.dhe] = {'success': True, 'info': ''}


def analysis_asic(analysispath, asicpair, calibrationData_dict, current_source_ranges,
                  logger, module, nDrains, nGates, path, quality_dict, successful_asicpairs,
                  user_badPixelMap, ped_mask_path=None):

    logger.fine("Performing analysis for DHE - %s, asicpair - %s" % (module.dhe,asicpair))
    #print "performing analysis_asic for asic-",asicpair,", and module-",module,". DHE is ",module.dhe

    
    # Perform calculations
    try:

        calc.getQuality_params(logger, path, module, nGates, nDrains, current_source_ranges, asicpair,
                          bad_pixel_map=None, ped_mask_path=None)

    except Exception as e:
        logger.warning('Could not perform calculations ASIC %i on module %s' % (asicpair, module.dhe))
        print(e)
    else:
        successful_asicpairs.append(asicpair)  # We want to know for which asicpair it has worked
        #plot_offsets(analysispath, expPedestals, quality, offsetMatrixFormat, calibrationData, module.dhe,
                    # asicpair, ipdac_ranges)
        #quality_dict[asicpair] = quality
        #calibrationData_dict[asicpair] = calibrationData



def main(logger, local_ini, path=None, noelog=False, dhc_objects=None, elogcredentials=None, useprogresspv=False,
         quietmode=False):
    logger.info("Start of VnSubOut Calibration analysis")

    # deal with elog credentials
    if not noelog:
        logger.finest('Creating elog object.')
        elog_auth = config_utils.get_elog_authentification_method()
        if elogcredentials is not None:
            credentials = elogcredentials
        elif elog_auth == "credentials":
            credentials = elog.credentials(noinput=False)
        elif elog_auth == "sshtunnel":
            credentials = elog.credentials(noinput=True)
        else:
            logger.exception('No valid elog authentification method specified in master.setup.ini! '
                             'Aborting analysis now!')
            return -1

    # read analysis.ini
    config_ana = configparser.ConfigParser(delimiters="=")
    config_ana.optionxform = str
    config_ana.read(local_ini)


    # get path
    if path is None:
        if config_ana.get("general", "path") in [None, "", "newest", "latest"]:
            # determine directory of script and read .latestpath file
            latestpathfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".latestpath")

            with open(latestpathfile, "r") as f:
                path = f.read()
        # use fixed path if given
        else:
            path = config_ana.get("general", "path")
        path = os.path.expanduser(path)
    logger.fine("analyze data from %s" % path)

    # get the base oath for the pedestal mask
    ped_mask_path = config_ana.get("general", "ped_mask_path")

    # load measure.ini from data path!
    config_measure = configparser.ConfigParser(delimiters='=')
    config_measure.optionxform = str
    config_measure_filename = os.path.join(path, "measure.ini")
    print config_measure_filename
    config_measure.read(config_measure_filename)

    # get parameters from measure.ini
    # not the path!
    user = config_measure.get("general", "user")
    useDHC = config_measure.get("general", "useDHC")
    current_source_ranges = config_utils.get_scan_values(config_measure["current_source_ranges"])

    #print current_source_ranges

    # load info about the system from the measure.ini
    if dhc_objects is None:
        dhc_objects = config_utils.get_setup_from_scan_config(config_measure_filename)

    # FIXME: obsolete now
    # get parameters from analysis.ini
    use_multiprocessing = config_ana.getboolean("general", "use_multiprocessing")

    # copy ini file for analysis to folder
    try:
        shutil.copy(local_ini, os.path.join(path, os.path.basename(local_ini)))
    except Exception as e:
        logger.exception(
            "cannot copy ini file for analysis to data measurement folder! Maybe source and analysis is the same.")
        logger.warning(repr(e))

    # ---------------Do calculation/analysis of data here------------------------------------------------------
    manager = Manager()
    return_dict = manager.dict()
    process_list = []
    mydict = {}  # dictionary, that will be returned at the end (after the analysis is complete)
    for dhc in dhc_objects:
        for module in dhc.modules:
            analysispath = os.path.join(path, module.dhe)
            #print "analysispath = ", analysispath
            arguments = {'logger': logger, 'module': module, 'path': path, 'analysispath': analysispath,
                         'current_source_ranges': current_source_ranges,
                         'return_dict': return_dict, 'ped_mask_path' : ped_mask_path}
            process_list.append(CAProcess(target=analysis, kwargs=arguments))

    [p.start() for p in process_list]
    [p.join() for p in process_list]
    # Submit all the elog entries
    if not noelog:
        __submit_elog(credentials, dhc_objects, local_ini, logger, noelog, return_dict)

 #   print "return_dict = ", return_dict

    analysis_files = []
    for dhc in dhc_objects:
        for module in dhc.modules:
            if "%spath" % module.dhe in return_dict:
                analysis_files.append(os.path.join(return_dict["%spath" % module.dhe], 'analysis.npy'))
            if module.dhe in return_dict:
                mydict[module.dhe] = return_dict[module.dhe]
    mydict['analysis.npy'] = analysis_files
    return mydict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--config', dest='config', default='analysis.ini')
    parser.add_argument('-n', '--no-elog', action='store_true', dest='noelog', default=True,
                        help='Option to disable the elog logging feature.')
    args = parser.parse_args()
    local_ini = args.config.decode('utf-8')

    # initialize logger and start the elog entry
    globallogger = log_utils.get_pxd_main_logger(application_name="VnSubOut Calibration Analysis",
                                                 loglevel=log_utils.FINE, no_remote=True)
    main(globallogger, local_ini, noelog=args.noelog)
