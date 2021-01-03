# QuantumRouteOptimizer
Quantum Route Optimizer, made as a supplement to my bachelor thesis - uses D-Wave annealers to solve a TSP problem

Uses the [CERDI seadistance database](https://ferdi.fr/en/indicators/the-cerdi-seadistance-database) and a modified [ISO 3116 shortcode database](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes) by Luke Duncalfe to setup a distance matrix from user-selected countries to visist, converts them to a QUBO using code snippets adapted from [Michał](https://github.com/BOHRTECHNOLOGY/quantum_tsp) [Stęchły's](https://github.com/BOHRTECHNOLOGY/tsp-demo-unitary-fund) repos, sends them to be solved on D-Wave's QPU, then interprets the results.
The results are usually unsatisfactory, which could be improved by improving the constraints of the QUBO and the result interpretation.
