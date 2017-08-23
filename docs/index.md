# AutoMaths

[![Build Status](https://travis-ci.org/Xide/AutoMaths.svg?branch=master)](https://travis-ci.org/Xide/AutoMaths)

## About

The AutoMaths project aim to create an helper for automated theorem proving using Coq.

This repository contain the sources used to create the dataset, for more details
about this check out the [Data page](./data.md).

Features: (see [Roadmap](./roadmap.md) for more details)

- [X] Coq files dataset
- [X] Dependencies graph
- [ ] Model
- [ ] Coq ecosystem integration

## Requirements

- `make`
- `python3` (tested with python 3.4.5)
- `pip`
- Optional: `jupyter` for visualization

## Install

```bash
# Clone the GitHub repository
git clone https://github.com/Xide/AutoMaths.git

# Install the python dependencies (can be seen in requirements.txt)
# Default install them in the user home directory.
make install

# Build the dataset
# You can add the -j flag for faster preprocessing
make preprocess # -j 9

# Optional: If you want to edit the documentation

```
