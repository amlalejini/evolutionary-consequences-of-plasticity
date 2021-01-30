# Reproducing the problem:

## Steps to reproduce

- Using an older, slightly modified version of Empirical on my [fork](git clone https://github.com/amlalejini/Empirical.git).
  - Here's the commit hash: `68d17bff67dde19472f7a0b9b4bdff1dc3e846f7`
- Modify the `GetMRCA` function in the systematics manager to let calls force a MRCA recalculation
  - Version I'm using is below.
- Build the version of avida in this repository (the Avida+Empirical mashup) in the avida/ directory
- Move the avida executable to bug-replication/
- Run avida with run command [below](#avida-run-command)
  - use `-set FORCE_MRCA_COMP` avida config to turn on/off forced MRCA recalculations every update
- Without forcing MRCA the phylodiversity file should report that the mrca is the root of the phylogeny:
  depth = 0. If you take a look at the phylogeny snapshot file (from Empirical) at update 1000,
  ancestor #276 should be the mrca.


## Changes to Systematics manager

Add option to force MRCA recalculation. Here's the modified `GetMRCA`.

```
  // Request a pointer to the Most-Recent Common Ancestor for the population.
  template <typename ORG, typename ORG_INFO, typename DATA_STRUCT>
  Ptr<typename Systematics<ORG, ORG_INFO, DATA_STRUCT>::taxon_t> Systematics<ORG, ORG_INFO, DATA_STRUCT>::GetMRCA(bool force) const {
    if ( (!mrca && num_roots == 1) || force) {  // Determine if we need to calculate the MRCA.
      // First, find a candidate among the living taxa.  Only taxa that have one offsrping
      // can be on the line-of-descent to the MRCA, so anything else is a good start point.
      // There must be at least one!  Stop as soon as we find a candidate.
      Ptr<taxon_t> candidate(nullptr);
      for (auto x : active_taxa) {
        if (x->GetNumOff() != 1) { candidate = x; break; }
      }

      // Now, trace the line of descent, updating the candidate as we go.
      Ptr<taxon_t> test_taxon = candidate->GetParent();
      while (test_taxon) {
        emp_assert(test_taxon->GetNumOff() >= 1);
        // If the test_taxon is dead, we only want to update candidate when we hit a new branch point
        // If test_taxon is still alive, though, we always need to update it
        if (test_taxon->GetNumOff() > 1 || test_taxon->GetNumOrgs() > 0) candidate = test_taxon;
        test_taxon = test_taxon->GetParent();
      }
      mrca = candidate;
    }
    return mrca;
  }
```


## Avida run command:

```
./avida -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set ENVIRONMENT_FILE environment.cfg -set EVENT_FILE events_env-chg_rate-u100_phase-two.cfg -set PHYLOGENY_SNAPSHOT_RES 1000 -set RANDOM_SEED 110462 -set REACTION_SENSORS_NEUTRAL 0.0 -set SYSTEMATICS_RES 100
```
