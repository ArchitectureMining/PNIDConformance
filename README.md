# PNIDConformance
 ProM package for conformance checking on Petri nets with identifiers. Uses [PNID repo](https://github.com/ArchitectureMining/PNID) for its base models.

# Algorithms
- NaiveCC \
 Given a sequence of events and a PNID model, flattens the PNID (up to identifier bound) and finds the closest firing sequence (alignment) of the sequence of events opposed to the flat Petri Net.

# Instructions
Option 1: import plugins into ProM
- Make sure ProM is installed
- Run `ProM Package Manager (PNIDConformance).launch` (using Java 9) and install packages in the ProM Package manager
- Run `ProM with UITopia (PNIDConformance).launch` (using Java 9) and select plugin

Option 2: run as JUnit test
- Run the test file `PNIDConformancePluginTest` in the folder `src-test`