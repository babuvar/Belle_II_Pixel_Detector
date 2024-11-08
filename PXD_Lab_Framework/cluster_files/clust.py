import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as pl
import tables
import os





## add sensor region
#rows=768
#r_start=1; r_end=768
#r_start=250; r_end=550
#cloumns=256
c_start=1; c_end=256

#wafer= 'W03_IB_2017_12_04_002'
#wafer= 'W41_IF_2018_03_28_001'
#wafer = 'W44_IF_2018_03_20_001'
#wafer= 'W45_IB_2017_12_04_002'

#wafers=['W03_IB_2017_12_04_002', 'W41_IF_2018_03_28_001', 'W44_IF_2018_03_20_001', 'W45_IB_2017_12_04_002']; r_start=1; r_end=768
#wafers=['W03_IB_2017_12_04_002']; r_start=240; r_end=440
#wafers=['W41_IF_2018_03_28_001']; r_start=1; r_end=768
#wafers=['W44_IF_2018_03_20_001']; r_start=340; r_end=540
wafers=['W45_IB_2017_12_04_002']; r_start=300; r_end=500



for wafer in wafers:

    plot_dir=os.path.join('plots',wafer)
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)


    input_dir='/home/bonndaq_pc/tmp_hye/source_scan_opt/%s'%wafer

    names = {}
    for directory in os.listdir(input_dir):
        subdir =  os.path.join(input_dir,directory)
        if os.path.isdir(subdir):
            for filename in os.listdir(subdir):
                fullname = os.path.join(subdir,filename)
                names[directory] = fullname



    for name, fullname in names.items():
        clusterdata = tables.open_file(fullname, mode="r")
        ## get the hitmap and cluster charge data
        hitmap = clusterdata.root.hitmap[r_start-1 : r_end, c_start-1 : c_end]
        fig=pl.figure(figsize=(15,15))
        pl.imshow(hitmap, interpolation="none",vmin=0, vmax=np.percentile(hitmap, 95)); pl.colorbar(); pl.title('Hitmap')
        #pl.imshow(hitmap, interpolation="none", origin="lower", aspect="auto", vmin=0, vmax=np.percentile(hitmap, 95))
        fig.savefig("plots/%s/hitmap_%s.png" %(wafer,name))
        pl.close(fig)
        clusterdata.close()







