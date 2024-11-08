#!/usr/bin/env python
# coding:utf8

"""
pedestal/update.py
==================


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
import ped_readback
import epics_utils


def main(logger, commitid=-1, path=None, db=False, system=False, dhes=None):

    if system==False and db==False :
        logger.info("Neither system nor database chosen. Nothing to update. Exiting.")
        return


    # resolve path
    if path is None:
        latestpathfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".latestpath")
        with open(latestpathfile, "r") as f:
            path = f.read().rstrip()
    logger.fine("Using optimized current source values from this path: %s" % path)


    # load measure.ini to get list of dhes if dhes are not specified
    if dhes is  None:
        if os.path.isfile(os.path.join(path, "measure.ini")):
            measureini_file = os.path.join(path, "measure.ini")
            dhes = []
            dhcs = config_utils.get_setup_from_scan_config(measureini_file)
            for dhc in dhcs:
                for module in dhc.modules:
                    dhes.append(module.dhe)
        else:
            logger.info("No dhes specified and no measure.ini found. Exiting.")
            return


    #Look for numpy file
    if os.path.isfile(os.path.join(path, "analysis.npy")):
        npy_file = os.path.join(path, "analysis.npy")
    else:
        logger.info("No analysis.npy found. Exiting")
        return


    #Upload to system
    if system:
        logger.fine("Updating system")
        optimal_dict = np.load(npy_file).item()
        pvlist=[]
        for dhe in dhes:
            for key, val in optimal_dict.iteritems():
                if dhe in key:
                    pvlist.append([key,val])
        epics_utils.pvlist_put(pvlist)
        epics_utils.write_to_JTAG_parallel(dhes, 0, JTAGtype="dcd", parallel=True)


    '''
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
    '''

    '''
    # update configDB
    if db and (commitid > 0) :
        filenames=[]
        for dhe in dhes:
            filenames.append(os.path.join(path, "%s/analysis.npy" % dhe))
        updateFromAnalysisNPY(filenames, commitid=commitid, dryrun=False)
    '''

if __name__ == "__main__":
    # initialize logger
    globallogger = log_utils.get_pxd_main_logger(application_name="Current source calibration update", no_remote=True, loglevel='FINEST')
    globallogger.info("Start of current source update")

    # get command line parameters
    parser = ArgumentParser(description='Upload best current source values to the DCD and/or the ConfigDB')
    parser.add_argument('-id', '--commitid', default=-1, type=int,
                        help="commitID to be updated, if not given current ID is used (must be HEAD of a branch)")
    parser.add_argument('-p', '--path', default=None, type=str,
                        help="look for .npy-file in this folder, only useable with DHC data")
    parser.add_argument('--db', default=False, action='store_true',
                        help="upload to configDB")
    parser.add_argument('--system', default=False, action='store_true',
                        help="upload to DHP")
    parser.add_argument('--dhe', default=None, nargs='+', help="name of the DHE(s)")
    args = parser.parse_args()

    main(globallogger, args.commitid, args.path, args.db, args.system, args.dhe,
         use_sequential_upload=args.sequential, verifyUpload=args.verify)
