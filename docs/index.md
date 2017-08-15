# AutoMaths

[![Build Status](https://travis-ci.org/Xide/AutoMaths.svg?branch=master)](https://travis-ci.org/Xide/AutoMaths)

## Context

The AutoMaths project aim to create an helper for automated theorem proving using Coq.


### Limits


## Requirements

- Python3 (tested with python 3.4.5)
- Tensorflow

## Install

```bash
# Clone the GitHub repository
git clone https://github.com/Xide/AutoMaths.git

# Install the python dependencies (can be seen in requirements.txt)
# Default install them in the user home directory.
make install

# Optional : if you want to build the dataset
# Clone the data repositories
make download
# You can add the -j flag for faster preprocessing
make preprocess # -j 9
```

## Usage

## Architecture


### Neural network
#### DNC framework
- [Implementation](https://github.com/deepmind/dnc)
- [Paper](https://www.nature.com/articles/nature20101.epdf?author_access_token=ImTXBI8aWbYxYQ51Plys8NRgN0jAjWel9jnR3ZoTv0MggmpDmwljGswxVdeocYSurJ3hxupzWuRNeGvvXnoO8o4jTJcnAyhGuZzXJ1GEaD-Z7E6X_a9R-xqJ9TfJWBqz)
- [Blog post](https://deepmind.com/blog/differentiable-neural-computers/)

## Training

## Issues

- The token stream and raw text shouldn't be handled by different networks.
This could be solved by training the network with different kind of input datas,
as deepmind did on the DNC paper. Or we could encode the token type into the
neural network input along with the raw stream.

- The network should learn categorical data instead of an unstructured character
stream. We need to find a way to turn text data into categorical representations.
We could use one-hot encoding to do so, by encoding differently free text (such
  as naming) and language operators to avoid confusion.

- There is no Coq parser avaliable in Python, therefore, the dependencies parsing
will be done using regex, which is weaker than a generated `Yacc` parser. However
as Coq was developped on the top of ML language, there is no centralised BNF grammar
avaliable.
