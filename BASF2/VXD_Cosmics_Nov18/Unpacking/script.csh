#! /bin/tcsh -f

cd /home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/Unpacking


basf2 UnpackFromSeqroot.py -i /hsm/belle2/bdata/group/detector/VXD/commissioning/b4test_data/b4test.0004.00190.HLT5.$1.sroot -o /home/belle/varghese/DESY/BASF2/PXD/RawHit_RootFiles/PXDRawHit.run190.$1.root -l ERROR

