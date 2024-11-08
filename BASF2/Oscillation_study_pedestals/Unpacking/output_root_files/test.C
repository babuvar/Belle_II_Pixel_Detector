
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

using namespace RooFit;
using namespace Belle2;
using namespace std;

void test()
{

int counter=0;

//  TChain* chain=new TChain("tree");
//  chain->Add("../output_root_files/H50rawframe_data.root");

TFile *file = TFile::Open("H50rawframe_data.root");
  TTree* tree = (TTree*)file->Get("tree");


//  Int_t nevt=(int)file->GetEntries();
//  Int_t nevt=(int)chain->GetEntries();

//unsigned shortadc(reader, "PXDRawAdcs.m_adcs

//unsigned short sensor;
//vector<UShort_t> sensor;
vector<VxdID> sensor;

  tree->SetBranchAddress("PXDRawAdcs.m_sensorID",&sensor);

//  for(int i=0;i<nevt;i++) 
  for(int i=0;i<3;i++) 
    {
      tree->GetEntry(i);
cout<<"sensor size = "<<sensor.size()<<endl;

}




}//test()








