#!/usr/bin/env python2.7
#coding: utf8

import numpy as np
import config_utils
import epics_utils
import dhp_utils
import os
import time
import mapping
import argparse

# single imports
from daq import record_memorydump

TARGET_ADU = 128
TARGET_GATEON = -2000
VNSUBIN_START = 10
VNSUBIN_END = 50
VNSUBIN_STEP = 2


def getPedQuality(systemparams, target=TARGET_ADU, dcd=0, gateon=0, history=None):
    # check and reset links
    dhp_utils.get_link(systemparams["dhe"], 0, useGTXrst=True, useShortRst=True, useLongRst=False, trials=3)
    time.sleep(1)
    # get data
    for trial in range(3):
        try:
            data = record_memorydump(0, 10, systemparams["user"]+":"+systemparams["dhe"])
            break
        except IOError as ioe:
            print "WARNING: NO DATA RECORDED!!!"
            dhp_utils.get_link(systemparams["dhe"], 0, useGTXrst=True, useShortRst=True, useLongRst=False, trials=3)
            time.sleep(2)
            if trial == 2:
                raise ioe
    # map data
    data = np.asarray(mapping.matrixToDcd(data), dtype=int)
    # determine chi2 form selected region
    if dcd == 0:
        drain_start = 0
        drain_end = 1024
    else:
        drain_start = (dcd-1) * 256
        drain_end = drain_start + 256
    if gateon == 0:
        gate_start = 0
        gate_end = 192
    else:
        gate_start = (gateon-1) * 64
        gate_end = gate_start + 64
    chi2 = np.sum( np.square( data[gate_start:gate_end, drain_start:drain_end] - target ) )
    print "chi2: %.2d" %chi2
    return chi2


def getOptimalGateOn(systemparams, target, gaterange=150, step=10, dcd=0, gateon=0, history=None):
    # loop over gateon
    gateon_list = []
    chi2_list = []
    for gateon_value in np.arange(target-gaterange, target+gaterange+step, step):
        # apply gate-on voltages
        putGateOnVoltage(systemparams, gateon_value, gateon=gateon)
        chi2 = getPedQuality(systemparams, dcd=dcd, gateon=gateon, history=history)
        gateon_list.append(gateon_value)
        chi2_list.append(chi2)
    with open("getOptimalGateOn_DCD%i-GATEON%i-TARGET%i.txt"%(dcd, gateon, target), "a") as fwriter:
        fwriter.write("gateon,\tchi2\n")
        for i, chi2_i in enumerate(chi2_list):
            fwriter.write("%s,\t%s\n" % (gateon_list[i], chi2_i))
    return gateon_list[chi2_list.index(min(chi2_list))]


def getOptimalDAC(systemparams, target, dacrange=20, step=2, dcd=0, gateon=0, current_source="vnsubin", history=None):
    # loop over DACVnSubIn
    dac_list = []
    chi2_list = []
    if current_source == "vnsubin":
        putDAC = putVNSubIn
    elif current_source == "vnsubout":
        putDAC = putVNSubOut
    else:
        raise IOError("unsupported current source %s" % current_source)
    for dac in np.arange(target-dacrange, target+dacrange+step, step):
        # apply DAC
        putDAC(systemparams, dac, dcd=dcd)
        chi2 = getPedQuality(systemparams, dcd=dcd, gateon=gateon, history=history)
        dac_list.append(dac)
        chi2_list.append(chi2)
    with open("getOptimalDAC_DCD%i-GATEON%i-TARGET%i.txt"%(dcd, gateon, target), "a") as fwriter:
        fwriter.write("DAC,\tchi2\n")
        for i, chi2_i in enumerate(chi2_list):
            fwriter.write("%s,\t%s\n" % (dac_list[i], chi2_i))
    return dac_list[chi2_list.index(min(chi2_list))]


def putVNSubIn(systemparams, value, dcd=0):
    dcds = [1, 2, 3, 4] if dcd == 0 else [dcd]
    assert value in range(0,128), "invalid VNSubIn value %s" % value
    # set VNSubIn DAC
    for vnsubin_pv in [epics_utils.get_pv(systemparams["user"], systemparams["dhe"], "R%i" % i, "dacvnsubin:VALUE:set") for i in dcds]:
        vnsubin_pv.put(value)
        print "-> setting %s to %i" % (vnsubin_pv.pvname, value)
    # pull JTAG write register triggers
    for regTrg_pv in [epics_utils.get_pv(systemparams["user"], systemparams["dhe"], "R%i" % i, "globalsr:trg:set") for i in dcds]:
        regTrg_pv.put(1)
        print "-> pulling %s" % regTrg_pv.pvname
        time.sleep(1)

def putVNSubOut(systemparams, value, dcd=0):
    dcds = [1, 2, 3, 4] if dcd == 0 else [dcd]
    assert value in range(0,128), "invalid VNSubOut value %s" % value
    # set VNSubIn DAC
    for vnsubout_pv in [epics_utils.get_pv(systemparams["user"], systemparams["dhe"], "R%i" % i, "dacvnsubout:VALUE:set") for i in dcds]:
        vnsubout_pv.put(value)
        print "-> setting %s to %i" % (vnsubout_pv.pvname, value)
    # pull JTAG write register triggers
    for regTrg_pv in [epics_utils.get_pv(systemparams["user"], systemparams["dhe"], "R%i" % i, "globalsr:trg:set") for i in dcds]:
        regTrg_pv.put(1)
        print "-> pulling %s" % regTrg_pv.pvname
        time.sleep(1)

def putGateOnVoltage(systemparams, value, gateon=0):
    gateons = [1, 2, 3] if gateon == 0 else [gateon]
    assert value in range(-2600, 0), "unreasonable gate-on voltage %s" % value
    for gateon_pv in [epics_utils.get_pv(systemparams["user"], systemparams["ps"], "gate-on%i:VOLT:req" % i) for i in gateons]:
        gateon_pv.put(value)
        print "-> setting %s to %i" % (gateon_pv.pvname, value)
        time.sleep(0.5)

def main(systemparams, measureparams):

    opt_gateon1, opt_gateon2, opt_gateon3, opt_dac1, opt_dac2, opt_dac3, opt_dac4 = (-1, -1, -1, -1, -1, -1, -1)

    if measureparams["optimize_dac"]:
        if measureparams["current_source"] == "vnsubin":
            putDAC = putVNSubIn
        elif measureparams["current_source"] == "vnsubout":
            putDAC = putVNSubOut
        else:
            raise IOError("unsupported current source %s" % measureparams["current_source"])

    if measureparams["optimize_gateon"]:
        # set all gate-on to target voltage
        putGateOnVoltage(systemparams, measureparams["gateon_target"], gateon=0)
        # optimal gate-on2 voltage is target voltage
        opt_gateon2 = measureparams["gateon_target"]

    if measureparams["optimize_dac"]:
        # find optimal DAC for DCD1 and gate-on2
        opt_dac1 = getOptimalDAC(systemparams, measureparams["dac_target"], dacrange=measureparams["dac_range"], step=measureparams["dac_step"], dcd=1, gateon=2, current_source=measureparams["current_source"])
        putDAC(systemparams, opt_dac1, dcd=1)

    if measureparams["optimize_gateon"]:
        opt_gateon3 = getOptimalGateOn(systemparams, measureparams["gateon_target"], gaterange=measureparams["gateon_range"], step=measureparams["gateon_step"], dcd=1, gateon=3)
        putGateOnVoltage(systemparams, opt_gateon3, gateon=3)

        opt_gateon1 = getOptimalGateOn(systemparams, measureparams["gateon_target"], gaterange=measureparams["gateon_range"], step=measureparams["gateon_step"], dcd=1, gateon=1)
        putGateOnVoltage(systemparams, opt_gateon1, gateon=1)

    if measureparams["optimize_dac"]:
        opt_dac2 = getOptimalDAC(systemparams, opt_dac1, dacrange=6, step=1, dcd=2, current_source=measureparams["current_source"])
        putDAC(systemparams, opt_dac2, dcd=2)
        opt_dac3 = getOptimalDAC(systemparams, opt_dac1, dacrange=6, step=1, dcd=3, current_source=measureparams["current_source"])
        putDAC(systemparams, opt_dac3, dcd=3)
        opt_dac4 = getOptimalDAC(systemparams, opt_dac1, dacrange=6, step=1, dcd=4, current_source=measureparams["current_source"])
        putDAC(systemparams, opt_dac4, dcd=4)

    with open("result.txt", "a") as fwriter:
        fwriter.write("%s,\t%s,\t%s,\t%s,\t%s,\t%s,\t%s,\t\n" % (opt_gateon1, opt_gateon2, opt_gateon3, opt_dac1, opt_dac2, opt_dac3, opt_dac4))


def return_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--config', default="measure.ini", help="configuration file (default: %(default)s)")
    return parser


def readConfigFile(filename):

    if not os.path.isfile(filename):
        raise IOError("%s is not a file" % filename)
    # read config file
    config = config_utils.read_config(filename)
    general_config = config_utils.read_general_config(filename, required_values={"dhe": str})
    # prepare parameters dictionaries
    systemparams = {}
    measureparams = {}
    # fill parameters dictionaries
    systemparams["dhe"] = general_config["dhe"]
    systemparams["ps"] = general_config["ps"] if "ps" in general_config else systemparams["dhe"].replace("H", "P")
    systemparams["user"] = general_config["user"] if "user" in general_config else "PXD"
    measureparams["optimize_gateon"] = config.getboolean("general", "optimize_gateon")
    if measureparams["optimize_gateon"]:
        measureparams["gateon_target"] = config.getint("gateon", "target")
        measureparams["gateon_range"] = config.getint("gateon", "range")
        measureparams["gateon_step"] = config.getint("gateon", "step")
    measureparams["optimize_dac"] = config.getboolean("general", "optimize_dac")
    if measureparams["optimize_dac"]:
        current_source = config.get("general", "current_source")
        measureparams["current_source"] = current_source
        measureparams["dac_target"] = config.getint(current_source, "target")
        measureparams["dac_range"] = config.getint(current_source, "range")
        measureparams["dac_step"] = config.getint(current_source, "step")
        measureparams["iterations"] = config.getint("general", "iterations", fallback=2)

    return systemparams, measureparams


if __name__ == "__main__":

    # get cli parameters
    args = return_parser().parse_args()

    systemparams, measureparams = readConfigFile(args.config)

    for i in range(measureparams["iterations"]):

        main(systemparams, measureparams)
