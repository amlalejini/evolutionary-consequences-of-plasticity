# Experiment Log

Most experiments have README notes in each of their directories.

Here, we log information/changes that are not necessarily experiment specific.

## Code dependencies

Both 2020-08-17-capacity and 2020-08-19-phased use vanilla avida (the most recent Avida commit as of 2020-08-17).

2020-08-26 Avida merged with Avida+Empirical mashup version (from Dolson et al.'s Interpreting the Tape
of Life paper). We updated the code base to compile successfully against a newer version of Empirical.
This version: <https://github.com/amlalejini/Empirical/tree/2020-avida-plasticity>.

We automate various aspects of our experiment pipeline with Python scripts. These scripts require a variety of python packages be installed. We recommend using python virtual environments:

```bash
python3 -m venv pyenv
source pyenv/bin/activate
pip3 install -r requirements.txt
```