#!/usr/bin/env python
# coding:utf8

"""
pedestal/update.py
==================

:authors: Varghese Babu, Felix J. Mueller

Upload of 'best' current-source values to the modules ASIC-pairwise and/or to the ConfigDB from file (analysis.npy)


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
from updatedb import updateFromAnalysisNPY
import config_utils
import os
import log_utils
from epics_utils import  get_pv

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


    #Load numpy files
    filenames=[]
    for dhe in dhes:
        if os.path.isfile(os.path.join(path, dhe, "analysis.npy")):
            filenames.append(os.path.join(path, dhe, "analysis.npy"))
        else:
            logger.info("No analysis.npy found for module %s" % dhe)

    
    #Upload to system
    if  system:
        pvlist=[]
        for filename in filenames:
            load_dict=np.load(filename).item()
            for key, val in load_dict.iteritems():
                pvlist.append([key,val])
        epics_utils.pvlist_put(pvlist)
        epics_utils.write_to_JTAG_parallel(dhes, 0, JTAGtype="dcd", parallel=True)



    # update configDB
    if db :
        # Load current commitid if not specified
        if commitid == -1:
            commitid = get_pv("PXD:B:config-commitid").get()

        if commitid > 0:
            updateFromAnalysisNPY(filenames, commitid=commitid, dryrun=False)
        else:
            #If a negative commit-id was provided, for instance
            logger.warning("Please provide a valid commit-id")
    

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

    main(globallogger, args.commitid, args.path, args.db, args.system, args.dhe)
