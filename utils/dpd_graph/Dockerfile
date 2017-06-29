FROM ubuntu:xenial


RUN apt-get update -y && \
    apt-get install -y \
      build-essential \
      autoconf \
      ocaml \
      ocaml-native-compilers \
      camlp5 \
      liblablgtk2-ocaml-dev \
      liblablgtksourceview2-ocaml-dev \
      libgtk2.0-dev \
      git

RUN apt-get install -y \
    libocamlgraph-ocaml-dev

ADD https://coq.inria.fr/distrib/V8.6/files/coq-8.6.tar.gz .

RUN tar -xvzf coq-8.6.tar.gz

WORKDIR coq-8.6
RUN ./configure -prefix /usr/local && \
    make && \
    make install

WORKDIR /
RUN git clone https://github.com/Karmaki/coq-dpdgraph.git

WORKDIR coq-dpdgraph

RUN autoconf && \
    ./configure && \
    make && \
    make install

CMD sh
