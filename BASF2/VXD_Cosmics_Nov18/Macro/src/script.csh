#! /bin/tcsh -f

cd /home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/Macro/src


root -b  analysis_$1.C >  /home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/Macro/log/log_$1.txt

