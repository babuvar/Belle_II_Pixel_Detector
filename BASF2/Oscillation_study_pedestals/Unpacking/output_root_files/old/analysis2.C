
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

void analysis2()
{


  TFile* file = TFile::Open("H30rawframe_data.root");

//ROOT::Experimental::
RDataFrame d("tree", file); // build a TDataFrame like you would build a TTreeReader
//auto h1 = d.Histo1D("PXDRawAdcs.m_sensorID");
//auto h2 = d.Histo1D("m_event");
//auto h3 = d.Histo1D("PXDRawAdcs.m_adcs");

//cout<<"Max is "<<d.Mean("m_event");
cout<<"col type is "<<d.GetColumnType("PXDRawAdcs.m_sensorID")<<endl;

//TCanvas* cnv = new TCanvas("cnv","cnv",1200,900) ; cnv->cd(); 
//h1->Draw(); cnv->SaveAs("plot1.png");
//h2->Draw(); cnv->SaveAs("plot2.png");
//h3->Draw(); cnv->SaveAs("plot3.png");


}//main

 





