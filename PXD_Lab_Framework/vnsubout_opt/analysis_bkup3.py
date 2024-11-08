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

import matplotlib
matplotlib.use('agg')
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
import file_utils
from matplotlib import pyplot as pl
import numpy as np
import numpy.ma as ma


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



def analysis(logger, module, path, analysispath, current_source_ranges, return_dict, ped_mask_path=None, limit_low=20, limit_high=250):
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
    #expPedestals_dict = multiprocessing.Manager().dict()
    #quality_dict = multiprocessing.Manager().dict()
    #calibrationData_dict = multiprocessing.Manager().dict()

    logger.fine("Performing analysis for module - %s ,DHE - %s" % (module, module.dhe))
    #successful_asicpairs = multiprocessing.Manager().list()

    current_source_value = np.zeros(len(current_source_ranges))
    #rangeData = np.zeros((4 * nGates, 64, len(current_source_ranges), 4))
    rangeData = np.zeros((4 * nGates, 250, len(current_source_ranges), 4))
    bad_pix_count = np.zeros((len(current_source_ranges), 4))
    COG_ped = np.zeros((len(current_source_ranges), 4))

    #Broken drains mask
    #path_mask = os.path.join(ped_mask_path, module.dhe, "pedestal_mask")
    #filename_mask = os.path.join(path_mask, "broken_drains.npy")
    #if os.path.exists(filename_mask):
        #print "mask exists"
        #asicpair=2
        #mask_broken_columns = np.load(filename_mask)
        #mask_broken_columns = mask_broken_columns[:, (asicpair-1)*64: asicpair*64]
        #print mask_broken_columns.shape

    #print "module.dhe", module.dhe
    #if module.dhe == 'H1021':
        #mapFunc = mapping.mapper("pxd9", "if", fill_value=255)
        #print "module is if"
    #elif module.dhe == 'H1022':
        #mapFunc = mapping.mapper("pxd9", "ib", fill_value=255)
        #print "module is ib"

    #Module flavour
    flavour_list = {
            "if": ['H1011','H1021','H1031','H1041','H1051','H1061','H1071','H1081'],
            "ib": ['H1012','H1022','H1032','H1042','H1052','H1062','H1072','H1082'],
            "of": ['H2011','H2021','H2031','H2041','H2051','H2061','H2071','H2081','H2091','H2101','H2111','2121'],
            "ob": ['H2012','H2022','H2032','H2042','H2052','H2062','H2072','H2082','H2092','H2102','H2112','2122']
    }
    if any(module.dhe in s for s in flavour_list["if"]):
        module_flavor='if'
    elif any(module.dhe in s for s in flavour_list["ib"]):
        module_flavor='ib'
    elif any(module.dhe in s for s in flavour_list["of"]):
         module_flavor='of'
    elif any(module.dhe in s for s in flavour_list["ob"]):
         module_flavor='ob'
    #print module.dhe," has flavour", module_flavor
    
    
    #Read data and apply masks
    for index, value in enumerate(current_source_ranges):
        current_source_value[index] = value
        fullname = os.path.join(path, "%srawframe_data_%d.dat" % (module.dhc if module.dhc is not None else "", value))
        #data = file_utils.read_raw_file(filename=fullname, dhePrefix="PXD:%s" % module.dhe,asicpair=0, use_header=False)[0]
        for asicpair in asicpairs:
            data = file_utils.read_raw_file(filename=fullname, dhePrefix="PXD:%s" % module.dhe,asicpair=asicpair, use_header=False)[0]
            #print "asicpair = ",asicpair
            mapFunc = mapping.mapper(module_type="pxd9", module_flavor=module_flavor, fill_value=255, asicpair=asicpair)
            #mapFunc = mapping.mapper(module_type="pxd9", module_flavor=module_flavor, asicpair=asicpair)
            map_ped = mapFunc.raw(data)
            #print map_ped.shape
            #data = file_utils.read_raw_file(filename=fullname, dhePrefix="PXD:%s" % module.dhe, asicpair=asicpair, use_header=False)[0]
            #print "data.shape = ", data.shape
            ped_mean = np.mean(map_ped, axis=2)
            #print ped_mean.shape
            #if os.path.exists(filename_mask):
                #mask_broken_columns = np.load(filename_mask)
                #mask_broken_columns = mask_broken_columns[:, (asicpair-1)*64: asicpair*64]
                #ped_mean=ma.masked_arrayi(ped_mean_raw, mask_broken_columns)
            #else:
                #ped_mean=ped_mean_raw
            

            pedestal_COG=np.mean(ped_mean)
            num_bad_pix=ped_mean[(ped_mean<limit_low)+(ped_mean>limit_high)].size

            #print ped_mean[:10,:5]
            
            asic_index=asicpair-1
            bad_pix_count[index, asic_index] = num_bad_pix
            COG_ped[index, asic_index] = pedestal_COG
            rangeData[:, :, index, asic_index] = ped_mean
            


    
    #Quality plots
    module_path = os.path.join(path, module.dhe)

    fullfilename_q= os.path.join(module_path, "%s_QualityPlots.png" % module.dhe)
    fig, ax1 = pl.subplots(2, 2)
    for asicpair in asicpairs:
        asic_index=asicpair-1
        i=asic_index//2
        j=asic_index%2
        color = 'tab:red'
        ax1[i,j].set_title('ASIC : D%i' %asicpair )
        ax1[i,j].set_xlabel('VnSubOut')
        ax1[i,j].set_ylabel('Bad pixel count', color=color)
        ax1[i,j].plot(current_source_value, bad_pix_count[:,asic_index], color=color)
        ax1[i,j].tick_params(axis='y', labelcolor=color)
        ax2 = ax1[i,j].twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:blue'
        ax2.set_ylabel('Pedestal center of gravity', color=color)  # we already handled the x-label with ax1
        ax2.plot(current_source_value, COG_ped[:,asic_index], color=color)
        ax2.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    pl.show()
    logger.fine("Saving quality plots in %s" % fullfilename_q)
    fig.savefig(fullfilename_q)
    
    #Pedestal plots
    #a) Pedestal distributions
    for index, value in enumerate(current_source_ranges):
        fig2, ax = pl.subplots(2, 2)
        fullfilename_ph= os.path.join(module_path, "%s_pedestal_hists_%i.png" % (module.dhe,value) )
        for asicpair in asicpairs:
            asic_index=asicpair-1
            i=asic_index//2
            j=asic_index%2
            ax[i,j].set_title('ASIC : D%i' %asicpair )
            ax[i,j].set_xlabel('Pedestal dist. @ VnSubOut = %i' %value)
            ax[i,j].set_yscale('log')
            ped_hist=rangeData[:, :, index, asic_index].flatten()
            ax[i,j].hist(ped_hist, range=[0, 255], bins=256)
            ax[i,j].axvline(20, color='r', linestyle='dashed', linewidth=1)
        fig2.tight_layout()
        pl.show()
        logger.fine("Saving pedestal distribution plots in %s" % fullfilename_ph)
        fig2.savefig(fullfilename_ph)
    
    #b) Pedestal maps
    for index, value in enumerate(current_source_ranges):
        fig3, axx = pl.subplots(2, 2)
        fullfilename_pm= os.path.join(module_path, "%s_pedestal_maps_%i.png" % (module.dhe,value) )
        for asicpair in asicpairs:
            asic_index=asicpair-1
            i=asic_index//2
            j=asic_index%2
            axx[i,j].set_title('ASIC : D%i' %asicpair )
            #axx[i,j].set_xlabel('Pedestal map @ VnSubOut = %i' %value)
            pcm = axx[i,j].pcolormesh(rangeData[:, :, index, asic_index], cmap='viridis')
            fig3.colorbar(pcm, ax=axx[i,j])
        fig3.tight_layout()
        pl.show()
        logger.fine("Saving pedestal map plots in %s" % fullfilename_pm)
        fig3.savefig(fullfilename_pm)
    



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

    '''
    analysis_files = []
    for dhc in dhc_objects:
        for module in dhc.modules:
            if "%spath" % module.dhe in return_dict:
                analysis_files.append(os.path.join(return_dict["%spath" % module.dhe], 'analysis.npy'))
            if module.dhe in return_dict:
                mydict[module.dhe] = return_dict[module.dhe]
    mydict['analysis.npy'] = analysis_files
    return mydict
    '''

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
