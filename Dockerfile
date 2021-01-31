# ======= USAGE =======
# Run interactively:
#   docker run -it --entrypoint bash dockertest:latest

# Pull a base image
FROM ubuntu:20.04

COPY . /opt/evolutionary-consequences-of-plasticity

# To make installs not ask questions about timezones
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

##############################
# install base dependencies
# - for R repository
#   - dirmngr
#   - gpg-agent
# - for bookdown compilation
#   - pandoc, pandoc-citeproc, texlive-base, texlive-latex-extra
##############################
RUN \
  apt-get update \
    && \
  apt-get install -y -qq --no-install-recommends \
    software-properties-common \
    curl=7.68.0-1ubuntu2.4 \
    g++-10=10.2.0-5ubuntu1~20.04 \
    make=4.2.1-1.2 \
    cmake=3.16.3-1ubuntu1  \
    python3=3.8.2-0ubuntu2 \
    python3-pip \
    python3-virtualenv \
    git=1:2.25.1-1ubuntu3 \
    dirmngr \
    gpg-agent \
    pandoc \
    pandoc-citeproc \
    texlive-base \
    texlive-latex-extra \
    lmodern \
    && \
  echo "installed base dependencies"

# alias wire g++-10 up to g++ ln -s gcc-10 gcc &&
RUN cd /usr/bin/ && ln -s g++-10 g++ && cd /

########################################################
# install project python dependencies
# - Script dependencies listed in requirements.txt
# - Install osfclient to use to download data from OSF
########################################################
RUN \
  pip3 install -r /opt/evolutionary-consequences-of-plasticity/requirements.txt \
    && \
  pip3 install osfclient \
    && \
  echo "installed python dependencies"

########################################################
# download experiment data using python osfclient
# move data into expected directories
########################################################
RUN \
  export OSF_PROJECT=sav2c \
    && \
  export PROJECT_PATH=/opt/evolutionary-consequences-of-plasticity \
    && \
  cd ${PROJECT_PATH} \
    && \
  export EXP_TAG=2021-01-07-validation \
    && \
  ./download_exp_data.sh \
    && \
  export EXP_TAG=2021-01-30-evo-dynamics \
    && \
  ./download_exp_data.sh

########################################################
# install r
# - source: https://rtask.thinkr.fr/installation-of-r-4-0-on-ubuntu-20-04-lts-and-tips-for-spatial-packages/
########################################################
RUN \
  gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 \
    && \
  gpg -a --export E298A3A825C0D65DFD57CBB651716619E084DAB9 | apt-key add - \
    && \
  apt update \
    && \
  add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/' \
    && \
  apt-get install -y -q --no-install-recommends \
    r-base=4.0.3-1.2004.0 \
    r-base-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libfreetype6-dev \
    libmagick++-dev \
    libxml2-dev \
    libfontconfig1-dev \
    cargo \
    && \
  R -e "install.packages('rmarkdown', dependencies=NA, repos='http://cran.rstudio.com/')" \
    && \
  R -e "install.packages('knitr', dependencies=NA, repos='http://cran.rstudio.com/')" \
    && \
  R -e "install.packages('bookdown', dependencies=NA, repos='http://cran.rstudio.com/')" \
    && \
  R -e "install.packages('tidyverse', dependencies=NA, repos='http://cran.rstudio.com/')" \
    && \
  R -e "install.packages('cowplot', dependencies=NA, repos='http://cran.rstudio.com/')" \
    && \
  R -e "install.packages('plyr', dependencies=NA, repos='http://cran.rstudio.com/')" \
    && \
  R -e "install.packages('Hmisc', dependencies=NA, repos='http://cran.rstudio.com/')" \
    && \
  echo "installed r and configured r environment"


########################################################
# download Empirical @ appropriate commit
########################################################
RUN \
  git clone https://github.com/amlalejini/Empirical.git /opt/Empirical \
    && \
  cd /opt/Empirical \
    && \
  git checkout c49ca476e371ef70d3c0f6126fc7cfeeaf3c8908 \
    && \
  git submodule init \
    && \
  git submodule update \
    && \
  echo "downloaded Empirical"

########################################################
# compile experiment code (modified avida)
########################################################
# RUN \
#   cd /opt/evolutionary-consequences-of-plasticity/avida/ \
#     && \
#   ./build_avida \
#     && \
#   cp /opt/evolutionary-consequences-of-plasticity/avida/cbuild/work/avida /bin/avida \
#     && \
#   echo "compiled avida"

########################################################
# build supplemental material (will also run data analyses)
########################################################
RUN \
  cd /opt/evolutionary-consequences-of-plasticity/ \
    && \
  ./build_book.sh \
    && \
  echo "ran analyses and built supplemental material"