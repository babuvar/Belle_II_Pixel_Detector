
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

void analysis3()
{

int counter=0;


TFile *file = TFile::Open("../output_root_files/H50rawframe_data.root");
  TTree* tree = (TTree*)file->Get("tree");

//PXDRawAdc ADC;
UShort_t  sen[20];
//vector<10, unsigned char>  adc[20][20];
unsigned char  adc[21][21];


tree->SetBranchAddress("PXDRawAdcs.m_sensorID",sen);
tree->SetBranchAddress("PXDRawAdcs.m_adcs",adc);


  for(int i=0;i<1;i++) {

      tree->GetEntry(i);

for(int j=0;j<100;j++){
cout<<"adc[0]["<<j<<"] = "<<(int)adc[3][j]<<endl;
}
cout<<"---------------------------"<<endl;


}


/*
  for(int i=0;i<3;i++) 
    {
      tree->GetEntry(i);

for(int j=0;j<21;j++){
//cout<<"sen[j] = "<<(int)sen[j]<<endl;
cout<<"adc[j].at(2) = "<<(int)adc[j][0]<<endl;

   }
cout<<"-------"<<endl;
*/


//}//for




}//analysis3




