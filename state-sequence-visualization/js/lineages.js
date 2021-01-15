var vis_config = {
  data_file_path: "../experiments/2021-01-12-evo-dynamics/analysis/data/lineage_sequences.csv",

  num_tasks: 6,
  tasks: ["not","nand","and","ornot","or","andnot"],

  lineage_states_div_id: "lineage-states",

  environment_sequence: {
    states: ["ENV-A", "ENV-B"],
    interval: 100
  },

  full_update_range: {min: null, max: null},

  data_filter: function(d) {
    return(!d.sensors && d.environment == "env-chg_rate-u100");
  }

};

var IsSliced = function() {
  return $("#slice-toggle").prop("checked");
}

var LineageStateSequenceDataAccessor = function(row) {
  // header information:
  // COPY_MUT_PROB,DISABLE_REACTION_SENSORS,ENVIRONMENT_FILE,EVENT_FILE,PHYLOGENY_SNAPSHOT_RES,RANDOM_SEED,REACTION_SENSORS_NEUTRAL,SYSTEMATICS_RES,chg_env,environment,genotype_seq_length,genotype_seq_unique_state_cnt,max_update,phase,phen_seq_by_geno_duration,phen_seq_by_geno_start,phen_seq_by_geno_state,phen_seq_by_phen_duration,phen_seq_by_phen_start,phen_seq_by_phen_state,phenotype_seq_length,phenotype_seq_unique_state_cnt
  // Extract relevant data.
  const environment = row.environment;
  const sensors = row.DISABLE_REACTION_SENSORS == "0";
  const replicate_id = row.RANDOM_SEED;
  const phen_seq_states = row.phen_seq_by_phen_state.split(",");
  const phen_seq_starts = row.phen_seq_by_phen_start.split(",");
  const phen_seq_durations = row.phen_seq_by_phen_duration.split(",");
  // Build a phenotype state sequence.
  var phen_seq = [];
  for (i = 0; i < phen_seq_states.length; i++) {
    var state = phen_seq_states[i];
    var env_a_profile = state.substring(0, vis_config.num_tasks);
    var env_b_profile = state.substring(vis_config.num_tasks, state.length);
    var env_a_tasks = new Set();
    var env_b_tasks = new Set();
    for (t = 0; t < vis_config.tasks.length; t++) {
      if (env_a_profile[t] == "1") {
        env_a_tasks.add(vis_config.tasks[t]);
      }
      if (env_b_profile[t] == "1") {
        env_b_tasks.add(vis_config.tasks[t]);
      }
    }
    phen_seq.push({
      state: state,
      env_a_profile: env_a_profile,
      env_b_profile: env_b_profile,
      env_a_tasks: env_a_tasks,
      env_b_tasks: env_b_tasks,
      duration: +phen_seq_durations[i],
      start: +phen_seq_starts[i]
    });
  }

  var max_update = phen_seq[phen_seq.length - 1].start + phen_seq[phen_seq.length - 1].duration;
  var min_update = phen_seq[0].start;

  // Update max time
  if (vis_config.full_update_range.max == null) {
    vis_config.full_update_range.max = max_update;
  } else if (vis_config.full_update_range.max < max_update) {
    vis_config.full_update_range.max = max_update;
  }

  // Update min time
  if (vis_config.full_update_range.min == null) {
    vis_config.full_update_range.min = min_update;
  } else if (vis_config.full_update_range.min > min_update) {
    vis_config.full_update_range.min = min_update;
  }

  // Return data entry
  return {
    environment: environment,
    sensors: sensors,
    replicate_id: replicate_id,
    phenotype_seq: phen_seq
  }

}

var BuildVisualization = function(data) {
  console.log("BuildVisualization!");
  // Filter data
  data = data.filter(vis_config.data_filter);
  console.log(data);
  // Setup the canvas
  var chart_area = d3.select("#"+vis_config.lineage_states_div_id);
  var frame = chart_area.append("svg").attr("class", "lineage-frame");
  var canvas = frame.append("g").attr("class", "lineage-canvas");

  // Call this function to redraw the lineage visualization on the page.
  var DrawVisualization = function() {
    console.log("DrawVisualization!");

    var display_full = !IsSliced();

    // Clear canvas.
    canvas.selectAll("g").remove();

    // Build environment sequence.

  }

  // TODO - disable inputs until after wiring things up!

  // Wire DrawVisualization up to slice toggle
  $("#slice-toggle").change(
    function() {
      DrawVisualization();
    }
  );

  // Wire DrawVisualization up window
  $(window).resize(
    function() {
      DrawVisualization();
    }
  );

  DrawVisualization();

}

var main = function() {
  d3.csv(vis_config.data_file_path, LineageStateSequenceDataAccessor)
    .then(BuildVisualization);

}

// Call main!
main();