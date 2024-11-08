
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


void analysis4()
{

int counter=0;

   TFile *f = new TFile("H50rawframe_data.root");
   TTree *tree = (TTree*)f->Get("tree");
   
   TBranch *sen = tree->GetBranch("PXDRawAdcs.m_sensorID");
   TBranch *adc = tree->GetBranch("PXDRawAdcs.m_adcs");

//   TLeaf *run = tree->GetBranch("EventMetaData");
//   TLeaf *run = tree->GetBranch("EventMetaData.m_run");




cout<<"sen->GetBasketSize() = "<<sen->GetBasketSize()<<endl;
cout<<"adc->GetBasketSize() = "<<adc->GetBasketSize()<<endl;

cout<<"sen->GetTotalSize() = "<<sen->GetTotalSize()<<endl;
cout<<"adc->GetTotalSize() = "<<adc->GetTotalSize()<<endl;




//cout<<"sen->GetBasketBytes() = "<<sen->GetBasketBytes()<<endl;
//cout<<"sen->GetEntry() = "<<sen->GetEntry()<<endl;

//cout<<"tree->GetBasketBytes() = "<<tree->GetEntry(2)<<endl;

//sen->AddLastBasket(20);


//sen->Fill();

//cout<<"sen->GetBasketBytes() = "<<(int)*(unsigned char*)sen->GetBasketBytes()<<endl;
//cout<<"adc->GetBasketBytes() = "<<(int)*(unsigned char*)adc->GetBasketBytes()<<endl;





//cout<<"adc->GetEntry() = "<<adc->GetEntry()<<endl;




}//main

 





