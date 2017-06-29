#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR

mkdir -p $DIR/raw

cd $DIR/raw

git clone https://github.com/UniMath/UniMath.git
git clone https://github.com/HoTT/HoTT.git

cd $DIR

# TODO: Preprocess repositories to remove non-Coq files ?
