import networkx as nx

# -*- coding=utf-8 -*-

"""TODO: DESCRIPTION."""

from pulp import PULP_CBC_CMD, LpMinimize, LpProblem, LpStatus, LpVariable, LpBinary, LpInteger, lpSum


# ============================================================================ #
#                                  SET MODEL                                   #
# ============================================================================ #
def set_graphe(G, M, C, BigM, li):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Linear problem with maximization
    # ------------------------------------------------------------------------ #
    probmin = LpProblem(name='graphe_maximize', sense=LpMinimize)

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
    probmin += lpSum(
        variable_y[(i, j)] * C[(i, j)] for i in M for j in M if (li[i], li[j]) in list(G.edges)), 'obj_min'

    # ------------------------------------------------------------------------ #
    # The constraints
    # ------------------------------------------------------------------------ #
    # TODO: write constraints
    for i in M:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmin += (variable_x[i] - variable_x[j] + variable_y[(i, j)] >= 0), f'inter_som{(i, j)}',

    probmin += (variable_x[M[-1]] - variable_x[M[0]] >= 1), f'contrainte_arr_dep_min',

    # QUESTION  5
    for i in M:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmin += (pos[j] >= pos[i] + variable_y[(i, j)] - ((
                                                                             1 - variable_y[
                                                                         (i, j)]) * BigM)), f'posion_som_min_o{(i, j)}',
                probmin += (pos[j] <= pos[i] + variable_y[(i, j)] + (
                        (1 - variable_y[(i, j)]) * BigM)), f'posion_som_min_u{(i, j)}',
    # QUESTION  6
    for i in (M[1:-1]):
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmin += (pos[i] <= BigM * lpSum(variable_y[(i, j)])), f'posion_min_{(i, j)}',

    return probmin, variable_x, variable_y, pos


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
    probmin, variable_x, variable_y, pos = set_graphe(G, M, C, BigM, li)

    # Coin Branch and Cut solver is used to solve the instanced model
    # TODO: change the log path file
    probmin.solve(
        PULP_CBC_CMD(
            msg=False, logPath=str('./CBC_log_TP3_max.log'),
        ),
    )

    # ------------------------------------------------------------------------ #
    # Print the solver output
    # ------------------------------------------------------------------------ #
    print_log_output(probmin, variable_x, variable_y, pos)


# ============================================================================ #
#                                   UTILITIES                                  #
# ============================================================================ #
def print_log_output(probmin: LpProblem, variable_x, variable_y, pos):
    """Print the log output and problem solutions."""
    print()
    print('-' * 40)
    print('Stats')
    print('-' * 40)
    print()
    print(f'Number variables for max: {probmin.numVariables()}')
    print(f'Number constraints for max: {probmin.numConstraints()}')
    print()
    print()
    print('Time:')
    print(f'- (real for max) {probmin.solutionTime}')
    print(f'- (CPU for max) {probmin.solutionCpuTime}')
    print()
    print()
    print(f'Solve status for max: {LpStatus[probmin.status]}')
    print(f'Objective value for max: {probmin.objective.value()}')
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

    G = nx.Graph()

    G.add_nodes_from(['S', 'B', 'C', 'D', 'E', 'T'])

    G.add_weighted_edges_from(
        [('S', 'B', 250), ('S', 'C', 1000), ('B', 'C', 700), ('B', 'D', 150), ('D', 'T', 1000), ('C', 'T', 300),
         ('C', 'E', 50), ('E', 'T', 350)])

    M = [i for i in range(G.number_of_nodes())]

    li = list(G.nodes)

    C = {}
    for i in M:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                C[(i, j)] = G[li[i]][li[j]]['weight']

    BigM = 500000

    solve_graphe(G, M, C, BigM, li)