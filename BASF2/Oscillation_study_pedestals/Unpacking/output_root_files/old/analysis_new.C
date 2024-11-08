#include "TMath.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TCanvas.h"
#include <vxd/dataobjects/VxdID.h>

using namespace Belle2;
using namespace std;

void analysis_new()
{

  TFile* infile = TFile::Open("H30rawframe_data.root");
  TTree* tree = (TTree*) infile->Get("tree");

int m_event;
vector<VxdID> sensor_id;


  TBranch *sensor = tree->GetBranch("PXDRawAdcs.m_sensorID");
  sensor->SetAddress(&sensor_id);

//  TBranch *event = tree->GetBranch("EventMetaData::m_event");
//  event->SetAddress(&m_event);



//for (Int_t i=0; i<nentries; i++) {
for (Int_t i=0; i<3; i++) {

    tree->GetEntry(i);
//    cout<<"event no is"<<m_event<<endl;
    cout<<"sensor-id is "<<sensor_id<<endl;


}//event loop



}
