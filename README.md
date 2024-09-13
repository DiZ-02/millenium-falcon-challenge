# Millenium Falcon Challenge

[![ci](https://github.com/DiZ-02/millenium-falcon-challenge/workflows/ci/badge.svg)](https://github.com/DiZ-02/millenium-falcon-challenge/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://DiZ-02.github.io/millenium-falcon-challenge/)

[//]: # ([![pypi version]&#40;https://img.shields.io/pypi/v/millenium-falcon-challenge.svg&#41;]&#40;https://pypi.org/project/millenium-falcon-challenge/&#41;)
[//]: # ([![gitpod]&#40;https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat&#41;]&#40;https://gitpod.io/#https://github.com/DiZ-02/millenium-falcon-challenge&#41;)
[//]: # ([![gitter]&#40;https://badges.gitter.im/join%20chat.svg&#41;]&#40;https://app.gitter.im/#/room/#millenium-falcon-challenge:gitter.im&#41;)

Developer Technical Test @ Dataiku

## Installation

With `make`:

```bash
make setup
```

If not available:

```bash
bash scripts/setup.sh
```

## Usage

Be sure to be in the right virtual env.

```bash
cd project-dir
eval $(pdm venv activate)
```

### Standalone CLI

Run the CLI with:

```bash
give-me-the-odds cfg_file input_file
```

More help with:

```bash
give-me-the-odds -h
```

### App

Run the application with:

```bash
pdm run [dev|prod]
```

*Change port to 8080 if you launched the prod config.*

Application is now accessible [here](http://127.0.0.1:8000).

You can test the **API** using Swagger [here](http://127.0.0.1:8000/docs).

Or you can go to the **GUI** [here](http://127.0.0.1:8000/gui/).

## Assumptions


Functional assumptions:

- Departure and arrival are in the given graph.
- All travel times are strictly positive.
- The planets in intercepted communication that are not in the given graph are ignored.


Performance assumptions:

This app focus is on performance.
Data are stored in memory, so limits have been set on inputs:

- autonomy < 4096
- number of nodes < 2048


## Improvements

All improvements are in code base under `# TODO` sections at the relevant places.
Most notable ones are to:

- use numpy to increase performances.
- use more lightweight structures and weakref to spare memory.
- implement front end tests.
- create the Dockerfile to deploy the project on Gitpod.
