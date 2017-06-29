# DPD_GRAPH


This little docker wrapper can be used to launch
[coq-dpdgraph](https://github.com/Karmaki/coq-dpdgraph) program.


## Usage

```sh
# From the root directory
cd utils/dpd_graph

# Directories configuration
DATA_DIRECTORY=$(realpath ../data)
OUT_DIRECTORY=/tmp/dpd-output

mkdir -p /tmp/dpd-output


# This command will compile `ocaml` and dpd-graph, can be pretty slow
# ~15mn on my laptop.
docker build -t dpd .

docker run \
  -v $DATA_DIRECTORY:/data \
  -v $OUT_DIRECTORY:/output \
  -it dpd
```

You will get to a shell with coq-dpdgraph installed, please refer to the package documentation for instructions on how to use it.
