
#ifndef __CINT__
#include "RooGlobalFunc.h"
#endif
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooGaussian.h"
#include "RooConstVar.h"
#include "RooChebychev.h"
#include "RooAddPdf.h"
#include "RooSimultaneous.h"
#include "RooCategory.h"
#include "TCanvas.h"
#include "TAxis.h"
#include "RooPlot.h"

#include <TFile.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>

 #include <vector>
 #include <iostream>

using namespace ROOT;
using namespace Belle2;
using namespace std;

/*
 bool CheckValue(TTreeReaderValueBase& value) {
    if (value->GetSetupStatus() < 0) {
       std::cerr << "Error " << value->GetSetupStatus()
                 << "setting up reader for " << value->GetBranchName() << '\n';
       return false;
    }
    return true;
 }
*/


void analysis()
{

int counter=0;

  TChain* chain=new TChain("tree");
//  chain->Add("../output_root_files/H50rawframe_data.root");
  chain->Add("H50rawframe_data.root");


  TTreeReader reader(chain);
   //Read the contents of PXDRawHits


TTreeReaderArray<vector<unsigned char>>ADC(reader, "PXDRawAdcs.m_adcs");
//TTreeReaderArray<unsigned char>ADC(reader, "PXDRawAdcs.m_adcs");


   TTreeReaderArray<unsigned short>sensor(reader, "PXDRawAdcs.m_sensorID");



while (reader.Next()) {//Looping over many events
counter++;

cout<<"done"<<endl;

cout<<"sensor["<<1<<"] id is "<<sensor[1]<<endl;
cout<<"sensor*["<<1<<"] id is "<<&sensor[1]<<endl;
//cout<<"sensor["<<1<<"] id is "<<*(unsigned short*)&sensor[1]<<endl;
//cout<<"sensor["<<1<<"] id is "<<*(unsigned short*)0x42440bc<<endl;

vector<unsigned char*>adc_tmp=ADC[0];



//cout<<"ADC["<<1<<"] id is "<<ADC[1]<<endl;




/*
for(int i=0;i<20;i++){
cout<<"sensor["<<i<<"] id is "<<sensor[i]<<endl;

cout<<"sensor.GetSize() = "<<sensor.GetSize()<<endl;
//cout<<"ADC.GetSize() = "<<ADC[0].size()<<endl;

//for (vector<unsigned char>::iterator it = ADC[0].begin() ; it != ADC[0].end(); ++it){    cout << ' ' << *it; }
cout<<"done-1"<<endl;
vector<unsigned char>::iterator it = ADC[0].begin() ;
cout<<"done-2"<<endl;
cout << ' ' << *it; 
cout<<"done-3"<<endl;
}
*/

cout<<"-----------------"<<endl;

if(counter>=2)break;
}



/*
cout<<"done"<<endl;

while (reader.Next()) {//Looping over many events
counter++;
cout<<"size of 'sensor' array = "<<sensor.GetSize()<<endl;
cout<<"sensor[1] = "<<sensor[1]<<endl;
cout<<"size of 'adc' array = "<<adc.GetSize()<<endl;
*/

//vector<unsigned char>adc_tmp=ADC[0];

/*

//cout<<"adc[1] = "<<adc[1]<<endl;


//cout<<"adc[0][0] = "<<adc[1][1]<<endl;
if(counter>=2)break;
}
*/

}//main

 





