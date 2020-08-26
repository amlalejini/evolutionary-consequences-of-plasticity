/*
 *  cWorld.h
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

#ifndef cWorld_h
#define cWorld_h

#include "avida/core/Types.h"
#include "avida/data/Types.h"
#include <functional>

#include "apto/rng.h"

#include "cAvidaConfig.h"
#include "cAvidaContext.h"
#include "avida/core/InstructionSequence.h"
#include "avida/core/Genome.h"

#include "Evolve/Systematics.h"
#include "Evolve/SystematicsAnalysis.h"
#include "Evolve/OEE.h"
#include "control/Signal.h"
#include "control/SignalControl.h"
#include "tools/memo_function.h"
#include "base/Ptr.h"
#include "base/vector.h"
#include "data/DataFile.h"

#include <array>
#include <cassert>

class cAnalyze;
class cAnalyzeGenotype;
class cEnvironment;
class cEventList;
class cHardwareManager;
class cMigrationMatrix;
class cOrganism;
class cPopulation;
class cMerit;
class cPopulationCell;
class cStats;
class cTestCPU;
class cUserFeedback;
template<class T> class tDataEntry;

struct Phenotype {
  int gestation_time = -1;
  int start_generation = -1;
  emp::vector<int> final_task_count;

  bool operator==(const Phenotype & other) const {
    return gestation_time == other.gestation_time && final_task_count == other.final_task_count; 
  }

  bool operator<(const Phenotype & other) const {
    return std::tie(gestation_time, final_task_count) < std::tie(other.gestation_time, other.final_task_count); 
  }

  bool operator!=(const Phenotype & other) const {
    return gestation_time != other.gestation_time || final_task_count != other.final_task_count; 
  }


  // bool operator<(Phenotype other) const {
  //   return merit < other.merit;// && gestation_time < other.gestation_time; //&& final_task_count < other.final_task_count; 
  // }


};

namespace std
{
    //from fredoverflow's answer to
    //http://stackoverflow.com/questions/8026890/c-how-to-insert-array-into-hash-set
    template <> struct hash<Avida::InstructionSequence>
    {
        typedef Avida::InstructionSequence argument_type;
        typedef unsigned int result_type;
        result_type operator()(argument_type const& genome) const
        {
            unsigned int total = 0;

            for (int i = 0; i < genome.GetSize(); i++) {
              total += (genome[i].GetOp() + 3) * i;
            }

            return total % 3203;
        }
    };

    //From http://stackoverflow.com/questions/20511347/a-good-hash-function-for-a-vector
    template <> struct hash<emp::vector<Avida::Instruction> >
    {
        std::size_t operator()(emp::vector<Avida::Instruction> const& vec) const {
          std::size_t seed = vec.size();
          for(std::size_t i=0; i < vec.size(); i++) {
            seed ^= vec[i].GetOp() + 0x9e3779b9 + (seed << 6) + (seed >> 2);
          }
          return seed;
        }
    };

    //From http://stackoverflow.com/questions/20511347/a-good-hash-function-for-a-vector
    template <> struct hash<Avida::Instruction>
    {
        std::size_t operator()(Avida::Instruction const& inst) const {
          std::hash<int> int_hash;
          return int_hash(inst.GetOp());
        }
    };

}

using namespace Avida;


class cWorld
{
protected:
  World* m_new_world;
  cString m_working_dir;

  cAnalyze* m_analyze;
  cAvidaConfig* m_conf;
  cAvidaContext* m_ctx;
  cEnvironment* m_env;
  cEventList* m_event_list;
  cHardwareManager* m_hw_mgr;
  Apto::SmartPtr<cPopulation, Apto::InternalRCObject> m_pop;
  Apto::SmartPtr<cStats, Apto::InternalRCObject> m_stats;
  cMigrationMatrix* m_mig_mat;
  WorldDriver* m_driver;

  HashPropertyMap props;

  Data::ManagerPtr m_data_mgr;

  Apto::RNG::AvidaRNG m_rng;

  bool m_test_on_div;     // flag derived from a collection of configuration settings
  bool m_test_sterilize;  // flag derived from a collection of configuration settings

  bool m_own_driver;      // specifies whether this world object should manage its driver object

  cWorld(cAvidaConfig* cfg, const cString& wd);


public:
  static cWorld* Initialize(cAvidaConfig* cfg, const cString& working_dir, World* new_world, cUserFeedback* feedback = NULL, const Apto::Map<Apto::String, Apto::String>* mappings = NULL);
  virtual ~cWorld();

  // Signals triggered by the world.
  emp::SignalControl control;  // Setup the world to control various signals.
  emp::Signal<void(int)> before_repro_sig;       // Trigger: Immediately prior to producing offspring
  emp::Signal<void(Avida::InstructionSequence)> offspring_ready_sig;  // Trigger: Offspring about to enter population
  emp::Signal<void(const Avida::InstructionSequence*)> inject_ready_sig;     // Trigger: New org about to be added to population
  emp::Signal<void(int)> org_placement_sig;      // Trigger: Organism has been added to population
  emp::Signal<void(int)> org_death_sig;      // Trigger: Organism has been added to population
  emp::Signal<void(int)> on_update_sig;          // Trigger: New update is starting.

  Avida::InstructionSequence non_const_seq;
  int next_cell_id = -1;
  emp::DataFile oee_file;
  emp::DataFile phylodiversity_file;
  emp::DataFile lineage_file;
  emp::DataFile dom_file;

  std::function<double(const Avida::InstructionSequence&)> fit_fun;
  std::function<std::string(const Avida::InstructionSequence&)> skel_fun;

  emp::SignalKey OnBeforeRepro(const std::function<void(int)> & fun) { return before_repro_sig.AddAction(fun); }
  emp::SignalKey OnOffspringReady(const std::function<void(Avida::InstructionSequence)> & fun) { return offspring_ready_sig.AddAction(fun); }
  emp::SignalKey OnOrgPlacement(const std::function<void(int)> & fun) { return org_placement_sig.AddAction(fun); }
  emp::SignalKey OnOrgDeath(const std::function<void(int)> & fun) { return org_death_sig.AddAction(fun); }
  emp::SignalKey OnUpdate(const std::function<void(int)> & fun) { return on_update_sig.AddAction(fun); }
  emp::SignalKey OnInjectReady(const std::function<void(const Avida::InstructionSequence*)> & fun) { return inject_ready_sig.AddAction(fun); }

  void SetDriver(WorldDriver* driver, bool take_ownership = false);

  const cString& GetWorkingDir() const { return m_working_dir; }

  // General Object Accessors
  cAnalyze& GetAnalyze();
  cAvidaConfig& GetConfig() { return *m_conf; }
  cAvidaContext& GetDefaultContext() { return *m_ctx; }
  cEnvironment& GetEnvironment() { return *m_env; }
  cHardwareManager& GetHardwareManager() { return *m_hw_mgr; }
  cMigrationMatrix& GetMigrationMatrix(){ return *m_mig_mat; };
  cPopulation& GetPopulation() { return *m_pop; }
  Apto::Random& GetRandom() { return m_rng; }
  cStats& GetStats() { return *m_stats; }
  WorldDriver& GetDriver() { return *m_driver; }
  World* GetNewWorld() { return m_new_world; }

  std::array<int, 9> tasks = {{0,0,0,0,0,0,0,0,0}};
  bool all_tasks = false;
  int latest_gen = -1; // Force time to go forward

  using systematics_t = emp::Systematics<Avida::InstructionSequence, Avida::InstructionSequence, emp::datastruct::mut_landscape_info<Phenotype>>;
  using taxon_t = emp::Taxon< Avida::InstructionSequence, emp::datastruct::mut_landscape_info<Phenotype>>;
  emp::Ptr<taxon_t> best_tax;

  std::function<void(emp::Ptr<taxon_t>)> eval_fun;
  const emp::vector<std::string> MUTATION_TYPES = {"substitution", "insertion", "deletion"};

  using mut_count_t = std::unordered_map<std::string, double>;
  mut_count_t last_mutation;

  emp::Ptr<systematics_t> systematics_manager;
  // // If there are multiple instruction ets this could be a problem
  emp::Ptr<emp::OEETracker<systematics_t, std::string, emp::SeenBloomFilter> > OEE_stats;
  Genome curr_genome;

  Data::ManagerPtr& GetDataManager() { return m_data_mgr; }

  Data::ProviderPtr GetStatsProvider(World*);
  Data::ArgumentedProviderPtr GetPopulationProvider(World*);

  // Config Dependent Modes
  bool GetTestOnDivide() const { return m_test_on_div; }
  bool GetTestSterilize() const { return m_test_sterilize; }

  // Convenience Accessors
  int GetNumResources();
  inline int GetVerbosity() { return m_conf->VERBOSITY.Get(); }
  inline void SetVerbosity(int v) { m_conf->VERBOSITY.Set(v); }

  void GetEvents(cAvidaContext& ctx);

	cEventList* GetEventsList() { return m_event_list; }

	//! Migrate this organism to a different world (does nothing here; see cMultiProcessWorld).
	virtual void MigrateOrganism(cOrganism* org, const cPopulationCell& cell, const cMerit& merit, int lineage);

	//! Returns true if an organism should be migrated to a different world.
	virtual bool TestForMigration() { return false; }

	//! Returns true if the given cell is on the boundary of the world, false otherwise.
	virtual bool IsWorldBoundary(const cPopulationCell& cell);

	//! Process post-update events.
	virtual void ProcessPostUpdate(cAvidaContext&);

	//! Returns true if this world allows early exits, e.g., when the population reaches 0.
	virtual bool AllowsEarlyExit() const { return true; }

	//! Calculate the size (in virtual CPU cycles) of the current update.
	virtual int CalculateUpdateSize();

protected:
  // Internal Methods
  bool setup(World* new_world, cUserFeedback* errors,  const Apto::Map<Apto::String, Apto::String>* mappings);

};

#endif
