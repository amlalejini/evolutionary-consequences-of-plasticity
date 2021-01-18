var vis_config = {
  data_file_path: "../experiments/2021-01-12-evo-dynamics/analysis/data/lineage_sequences.csv",

  num_tasks: 6,
  tasks: ["not","nand","and","ornot","or","andnot"],

  lineage_states_div_id: "lineage-states",

  margin: {top: 20, right: 40, bottom: 20, left: 100},
  tick_height:0.2,                                    // Vertical height of each 'update'.
  max_seq_width: 20,
  max_seq_hspacer: 3,
  slice_vspacer: 30,

  env_seq_width: 10,
  env_seq_hspacer: 5,

  time_tick_interval: 500,

  environment_sequence: {
    states: ["ENV-A", "ENV-B"],
    interval: 100
  },

  full_update_range: {min: null, max: null},
  sliced_update_ranges: [
    {min: 0,      max: 500},
    {min: 97500,  max: 102500},
    {min: 195000, max: 200000}
  ],

  data_filter: function(d) {
    const max_replicates = 50;
    return( (!d.sensors && d.environment == "env-chg_rate-u100") && d.index < max_replicates);
  },

  seeds_by_condition: {},
  expressed_states: new Set()

};

// Should we slice the visualization?
var IsSliced = function() {
  return $("#slice-toggle").prop("checked");
}

// What is the width of the parent element for the visualization?
// We'll use this value to dynamically size the visualization.
var GetVisParentWidth = function() {
  return $("#"+vis_config.lineage_states_div_id).parent().width();
};

// Given a list of states (in order), an interval (how long each state lasts), and an end point,
// generate and return the environment sequence of states.
var GenEnvSequence = function(states, interval, end) {
  var seq = [];
  var cur_env_id = 0;
  for (var i = 0; i < end; i += interval) {
    seq.push(
      {
        state: states[cur_env_id],
        start: i,
        duration: interval
      }
    );
    cur_env_id += 1;
    cur_env_id %= states.length;
  }
  return seq;
}

// d3js data accessor for lineage state sequence data
var LineageStateSequenceDataAccessor = function(row) {
  // header information:
  // COPY_MUT_PROB,DISABLE_REACTION_SENSORS,ENVIRONMENT_FILE,EVENT_FILE,PHYLOGENY_SNAPSHOT_RES,RANDOM_SEED,REACTION_SENSORS_NEUTRAL,SYSTEMATICS_RES,chg_env,environment,genotype_seq_length,genotype_seq_unique_state_cnt,max_update,phase,phen_seq_by_geno_duration,phen_seq_by_geno_start,phen_seq_by_geno_state,phen_seq_by_phen_duration,phen_seq_by_phen_start,phen_seq_by_phen_state,phenotype_seq_length,phenotype_seq_unique_state_cnt
  // Extract relevant data.
  const environment = row.environment;
  const sensors = row.DISABLE_REACTION_SENSORS == "0";
  const exp_condition = `${environment}__${sensors}`
  const random_seed = row.RANDOM_SEED;
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
    var plastic = true;
    if (env_a_profile == env_b_profile) {
      state = env_a_profile;
      plastic = false;
    }
    phen_seq.push({
      state: state,
      plastic: plastic,
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

  // Track replicate id
  if (!(exp_condition in vis_config.seeds_by_condition)) {
    vis_config.seeds_by_condition[exp_condition] = new Set();
  }
  const index = vis_config.seeds_by_condition[exp_condition].size;
  vis_config.seeds_by_condition[exp_condition].add(random_seed);

  // Return data entry
  return {
    environment: environment,
    sensors: sensors,
    random_seed: random_seed,
    phenotype_seq: phen_seq,
    index: index
  }

}

var x_scale = "";
// Call this function once to build the state sequence visualization and then to wire up the DrawVisualization function
// to page events.
var BuildVisualization = function(data) {
  console.log("BuildVisualization!");
  // Filter data
  data = data.filter(vis_config.data_filter);
  vis_config.expressed_states = new Set();
  console.log(data);
  for (di = 0; di < data.length; di++) {
    for (pi = 0; pi < data[di].phenotype_seq.length; pi++) {
      vis_config.expressed_states.add(data[di].phenotype_seq[pi].state);
    }
  }

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
    var env_data = GenEnvSequence(
      vis_config.environment_sequence.states,
      vis_config.environment_sequence.interval,
      vis_config.full_update_range.max
    );

    // Slice the data?
    var data_ranges = [];
    if (display_full) {
      data_ranges = [vis_config.full_update_range];
    } else {
      data_ranges = vis_config.sliced_update_ranges;
    }

    // Helper function to get range ID of seq object
    var GetRangeID = function(seq_obj) {
      var start = seq_obj.start;
      for (var i = 0; i < data_ranges.length; i++) {
        if (start >= data_ranges[i].min && start <= data_ranges[i].max) {
          return i;
        }
      }
      // Failure
      return -1;
    }

    // Calculate the total size of the display range.
    var total_range = 0;
    for (var i = 0; i < data_ranges.length; i++) {
      total_range += data_ranges[i].max - data_ranges[i].min;
    }

    // Setup the frame/canvas
    // Frame width based on width of parent HTML element
    var frame_width = GetVisParentWidth(); // todo - add in some padding?

    // Height scales directly with data
    var canvas_height = (total_range * vis_config.tick_height) +
                        ((data_ranges.length-1) * vis_config.slice_vspacer);
    var frame_height = canvas_height + vis_config.margin.top + vis_config.margin.bottom;

    // Compute canvas width, but don't go over maximum size.
    var max_canvas_width = (data.length+1) * (vis_config.max_seq_width+vis_config.max_seq_hspacer);
    var canvas_width = Math.min(
      frame_width - vis_config.margin.left - vis_config.margin.right,
      max_canvas_width
    );

    frame.attr("width", frame_width);
    frame.attr("height", frame_height);
    canvas.attr("transform", `translate(${vis_config.margin.left}, ${vis_config.margin.top})`);

    // Compute x/y domains for visualization
    var x_domain = [0, data.length];
    var x_range = [0, canvas_width];
    x_scale = d3.scaleLinear()
      .domain(x_domain)
      .range(x_range);

    // Clear old axes.
    canvas.selectAll(".x-axis").remove();
    // Append new x axis
    var x_axis = d3.axisTop().scale(x_scale).tickValues([]);
    canvas.append("g")
      .attr("class", "axis x-axis")
      .attr("id", "lineage-seq-vis_x-axis")
      .call(x_axis);

    var data_canvas = canvas.append("g").attr("class", "data-canvas");

    var slices = data_canvas.selectAll("g").data(data_ranges);

    slices.enter()
      .append("g")
      .attr("class", "data-slice")
      .attr("rmin", function(d) { return d.min; })
      .attr("rmax", function(d) { return d.max; })
      .attr(
        "transform",
        function(d, i) {
          // calculate how far down this slice should be transformed
          var down = 0;
          for (var ri = 0; ri < i; ri++) {
            down += ( (data_ranges[ri].max - data_ranges[ri].min) * vis_config.tick_height ) + vis_config.slice_vspacer;
          }
          return `translate(0, ${down})`;

        }
      );

    // Draw each slice as a (somewhat) separate sub-visualization.
    data_canvas.selectAll(".data-slice")
      .each(
        function(slice_range, slice_id) {
          // Make a y axis for this data slice
          var y_domain = [slice_range.min, slice_range.max];
          var y_range = [0, (slice_range.max - slice_range.min) * vis_config.tick_height];
          var y_scale = d3.scaleLinear()
            .domain(y_domain)
            .range(y_range)
            .clamp(true);

          var y_axis = d3.axisLeft().scale(y_scale).ticks( (slice_range.max - slice_range.min) / vis_config.time_tick_interval );
          d3.select(this)
            .append("g")
            .attr("class", "axis y-axis")
            .attr("id", `lineage-seq-vis_y-axis_r${slice_id}`)
            .attr(
              "transform",
              function(d) {
                return `translate(${-1*(vis_config.env_seq_width+vis_config.env_seq_hspacer)}, 0)`;
              }
            )
            .style("font-size", "75%")
            .call(y_axis);
          // Here's the sub-canvas to work in for this slice.
          var slice_data_canvas = d3.select(this).append("g").attr("class", "data-slice-canvas");
          var sequences = slice_data_canvas.selectAll("g").data(data);
          sequences.enter()
            .append("g")
            .attr("class", function(d, i) { return `lineage-sequence-${i}`; })
            .attr(
              "transform",
              function(seq, i) {
                const xtrans = x_scale(i);
                const ytrans = y_scale(0);
                return `translate(${xtrans}, ${ytrans})`;
              }
            )
            .each(
              function(seq, seq_id) {
                // Filter sequence data down to only what fall in the appropriate range
                var seq_data = seq.phenotype_seq.filter(
                  function(d) {
                    const begin_t = d.start;
                    const end_t = d.start + d.duration;
                    const begins_in = begin_t >= slice_range.min && begin_t <= slice_range.max;
                    const ends_in = end_t >= slice_range.min && end_t <= slice_range.max;
                    const over = (end_t > slice_range.max) && (begin_t < slice_range.min);
                    return ends_in || begins_in || over;
                  }
                );
                var states = d3.select(this).selectAll("rect").data(seq_data);
                states.enter()
                  .append("rect")
                  .attr(
                    "class",
                    function(state) {
                      return state.state;
                    }
                  )
                  .attr("state", function(state) { return state.state; })
                  .attr("start", function(state) { return state.start; })
                  .attr("end", function(state) { return state.end; })
                  .attr("duration", function(state) { return state.duration; })
                  .attr(
                    "transform",
                    function(state) {
                      return `translate(0, ${y_scale(state.start)})`;
                    }
                  )
                  .attr(
                    "height",
                    function(state) {
                      return y_scale( slice_range.min + Math.min(slice_range.max - state.start, state.duration)) - 0.5;
                    }
                  )
                  .attr(
                    "width",
                    x_scale(0.9)
                  )
                  .attr(
                    "fill",
                    function(state) {
                      if (state.state == "000000000000") {
                        return "grey";
                      } else {
                        return "blue";
                      }
                    }
                  );
              }
            );
          // Overlay environment sequence
          var slice_env_canvas = d3.select(this)
            .append("g")
            .attr("class", "env-slice-canvas")
            .attr(
              "transform",
              function(seq, i) {
                const xtrans = -1 * (vis_config.env_seq_width + vis_config.env_seq_hspacer);
                const ytrans = y_scale(0);
                return `translate(${xtrans}, ${ytrans})`;
              }
            );
          // Filter environment data down to just this slice
          var slice_env_data = env_data.filter(
            function(d) {
              const begin_t = d.start;
              const end_t = d.start + d.duration;
              const begins_in = begin_t >= slice_range.min && begin_t <= slice_range.max;
              const ends_in = end_t >= slice_range.min && end_t <= slice_range.max;
              return ends_in || begins_in;
            }
          );
          var env_states = slice_env_canvas.selectAll("rect").data(slice_env_data);
          env_states.enter()
            .append("rect")
            .attr("class", function(state) { return state.state; })
            .attr("state", function(state) { return state.state; })
            .attr("start", function(state) { return state.start; })
            .attr("end", function(state) { return state.start + state.duration; })
            .attr("duration", function(state) { return state.duration; })
            .attr(
              "transform",
              function(state) {
                return `translate(0, ${y_scale(state.start)})`;
              }
            )
            .attr(
              "height",
              function(state) {
                return y_scale(slice_range.min + Math.min(slice_range.max-state.start,state.duration)) - 0.5;
              }
            )
            .attr(
              "width",
              vis_config.env_seq_width
            );
        }
      );
      // Add some default styling to the axes
      var axes = canvas.selectAll(".axis");
      axes.selectAll("path")
        .style("fill", "none")
        .style("stroke", "black")
        .style("shape-rendering", "crispEdges");
      // Add y axis label
      canvas.selectAll(".axis-label").remove();
      canvas.append("text")
        .attr("class", "axis-label")
        .style("text-anchor", "middle")
        .attr("x", 0 - (canvas_height / 2))
        .attr("y", 0 - vis_config.margin.left / 1.5)
        .attr("transform", "rotate(-90)")
        .text("Time")
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