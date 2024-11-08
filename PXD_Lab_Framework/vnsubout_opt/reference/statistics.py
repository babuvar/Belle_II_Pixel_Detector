'''
statistics.py

Returns some statistics for a list of pedestal scans regarding the number of pixels inside a defined valid dynamic range:

- creates ADU histogram for each pedestal scan in filelist
- fits gaussian to pedestal distribution for each scan
- saves fitted distribution as pdf in directory of respective scan
- defines ADU range that indicate valid pixels (limits given by user as arguments) and calculates number of valid&invalid pixels for each module
- creates histograms(combination of all modules) for 1) percentage of valid pixels on module, 2) amplitude of fit, 3) mu of fit, 4) sigma of fit

REQUIRED:
path to a .txt file that contains directories of all pedestal scans, that shall be included in analysis, e.g. :

'/home/pedestals/W01_IB_2018_03_01_003
/home/pedestals/W01_IB_2018_03_01_003'


The statistics plot and logfile will be saved in the same directory, where this .txt file is located

author: Benedikt Wach

'''



from argparse import ArgumentParser
import os
import configparser
import file_utils
import plots
from matplotlib import pyplot as plt
import numpy as np
import dhp_utils
from epics_utils import pvname
import datetime





parser = ArgumentParser()
parser.add_argument("filelist", help="path to .txt file, that contains paths to all modules to be analyzed",
                    type=str)
parser.add_argument("--lower_limit", "-ll", help="lower limit of ADU range that defines valid pixels; default is 5",
                    type=int, default=5)
parser.add_argument("--upper_limit", "-ul", help="upper limit of ADU range that defines valid pixels; default is 235",
                    type=int, default=235)
parser.add_argument("--min_percentage", "-mp", help="percentage of valid pixels on module, below which to display pedestal plot and mark in logfile; default is 98%",
                    type=int, default=98)
args = parser.parse_args()
filelist = args.filelist
lower_limit = args.lower_limit
upper_limit = args.upper_limit
min_percentage = args.min_percentage


directory = os.path.dirname(filelist)
filelist = open(filelist, 'r')

# initializing logfile 'statistics.txt'
logfile = open(os.path.join(directory, "statistics.txt"), 'w')
logfile.write('Logfile for statistics.py \nexecuted: ' + str(datetime.datetime.now()) + '\nValid range defined as (' + str(lower_limit) + ',' + str(upper_limit) + ')' +'\n-----------\n')

percentage_list = []
a_list = []
mu_list = []
sigma_list = []

# retrieving parameters from each pedestal scan
for line in filelist:
    path= line.strip()
    data=np.load(path+"/rawframe_data.npy")
    # get values from measure.ini
    config_measure = configparser.ConfigParser(delimiters='=')
    config_measure.optionxform = str
    config_measure.read(os.path.join(path, "measure.ini"))
    device = config_measure.get("general", "device_config")  # pxd9 or hybrid5
    module = config_measure.get("general", "device_module")  # W37_OF1, H5006, ....
    framenr = config_measure.getint("general", "framenr")

    mapping_style = device        # here: set manually, otherweise analysis.ini must be provided

    # get fit parameters and percentage of valid pixels
    param = plots.plot_statistics(data=data, device=mapping_style, module_name=module, path=path, lower_limit=lower_limit, upper_limit=upper_limit, min_percentage=min_percentage)

    percentage = param[6]
    a_norm = param[0]/framenr    # normalize fit amplitude to make it comparable among all pedestal scans
    mu = param[1]
    sigma = param[2]
    a_list.append(a_norm)
    mu_list.append(mu)
    sigma_list.append(sigma)
    percentage_list.append(percentage)

    logfile.write('file:\t'+ path +
    '\n\tfraction of pixels inside valid range: {0:.2f}'.format(percentage) + '%' +
    '\n\tno_below='+ str(param[3]) + ', no_in='+ str(param[4]) + ', no_above='+ str(param[5]) + 
    '\n\tfit: a_norm={0:.2f}'.format(a_norm) + ', mu={0:.2f}'.format(mu) + ', sigma={0:.2f}'.format(sigma) + '\n')
    if percentage < min_percentage:
        logfile.write('LESS THAN {0:.0f}% OF PIXELS IN RANGE! CONSIDER LOOKING AT "pedestals_fit_plot.pdf"! \n\n'.format(min_percentage))
    else:
        logfile.write('\n')

# create histograms for all four parameters

percentage_list = np.asarray(percentage_list)
a_list = np.asarray(a_list)
mu_list = np.asarray(mu_list)
sigma_list = np.asarray(sigma_list)

plt.figure(figsize=(11.69,8.27))

# percentage
axes_p = plt.subplot(221)
n_p, bins_p, patches_p = plt.hist(percentage_list, np.arange(0,101,0.5))
axes_p.set_title('distribution of pixels within valid range')
axes_p.set_xlabel('fraction of valid pixels in %')
axes_p.set_ylabel('number of modules')
axes_p.set_xlim(percentage_list.min()-5, percentage_list.max()+5)
axes_p.set_ylim(0, max(n_p)+1)
axes_p.minorticks_on()


# amplitude
axes_a = plt.subplot(222)
n_a, bins_a, patches_a = plt.hist(a_list, 100)
axes_a.set_title('distribution of fit amplitudes')
axes_a.set_xlabel('normalized fit amplitude')
axes_a.set_ylabel('number of modules')
axes_a.set_yticks(np.arange(100))
axes_a.set_xlim(a_list.min()-0.05*(a_list.max()-a_list.min()), a_list.max()+0.05*(a_list.max()-a_list.min()))
axes_a.set_ylim(0, max(n_a)+1)
axes_a.minorticks_on()
axes_a.ticklabel_format(style='sci', axis='x', scilimits=(-3,3))


# mu
axes_mu = plt.subplot(223)
n_mu, bins_mu, patches_mu = plt.hist(mu_list, 100)
axes_mu.set_title('distribution of fit mu')
axes_mu.set_xlabel('mu')
axes_mu.set_ylabel('number of modules')
axes_mu.set_yticks(np.arange(100))
axes_mu.set_xlim(mu_list.min()-0.05*(mu_list.max()-mu_list.min()), mu_list.max()+0.05*(mu_list.max()-mu_list.min()))
axes_mu.set_ylim(0, max(n_mu)+1)
axes_mu.minorticks_on()


# sigma
axes_s = plt.subplot(224)
n_s, bins_s, patches_s = plt.hist(sigma_list, np.arange(sigma_list.min(),sigma_list.max()+1,1))
axes_s.set_title('distribution of fit sigma')
axes_s.set_xlabel('sigma')
axes_s.set_ylabel('number of modules')
axes_s.set_yticks(np.arange(100))
axes_s.set_xlim(sigma_list.min()-0.05*(sigma_list.max()-sigma_list.min()), sigma_list.max()+0.05*(sigma_list.max()-sigma_list.min()))
axes_s.set_ylim(0, max(n_s)+1)
axes_s.minorticks_on()


plt.tight_layout()


#save the statistics figure as statistics.pdf 
plt.savefig(os.path.join(directory, 'statistics.pdf'))

#show all desired plots
plt.show()

logfile.close()
#filelist.close()
