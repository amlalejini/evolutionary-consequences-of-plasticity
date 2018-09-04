/*
 *  cWorld.cc
 *  Avida
 *
 *  Created by David on 10/18/05.
 *  Copyright 1999-2011 Michigan State University. All rights reserved.
 *
 *
 *  This file is part of Avida.
 *
 *  Avida is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
 *  as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
 *
 *  Avida is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public License along with Avida.
 *  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include "cWorld.h"

#include "avida/Avida.h"
#include "AvidaTools.h"

#include "avida/data/Manager.h"
#include "avida/environment/Manager.h"
#include "avida/output/Manager.h"
#include "avida/systematics/Arbiter.h"
#include "avida/systematics/Manager.h"

#include "avida/private/systematics/GenotypeArbiter.h"

#include "cAnalyze.h"
#include "cAnalyzeGenotype.h"
#include "cEnvironment.h"
#include "cEventList.h"
#include "cHardwareManager.h"
#include "cMigrationMatrix.h"
#include "cInstSet.h"
#include "cPopulation.h"
#include "cStats.h"
#include "cTestCPU.h"
#include "cUserFeedback.h"

#include <cassert>


using namespace AvidaTools;

cWorld::cWorld(cAvidaConfig* cfg, const cString& wd)
  : m_working_dir(wd), m_analyze(NULL), m_conf(cfg), m_ctx(NULL)
  , m_env(NULL), m_event_list(NULL), m_hw_mgr(NULL), m_pop(NULL), m_stats(NULL), m_mig_mat(NULL), m_driver(NULL), m_data_mgr(NULL)
  , m_own_driver(false), control(), before_repro_sig("before-repro", control)
  , offspring_ready_sig("offspring-ready", control), inject_ready_sig("inject-ready", control)
  , org_placement_sig("org-placement", control), on_update_sig("on-update", control)
  , org_death_sig("on-death", control), oee_file("oee.csv")
{

    fit_fun = [this](const Avida::InstructionSequence& seq){
       Avida::Genome gen(curr_genome.HardwareType(), curr_genome.Properties(), GeneticRepresentationPtr(new InstructionSequence(seq)));
      //  cAnalyzeGenotype genotype(this, gen);
      //  genotype.Recalculate(*m_ctx);
      cCPUTestInfo test_info;
      cTestCPU* test_cpu = GetHardwareManager().CreateTestCPU(*m_ctx);
      // test_info.UseManualInputs(curr_target_cell.GetInputs()); // Test using what the environment will be
      test_cpu->TestGenome(*m_ctx, test_info, gen);  // Use the true genome
      return test_info.GetGenotypeFitness();
   };
  
   // OnUpdate([](int update){std::cout << update << " it works!" << std::endl;});
}

cWorld* cWorld::Initialize(cAvidaConfig* cfg, const cString& working_dir, World* new_world, cUserFeedback* feedback, const Apto::Map<Apto::String, Apto::String>* mappings)
{
  cWorld* world = new cWorld(cfg, working_dir);
  if (!world->setup(new_world, feedback, mappings)) {
    delete world;
    world = NULL;
  }
  return world;
}

cWorld::~cWorld()
{
  // m_actlib is not owned by cWorld, DO NOT DELETE

  // These must be deleted first
  delete m_analyze; m_analyze = NULL;

  // Forcefully clean up population before classification manager
  m_pop = Apto::SmartPtr<cPopulation, Apto::InternalRCObject>();

  delete m_env; m_env = NULL;
  delete m_event_list; m_event_list = NULL;
  delete m_hw_mgr; m_hw_mgr = NULL;

  delete m_mig_mat;

  // Delete Last
  delete m_conf; m_conf = NULL;

  // cleanup driver object, if needed
  if (m_own_driver) { delete m_driver; m_driver = NULL; }

  delete m_ctx;
  delete m_new_world;
}


bool cWorld::setup(World* new_world, cUserFeedback* feedback, const Apto::Map<Apto::String, Apto::String>* defs)
{

  m_new_world = new_world;

  bool success = true;

  // Setup Random Number Generator
  m_rng.ResetSeed(m_conf->RANDOM_SEED.Get());
  m_ctx = new cAvidaContext(NULL, m_rng);

  // Initialize new API-based data structures here for now
  {
    // Data Manager
    m_data_mgr = Data::ManagerPtr(new Data::Manager);
    m_data_mgr->AttachTo(new_world);

    // Environment
    Environment::ManagerPtr(new Environment::Manager)->AttachTo(new_world);

    // Output Manager
    Apto::String opath = Apto::FileSystem::GetAbsolutePath(Apto::String(m_conf->DATA_DIR.Get()), Apto::String(m_working_dir));
    Output::ManagerPtr(new Output::Manager(opath))->AttachTo(new_world);
  }


  m_env = new cEnvironment(this);

  m_mig_mat = new cMigrationMatrix();


  // Initialize the default environment...
  // This must be after the HardwareManager in case REACTIONS that trigger instructions are used.
  if (!m_env->Load(m_conf->ENVIRONMENT_FILE.Get(), m_working_dir, *feedback, defs)) {
    success = false;
  }

  if(m_conf->DEMES_MIGRATION_METHOD.Get() == 4){
    bool count_parasites = false;
    bool count_offspring = false;
    if(m_conf->DEMES_PARASITE_MIGRATION_RATE.Get() > 0.0)
      count_parasites = true;
    if(m_conf->DEMES_MIGRATION_RATE.Get() > 0.0)
      count_offspring = true;

    if(!m_mig_mat->Load(m_conf->NUM_DEMES.AsString().AsInt(), m_conf->MIGRATION_FILE.Get(), m_working_dir,count_parasites,count_offspring,false,*feedback))
      success = false;
  }


  // Systematics
  Systematics::ManagerPtr systematics(new Systematics::Manager);
  systematics->AttachTo(new_world);
  systematics->RegisterArbiter(Systematics::ArbiterPtr(new Systematics::GenotypeArbiter(new_world, "genotype", m_conf->THRESHOLD.Get(), m_conf->DISABLE_GENOTYPE_CLASSIFICATION.Get())));


  // Setup Stats Object
  m_stats = Apto::SmartPtr<cStats, Apto::InternalRCObject>(new cStats(this));
  Data::Manager::Of(m_new_world)->AttachRecorder(m_stats);


  // Initialize the hardware manager, loading all of the instruction sets
  m_hw_mgr = new cHardwareManager(this);
  if (m_conf->INST_SET_LOAD_LEGACY.Get()) {
    if (!m_hw_mgr->ConvertLegacyInstSetFile(m_conf->INST_SET.Get(), m_conf->INSTSETS.Get(), feedback)) success = false;
  }
  if (!m_hw_mgr->LoadInstSets(feedback)) success = false;
  if (m_hw_mgr->GetNumInstSets() == 0) {
    if (feedback) {
      feedback->Error("no instruction sets defined");
      if (!m_conf->INST_SET_LOAD_LEGACY.Get() && m_conf->INST_SET.Get() != "" && m_conf->INST_SET.Get() != "-") {
        feedback->Notify("It looks like you are attempting to load a legacy format instruction set file.  Try setting INST_SET_LOAD_LEGACY to 1.");
      }
    }
    success = false;
  }
  
  // If there were errors loading at this point, it is perilous to try to go further (pop depends on an instruction set)
  if (!success) return success;

  // std::cout << "Number of instruction sets: " << m_hw_mgr->GetNumInstSets() << " " << m_hw_mgr->GetInstSet("heads_default").N std::endl;
  auto null_inst = m_hw_mgr->m_inst_sets[0]->ActivateNullInst();

  // @MRR CClade Tracking
//	if (m_conf->TRACK_CCLADES.Get() > 0)
//		m_class_mgr->LoadCCladeFounders(m_conf->TRACK_CCLADES_IDS.Get());

  const bool revert_fatal = m_conf->REVERT_FATAL.Get() > 0.0;
  const bool revert_neg = m_conf->REVERT_DETRIMENTAL.Get() > 0.0;
  const bool revert_neut = m_conf->REVERT_NEUTRAL.Get() > 0.0;
  const bool revert_pos = m_conf->REVERT_BENEFICIAL.Get() > 0.0;
  const bool revert_taskloss = m_conf->REVERT_TASKLOSS.Get() > 0.0;
  const bool revert_equals = m_conf->REVERT_EQUALS.Get() > 0.0;
  const bool sterilize_unstable = m_conf->STERILIZE_UNSTABLE.Get() > 0;
  m_test_on_div = (revert_fatal || revert_neg || revert_neut || revert_pos || revert_taskloss || revert_equals || sterilize_unstable);

  const bool sterilize_fatal = m_conf->STERILIZE_FATAL.Get() > 0.0;
  const bool sterilize_neg = m_conf->STERILIZE_DETRIMENTAL.Get() > 0.0;
  const bool sterilize_neut = m_conf->STERILIZE_NEUTRAL.Get() > 0.0;
  const bool sterilize_pos = m_conf->STERILIZE_BENEFICIAL.Get() > 0.0;
  const bool sterilize_taskloss = m_conf->STERILIZE_TASKLOSS.Get() > 0.0;
  m_test_sterilize = (sterilize_fatal || sterilize_neg || sterilize_neut || sterilize_pos || sterilize_taskloss);

  m_pop = Apto::SmartPtr<cPopulation, Apto::InternalRCObject>(new cPopulation(this));

  // Setup Event List
  m_event_list = new cEventList(this);
  if (!m_event_list->LoadEventFile(m_conf->EVENT_FILE.Get(), m_working_dir, *feedback, defs)) {
    if (feedback) feedback->Error("unable to load event file");
    success = false;
  }

  // std::cout << "startging setup" << std::endl;
  // lineageM.Setup(this);
  // std::cout << "lineage setup" << std::endl;
  //OEE_stats.Setup(this);
  // std::cout << "Stats set up" << std::endl;
  // std::cout << this->GetHardwareManager().GetNumInstSets() << std::endl;
  // std::cout << "test" << std::endl;

  // std::cout << "Got hardware manager" << std::endl;
  
  skel_fun = [this, null_inst](const Avida::InstructionSequence & seq){
    // std::cout << std::endl; for (auto inst : emp::Skeletonize(seq, null_inst, fit_fun.to_function())){std::cout << inst.AsString() << std::endl;}; std::cout << std::endl;
    return emp::Skeletonize(seq, null_inst, fit_fun.to_function());
  };

  systematics_manager.New(skel_fun);
  // systematics_manager->PrintStatus();
  OEE_stats.New(systematics_manager, [null_inst](emp::Ptr<emp::Taxon<emp::vector<Instruction>, emp::datastruct::no_data>> org){return org->GetInfo().size() - std::count(org->GetInfo().begin(), org->GetInfo().end(), null_inst);});
  OEE_stats->SetGenerationInterval(100);
  OEE_stats->SetResolution(100);

  OnBeforeRepro([this](int pos){
    // std::cout << "Next parent is: " << pos; 
    // if(systematics_manager->IsTaxonAt(pos)){
    //   std::cout << systematics_manager->GetTaxonAt(pos)->GetID();
    // } 
    systematics_manager->SetNextParent(pos);});
  OnOffspringReady([this](Avida::InstructionSequence seq){ systematics_manager->AddOrg(seq, next_cell_id, GetStats().GetUpdate(), false);});
  OnOrgDeath([this](int pos){ systematics_manager->RemoveOrgAfterRepro(pos);});
  OnUpdate([this](int ud){OEE_stats->Update(ud); oee_file.Update(ud);});

  std::function<int()> update_fun = [this](){return GetStats().GetUpdate();};

  oee_file.AddFun(update_fun, "update", "Update");
  oee_file.AddCurrent(*OEE_stats->GetDataNode("change"), "change", "change potential");
  oee_file.AddCurrent(*OEE_stats->GetDataNode("novelty"), "novelty", "novelty potential");
  oee_file.AddCurrent(*OEE_stats->GetDataNode("diversity"), "ecology", "ecology potential");
  oee_file.AddCurrent(*OEE_stats->GetDataNode("complexity"), "complexity", "complexity potential");
  oee_file.PrintHeaderKeys();
  oee_file.SetTimingRepeat(100);
  
  // std::cout << "Null set" << std::endl;
  //const char * inst_set_name = (const char*)is.GetInstSetName();
  //cHardwareManager::SetupPropertyMap(props, inst_set_name);
  //OEE_stats.SetDefaultFitnessFun(fit_fun);
  // std::cout << "initialized" << std::endl;

  return success;
}

Data::ProviderPtr cWorld::GetStatsProvider(World*) { return m_stats; }
Data::ArgumentedProviderPtr cWorld::GetPopulationProvider(World*) { return m_pop; }

void cWorld::ProcessPostUpdate(cAvidaContext&) {on_update_sig.Trigger(GetStats().GetUpdate()); }

cAnalyze& cWorld::GetAnalyze()
{
  if (m_analyze == NULL) m_analyze = new cAnalyze(this);
  return *m_analyze;
}

void cWorld::GetEvents(cAvidaContext& ctx)
{
  if (m_pop->GetSyncEvents() == true) {
    m_event_list->Sync();
    m_pop->SetSyncEvents(false);
  }
  m_event_list->Process(ctx);
}

int cWorld::GetNumResources()
{
  return m_env->GetResourceLib().GetSize();
}


void cWorld::SetDriver(WorldDriver* driver, bool take_ownership)
{
  // cleanup current driver, if needed
  if (m_own_driver) delete m_driver;
  if (m_ctx) delete m_ctx;
  m_ctx = new cAvidaContext(driver, m_rng);

  // store new driver information
  m_driver = driver;
  m_own_driver = take_ownership;
}

/*! Calculate the size (in virtual CPU cycles) of the current update.
 */
int cWorld::CalculateUpdateSize()
{
	return GetConfig().AVE_TIME_SLICE.Get() * GetPopulation().GetNumOrganisms();
}

void cWorld::MigrateOrganism(cOrganism* org, const cPopulationCell& cell, const cMerit& merit, int lineage)
{
  (void)org; (void)cell; (void)merit; (void)lineage;
}

bool cWorld::IsWorldBoundary(const cPopulationCell& cell) { (void)cell; return false; }
