#! /bin/bash

# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#
# cd $DIR

mkdir -p $1

cd $1

git clone https://github.com/UniMath/UniMath.git
git clone https://github.com/HoTT/HoTT.git

# TODO: Preprocess repositories to remove non-Coq files ?
