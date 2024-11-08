#!/usr/bin/env python
# coding:utf8

"""
pedestal/update.py
==================

:author: Harrison Schreeck

Upload of pedestals to the DHP and/or ConfigDB from file (analysis.npy)

This script loads the pedestal data from the given numpy file and uploads it either to the ConfigDB or the DHP or both.
If you update the ConfigDB, the specified commit (via -id) has to the HEAD of its branch. If you do not specify the
commit via the -id option, the currently active commitid is used (from the PV 'PXD:B:config-commitid').

To update only the db use the --db option:
>>> update.py -id 523 -f analysis.npy --db

If you leave the -id option, the current commit is updated:
>>> update.py -f analysis.npy --db

If you want to update only the system, the commitid is not needed:
>>> update.py -f analysis.npy --system

If you want to update the ConfigDB and the system, you can use both flags (--db and --system) or don't set them at all.
Here you can again leave the -id option if you want to update the current commit.
>>> update.py -f analysis.npy --system --db
or
>>> update.py -f analysis.npy
"""

import numpy as np
from argparse import ArgumentParser
from epics_utils import get_pv
from updatedb import updateFromAnalysisNPY
import config_utils
import os
import upload_utils
import log_utils
from configparser import NoSectionError
from dhc_utils import get_put_progress
import configparser

def prepare_pedestal(logger, path, dhe, mask, pedestal_mem=0):
    assert pedestal_mem == 0 or pedestal_mem == 1
    pedestals = []
    user = 'PXD'
    logger.finer("Preparing pedestals for DHE %s, Pedestal memory %d" % (dhe, 512 if pedestal_mem == 0 else 768))
    analysisfile = os.path.join(path, "%s/analysis.npy" % dhe)
    try:
        ana = np.load(analysisfile).item()
    except IOError:
        try:
            ana = np.load(analysisfile.replace("%s/" % dhe, "")).item()
        except IOError:
            logger.warning("No data found for dhe %s" % dhe)
            return None
    for asic in [1, 2, 3, 4]:
        logger.finest("Preparing pedestals for DHP %d on DHE %s." % (asic, dhe))
        ped_512 = ana['%s:%s:D%s:pedestal_data_%i' % (user, dhe, asic, 512 if pedestal_mem == 0 else 768)]
        if mask is not None:
            logger.finest("Adding noisemask for DHE %s, asicpair %i." % (dhe, asic))
            ped_512[np.where(mask[:, ((asic - 1) * 64):(asic * 64)])] = 255

        # FIXME: upload "timing pixels" to first DHP
        # if asic == 1:
        #    ped_512[0::4, 63] = 0

        # FIXME: mask half of last gate in DHP memory to overcome DHP timing bug
        ped_512 = np.round(ped_512).astype(np.uint8)
        ped_512[764:, :] = 255

        # manual pedestal offset to overcome DHP pedestal_offset bug
        ped_512[ped_512 < 10] = 10
        ped_512[ped_512 != 255] -= 10
        pedestals.append(ped_512)
    return np.hstack(tuple(pedestals))


def main(logger, commitid=-1, file=None, path=None, db=False, system=False, noisemask=False, dhes=None,
         useprogresspv=False, use_udp_upload=False, use_sequential_upload=False):
    # if not differently specified, update both: db and system
    if db is False and system is False:
        db = True
        system = True
    if db is True and system is True:
        logger.info("Updating System and ConfigDB.")
    elif db is True and system is False:
        logger.info("Updating ConfigDB.")
    elif db is False and system is True:
        logger.info("Updating System.")

    # catch some errors
    if db and commitid <= 0:
        logger.warning("Need to specify a valid commitID (%s given)!" % (str(commitid)))
        return 1
    if db and type(commitid) != int:
        logger.warning("-id/--commitid must be integer (given: %s of type %s)!" % (str(commitid), type(commitid)))
        return 1

    # commitid
    if commitid == -1:
        commitid = get_pv("PXD:B:config-commitid").get()

    # file and path given? This is not allowed!
    if file is not None and path is not None:
        logger.warning("You cannot specify a file and a path, exiting now!")
        return 1

    # resolve path
    if path is None:
        if file is None:
            latestpathfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".latestpath")
            with open(latestpathfile, "r") as f:
                path = f.read().rstrip()
        else:
            path = os.path.dirname(file)
            analysisfile = file
            logger.finest("Loading pedestals from %s" % analysisfile)
    logger.finest("Using pedestals from this path: %s" % path)

    # load measure.ini only if we are in 'path' mode!
    module_dict = {}
    if path is not None:
        if os.path.isfile(os.path.join(path, "measure.ini")):
            measureini = config_utils.read_config(os.path.join(path, "measure.ini"))
        else:
            logger.info("No measure.ini found, exiting.")
            return 0
        dhcs = measureini.get("general", "dhc", fallback='None').split(",")
        if dhes is None:
            dhe_dict = {}
            dhes = []
            for dhc in dhcs:
                try:
                    dhe_dict[dhc] = measureini.get(dhc, "dhes").split(",")
                except NoSectionError:
                    dhe_dict[dhc] = measureini.get("general", "dhe").split(",")
                for el in dhe_dict[dhc]:
                    module_dict[el] = measureini.get(el, "device_module")
                    dhes.append(el)
        else:
            dhes = [dhes]

    # load the noisemask
    if noisemask:
        noise_dict = {}
        for k, v in module_dict.iteritems():
            try:
                noise_dict[k] = np.load(
                    os.path.expanduser("~/lab_framework/calibrations/pedestal/masks/noisemask%s.npy" % v))
            except IOError:
                logger.warning("No noisemask found for DHE %s, unmodified pedestals will be uploaded." % k)

    # If the file is explicitly given, get the DHE name from the first key in the analysis dictionary
    if file is not None:
        dhes = [np.load(analysisfile).item().keys()[0].split(':')[1]]

    # update configDB
    if db:
        filenames=[]
        # TODO: What should be written into the 512/768 memory? The same pedestals?
        for dhe in dhes:
            filenames.append(os.path.join(path, "%s/analysis.npy" % dhe))
        updateFromAnalysisNPY(filenames, commitid=commitid, dryrun=False)

    # update system
    return_dict = {}
    if system:
        pedestal_list = [prepare_pedestal(logger, path, dhe,
                                          noise_dict[dhe] if noisemask and el in noise_dict else None,
                                          pedestal_mem=0) for dhe in dhes]
        if use_udp_upload:
            logger.info("Using deprecated UDP upload!")
        if not use_sequential_upload:
            logger.info("Performing parallel upload to all DHES.")
        upload_utils.parallelUpload(dhes, pedestal1_list=pedestal_list, pedestal2_list=None, data1_list=None,
                                    data2_list=None, user="PXD", parallel=not use_sequential_upload, old=use_udp_upload)


        config_local = configparser.ConfigParser(delimiters='=')
        config_local.optionxform = str
        
        update_latestpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), ".update_latestpath")
        if os.path.exists(update_latestpath):
            config_local.read(update_latestpath)
        else:
            config_local.add_section("DHE")

        for dhe in dhes:
            config_local.set("DHE", dhe, path)
            put_progress = get_put_progress(dhe, useprogresspv)
            put_progress(200 + 100)
            return_dict[dhe] = path
        with open(update_latestpath, 'w') as configfile:
            config_local.write(configfile)
        for dhe, pedestal in zip(dhes, pedestal_list):
            if pedestal is not None:
                for asic, pedestal_slice in enumerate(np.hsplit(pedestal, 4)):
                    return_dict['%s_D%i_pedestal' % (dhe, asic+1)] = pedestal_slice.astype(dtype=np.uint8)         
    return return_dict


if __name__ == "__main__":
    # initialize logger
    globallogger = log_utils.get_pxd_main_logger(application_name="pedestal/update", no_remote=True, loglevel='FINEST')
    globallogger.info("Start of Pedestal Update")

    # get command line parameters
    parser = ArgumentParser(description='Upload pedestals to the DHP memory and/or the ConfigDB')
    parser.add_argument('-id', '--commitid', default=-1, type=int,
                        help="commitID to be updated, if not given current ID is used (must be HEAD of a branch)")
    parser.add_argument('-f', '--file', default=None, type=str,
                        help="read pedestals from this .dat-file, if not specified .latestpath is read")
    parser.add_argument('-p', '--path', default=None, type=str,
                        help="look for .dat-file in this folder, only useable with DHC data")
    parser.add_argument('--db', default=False, action='store_true',
                        help="upload to configDB")
    parser.add_argument('--system', default=False, action='store_true',
                        help="upload to DHP")
    parser.add_argument('--dhe', default=None, help="name of the DHE")
    parser.add_argument('--noisemask', default=False, action='store_true',
                        help="look for a noisemask and use it")
    parser.add_argument('--udp', default=False, action='store_true',
                        help="Use the 'old' upload via UDP instead of EPICS.")
    parser.add_argument('--sequential', default=False, action='store_true',
                        help="Do not perform the upload in parallel but sequentially.")
    args = parser.parse_args()

    main(globallogger, args.commitid, args.file, args.path, args.db, args.system, args.noisemask, args.dhe,
         use_udp_upload=args.udp, use_sequential_upload=args.sequential)
