## Roadmap & Future work

- [X] Dataset creation
  - [X] Pipeline automation ( see `Makefile` )
  - [X] Download Coq source coq for processing ( see `make download`)
  - [X] Extract and aggreate token streams (and metadata) of all the source files

  - [X] Cleaning
    - [X] Useless values removal (e.g: empty space text token)
    - [ ] Lexing error handling (currently ignored)

  - [X] Dependencies extraction
    - [X] Dependency graph creation (see `srcs/preprocess/dependencies.py`)
    - [ ] Use a parser instead of raw token streams
    - [ ] Reduce the scope of the dependency (currently: file level)
    - [ ] Handle loops in the dependency graph (currently the whole loop is cleaned from graph)

- [ ] Implementation
  - [X] Command line interface to experiment (baked by `sacred`)
  - [ ] Proof generation
    - [X] Utility to iterate over proofs
    - [ ] Context aware proof picker (e.g: following a specific set of axioms)
  - [ ] Coq environment integration
  - [ ] Models
    - [ ] Differentiable neural computer
    - [ ] Imagination augmented agent
  - [ ] Deployment
    - [X] Documentation (using travis-ci, github pages and mkdocs)
    - [ ] Generated dataset artifacts

- [ ] Documentation
  - [X] Dataset creation
  - [ ] Implementation
    - [X] Models presentation
    - [ ] Project limits presentation
