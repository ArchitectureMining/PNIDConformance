# Conformance Checking a PNID using an SMT Solver
Implementation of the SMT approach as described in the thesis `Architecture Conformance Checking on Multi-Instance and Process-Aware software systems`.

## Instructions
See the main method of `PNIDConformanceSMT.py` and uncomment the function you want to run. Set debug to true for more info about alignment etc., example of usage of parameter be seen in `test.py`.
Note, an installation of the Yices SMT solver and Yices python binding is required for running this application, which instructions can be found on Github (https://github.com/SRI-CSL/yices2, https://github.com/SRI-CSL/yices2_python_bindings).

## About
A CSV log (see folder data/log) is used and converted to XES. Additionally, a .`pnml` file (see folder data/model) is read and loaded as PNID. PNID is then converted on identifier bound to a bounded reachability graph, and then to a PN. We then encode the trace in the log, the PN and the optimal alignment problem into the SMT solver. The solver finds an optimal alignment which we trim if necessary and decode to a printable alignment. This process is repeated for each trace in the log. The implementation used is partially based on the implementation of the [CoCoMot approach](https://arxiv.org/abs/2103.10507), an SMT approach on DPNs, proposed by Felli et al.