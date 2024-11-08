#!/usr/bin/env python

"""
wrapper.py
==========

:authors: Harrison Schreeck

Records pedestals and analyses them

This script executes the measure.py script to record pedestals and then analyses them by executing the analysis.py
script. In order to do that both ini files (measure.ini and analysis.ini) have to be given to the script.

>>> wrapper.py
>>> wrapper.py -m measure.ini -a analysis.ini

"""

from os import system
from os.path import join, dirname, abspath
from argparse import ArgumentParser

if __name__ == "__main__":
    # get inifiles from command line argument (if not supplied: default=measure.ini and analysis.ini)
    parser = ArgumentParser(description='Record Pedestals and analyse them')
    parser.add_argument('-m', '--measure', dest='measure_ini', default=join(dirname(abspath(__file__)), "measure.ini"))
    parser.add_argument('-a', '--analysis', dest='analysis_ini',
                        default=join(dirname(abspath(__file__)), "analysis.ini"))
    parser.add_argument('-tmp', '--temporary', action='store_true', dest='temporary', default=False,
                        help="If this flag is set, no elog entry will be created, the logging is turned off, and the "
                             "data is stored in /tmp/. In addition no PVDump is created. This is useful to speed up "
                             "the measurement.")
    args = parser.parse_args()

    if args.temporary:
        system(join(dirname(abspath(__file__)), "measure.py -tmp -c %s") % str(args.measure_ini))
        system(join(dirname(abspath(__file__)), "analysis.py -tmp -c %s") % str(args.analysis_ini))
    else:
        system(join(dirname(abspath(__file__)), "measure.py -c %s") % str(args.measure_ini))
        system(join(dirname(abspath(__file__)), "analysis.py -c %s") % str(args.analysis_ini))
