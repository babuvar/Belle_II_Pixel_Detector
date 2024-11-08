import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os


c_start=1; c_end=256
r_start=1; r_end=768



#/Data/source_scan/2020_01_14_002/hv-60000_drift-3000_clear-off2000/data.h5


input_dir='/Data/source_scan/2020_01_14_002/'
files=[]
plot_dir='plots/'
for subdir in os.listdir(input_dir):
    fullname = os.path.join(input_dir,subdir,'data.h5')
    if os.path.exists(fullname):
        #print "fullname =",fullname 
        #print "plots/%s/hitmap_%s.png" %(date,subdir)
        clusterdata = tables.open_file(fullname, mode="r")
        #print clusterdata
        hitmap = clusterdata.root.full.hitmap[r_start-1 : r_end, c_start-1 : c_end]
        fig=pl.figure(figsize=(5,12))
        pl.imshow(hitmap, interpolation="none",vmin=0, vmax=np.percentile(hitmap, 95)); pl.colorbar(); pl.title('Hitmap : %s ' %subdir)
        fig.savefig('plots/hitmap_%s.png'%subdir)
        pl.close(fig)
        clusterdata.close()


