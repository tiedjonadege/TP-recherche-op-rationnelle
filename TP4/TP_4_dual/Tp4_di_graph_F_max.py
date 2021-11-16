import networkx as nx

# -*- coding=utf-8 -*-

"""TODO: DESCRIPTION."""

from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpStatus, LpVariable, LpBinary, LpInteger, lpSum


# ============================================================================ #
#                                  SET MODEL                                   #
# ============================================================================ #
def set_graphe(G, M, C, BigM, li):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Linear problem with maximization
    # ------------------------------------------------------------------------ #
    probmax = LpProblem(name='graphe_maximize', sense=LpMaximize)

    # FIXME: it is not always a maximization problem ...

    # ------------------------------------------------------------------------ #
    # The variables
    # ------------------------------------------------------------------------ #
    # TODO: set variables
    variable_x = {j: LpVariable(f'sommet{j}', lowBound=0, cat=LpBinary) for j in M}
    variable_y = {(i, j): LpVariable(f'arc_{i}_{j}', lowBound=0, cat=LpBinary) for j in M for i in M}
    pos = {j: LpVariable(f'position_{j}', lowBound=0, cat=LpInteger) for j in M}

    # ------------------------------------------------------------------------ #
    # The objective function
    # ------------------------------------------------------------------------ #
    # TODO: write the objective function
    probmax += lpSum(
        variable_y[(i, j)] * C[(i, j)] for i in M for j in M if (li[i], li[j]) in list(G.edges)), 'obj_min'

    # ------------------------------------------------------------------------ #
    # The constraints
    # ------------------------------------------------------------------------ #
    # TODO: write constraints
    for i in M:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmax += (variable_x[i] - variable_x[j] + variable_y[(i, j)] >= 0), f'inter_som{(i, j)}',

    probmax += (variable_x[M[-1]] - variable_x[M[0]] >= 1), f'contrainte_arr_dep_min',



# ============================================================================ #
#                               SOLVE WITH DATA                                #
# ============================================================================ #
def solve_graphe(G, M, C, BigM, li):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Set data
    # ------------------------------------------------------------------------ #
    # TODO: set data

    # ------------------------------------------------------------------------ #
    # Solve the problem using the model
    # ------------------------------------------------------------------------ #
    probmax, variable_x, variable_y, pos = set_graphe(G, M, C, BigM, li)

    # Coin Branch and Cut solver is used to solve the instanced model
    # TODO: change the log path file
    probmax.solve(
        PULP_CBC_CMD(
            msg=False, logPath=str('./CBC_log_TP3_max.log'),
        ),
    )

    # ------------------------------------------------------------------------ #
    # Print the solver output
    # ------------------------------------------------------------------------ #
    print_log_output(probmax, variable_x, variable_y, pos)


# ============================================================================ #
#                                   UTILITIES                                  #
# ============================================================================ #
def print_log_output(probmax: LpProblem, variable_x, variable_y, pos):
    """Print the log output and problem solutions."""
    print()
    print('-' * 40)
    print('Stats')
    print('-' * 40)
    print()
    print(f'Number variables for max: {probmax.numVariables()}')
    print(f'Number constraints for max: {probmax.numConstraints()}')
    print()
    print()
    print('Time:')
    print(f'- (real for max) {probmax.solutionTime}')
    print(f'- (CPU for max) {probmax.solutionCpuTime}')
    print()
    print()
    print(f'Solve status for max: {LpStatus[probmax.status]}')
    print(f'Objective value for max: {probmax.objective.value()}')
    print()
    print('-' * 40)
    print("Variables' values")
    print('-' * 40)
    print()
    # TODO: you can print variables value here

    for num_arc, lpvar in enumerate(variable_x.values()):
        arc = lpvar.varValue
        print(lpvar, arc)

    # TODO: you can print variables value here


if __name__ == '__main__':
    F = nx.DiGraph()

    F.add_nodes_from(['S', 'B', 'C', 'D', 'E', 'T'])

    F.add_weighted_edges_from(
        [('S', 'B', 250), ('C', 'S', 1000), ('B', 'C', 700), ('B', 'D', 150), ('D', 'T', 1000), ('C', 'T', 300),
         ('E', 'C', 50), ('T', 'E', 350), ('D', 'C', 350)])

    M = [i for i in range(F.number_of_nodes())]

    li = list(F.nodes)

    C = {}
    for i in M:
        for j in M:
            if (li[i], li[j]) in list(F.edges):
                C[(i, j)] = F[li[i]][li[j]]['weight']

    BigM = 500000

    solve_graphe(F, M, C, BigM, li)
