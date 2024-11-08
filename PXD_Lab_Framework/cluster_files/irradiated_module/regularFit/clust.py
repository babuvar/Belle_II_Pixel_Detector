import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os


c_start=1; c_end=256
r_start=1; r_end=768





dates=['2018_10_25_007', '2019_03_21_002']

for date in dates:
    input_dir='/home/bonndaq_pc/tmp_varghese/W05_OB1/source_scan/%s'%date
    files=[]
    plot_dir='plots/%s'%date
    for subdir in os.listdir(input_dir):
        fullname = os.path.join(input_dir,subdir,'data.h5')
        #print "fullname =",fullname 
        #print "plots/%s/hitmap_%s.png" %(date,subdir)
        clusterdata = tables.open_file(fullname, mode="r")
        #print clusterdata
        hitmap = clusterdata.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
        fig=pl.figure(figsize=(5,12))
        pl.imshow(hitmap, interpolation="none",vmin=0, vmax=np.percentile(hitmap, 95)); pl.colorbar(); pl.title('Hitmap : %s ' %subdir)
        fig.savefig('plots/%s/hitmap_%s.png'%(date,subdir))
        pl.close(fig)
        clusterdata.close()



