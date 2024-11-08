#!/usr/bin/env python

"""
analysis_broken_drains.py
-------------------------

:author: Felix Mueller (Nov 24, 2017)

This script analysis the pedestals and masks all pixels which have a ADU value lower than 20. The mask is
written to a separate file as described below.


1) Adjust the VnSubIn or the gate voltages that most of the pixels are in the upper dynamic range of the DCD.
   The pixels which are not connected show a low ADU value, typically below 20.
   Be careful that you do not have pixels with ADU values below 20 which threshold voltage is shifted, e.g.,
   due to irradiation.

2) Therefore, use the normal measure.py script in this folder and record pedestals.

3) Run the analysis.py script

4) Run this script, a mask in the <basepath>/<module>/pedestal_mask/ folder will be created if not existing
   - broken_columns.npy will be created, this is a npy file consiting of a 2D-bool array with True for masking
     and False for not masking
   - readme.md where the path of the pedestal data which was used is stored


This numpy file is currently (Nov 24, 2017) used in offets_calibration but can be also used in other scripts.
"""

import log_utils
from argparse import ArgumentParser
import os
import sys
import configparser
import elog
import file_utils
import plots
from matplotlib import pyplot as pl
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import mapping
import cm_corr
import dhp_utils
from epics_utils import pvname
import config_utils

if __name__ == "__main__":

    # get inifile from command line argument (if not supplied: default=analysis.ini)
    parser = ArgumentParser(description='Analyse Pedestals and detect broken drains')
    parser.add_argument('-c', '--local_ini', dest='local_ini',
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis.ini"))
    parser.add_argument('--hot-drains', action='store_true', dest='hot_drains', default=False,
                        help='If this flag is set, the hot drains are masked, else the broken drains are masked.')
    parser.add_argument('-t', '--threshold', type=int, required=True, help='Set the threshold for the pixels to be masked. '
                        'If argument hot is specified: mask for hot pixels with values above threshold, else mask for '
                        'broken pixels with values below threshold')
    parser.add_argument('-n', '--no-elog', action='store_true', dest='noelog', default=False,
                        help='Option to disable the elog logging feature. In contrast to the \'-tmp\' flag, plots are '
                             'still saved at the location specified in the *.ini file and not in /tmp/.')
    args = parser.parse_args()

    threshold = args.threshold

    local_ini = args.local_ini.decode('utf-8')
    noelog = args.noelog
    elogcredentials = None

    # initialize logger and start the elog entry
    logger = log_utils.get_pxd_main_logger(application_name="pedestal/analysis_dead_columns", no_remote=True)

    # deal with elog credentials
    if not noelog:
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
            sys.exit(1)

    logger.info("Start of Pedestal analysis")

    # load required values from ini file
    config_ana = configparser.ConfigParser(delimiters='=')
    config_ana.optionxform = str
    config_ana.read(local_ini)

    # get path
    # if path is loaded from .latestpath do this with highest priority
    path = config_ana.get("general", "path")
    if path in [None, "", "newest", "latest"]:
        # determine directory of script and read .latestpath file
        latestpathfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".latestpath")
        with open(latestpathfile, "r") as f:
            path = f.read()

    # load measure.ini from data path!
    config_measure = configparser.ConfigParser(delimiters='=')
    config_measure.optionxform = str
    config_measure.read(os.path.join(path, "measure.ini"))

    # getting new dhc_objects
    dhc_objects = config_utils.get_setup_from_scan_config(os.path.join(path, "measure.ini"))

    # load values from measure.ini
    user = config_measure.get("general", "user")
    asicpair = config_measure.getint("general", "asicpair")  # this is either 0,1,2,3,4 where 0 means all!
    framenr = config_measure.getint("general", "framenr")
    mapping_style = config_ana.get("plots", "mapping")  # pxd9, hybrid5, electrical, matrix, device
    useDHC = config_measure.getboolean("general", "useDHC")

    # get some of the values from the dhc_objects
    for dhc in dhc_objects:
        for module in dhc.modules:
            device = module.device_type
            device_module = module.module_name
            module_type = module.module_flavor
            dhe = module.dhe
            if not noelog:
                try:
                    myelog = elog.elog(local_ini, type="Pedestal Broken Drains Analysis", dhe=dhe, dhc_objects=dhc_objects,
                                       username=credentials.getusername(),
                                       password=credentials.getpassword())
                except Exception as e:
                    logger.severe("elog.elog: " + repr(e))
                    raise e
            try:
                if useDHC:
                    filename = os.path.join(path, "%srawframe_data.dat" % dhc.name)
                else:
                    filename = os.path.join(path, "rawframe_data.dat")

                # device = config_measure.get("general", "device_config")  # pxd9 or hybrid5
                # device_module = config_measure.get("general", "device_module")  # W37_OF1, H5006, ....
                # module_type = config_measure.get("general", "module_type")  # if, of, ib, ob or none
                asicpairs = dhp_utils.getListOfAsicpairs(pvname(user, dhe), asicpair)  # this is always a list (can be one asic!)
                # acmc_status = [config_measure.get("general", "ACMC_DCD%i" % el) for el in asicpairs]
                # offset_status = [config_measure.get("general", "OFFSET_DHP%i" % el) for el in asicpairs]

                # load data
                data = file_utils.read_raw_file(filename, dhe, asicpair=asicpair, frames=framenr, use_header=True)[0]  # we want the first numpy array containing the actual pedestals

            except IOError as e:
                logger.warning("No data for DHE %s (DHC %s)" % (dhe, dhc.name))
                logger.warning("Error: %s" % repr(e))
                continue

            # calcualte the mean
            mean_data = np.mean(data, axis=2)

            # create path and filename for the mask
            path_mask = os.path.join(path, dhe, "pedestal_mask")
            if not os.path.exists(path_mask):
                os.makedirs(path_mask)
            filename_mask = os.path.join(path_mask, "broken_drains.npy")

            if not args.hot_drains:
                # analysis broken drains
                # we set everywhere a True where the ADU value is below the threshold
                mask = np.zeros(mean_data.shape, dtype=bool)
                mask = np.where(mean_data < threshold, True, False)

                logger.info("Save mask to %s" % filename_mask)
                np.save(filename_mask, mask)
                readme = os.path.join(path_mask, "readme.md")
                with open(readme, "w") as readmef:
                    readmef.write("created mask based on measurements from %s\n" % path)
                readmef.close()
            else:
                # analysis hot drains
                # we set everywhere a True where the ADU value is over the threshold
                mask_hot = np.zeros(mean_data.shape, dtype=bool)
                mask_hot = np.where(mean_data > threshold, True, False)

                # load the mask for the broken drains
                try:
                    mask_broken = np.load(filename_mask)
                    # create the total mask containing broken and hot drains
                    mask = np.logical_or(mask_hot, mask_broken)
                except IOError as e:
                    logger.warning("No broken_drains mask found: %s" % e)
                    mask = mask_hot

                # save the new mask containing boken and hot drains
                logger.info("Save mask to %s" % filename_mask)
                np.save(filename_mask, mask)
                readme = os.path.join(path_mask, "readme.md")
                with open(readme, "w") as readmef:
                    readmef.write("created mask based on measurements from %s\n" % path)
                readmef.close()

            if mapping_style == "device":
                mapping_style = device

            fig, axes = pl.subplots(1, 3, sharex=True, sharey=True, figsize=(11.69, 8.27))

            fig.suptitle("%s - %s" % (module.dhe, device_module))

            # plot pedestals mean
            plots.plot_occupancyXY(mean_data, axes[0], format=mapping_style, asicpair=0, device=None, module=device_module,
                                   module_type=module_type, title="Pedestals", titlesize=14, labelsize=14, legendsize=14,
                                   xlabelsize=14, ylabelsize=14, colorbarsize=14, xlabel_coords=None, ylabel_coords=None,
                                   colorbar=False, set_xlabel=True, set_ylabel=True, vmin=0, vmax=255, colorbartext="ADU",
                                   mask_electrical_col=None, pixel_mask=np.array([]), use_pixel_mask=False )

            # plot mask
            mask_to_plot = np.zeros(mask.shape)
            mask_to_plot = np.ma.array(mask_to_plot, mask=mask)
            plots.plot_occupancyXY(mask_to_plot, axes[1], format=mapping_style, asicpair=0, device=None, module=device_module,
                                   module_type=module_type, title="Mask (=white pixel)", titlesize=14, labelsize=14, legendsize=14,
                                   xlabelsize=14, ylabelsize=14, colorbarsize=14, xlabel_coords=None, ylabel_coords=None,
                                   colorbar=False, set_xlabel=True, set_ylabel=True, vmin=0, vmax=1, colorbartext="ADU",
                                   mask_electrical_col=None, pixel_mask=np.array([]), use_pixel_mask=False)

            # plot masked pedestals
            ped_masked = np.ma.array(mean_data, mask=mask)
            plots.plot_occupancyXY(ped_masked, axes[2], format=mapping_style, asicpair=0, device=None, module=device_module,
                                   module_type=module_type, title="Pedestals masked", titlesize=14, labelsize=14, legendsize=14,
                                   xlabelsize=14, ylabelsize=14, colorbarsize=14, xlabel_coords=None, ylabel_coords=None,
                                   colorbar=False, set_xlabel=True, set_ylabel=True, vmin=0, vmax=255, colorbartext="ADU",
                                   mask_electrical_col=None, pixel_mask=np.array([]), use_pixel_mask=False )

            pdf = PdfPages(os.path.join(path_mask, "broken_drains_mask.pdf"))
            pdf.savefig(fig)
            pdf.close()

            if not noelog:
                try:
                    if myelog is not None:
                        myelog.submitEntry(path=path)
                except Exception as e:
                    logger.warning("elog.submitEntry:" + repr(e))

    pl.show()
