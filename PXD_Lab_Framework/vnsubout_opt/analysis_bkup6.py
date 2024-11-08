#!/usr/bin/env python

"""
analysis.py
===========

This script caculates the optimal current-source-values per ASIC using calibration data.

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



def analysis(logger, module, path, analysispath, current_source_ranges, return_dict, ped_mask_path=None, limit_low=20, limit_high=250, w_opt=1, plot_all = False ):
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

    logger.fine("Performing analysis for module - %s ,DHE - %s" % (module, module.dhe))
    w_opt=float(w_opt)

    # Create the analysispath
    if not os.path.isdir(analysispath):
        os.makedirs(analysispath)


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


    #Initialize numpy arrays
    #Current source list
    current_source_value = np.zeros(len(current_source_ranges))
    #Array to hold ASIC data
    ASICdata = np.zeros((4 * nGates, 64, len(current_source_ranges), 4))
    #Number of pixels outside the 'good region'
    bad_pix_count = np.zeros((len(current_source_ranges), 4))
    #'Center of gravity of the distribution'
    COG_ped = np.zeros((len(current_source_ranges), 4))
    #Effective Figure-of-Merit
    FOM_eff = np.zeros((len(current_source_ranges), 4))
    #Optimal current source 'indices'
    best_index = np.zeros(4)

    #Read and fill ASIC arrays
    for index, value in enumerate(current_source_ranges):
        current_source_value[index] = value
        fullname = os.path.join(path, "%srawframe_data_%d.dat" % (module.dhc if module.dhc is not None else "", value))
        for asicpair in asicpairs:
            data = file_utils.read_raw_file(filename=fullname, dhePrefix="PXD:%s" % module.dhe,asicpair=asicpair, use_header=False)[0]
            ped_mean=np.mean(data, axis=2)
            pedestal_COG=np.mean(ped_mean)
            num_bad_pix=ped_mean[ped_mean<limit_low].size+ped_mean[ped_mean>limit_high].size
            eff_fom=num_bad_pix+(w_opt*pedestal_COG) 
            asic_index=asicpair-1
            bad_pix_count[index, asic_index] = num_bad_pix
            COG_ped[index, asic_index] = pedestal_COG
            ASICdata[:, :, index, asic_index] = ped_mean
            FOM_eff[index, asic_index] = eff_fom

    #Make path for module specific plots
    module_path = os.path.join(path, module.dhe)
    #print "w_opt = ",w_opt

    #Best values dictionary
    best_dict = {}

    #Optimal current source values
    best_index = FOM_eff.argmin(axis=0)

    #Plot best pedestals
    fullfilename_best = os.path.join(module_path, "%s_BestPedestals.png" % module.dhe)
    fig_bst, ax_bst = pl.subplots(2, 2, figsize=(10,10))
    for asicpair in asicpairs:
        asic_index=asicpair-1
        i=asic_index//2
        j=asic_index%2
        ax_bst[i,j].set_title('ASIC : D%i' %asicpair )
        ax_bst[i,j].set_xlabel('Pedestal dist. @ VnSubOut = %i' %current_source_value[best_index[asic_index]])
        ax_bst[i,j].set_yscale('log')
        ped_hist=ASICdata[:, :, best_index[asic_index], asic_index].flatten()
        ax_bst[i,j].hist(ped_hist, range=[0, 255], bins=256)
        ax_bst[i,j].axvline(limit_low, color='r', linestyle='dashed', linewidth=1)
        ax_bst[i,j].axvline(limit_high, color='r', linestyle='dashed', linewidth=1)
        #Put into dictionary
        best_dict[asicpair]=current_source_value[best_index[asic_index]]
    fig_bst.tight_layout()
    pl.show()
    logger.fine("Saving best-pedestal plots in %s" % fullfilename_best)
    fig_bst.savefig(fullfilename_best)

    #Put into process dictionary
    return_dict[module.dhe]= best_dict

    #Quality plots
    fullfilename_q= os.path.join(module_path, "%s_QualityPlots.png" % module.dhe)
    fig, ax1 = pl.subplots(2, 2, figsize=(10,10))
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
        ax2 = ax1[i,j].twinx()
        color = 'tab:green'
        ax2.set_ylabel('Pedestal center of gravity', color=color)
        ax2.plot(current_source_value, COG_ped[:,asic_index], color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax3 = ax1[i,j].twinx()
        color = 'tab:blue'
        ax3.set_ylabel('Effective Figure-of-Merit', color=color)
        ax3.plot(current_source_value, FOM_eff[:,asic_index], color=color)
        ax3.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()
    pl.show()
    logger.fine("Saving quality plots in %s" % fullfilename_q)
    fig.savefig(fullfilename_q)

    if plot_all == True :
        for index, value in enumerate(current_source_ranges):
            fig2, ax = pl.subplots(2, 2, figsize=(10,10))
            fullfilename_ph= os.path.join(module_path, "%s_pedestal_hists_%i.png" % (module.dhe,value) )
            for asicpair in asicpairs:
                asic_index=asicpair-1
                i=asic_index//2
                j=asic_index%2
                ax[i,j].set_title('ASIC : D%i' %asicpair )
                ax[i,j].set_xlabel('Pedestal dist. @ VnSubOut = %i' %value)
                ax[i,j].set_yscale('log')
                ped_hist=ASICdata[:, :, index, asic_index].flatten()
                ax[i,j].hist(ped_hist, range=[0, 255], bins=256)
                ax[i,j].axvline(limit_low, color='r', linestyle='dashed', linewidth=1)
                ax[i,j].axvline(limit_high, color='r', linestyle='dashed', linewidth=1)
            fig2.tight_layout()
            pl.show()
            logger.fine("Saving pedestal distribution plots in %s" % fullfilename_ph)
            fig2.savefig(fullfilename_ph)



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

    # get the base path for the pedestal mask
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


    # load info about the system from the measure.ini
    if dhc_objects is None:
        dhc_objects = config_utils.get_setup_from_scan_config(config_measure_filename)

    # FIXME: obsolete now
    # get parameters from analysis.ini
    use_multiprocessing = config_ana.getboolean("general", "use_multiprocessing")
    w_opt = config_ana.get("general", "w_opt", fallback=1)
    plot_all = config_ana.getboolean("general", "plot_all", fallback=False)


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
                         'return_dict': return_dict, 'ped_mask_path' : ped_mask_path, 
                         'w_opt' : w_opt, 'plot_all' : plot_all}
            process_list.append(CAProcess(target=analysis, kwargs=arguments))

    [p.start() for p in process_list]
    [p.join() for p in process_list]
    # Submit all the elog entries
    if not noelog:
        __submit_elog(credentials, dhc_objects, local_ini, logger, noelog, return_dict)


    if return_dict:
        mydict={}
        for dhc in dhc_objects:
            for module in dhc.modules:
                mydict[module.dhe]=return_dict[module.dhe]
        np.save(os.path.join(path, 'analysis.npy'), mydict)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--config', dest='config', default='analysis.ini')
    parser.add_argument('-n', '--no-elog', action='store_true', dest='noelog', default=True,
                        help='Option to disable the elog logging feature.')
    args = parser.parse_args()
    local_ini = args.config.decode('utf-8')

    # initialize logger and start the elog entry
    globallogger = log_utils.get_pxd_main_logger(application_name="Current source Calibration Analysis",
                                                 loglevel=log_utils.FINE, no_remote=True)
    main(globallogger, local_ini, noelog=args.noelog)
