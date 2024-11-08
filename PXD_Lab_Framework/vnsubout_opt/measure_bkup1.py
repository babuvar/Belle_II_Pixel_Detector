#!/usr/bin/env python

"""
measure.py
==========

:authors: Harrison Schreeck

Records pedestals

This script records pedestals.

Usage:
The script takes all configuration from an ini-file which is given via the -c parameter:
>>> measure.py -c measure.ini

Config:

[general]
asicpair = 1                #[REQ]  asicpairs to scan, can be 0, 1, 2, 3 or 4 where 0 means all asics.
path =                      #[OPT]  path overwrites automatic path creation, should only be set when this is explicitly
                                    wanted). ~ will be expanded with user's home directory
device =                    #[OPT]  which device? hybrid5 or pxd9? , if not given will be determined from configDB
module =                    #[OPT]  module name? e.g. W30_IB or H5006, if not given will be determined from configDB
module_type =               #[OPT]  module type? ib, if, ob, of or none for hyrid5, if not given will be determined from
                                    configDB
framenr = 200               #[REQ]  number of frames that will be recorded
useExternalTrigger = False  #[REQ]  Is an external trigger used? For lab setups the internal trigger is used most of the
                                    time.
triggerTime = 5             #[REQ]  Time between external triggers, default is 5 (seconds)
daqport = 6000              #[REQ]  Port to which the data (UDP packages) is sent, default is 6000. Check DHE settings
                                    'UDP port DEST'.
"""

import log_utils
import os
import elog
import config_utils
import dhp_utils
import configparser
from epics_utils import get_pv
from argparse import ArgumentParser
import daq
import numpy as np
import dcd_utils
from epics import CAProcess
from epics.ca import create_context, destroy_context
from multiprocessing import Manager
from config_utils import createDataFolder
import ftsw_control
import multiprocessing
import time
import epics_utils


def getACMCAndOffsetStatus(user, dhe, asicpair):
    acmc_status = dcd_utils.getAnalogCommonModeStatus(user=user, dhe=dhe, asicpair=asicpair)
    offset_status = dhp_utils.getOffsetStatus(user=user, dhe=dhe, asicpair=asicpair)
    if acmc_status:
        acmc_status = 'On'
    else:
        acmc_status = 'Off'
    if offset_status:
        offset_status = 'On'
    else:
        offset_status = 'Off'

    return acmc_status, offset_status


def performMeasurement(logger, dhc, dhe, path, asicpairs, framenr, freq, useExternalTrigger, daqport, dataport,
                       controlport, useDHC, useprogresspv, return_dict, event_daq, event_triggering, current_source_list,
                       current_source_ranges):
    create_context()
    dhes = [module.dhe for module in dhc.modules]
    error_occured = 0

    #Loop over VnSubOut values
    for current_source_Val in current_source_ranges:

        # create filename and fullfilename (with path!)
        if not useDHC:
            filename = "rawframe_data_%i.dat" %current_source_Val
            #npyfilename = "rawframe_data.npy"
        else:
            filename = "%srawframe_data_%i.dat" % (dhc.name,current_source_Val)
            #npyfilename = "%srawframe_data.npy" % dhc
        fullfilename = os.path.join(path, filename)


        #Write new VnSubOut value to DCD via JTAG
        epics_utils.pvlist_put_same(current_source_list, current_source_Val)
        #epics_utils.write_to_JTAG_parallel(dhes, asicpairs, JTAGtype="dcd", parallel=False)
        epics_utils.write_to_JTAG_parallel(dhes, asicpairs, JTAGtype="dcd", parallel=True)
        logger.fine("VnSubOut changed to new value: %i" % (current_source_Val))

        # perform measurement
        logger.fine("Taking %i memdump frames and saving to %s" % (framenr, fullfilename))
        try:
            triggerTime = 1. / freq
            sleeptime = 1. / freq
            data = daq.record_memorydump(asicpair=asicpairs, framenr=framenr, dhc=dhc.name, dhePrefix=dhe,
                                 filename=fullfilename, externalTrigger=useExternalTrigger,
                                 trigggerTime=triggerTime, daqport=int(daqport), dataport=dataport,
                                 controlport=controlport, useDHC=useDHC, sleep_time=sleeptime, readdata=False,
                                 useprogresspv=useprogresspv, event_daq=event_daq, event_triggering=event_triggering)
        except IOError as e:
            error_occured = 1
            return_dict[dhc.name] = {'success': False}

        # save data as npy
        #if error_occured == 0:
            #return_dict[dhc] = {'success': True}
            #np.save(os.path.join(path, npyfilename), data)
            #logger.fine("Data saved to disk.")
    destroy_context()


def main(logger, local_ini, tmp=False, noelog=False, elogcredentials=None, useprogresspv=False, create_pvdump=True,
         dhcs=None):
    if tmp:
        # no elog or PV dump for tmp runs
        noelog=True
        create_pvdump=False
        logger.setLevel(log_utils.FINEST)
    logger.info("Start of VnSubOut Scan")
    # ------------ read configuration ----------------------------------------------------------------------------------
    logger.fine("Read configuration from %s", os.path.abspath(local_ini))
    # read general config from master/measure ini
    required_values = {
        "asicpair": str,
        "framenr": int,
        "triggerfrequency": float,
    }

    # Load the config (merged with master setup config file!)
    config, dhcs = config_utils.read_and_merge_config(local_ini, required_values, dhcs=dhcs)

    # read some guaranteed values
    useDHC = config.getboolean('general', 'useDHC')
    useExternalTrigger = config.getboolean('general', 'useExternalTrigger')
    if not useDHC:
        dhe = config.get('general', 'dhe', fallback=None)
    else:
        dhe = None

    current_source = config["general"]["current_source"]
    current_source_ranges=config_utils.get_scan_values(config["current_source_ranges"])
    #ipdac_ranges = config_utils.get_scan_values(config["ipdac_ranges"])

    # inform the user about what is going on
    if useDHC:
        for i, dhc in enumerate(dhcs):
            if i == 0:
                msg = 'Performing pedestal measurement for DHC %s, with DHEs %s' % (dhc.name, [el.dhe for el in dhc.modules])
            else:
                msg += '\nand DHC %s, with DHEs %s' % (dhc, [el.dhe for el in dhc.modules])
        logger.info(msg)

    # get required values
    logger.finest('Get required values from general_config.')
    if useDHC:
        asicpair = 0  # For DHC mode we only support all 4 asics
    else:
        asicpair = config.getint('general', 'asicpair')
    asicpairs = dhp_utils.getListOfAsicpairs(dhe, asicpair, offline=True)
    framenr = config.getint('general', 'framenr')
    freq = config.getfloat('general', 'triggerfrequency')

    # get values from current system configuration
    logger.finest('Get values from current system configuration')
    for dhc in dhcs:
        for module in dhc.modules:
            config.add_section(module.dhe)
            for i in asicpairs:
                acmc_status, offset_status = getACMCAndOffsetStatus(config['general']['user'], module.dhe, i)
                config.set(module.dhe, "ACMC_DCD%i" % i, acmc_status)
                config.set(module.dhe, "OFFSET_DHP%i" % i, offset_status)
            device_module = get_pv("PXD:B:config-" + module.dhe, "device_module:VALUE:set").get(as_string=True)
            device_config = get_pv("PXD:B:config-" + module.dhe, "device_config:VALUE:set").get(as_string=True)
            module_type = get_pv("PXD:B:config-" + module.dhe, "module_type:VALUE:set").get(as_string=True)
            config.set(module.dhe, "device_module", str(device_module))
            config.set(module.dhe, "device_config", str(device_config))
            config.set(module.dhe, "module_type", str(module_type))


    current_source_dict = {}
    for dhc in dhcs:
        current_source_dict[dhc.name] = []
        for module in dhc.modules:
            for asicpair in asicpairs:
                current_source_dict[dhc.name].append(epics_utils.pvname_dcd(module.dhe, asicpair, "dac%s:VALUE:set" % (current_source)))

    # Deal with the ELOG
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
                             'Aborting measurement now!')
            return -1
        myelog = None
        try:
            myelog = elog.elog(configfile=local_ini, type="Pedestal Scan", username=credentials.getusername(),
                               password=credentials.getpassword(), dhc_objects=dhcs)
        except Exception as e:
            logger.warning("elog.elog: " + repr(e))
            raise e

    # create data path
    if tmp:
        path = "/tmp/"
        logger.config("Data will be saved in: %s" % path)

        # save copy of measure.ini in datapath
        with open(os.path.join(path, os.path.basename("measure.ini.RunPedestalMeasurement")), 'w') as configfile:
            config.write(configfile)
        logger.finest('Copied measure.ini to datapath (%s)' % path)
    else:
        if useDHC:
            path = createDataFolder(config['general']['basepath'], None, "current_source_scan")
        else:
            path = createDataFolder(config['general']['basepath'], config[dhe]['device_module'], "current_source_scan")
        logger.config("Data will be saved in: %s" % path)

        # save copy of measure.ini in datapath
        with open(os.path.join(path, os.path.basename("measure.ini")), 'w') as configfile:
            config.write(configfile)
        logger.finest('Copied measure.ini to datapath (%s)' % path)

    # save system state and dump PV list
    # FIXME: Looks like the Configuration class does currently not work with a list of dhes, so I call the
    # FIXME: constructor multiple times to get the PVs from all DHEs
    if create_pvdump:
        logger.finest('Creating PVDump.')
        try:
            for dhc in dhcs:
                for module in dhc.modules:
                    system_cfg = config_utils.Configuration(commitid="current", dhe=module.dhe)
            system_cfg.read()
            system_cfg.save(os.path.join(path, "PVdump-prescan.npy"))
        except KeyError as e:
            logger.warning('Some keys not found, are you sure the DHEs match the ones in the current commit?'
                           'PVDump will not be created!')


    # external trigger
    if useExternalTrigger:
        def external_triggering(event_daq, event_triggering):
            # in future we will access the FTSW from CSS with PVs hopefully
            # => the next 3 lines will change in future & ftsw_control library
            ftsw_host = "localhost"
            ftsw_port = 10000
            ftsw_id = 232
            logger.fine("Initialize FTSW")
            ftsw = ftsw_control.ftsw_control(ftsw_host, ftsw_port, ftsw_id)
            # perform a reset of FTSW
            ftsw.reset()
            # we wait here until all DAQs are started, then we proceed with the triggering
            event_triggering.wait()
            # now we trigger
            logger.fine("Set trigger to FTSW")
            ftsw.set_trigger(freq=freq, count=framenr, type="pulse")
            logger.fine("Sucessfully set triggers to ftsw")
            time.sleep(framenr/float(freq))
            # we are done with the triggering and daq and continue
            event_daq.set()


    # ------------ Start measurement ----------------------------------------------------------------------------------
    try:
        processes = []
        manager = Manager()
        return_dict = manager.dict()



        # create 2 events to synchronize the processes, in particular data acquistion and external Trigger
        event_triggering = multiprocessing.Event()
        event_daq = multiprocessing.Event()
        # create the processes for DAQ
        for dhc in dhcs:
            processes.append(CAProcess(target=performMeasurement,
                                       args=(logger, dhc, dhe, path, asicpairs,
                                             framenr, freq, useExternalTrigger,
                                             dhc.udp_dst_port, dhc.data_port, dhc.control_port, useDHC,
                                             useprogresspv, return_dict, event_daq, event_triggering,
                                             current_source_dict[dhc.name], current_source_ranges)))

        if useExternalTrigger:
            # create the process for external trigger (in sync with DAQ)
            processes.append(CAProcess(target=external_triggering, args=(event_daq, event_triggering)))

        for p in processes:
            p.start()
        for p in processes:
            p.join()

        # store data path in .latestpath
        if not tmp:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".latestpath"), "w") as f:
                f.write(path)

        # submit to ELOG
        if not tmp and not noelog:
            try:
                if myelog is not None:
                    myelog.submitEntry(path=path)
            except Exception as e:
                logger.warning("elog.submitEntry:" + repr(e))

        # return dictionary with useful information like path and whether data taking was successful
        return_dict['path'] = path
        return return_dict

    except KeyboardInterrupt:
        logger.warning("Scan canceled by user, exiting")
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    # get inifile from command line argument (if not supplied: default=measure.ini)
    parser = ArgumentParser(description='Record Pedestals')
    parser.add_argument('-c', '--local_ini', dest='local_ini',
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "measure.ini"))
    parser.add_argument('-tmp', '--temporary', action='store_true', dest='temporary', default=False,
                        help="If this flag is set, no elog entry will be created, the logging is turned off, and the "
                             "data is stored in /tmp/. In addition no PVDump is created. This is useful to speed up "
                             "the measurement.")
    parser.add_argument('-n', '--no-elog', action='store_true', dest='noelog', default=False,
                        help='Option to disable the elog logging feature. In contrast to the \'-tmp\' flag, data is '
                             'still saved at the location specified in the *.ini file and not in /tmp/.')
    args = parser.parse_args()
    local_ini = args.local_ini.decode('utf-8')

    # initialize logger and start the elog entry
    logger = log_utils.get_pxd_main_logger(application_name="pedestal/measure", no_remote=True,
                                           loglevel=log_utils.FINEST)

    main(logger, local_ini, args.temporary, args.noelog, create_pvdump=True)
