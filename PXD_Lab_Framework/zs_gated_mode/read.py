#!/usr/bin/env python

import file_utils
import numpy as np
import mapping
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import  pyplot as pl

#day1: taken at standby for no-trg-offset and no-trg-length scan (2019_06_03)
#data_ids = ['03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '15', '16', '18', '19']

#day2: taken at peak for no-trg-offset, no-trg-length, gate-offset and gate-length scan (2019_06_04)
#data_ids = ['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27']

#Friday
data_ids = ['03', '04', '05', '06']

for data_id in data_ids:
    filename='/Data/runs/2019_06_07_0%s/data.dat' %data_id #Friday
    #filename='/Data/runs/2019_06_03_0%s/data.dat' %data_id #day1: taken at standby for no-trg-offset and no-trg-length scan (2019_06_03)
    #filename='/Data/runs/2019_06_04_0%s/data.dat' %data_id #day2: taken at peak for no-trg-offset, no-trg-length, gate-offset and gate-length scan (2019_06_04)
    

    hitmap = np.zeros((768, 256))
    

    data_all=file_utils.read_zs_file_dhc(filename, frames=10)
    #data_all=file_utils.read_zs_file_dhc(filename)


    data_1032 = data_all['H1032']

    #print data_1032

    #Create the hitmap
    for frame in data_1032:
        frame_pixel_info=frame[:,:2]
        #print frame_pixel_info
        frame_pixel_info_arr = np.array(frame_pixel_info)
        for hit in frame_pixel_info_arr:
            col=hit[0]
            row=hit[1]
            hitmap[row][col]= hitmap[row][col]+1
            
    

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



    
    #Plotting
    fig=pl.figure(figsize=(10,10))
    pl.subplot(121)
    title="Hitmap 1032"
    pl.imshow(mapped_hitmap); pl.colorbar(); pl.title(title)
    pl.xlabel('column')
    pl.ylabel('row')
    pl.gca().invert_yaxis()
    pl.subplot(122)        
    pl.plot(gate_map)
    pl.title('Projection onto gates')
    pl.xlabel('zero-start gates = %s, \n zero-end gates = %s' %(z_start,z_end))
    #savename='plots_day1/hitmap_1032_%s.png' %data_id
    #savename='plots_day2/hitmap_1032_%s.png' %data_id
    savename='plots_fri/hitmap_1032_%s.png' %data_id
    pl.savefig(savename)
    
    
    




