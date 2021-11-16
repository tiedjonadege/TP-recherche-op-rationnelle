import networkx as nx
from pulp import PULP_CBC_CMD, LpProblem, LpStatus, LpMaximize, LpVariable, LpInteger, lpSum, LpBinary


# ============================================================================ #
#                                  SET MODEL                                   #
# ============================================================================ #
def set_graphe(G, M, C, BigM, li):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Linear problem with maximization
    # ------------------------------------------------------------------------ #
    probmax = LpProblem(name='graphe_minimize', sense=LpMaximize)
    # FIXME: it is not always a maximization problem ...

    # ------------------------------------------------------------------------ #
    # The variables
    # ------------------------------------------------------------------------ #
    # QUESTION 2
    # TODO: set variables
    variable_fizero = LpVariable('fizero', lowBound=0)
    variable_fi = {(i, j): LpVariable(f'fi_{i}_{j}', lowBound=0) for i in M for j in M if
                   (li[i], li[j]) in list(G.edges)}

    variable_x = {(i, j): LpVariable(f'X_{i}_{j}', lowBound=0, cat=LpBinary) for i in M for j in M if
                  (li[i], li[j]) in list(G.edges)}
    posit = {j: LpVariable(f'position_{j}', lowBound=0, cat=LpInteger) for j in M}
    # ------------------------------------------------------------------------ #
    # The objective function
    # ------------------------------------------------------------------------ #
    # TODO: write the objective function
    # QUESTION 3
    probmax += variable_fizero, 'obj_min',
    # ------------------------------------------------------------------------ #
    # The constraints
    # ------------------------------------------------------------------------ #

    # TODO: write constraints
    # QUESTION 2 et 4

    for i in M:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmax += (variable_x[(i, j)] <= 1), f'limX_{i}_{j}',

    # condition sur fi
    probmax += variable_fizero == lpSum(
        variable_fi[(i, j)] for i in M for j in M if (li[i], li[j]) in list(G.edges)), f'fizero',

    for i in M:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmax += (variable_x[(i, j)] <= variable_fi[(i, j)]), f'flow{(i, j)}',
                probmax += (variable_fi[(i, j)] <= variable_x[(i, j)] * C[(i, j)]), f'flowCap{(i, j)}',

    probmax += lpSum(variable_x[(i, M[-1])] for i in M if (li[i], li[M[-1]]) in list(G.edges)) == 1, f'fi_S',

    probmax += (lpSum(variable_x[(0, j)] for j in M if (li[0], li[j]) in list(G.edges)) == 1), f'fi_T',

    for u in M[1:-1]:
        probmax += (lpSum(variable_x[(i, u)] for i in M if (li[i], li[u]) in list(G.edges)) == lpSum(
            variable_x[(u, j)] for j in M if (li[u], li[j]) in list(G.edges))), f'som_{u}',

    # QUESTION 5
    probmax += (posit[i] <= BigM * lpSum(variable_x[(i, j)] for i in (M[1:-1]) for j in M[1:] if
                                         (li[i], li[j]) in list(G.edges))), f'position_min',

    # QUESTION 6
    probmax += posit[0] == 1, f'posit_initial',

    for i in M[1:]:
        probmax += posit[i] >= 1, f'pos_decla{i}',

    for i in M[1:]:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmax += (posit[j] >= posit[i] + variable_x[(i, j)] - ((
                                                                                 1 - variable_x[
                                                                             (i, j)]) * BigM)), f'position_som{(i, j)}',
                probmax += (posit[j] <= posit[i] + variable_x[(i, j)] + ((
                                                                                 1 - variable_x[(
                                                                             i,
                                                                             j)]) * BigM)), f'position_som_BM{(i, j)}',

    return probmax, variable_fi, variable_fizero, variable_x, posit

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
    probmax, variable_fi, variable_fizero, variable_x, posit = set_graphe(G, M, C, BigM, li)

    # Coin Branch and Cut solver is used to solve the instanced model
    # TODO: change the log path file

    probmax.solve(
        PULP_CBC_CMD(
            msg=False, logPath='./CBC_log_TP4_maxG.log',
        ),
    )

    # ------------------------------------------------------------------------ #
    # Print the solver output
    # ------------------------------------------------------------------------ #
    print_log_output(probmax,  variable_fizero, variable_x)


# ============================================================================ #
#                                   UTILITIES                                  #
# ============================================================================ #
def print_log_output(probmax: LpProblem, variable_fizero, variable_x):
    """Print the log output and problem solutions."""
    print()
    print('-' * 40)
    print('Stats')
    print('-' * 40)
    print()
    print(f'Number variables for min: {probmax.numVariables()}')
    print(f'Number constraints for min: {probmax.numConstraints()}')
    print()
    print('Time:')
    print(f'- (real for min) {probmax.solutionTime}')
    print(f'- (CPU for min) {probmax.solutionCpuTime}')
    print()
    print(f'Solve status for min: {LpStatus[probmax.status]}')
    print(f'Objective value for min: {probmax.objective.value()}')

    print()
    print('-' * 40)
    print("Variables' values")
    print('-' * 40)
    print()

    # TODO: you can print variables value here

    print()
    print('-' * 40)
    print(f'le poids ={variable_fizero.value()}')
    print('-' * 40)

    print('Le chemin elementaire le plus lourd de G est:')

    for num_arc, lpvar in enumerate(variable_x.values()):
        arc = lpvar.varValue
        if arc == 1 :
           print (lpvar )

    print('avec  S = 0')
    print('avec  B = 1')
    print('avec  C = 2')
    print('avec  D = 3')
    print('avec  E = 4')
    print('avec  T = 5')


if __name__ == '__main__':

    # QUESTION 1
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
