#!/usr/bin/env python
"""
analysis.py
===========

:authors: Harrison Schreeck, Varghese Babu

Analyse pedestals for different VnSubOut values nd determine the optimal one

Usage:

Config:

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



def main(logger, local_ini, path=None, tmp=False, noelog=False, dhc_objects=None, elogcredentials=None,
         useprogresspv=False, quietmode=False, nowarnings=False, pvupdate=False, pdf_plotting=True):
    if nowarnings:
        np.warnings.filterwarnings('ignore')
    if tmp or quietmode:
        logger.setLevel(log_utils.SEVERE)
    if tmp:
        noelog = True
        local_ini = "/tmp/analysis.ini.RunPedestalMeasurement"

    logger.info("Start of Pedestal analysis")


if __name__ == "__main__":
    # get inifile from command line argument (if not supplied: default=analysis.ini)
    parser = ArgumentParser(description='Analyse Pedestals')
    parser.add_argument('-c', '--local_ini', dest='local_ini',
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis.ini"))
    parser.add_argument('-tmp', '--temporary', action='store_true', dest='temporary', default=False,
                        help="If this flag is set, no elog entry will be created, the logging is turned off, and the "
                             "data is stored in /tmp/. In addition no PVDump is created. This is useful to speed up "
                             "the measurement.")
    parser.add_argument('-n', '--no-elog', action='store_true', dest='noelog', default=True,
                         help='Option to disable the elog logging feature. In contrast to the \'-tmp\' flag, plots are '
                              'still saved at the location specified in the *.ini file and not in /tmp/.')
    parser.add_argument('--quiet', action='store_true', dest='quietmode', default=False,
                         help='Option to set the loglevel to severe. If enabled only errors will be shown.')
    parser.add_argument('--no_warnings', action='store_true', dest='nowarnings', default=False,
                        help='Option to suppress numpy warnings.')
    parser.add_argument('--pvupdate', action='store_true', dest='pvupdate', default=False,
                        help='Update of Pedestal Monitor.')
    args = parser.parse_args()
    local_ini = args.local_ini.decode('utf-8')

    #print local_ini

    # initialize logger and start the elog entry
    logger = log_utils.get_pxd_main_logger(application_name="pedestal/analysis", no_remote=True)

    main(logger, local_ini, tmp=args.temporary, noelog=args.noelog, quietmode=args.quietmode, nowarnings=args.nowarnings, pvupdate=args.pvupdate)








