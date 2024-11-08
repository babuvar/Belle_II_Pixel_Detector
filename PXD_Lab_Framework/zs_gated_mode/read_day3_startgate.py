#!/usr/bin/env python

import file_utils
import numpy as np
import mapping
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import  pyplot as pl

# Day3
data_ids = ['03', '04']
#data_ids = ['04']

for data_id in data_ids:
    filename='/Data/runs/2019_06_05_0%s/data.dat'  %data_id #day3


    #data_all=file_utils.read_zs_file_dhc(filename, frames=10)
    data_all=file_utils.read_zs_file_dhc(filename)


    data_1032 = data_all['H1032']

    #start gate array
    start_gate_array=[]

    #Create the hitmap
    for frame in data_1032:
        hitmap = np.zeros((768, 256))
        #print frame.shape
        frame_pixel_info=frame[:,:2]
        #print frame_pixel_info
        frame_pixel_info_arr = np.array(frame_pixel_info)


        for hit in frame_pixel_info_arr:
            col=hit[0]
            row=hit[1]
            hitmap[row][col]= hitmap[row][col]+1

        #converting to geometrical mapping per frame
        mapFunc = mapping.mapper("pxd9", "ib", fill_value=255)
        mapped_hitmap = mapFunc.raw(hitmap)

        #Row-projection
        mapped_hitmap_row_proj=np.sum(mapped_hitmap, axis=1)
    
        #Create gate-wise hit projection
        gate_map=np.sum(mapped_hitmap_row_proj.reshape(-1, 4), axis=1)

        #find start and end of 0-hit rows
        z_start=[]
        z_end=[]

        for j in  range(len(gate_map)):
            gate = j+1
            if (gate!=1) and (gate!=192): #Ignore these two gates
                if gate_map[j]==0:
                    #if gate_map[j-1]!=0:
                        #z_start.append(gate)
                    if gate_map[(j+1)%192]!=0:
                        z_end.append(gate)

        if z_end:
            z_end_np=np.asarray(z_end)
            #print "z_end =", z_end
            start_gate=np.ndarray.max(z_end_np)
            #print "start_gate = ",start_gate
            start_gate_array.append(start_gate)

    #print "start_gate_array = ", start_gate_array
    start_gate_np=np.asarray(start_gate_array)
    
    #Plotting
    fig=pl.figure(figsize=(10,10))
    pl.hist(start_gate_np, range=[95,195], bins=100);
    pl.xlabel('Gate at which no-trigger-veto starts')
    #pl.hist(start_gate_np)
    name='plots_startgate/gate_start_%s' %data_id
    fig.savefig(name)







