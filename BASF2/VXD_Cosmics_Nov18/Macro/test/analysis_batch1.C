
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
//using namespace std;

void analysis_batch1()
{

int counter =0;
//Different sensors: For the third index, [0] for integrated charge and [1] for number of hits 
double integrated_charge_8480[769][251][2]={0};
double integrated_charge_8736[769][251][2]={0};

  TChain* chain=new TChain("tree");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00001.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00002.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00003.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00004.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00005.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00006.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00007.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00008.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00009.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00010.root");



  TTreeReader reader(chain);
   //Read the contents of PXDRawHits
   TTreeReaderArray<short> row(reader, "PXDRawHits.m_row");
   TTreeReaderArray<short> column(reader, "PXDRawHits.m_column");
   TTreeReaderArray<short> charge(reader, "PXDRawHits.m_charge");
   TTreeReaderArray<unsigned short>frame(reader, "PXDRawHits.m_frameNr");
//   TTreeReaderArray<VxdID>sensor(reader, "PXDRawHits.m_sensorID");
   TTreeReaderArray<unsigned short>sensor(reader, "PXDRawHits.m_sensorID");


while (reader.Next()) {//Looping over many events

counter++;


       for (int i=0;i<row.GetSize();i++) {//Looping over hits

if(sensor[i]==8480){
integrated_charge_8480[row[i]][column[i]][0]=integrated_charge_8480[row[i]][column[i]][0]+charge[i];
integrated_charge_8480[row[i]][column[i]][1]++;
}
if(sensor[i]==8736){
integrated_charge_8736[row[i]][column[i]][0]=integrated_charge_8736[row[i]][column[i]][0]+charge[i];
integrated_charge_8736[row[i]][column[i]][1]++;
}

       }//Looping over hits

//if(counter>=200)break;
//if(counter>=20000)break;

} // TTree entry / Looping over many events


int count=-1;

//Plotting

TGraph2D *hitmap_8480 = new TGraph2D();
   hitmap_8480->SetNpy(251);
   hitmap_8480->SetNpx(769);
TGraph2D *hitmap_8736 = new TGraph2D();
   hitmap_8736->SetNpy(251);
   hitmap_8736->SetNpx(769);

TGraph2D *chargemap_8480 = new TGraph2D();
   chargemap_8480->SetNpy(251);
   chargemap_8480->SetNpx(769);
TGraph2D *chargemap_8736 = new TGraph2D();
   chargemap_8736->SetNpy(251);
   chargemap_8736->SetNpx(769);




for(int i=0;i<=768;i++){//row
for(int j=0;j<=250;j++){//column
count++;


 hitmap_8480->SetPoint(count,(float)j,(float)i,integrated_charge_8480[i][j][1]);
 hitmap_8736->SetPoint(count,(float)j,(float)i,integrated_charge_8736[i][j][1]);

 chargemap_8480->SetPoint(count,(float)j,(float)i,integrated_charge_8480[i][j][0]);
 chargemap_8736->SetPoint(count,(float)j,(float)i,integrated_charge_8736[i][j][0]);


}}


 TFile *outFile = new TFile("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/Macro/output/outputHist.root","update");
 outFile->cd();
   hitmap_8480->Write("hitmap_8480"); 
   hitmap_8736->Write("hitmap_8736");

   chargemap_8480->Write("chargemap_8480"); 
   chargemap_8736->Write("chargemap_8736");

 outFile->Write();


//exit();

}























