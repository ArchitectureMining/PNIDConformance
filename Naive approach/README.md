# PNIDConformance
 ProM package for conformance checking on Petri nets with identifiers. Uses [PNID repo](https://github.com/ArchitectureMining/PNID) for its base models. Implementation of the naive approach as described in the thesis `Architecture Conformance Checking on Multi-Instance and Process-Aware software systems`.

# Algorithms
- NaiveCC \
 Given a sequence of events and a PNID model, flattens the PNID (up to identifier bound) and finds the closest firing sequence (alignment) of the sequence of events opposed to the flat Petri Net.
 - FlattenPNID \
 Given a sequence of events and a PNID model, flattens the PNID (up to identifier bound).
- Alignment search (status: WIP)\
Given a Petri net and a sequence of events, finds an alignment using an alignment technique with A* search technique in the package `nl.tue.alignment`.

# Instructions
Option 1: import plugins into ProM
- Make sure ProM is installed
- Run `ProM Package Manager (PNIDConformance).launch` (using Java 9) and install packages in the ProM Package manager
- Run `ProM with UITopia (PNIDConformance).launch` (using Java 9) and select plugin

Option 2: run as JUnit test
- Run the test file `PNIDConformancePluginTest` in the folder `src-test`

## About
A CSV log (see folder tests/plugin/Input files (log)) is used and converted to XES. Additionally, a .`pnml` file (see folder tests/plugin/Input files (pnid)) is read and loaded as PNID. PNID is then converted on identifier bound to a Petri net using flattening. Using (one of) the alignment search algorithms proposed by Verbeek et al. it finds an optimal alignment.