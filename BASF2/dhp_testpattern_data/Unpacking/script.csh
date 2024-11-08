#! /bin/tcsh -f

cd /home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/Unpacking


basf2 UnpackFromSeqroot.py -i /home/belle/varghese/DESY/BASF2/PXD/dhp_testpattern_data/Unpacking/debug.0006.01310.HLT$1.f00000.sroot  -o /home/belle/varghese/DESY/BASF2/PXD/dhp_testpattern_data/Unpacking/HLT$1.root -l ERROR

