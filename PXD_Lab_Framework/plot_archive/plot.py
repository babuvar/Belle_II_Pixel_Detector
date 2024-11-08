#!/usr/bin/env python

import numpy as np
import epics_archiver
import datetime
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as pl


#belle2_archiver_address = '134.107.29.226'
#belle2_archiver_address = '172.22.16.73'
#data_retrieval_port = 80


from_date = '2019, 05, 15, 10, 0, 0'
to_date = '2017, 05, 16, 10, 0, 0'
from_date = datetime.datetime.strptime(from_date, "%Y, %m, %d, %H, %M, %S")
to_date = datetime.datetime.strptime(to_date, "%Y, %m, %d, %H, %M, %S")

#print from_date



# call an archiver instance and connect to it
archiver = epics_archiver.epics_archiver("%s:%s" % (belle2_archiver_address, data_retrieval_port))

#pv-list
pv_list =  [
        "PXD:P1021:sw-sub-load:VOLT:cur",
        "PXD:P1021:sw-dvdd-load:VOLT:cur"
        ]

# call the plotting function
epics_archiver.plot_archiver_data(archiver, pv_list, from_date, to_date, show_plot=False)




