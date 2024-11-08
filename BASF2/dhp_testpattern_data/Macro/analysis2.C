
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

//using namespace RooFit;
//using namespace Belle2;
using namespace ROOT;
using namespace std;

void analysis2()
{
//counters for number of fired pixels per event (one for each sensor)
int counter=0;

int num_8480, num_8736,num_8992,  num_9248,  num_9504,  num_9760,  num_10016,  num_10272,  num_8512,  num_8768, num_9024,  num_9280,  num_9536,  num_9792, num_10048,  num_10304,   num_17440,  num_17696,  num_17472,  num_17728;

//Histogram definitions
//Hit-maps
TH2F *hit_8480 = new TH2F("hit_8480","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8736 = new TH2F("hit_8736","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8992 = new TH2F("hit_8992","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9248 = new TH2F("hit_9248","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9504 = new TH2F("hit_9504","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9760 = new TH2F("hit_9760","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_10016 = new TH2F("hit_10016","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_10272 = new TH2F("hit_10272","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8512 = new TH2F("hit_8512","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8768 = new TH2F("hit_8768","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9024 = new TH2F("hit_9024","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9280 = new TH2F("hit_9280","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9536 = new TH2F("hit_9536","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9792 = new TH2F("hit_9792","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_10048 = new TH2F("hit_10048","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_10304 = new TH2F("hit_10304","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_17440 = new TH2F("hit_17440","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_17696 = new TH2F("hit_17696","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_17472 = new TH2F("hit_17472","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_17728 = new TH2F("hit_17728","",250,0.01,250.01,768,0.01,768.01);

TH1F *nfired_perEvt_8480 = new TH1F("nfired_perEvt_8480","",2900,0.01,2900.01);
TH1F *nfired_perEvt_8736 = new TH1F("nfired_perEvt_8736","",2900,0.01,2900.01);
TH1F *nfired_perEvt_8992 = new TH1F("nfired_perEvt_8992","",2900,0.01,2900.01);
TH1F *nfired_perEvt_9248 = new TH1F("nfired_perEvt_9248","",2900,0.01,2900.01);
TH1F *nfired_perEvt_9504 = new TH1F("nfired_perEvt_9504","",2900,0.01,2900.01);
TH1F *nfired_perEvt_9760 = new TH1F("nfired_perEvt_9760","",2900,0.01,2900.01);
TH1F *nfired_perEvt_10016= new TH1F("nfired_perEvt_10016","",2900,0.01,2900.01);
TH1F *nfired_perEvt_10272 = new TH1F("nfired_perEvt_10272","",2900,0.01,2900.01);
TH1F *nfired_perEvt_8512 = new TH1F("nfired_perEvt_8512","",2900,0.01,2900.01);
TH1F *nfired_perEvt_8768 = new TH1F("nfired_perEvt_8768","",2900,0.01,2900.01);
TH1F *nfired_perEvt_9024 = new TH1F("nfired_perEvt_9024","",2900,0.01,2900.01);
TH1F *nfired_perEvt_9280 = new TH1F("nfired_perEvt_9280","",2900,0.01,2900.01);
TH1F *nfired_perEvt_9536 = new TH1F("nfired_perEvt_9536","",2900,0.01,2900.01);
TH1F *nfired_perEvt_9792 = new TH1F("nfired_perEvt_9792","",2900,0.01,2900.01);
TH1F *nfired_perEvt_10048 = new TH1F("nfired_perEvt_10048","",2900,0.01,2900.01);
TH1F *nfired_perEvt_10304 = new TH1F("nfired_perEvt_10304","",2900,0.01,2900.01);
TH1F *nfired_perEvt_17440 = new TH1F("nfired_perEvt_17440","",2900,0.01,2900.01);
TH1F *nfired_perEvt_17696 = new TH1F("nfired_perEvt_17696","",2900,0.01,2900.01);
TH1F *nfired_perEvt_17472 = new TH1F("nfired_perEvt_17472","",2900,0.01,2900.01);
TH1F *nfired_perEvt_17728 = new TH1F("nfired_perEvt_17728","",2900,0.01,2900.01);


  TChain* chain=new TChain("tree");
//  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/dhp_testpattern_data/Root_files/HLT1.root");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/dhp_testpattern_data/Root_files/HLT2.root");
//  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/dhp_testpattern_data/Root_files/HLT3.root");



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

num_8480=0; num_8736=0; num_8992=0;  num_9248=0;  num_9504=0;  num_9760=0;  num_10016=0;  num_10272=0;  num_8512=0;  num_8768=0; num_9024=0;  num_9280=0;  num_9536=0;  num_9792=0; num_10048=0;  num_10304=0;   num_17440=0;  num_17696=0;  num_17472=0;  num_17728=0;


       for (int i=0;i<row.GetSize();i++) {//Looping over hits

//Case with unusual charge
if(charge[i]!=200){cout<<"event = "<<counter<<", sensor = "<<sensor[i]<<", pixel(r,c) = ("<<row[i]<<","<<column[i]<<"), charge = "<<charge[i]<<endl;}


if(sensor[i]==8480){ hit_8480->Fill(column[i],row[i]); num_8480++;}
else if(sensor[i]==8736){ hit_8736->Fill(column[i],row[i]); num_8736++;}
else if(sensor[i]==8992){ hit_8992->Fill(column[i],row[i]); num_8992++;}
else if(sensor[i]==9248){ hit_9248->Fill(column[i],row[i]); num_9248++;}
else if(sensor[i]==9504){ hit_9504->Fill(column[i],row[i]); num_9504++;}
else if(sensor[i]==9760){ hit_9760->Fill(column[i],row[i]); num_9760++;}
else if(sensor[i]==10016){ hit_10016->Fill(column[i],row[i]); num_10016++;}
else if(sensor[i]==10272){ hit_10272->Fill(column[i],row[i]); num_10272++;}
else if(sensor[i]==8512){ hit_8512->Fill(column[i],row[i]); num_8512++;}
else if(sensor[i]==8768){ hit_8768->Fill(column[i],row[i]); num_8768++;}
else if(sensor[i]==9024){ hit_9024->Fill(column[i],row[i]); num_9024++;}
else if(sensor[i]==9280){ hit_9280->Fill(column[i],row[i]); num_9280++;}
else if(sensor[i]==9536){ hit_9536->Fill(column[i],row[i]); num_9536++;}
else if(sensor[i]==9792){ hit_9792->Fill(column[i],row[i]); num_9792++;}
else if(sensor[i]==10048){ hit_10048->Fill(column[i],row[i]); num_10048++;}
else if(sensor[i]==10304){ hit_10304->Fill(column[i],row[i]); num_10304++;}
else if(sensor[i]==17440){ hit_17440->Fill(column[i],row[i]); num_17440++;}
else if(sensor[i]==17696){ hit_17696->Fill(column[i],row[i]); num_17696++;}
else if(sensor[i]==17472){ hit_17472->Fill(column[i],row[i]); num_17472++;}
else if(sensor[i]==17728){ hit_17728->Fill(column[i],row[i]); num_17728++;}

       }//Looping over hits

nfired_perEvt_8480->Fill(num_8480);
nfired_perEvt_8736->Fill(num_8736);
nfired_perEvt_8992->Fill(num_8992);
nfired_perEvt_9248->Fill(num_9248);
nfired_perEvt_9504->Fill(num_9504);
nfired_perEvt_9760->Fill(num_9760);
nfired_perEvt_10016->Fill(num_10016);
nfired_perEvt_10272->Fill(num_10272);
nfired_perEvt_8512->Fill(num_8512);
nfired_perEvt_8768->Fill(num_8768);
nfired_perEvt_9024->Fill(num_9024);
nfired_perEvt_9280->Fill(num_9280);
nfired_perEvt_9536->Fill(num_9536);
nfired_perEvt_9792->Fill(num_9792);
nfired_perEvt_10048->Fill(num_10048);
nfired_perEvt_10304->Fill(num_10304);
nfired_perEvt_17440->Fill(num_17440);
nfired_perEvt_17696->Fill(num_17696);
nfired_perEvt_17472->Fill(num_17472);
nfired_perEvt_17728->Fill(num_17728);

if(counter>=10000)break;


} // TTree entry / Looping over many events







 TFile *outFile = new TFile("/home/belle/varghese/DESY/BASF2/PXD/dhp_testpattern_data/Macro/Output/outputHist2.root","RECREATE");
 outFile->cd();

   hit_8480->Write("hit_8480");  nfired_perEvt_8480->Write("nfired_perEvt_8480");
   hit_8736->Write("hit_8736");  nfired_perEvt_8736->Write("nfired_perEvt_8736");
   hit_8992->Write("hit_8992");  nfired_perEvt_8992->Write("nfired_perEvt_8992");
   hit_9248->Write("hit_9248");  nfired_perEvt_9248->Write("nfired_perEvt_9248");
   hit_9504->Write("hit_9504");  nfired_perEvt_9504->Write("nfired_perEvt_9504");
   hit_9760->Write("hit_9760");  nfired_perEvt_9760->Write("nfired_perEvt_9760");
   hit_10016->Write("hit_10016");  nfired_perEvt_10016->Write("nfired_perEvt_10016");
   hit_10272->Write("hit_10272");  nfired_perEvt_10272->Write("nfired_perEvt_10272");
   hit_8512->Write("hit_8512");  nfired_perEvt_8512->Write("nfired_perEvt_8512");
   hit_8768->Write("hit_8768");  nfired_perEvt_8768->Write("nfired_perEvt_8768");
   hit_9024->Write("hit_9024");  nfired_perEvt_9024->Write("nfired_perEvt_9024");
   hit_9280->Write("hit_9280");  nfired_perEvt_9280->Write("nfired_perEvt_9280");
   hit_9536->Write("hit_9536");  nfired_perEvt_9536->Write("nfired_perEvt_9536");
   hit_9792->Write("hit_9792");  nfired_perEvt_9792->Write("nfired_perEvt_9792");
   hit_10048->Write("hit_10048");  nfired_perEvt_10048->Write("nfired_perEvt_10048");
   hit_10304->Write("hit_10304");  nfired_perEvt_10304->Write("nfired_perEvt_10304");
   hit_17440->Write("hit_17440");  nfired_perEvt_17440->Write("nfired_perEvt_17440");
   hit_17696->Write("hit_17696");  nfired_perEvt_17696->Write("nfired_perEvt_17696");
   hit_17472->Write("hit_17472");  nfired_perEvt_17472->Write("nfired_perEvt_17472");
   hit_17728->Write("hit_17728");  nfired_perEvt_17728->Write("nfired_perEvt_17728");

 outFile->Write();


//exit();

}























