#!/usr/bin/env python

"""
RunPedestalMeasurement.py
=========================

:author: Harrison Schreeck

Script to run a pedestal analysis (measurement + analysis using custom *.ini files)

This script can be used to create a customized measure.ini or analysis.ini and run a pedestal measurement + analysis.
The customized ini files are stored in /tmp/ and are overwritten each time you run this script. The main purpose of
this script is the usage in CS-Studio, where you want to push a button to measure and analyze pedestals.

>>> RunPedestalMeasurement.py
>>> RunPedestalMeasurement.py -m measure.ini.default -ma general asicpair 2 -ma general path /path/to/file
>>>                           -a analysis.ini.default -aa

"""

from argparse import ArgumentParser
import configparser
from os import system
from os.path import join, dirname, abspath

if __name__ == "__main__":
    parser = ArgumentParser(description='Creates customized ini file')
    parser.add_argument('-ma', '--measure-ini-argument', dest='measureiniargument', action='append', nargs=3,
                        metavar=('section', 'option', 'value'))
    parser.add_argument('-m', '--measure-ini-template', dest='measuretemplate', default="measure.ini.default")
    parser.add_argument('-aa', '--analysis-ini-argument', dest='analysisiniargument', action='append', nargs=3,
                        metavar=('section', 'option', 'value'))
    parser.add_argument('-a', '--analysis-ini-template', dest='analysistemplate', default="analysis.ini.default")
    parser.add_argument('-tmp', '--temporary', action='store_true', dest='temporary', default=False,
                        help="If this flag is set, no elog entry will be created, the logging is turned off, and the "
                             "data is stored in /tmp/. In addition no PVDump is created. This is useful to speed up "
                             "the measurement.")
    args = parser.parse_args()

    # Call createIniFromTemplate.py script for measure.ini
    if args.measureiniargument is not None:
        measureString = "../../configurations/createIniFromTemplate.py " \
                        "-c %s " \
                        "-o /tmp/measure.ini.RunPedestalMeasurement" % args.measuretemplate
        for argument in args.measureiniargument:
            measureString += " -a %s %s %s" % (argument[0], argument[1], argument[2])
        system(join(dirname(abspath(__file__)), measureString))
    else:
        system("cp %s /tmp/measure.ini.RunPedestalMeasurement" % args.measuretemplate)

    # Call createIniFromTemplate.py script for analysis.ini
    if args.analysisiniargument is not None:
        analysisString = "../../configurations/createIniFromTemplate.py " \
                        "-c %s " \
                        "-o /tmp/analysis.ini.RunPedestalMeasurement" % args.analysistemplate
        for argument in args.analysisiniargument:
            analysisString += " -a %s %s %s" % (argument[0], argument[1], argument[2])
        system(join(dirname(abspath(__file__)), analysisString))
    else:
        system("cp %s /tmp/analysis.ini.RunPedestalMeasurement" % args.analysistemplate)

    # Call wrapper.py script
    if args.temporary:
        system(join(dirname(abspath(__file__)), "wrapper.py -tmp -m /tmp/measure.ini.RunPedestalMeasurement "
                                                "-a /tmp/analysis.ini.RunPedestalMeasurement"))
    else:
        system(join(dirname(abspath(__file__)), "wrapper.py -m /tmp/measure.ini.RunPedestalMeasurement "
                                                "-a /tmp/analysis.ini.RunPedestalMeasurement"))
