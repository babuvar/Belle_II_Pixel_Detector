
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

void analysis_batch2()
{

int counter =0; float charge_sq;
int count_8480,count_8736,count_8992,count_9248,count_9504,count_9760,count_10016,count_10272,count_8512,count_8768,count_9024,count_9280,count_9536,count_9792,count_10048,count_10304,count_17440,count_17696,count_17472,count_17728;

//Different sensors: For the third index, [0] for integrated charge and [1] for number of hits 
TH2F *charge_8480 = new TH2F("charge_8480","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8480 = new TH2F("hit_8480","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_8736 = new TH2F("charge_8736","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8736 = new TH2F("hit_8736","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_8992 = new TH2F("charge_8992","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8992 = new TH2F("hit_8992","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_9248 = new TH2F("charge_9248","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9248 = new TH2F("hit_9248","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_9504 = new TH2F("charge_9504","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9504 = new TH2F("hit_9504","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_9760 = new TH2F("charge_9760","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9760 = new TH2F("hit_9760","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_10016 = new TH2F("charge_10016","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_10016 = new TH2F("hit_10016","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_10272 = new TH2F("charge_10272","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_10272 = new TH2F("hit_10272","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_8512 = new TH2F("charge_8512","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8512 = new TH2F("hit_8512","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_8768 = new TH2F("charge_8768","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_8768 = new TH2F("hit_8768","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_9024 = new TH2F("charge_9024","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9024 = new TH2F("hit_9024","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_9280 = new TH2F("charge_9280","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9280 = new TH2F("hit_9280","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_9536 = new TH2F("charge_9536","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9536 = new TH2F("hit_9536","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_9792 = new TH2F("charge_9792","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_9792 = new TH2F("hit_9792","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_10048 = new TH2F("charge_10048","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_10048 = new TH2F("hit_10048","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_10304 = new TH2F("charge_10304","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_10304 = new TH2F("hit_10304","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_17440 = new TH2F("charge_17440","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_17440 = new TH2F("hit_17440","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_17696 = new TH2F("charge_17696","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_17696 = new TH2F("hit_17696","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_17472 = new TH2F("charge_17472","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_17472 = new TH2F("hit_17472","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_17728 = new TH2F("charge_17728","",250,0.01,250.01,768,0.01,768.01);
TH2F *hit_17728 = new TH2F("hit_17728","",250,0.01,250.01,768,0.01,768.01);

TH2F *charge_sq_8480 = new TH2F("charge_sq_8480","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_8736 = new TH2F("charge_sq_8736","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_8992 = new TH2F("charge_sq_8992","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_9248 = new TH2F("charge_sq_9248","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_9504 = new TH2F("charge_sq_9504","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_9760 = new TH2F("charge_sq_9760","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_10016 = new TH2F("charge_sq_10016","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_10272 = new TH2F("charge_sq_10272","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_8512 = new TH2F("charge_sq_8512","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_8768 = new TH2F("charge_sq_8768","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_9024 = new TH2F("charge_sq_9024","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_9280 = new TH2F("charge_sq_9280","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_9536 = new TH2F("charge_sq_9536","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_9792 = new TH2F("charge_sq_9792","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_10048 = new TH2F("charge_sq_10048","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_10304 = new TH2F("charge_sq_10304","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_17440 = new TH2F("charge_sq_17440","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_17696 = new TH2F("charge_sq_17696","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_17472 = new TH2F("charge_sq_17472","",250,0.01,250.01,768,0.01,768.01);
TH2F *charge_sq_17728 = new TH2F("charge_sq_17728","",250,0.01,250.01,768,0.01,768.01);

TH1F *fired_pix_num_8480 = new TH1F("fired_pix_num_8480","",200000,0.01,200000.01);
TH1F *fired_pix_num_8736 = new TH1F("fired_pix_num_8736","",200000,0.01,200000.01);
TH1F *fired_pix_num_8992 = new TH1F("fired_pix_num_8992","",200000,0.01,200000.01);
TH1F *fired_pix_num_9248 = new TH1F("fired_pix_num_9248","",200000,0.01,200000.01);
TH1F *fired_pix_num_9504 = new TH1F("fired_pix_num_9504","",200000,0.01,200000.01);
TH1F *fired_pix_num_9760 = new TH1F("fired_pix_num_9760","",200000,0.01,200000.01);
TH1F *fired_pix_num_10016= new TH1F("fired_pix_num_10016","",200000,0.01,200000.01);
TH1F *fired_pix_num_10272 = new TH1F("fired_pix_num_10272","",200000,0.01,200000.01);
TH1F *fired_pix_num_8512 = new TH1F("fired_pix_num_8512","",200000,0.01,200000.01);
TH1F *fired_pix_num_8768 = new TH1F("fired_pix_num_8768","",200000,0.01,200000.01);
TH1F *fired_pix_num_9024 = new TH1F("fired_pix_num_9024","",200000,0.01,200000.01);
TH1F *fired_pix_num_9280 = new TH1F("fired_pix_num_9280","",200000,0.01,200000.01);
TH1F *fired_pix_num_9536 = new TH1F("fired_pix_num_9536","",200000,0.01,200000.01);
TH1F *fired_pix_num_9792 = new TH1F("fired_pix_num_9792","",200000,0.01,200000.01);
TH1F *fired_pix_num_10048 = new TH1F("fired_pix_num_10048","",200000,0.01,200000.01);
TH1F *fired_pix_num_10304 = new TH1F("fired_pix_num_10304","",200000,0.01,200000.01);
TH1F *fired_pix_num_17440 = new TH1F("fired_pix_num_17440","",200000,0.01,200000.01);
TH1F *fired_pix_num_17696 = new TH1F("fired_pix_num_17696","",200000,0.01,200000.01);
TH1F *fired_pix_num_17472 = new TH1F("fired_pix_num_17472","",200000,0.01,200000.01);
TH1F *fired_pix_num_17728 = new TH1F("fired_pix_num_17728","",200000,0.01,200000.01);



  TChain* chain=new TChain("tree");
  chain->Add("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/RawHit_RootFiles/PXDRawHit.run190.f00002.root");




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
//initialize sensor hits counter
count_8736=0;count_8992=0;count_9248=0;count_9504=0;count_9760=0;count_10016=0;count_10272=0;count_8512=0;count_8768=0;count_9024=0;count_9280=0;count_9536=0;count_9792=0;count_10048=0;count_10304=0;count_17440=0;count_17696=0;count_17472=0;count_17728=0;


       for (int i=0;i<row.GetSize();i++) {//Looping over hits
charge_sq=charge[i]*charge[i];

if(sensor[i]==8480){charge_8480->Fill(column[i],row[i],charge[i]); hit_8480->Fill(column[i],row[i]);
charge_sq_8480->Fill(column[i],row[i],charge_sq); count_8480++;}
if(sensor[i]==8736){charge_8736->Fill(column[i],row[i],charge[i]); hit_8736->Fill(column[i],row[i]);
charge_sq_8736->Fill(column[i],row[i],charge_sq); count_8736++;}
if(sensor[i]==8992){charge_8992->Fill(column[i],row[i],charge[i]); hit_8992->Fill(column[i],row[i]);
charge_sq_8992->Fill(column[i],row[i],charge_sq); count_8992++;}
if(sensor[i]==9248){charge_9248->Fill(column[i],row[i],charge[i]); hit_9248->Fill(column[i],row[i]);
charge_sq_9248->Fill(column[i],row[i],charge_sq); count_9248++;}
if(sensor[i]==9504){charge_9504->Fill(column[i],row[i],charge[i]); hit_9504->Fill(column[i],row[i]);
charge_sq_9504->Fill(column[i],row[i],charge_sq); count_9504++;}
if(sensor[i]==9760){charge_9760->Fill(column[i],row[i],charge[i]); hit_9760->Fill(column[i],row[i]);
charge_sq_9760->Fill(column[i],row[i],charge_sq); count_9760++;}
if(sensor[i]==10016){charge_10016->Fill(column[i],row[i],charge[i]); hit_10016->Fill(column[i],row[i]);
charge_sq_10016->Fill(column[i],row[i],charge_sq); count_10016++;}
if(sensor[i]==10272){charge_10272->Fill(column[i],row[i],charge[i]); hit_10272->Fill(column[i],row[i]);
charge_sq_10272->Fill(column[i],row[i],charge_sq); count_10272++;}
if(sensor[i]==8512){charge_8512->Fill(column[i],row[i],charge[i]); hit_8512->Fill(column[i],row[i]);
charge_sq_8512->Fill(column[i],row[i],charge_sq); count_8512++;}
if(sensor[i]==8768){charge_8768->Fill(column[i],row[i],charge[i]); hit_8768->Fill(column[i],row[i]);
charge_sq_8768->Fill(column[i],row[i],charge_sq); count_8768++;}
if(sensor[i]==9024){charge_9024->Fill(column[i],row[i],charge[i]); hit_9024->Fill(column[i],row[i]);
charge_sq_9024->Fill(column[i],row[i],charge_sq); count_9024++;}
if(sensor[i]==9280){charge_9280->Fill(column[i],row[i],charge[i]); hit_9280->Fill(column[i],row[i]);
charge_sq_9280->Fill(column[i],row[i],charge_sq); count_9280++;}
if(sensor[i]==9536){charge_9536->Fill(column[i],row[i],charge[i]); hit_9536->Fill(column[i],row[i]);
charge_sq_9536->Fill(column[i],row[i],charge_sq); count_9536++;}
if(sensor[i]==9792){charge_9792->Fill(column[i],row[i],charge[i]); hit_9792->Fill(column[i],row[i]);
charge_sq_9792->Fill(column[i],row[i],charge_sq); count_9792++;}
if(sensor[i]==10048){charge_10048->Fill(column[i],row[i],charge[i]); hit_10048->Fill(column[i],row[i]);
charge_sq_10048->Fill(column[i],row[i],charge_sq); count_10048++;}
if(sensor[i]==10304){charge_10304->Fill(column[i],row[i],charge[i]); hit_10304->Fill(column[i],row[i]);
charge_sq_10304->Fill(column[i],row[i],charge_sq); count_10304++;}
if(sensor[i]==17440){charge_17440->Fill(column[i],row[i],charge[i]); hit_17440->Fill(column[i],row[i]);
charge_sq_17440->Fill(column[i],row[i],charge_sq); count_17440++;}
if(sensor[i]==17696){charge_17696->Fill(column[i],row[i],charge[i]); hit_17696->Fill(column[i],row[i]);
charge_sq_17696->Fill(column[i],row[i],charge_sq); count_17696++;}
if(sensor[i]==17472){charge_17472->Fill(column[i],row[i],charge[i]); hit_17472->Fill(column[i],row[i]);
charge_sq_17472->Fill(column[i],row[i],charge_sq); count_17472++;}
if(sensor[i]==17728){charge_17728->Fill(column[i],row[i],charge[i]); hit_17728->Fill(column[i],row[i]);
charge_sq_17728->Fill(column[i],row[i],charge_sq); count_17728++;}

       }//Looping over hits

//Fill event occ. info
fired_pix_num_8480->Fill(count_8480);
fired_pix_num_8736->Fill(count_8736);
fired_pix_num_8992->Fill(count_8992);
fired_pix_num_9248->Fill(count_9248);
fired_pix_num_9504->Fill(count_9504);
fired_pix_num_9760->Fill(count_9760);
fired_pix_num_10016->Fill(count_10016);
fired_pix_num_10272->Fill(count_10272);
fired_pix_num_8512->Fill(count_8512);
fired_pix_num_8768->Fill(count_8768);
fired_pix_num_9024->Fill(count_9024);
fired_pix_num_9280->Fill(count_9280);
fired_pix_num_9536->Fill(count_9536);
fired_pix_num_9792->Fill(count_9792);
fired_pix_num_10048->Fill(count_10048);
fired_pix_num_10304->Fill(count_10304);
fired_pix_num_17440->Fill(count_17440);
fired_pix_num_17696->Fill(count_17696);
fired_pix_num_17472->Fill(count_17472);
fired_pix_num_17728->Fill(count_17728);



//if(counter>=200)break;
//if(counter>=20000)break;

} // TTree entry / Looping over many events



 TFile *outFile = new TFile("/home/belle/varghese/DESY/BASF2/PXD/VXD_Cosmics_Nov18/Macro/output/outputHist_run190_f00002.root","update");
 outFile->cd();
   hit_8480->Write("hit_8480"); charge_8480->Write("charge_8480"); charge_sq_8480->Write("charge_sq_8480");
   hit_8736->Write("hit_8736"); charge_8736->Write("charge_8736");  charge_sq_8736->Write("charge_sq_8736");
   hit_8992->Write("hit_8992"); charge_8992->Write("charge_8992"); charge_sq_8992->Write("charge_sq_8992");
   hit_9248->Write("hit_9248"); charge_9248->Write("charge_9248"); charge_sq_9248->Write("charge_sq_9248");
   hit_9504->Write("hit_9504"); charge_9504->Write("charge_9504"); charge_sq_9504->Write("charge_sq_9504");
   hit_9760->Write("hit_9760"); charge_9760->Write("charge_9760"); charge_sq_9760->Write("charge_sq_9760");
   hit_10016->Write("hit_10016"); charge_10016->Write("charge_10016"); charge_sq_10016->Write("charge_sq_10016");
   hit_10272->Write("hit_10272"); charge_10272->Write("charge_10272"); charge_sq_10272->Write("charge_sq_10272");
   hit_8512->Write("hit_8512"); charge_8512->Write("charge_8512"); charge_sq_8512->Write("charge_sq_8512");
   hit_8768->Write("hit_8768"); charge_8768->Write("charge_8768"); charge_sq_8768->Write("charge_sq_8768");
   hit_9024->Write("hit_9024"); charge_9024->Write("charge_9024"); charge_sq_9024->Write("charge_sq_9024");
   hit_9280->Write("hit_9280"); charge_9280->Write("charge_9280"); charge_sq_9280->Write("charge_sq_9280");
   hit_9536->Write("hit_9536"); charge_9536->Write("charge_9536"); charge_sq_9536->Write("charge_sq_9536");
   hit_9792->Write("hit_9792"); charge_9792->Write("charge_9792"); charge_sq_9792->Write("charge_sq_9792");
   hit_10048->Write("hit_10048"); charge_10048->Write("charge_10048"); charge_sq_10048->Write("charge_sq_10048");
   hit_10304->Write("hit_10304"); charge_10304->Write("charge_10304"); charge_sq_10304->Write("charge_sq_10304");
   hit_17440->Write("hit_17440"); charge_17440->Write("charge_17440"); charge_sq_17440->Write("charge_sq_17440");
   hit_17696->Write("hit_17696"); charge_17696->Write("charge_17696"); charge_sq_17696->Write("charge_sq_17696");
   hit_17472->Write("hit_17472"); charge_17472->Write("charge_17472"); charge_sq_17472->Write("charge_sq_17472");
   hit_17728->Write("hit_17728"); charge_17728->Write("charge_17728"); charge_sq_17728->Write("charge_sq_17728");

fired_pix_num_8480->Write("fired_pix_num_8480");
fired_pix_num_8736->Write("fired_pix_num_8736");
fired_pix_num_8992->Write("fired_pix_num_8992");
fired_pix_num_9248->Write("fired_pix_num_9248");
fired_pix_num_9504->Write("fired_pix_num_9504");
fired_pix_num_9760->Write("fired_pix_num_9760");
fired_pix_num_10016->Write("fired_pix_num_10016");
fired_pix_num_10272->Write("fired_pix_num_10272");
fired_pix_num_8512->Write("fired_pix_num_8512");
fired_pix_num_8768->Write("fired_pix_num_8768");
fired_pix_num_9024->Write("fired_pix_num_9024");
fired_pix_num_9280->Write("fired_pix_num_9280");
fired_pix_num_9536->Write("fired_pix_num_9536");
fired_pix_num_9792->Write("fired_pix_num_9792");
fired_pix_num_10048->Write("fired_pix_num_10048");
fired_pix_num_10304->Write("fired_pix_num_10304");
fired_pix_num_17440->Write("fired_pix_num_17440");
fired_pix_num_17696->Write("fired_pix_num_17696");
fired_pix_num_17472->Write("fired_pix_num_17472");
fired_pix_num_17728->Write("fired_pix_num_17728");
 

 outFile->Write();


//exit();

}























