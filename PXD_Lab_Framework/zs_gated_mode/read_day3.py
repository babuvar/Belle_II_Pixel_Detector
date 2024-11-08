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
    

    hitmap = np.zeros((768, 256))
    

    #data_all=file_utils.read_zs_file_dhc(filename, frames=10)
    data_all=file_utils.read_zs_file_dhc(filename)


    data_1032 = data_all['H1032']

    #print data_1032

    #Frame-size array
    frame_size=[]
    
    count = 0
    count_p = 0

    #Create the hitmap
    for frame in data_1032:
        #print frame.shape
        frame_pixel_info=frame[:,:2]
        #print frame_pixel_info
        frame_pixel_info_arr = np.array(frame_pixel_info)
        frame_size.append(frame_pixel_info_arr.shape[0])
        if frame_pixel_info_arr.shape[0] > 1400:
            count = count + 1
        else:
            count_p = count_p + 1

    print "count = ",count
    print "count_p = ",count_p




    #print "frame sizes = ", frame_size
    ''' 
        for hit in frame_pixel_info_arr:
            col=hit[0]
            row=hit[1]
            hitmap[row][col]= hitmap[row][col]+1
    '''


    '''
    
    #converting to geometrical mapping
    mapFunc = mapping.mapper("pxd9", "ib", fill_value=255)
    mapped_hitmap = mapFunc.raw(hitmap)

    #Row-projection
    mapped_hitmap_row_proj=np.sum(mapped_hitmap, axis=1)
    
    #Create gate-wise hit projection
    gate_map=np.sum(mapped_hitmap_row_proj.reshape(-1, 4), axis=1)

    #sanity-check
    #print mapped_hitmap.shape
    #print mapped_hitmap_row_proj.shape

    #find start and end of 0-hit rows
    z_start=[]
    z_end=[]

    for j in  range(len(gate_map)):
        gate = j+1
        if (gate!=1) and (gate!=192): #Ignore these two gates
            if gate_map[j]==0:
                if gate_map[j-1]!=0:
                    z_start.append(gate)
                if gate_map[(j+1)%192]!=0:
                    z_end.append(gate)


    #print "zero start gates = %s" %z_start
    #print "zero end gates = %s" %z_end



    '''
    #Plotting
    fig=pl.figure(figsize=(10,10))
    pl.plot(frame_size);
    pl.xlabel('Frame number')
    savename='plots_day3/hitmap_1032_%s.png' %data_id
    pl.savefig(savename)
    
    
    




