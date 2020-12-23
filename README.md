# QuantumRouteOptimizer
Quantum Route Optimizer, made as a supplement to my bachelor thesis - uses D-Wave annealers to solve a TSP problem

Uses the CERDI seadistance database to setup a distance matrix from user-selected countries to visist, converts them to a QUBO using code snippets adapted from Michał Stęchły's repo, sends them to be solved on D-Wave's QPU, then interprets the results.
The results are usually unsatisfactory, which could be improved by improving the constraints of the QUBO and the result interpretation.
