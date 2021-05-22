# Compile and run experiments locally

Here, we provide a brief guide to compiling and running our experiments using our Docker image.

Please file an [issue on GitHub](https://github.com/amlalejini/evolutionary-consequences-of-plasticity) if something is unclear or does not work.

## Docker

You can use the Dockerfile in our [repository](https://github.com/amlalejini/evolutionary-consequences-of-plasticity) to build a docker image locally, or you can pull the [latest docker image from DockerHub](https://hub.docker.com/r/amlalejini/evolutionary-consequences-of-plasticity) using

```
docker pull amlalejini/evolutionary-consequences-of-plasticity
```

This will pull down a docker image with:

- all of the requisite dependencies installed/downloaded
- all experiment source code
- the minimal set of raw data needed to compile the supplemental material
- a build of our supplemental material (which will also run all of our analyses)

To run the container interactively:

```
docker run -it --entrypoint bash amlalejini/evolutionary-consequences-of-plasticity
```

You can exit the container at any point with  `ctrl-d`.

Inside the container, you should be able to navigate to `/opt/evolutionary-consequences-of-plasticity`:

```
cd /opt/evolutionary-consequences-of-plasticity
```

To run Avida, you'll need to `cd` into the `avida` directory and run `./build_avida`.

All of the Avida configuration files necessary for re-running our experiments can be found here: <https://github.com/amlalejini/evolutionary-consequences-of-plasticity/tree/master/experiments>.

For example, the configuration files for our evolutionary change experiment are here: <https://github.com/amlalejini/evolutionary-consequences-of-plasticity/tree/master/experiments/2021-02-08-evo-dynamics/hpcc/config>.
