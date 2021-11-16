import networkx as nx
from pulp import PULP_CBC_CMD, LpProblem, LpStatus, LpMinimize, LpVariable, LpInteger, lpSum, LpBinary


# ============================================================================ #
#                                  SET MODEL                                   #
# ============================================================================ #
def set_graphe(G, M, C, BigM, li):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Linear problem with maximization
    # ------------------------------------------------------------------------ #
    probmin = LpProblem(name='graphe_minimize', sense=LpMinimize)
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
    probmin += variable_fizero, 'obj_min',
    # ------------------------------------------------------------------------ #
    # The constraints
    # ------------------------------------------------------------------------ #

    # TODO: write constraints
    # QUESTION 2 et 4

    for i in M:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmin += (variable_x[(i, j)] <= 1), f'limX_{i}_{j}',

    # condition sur fi
    probmin += variable_fizero == lpSum(
        variable_fi[(i, j)] for i in M for j in M if (li[i], li[j]) in list(G.edges)), f'fizero',

    for i in M:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmin += (variable_x[(i, j)] <= variable_fi[(i, j)]), f'flow{(i, j)}',
                probmin += (variable_fi[(i, j)] <= variable_x[(i, j)] * C[(i, j)]), f'flowCap{(i, j)}',

    probmin += lpSum(variable_x[(i, M[-1])] for i in M if (li[i], li[M[-1]]) in list(G.edges)) == 1, f'fi_S',

    probmin += (lpSum(variable_x[(0, j)] for j in M if (li[0], li[j]) in list(G.edges)) == 1), f'fi_T',

    for u in M[1:-1]:
        probmin += (lpSum(variable_x[(i, u)] for i in M if (li[i], li[u]) in list(G.edges)) == lpSum(
            variable_x[(u, j)] for j in M if (li[u], li[j]) in list(G.edges))), f'som_{u}',

    # QUESTION 5
    probmin += (posit[i] <= BigM * lpSum(variable_x[(i, j)] for i in (M[1:-1]) for j in M[1:] if
                                         (li[i], li[j]) in list(G.edges))), f'position_min',

    # QUESTION 6
    probmin += posit[0] == 1, f'posit_initial',

    for i in M[1:]:
        probmin += posit[i] >= 1, f'pos_decla{i}',

    for i in M[1:]:
        for j in M:
            if (li[i], li[j]) in list(G.edges):
                probmin += (posit[j] >= posit[i] + variable_x[(i, j)] - ((
                                                                                 1 - variable_x[
                                                                             (i, j)]) * BigM)), f'position_som{(i, j)}',
                probmin += (posit[j] <= posit[i] + variable_x[(i, j)] + ((
                                                                                 1 - variable_x[(
                                                                             i,
                                                                             j)]) * BigM)), f'position_som_BM{(i, j)}',

    return probmin, variable_fi, variable_fizero, variable_x, posit

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
    probmin, variable_fi, variable_fizero, variable_x, posit = set_graphe(G, M, C, BigM, li)

    # Coin Branch and Cut solver is used to solve the instanced model
    # TODO: change the log path file

    probmin.solve(
        PULP_CBC_CMD(
            msg=False, logPath='./CBC_log_TP4_minF.log',
        ),
    )

    # ------------------------------------------------------------------------ #
    # Print the solver output
    # ------------------------------------------------------------------------ #
    print_log_output(probmin, variable_fizero, variable_x)


# ============================================================================ #
#                                   UTILITIES                                  #
# ============================================================================ #
def print_log_output(probmin: LpProblem, variable_fizero, variable_x):
    """Print the log output and problem solutions."""
    print()
    print('-' * 40)
    print('Stats')
    print('-' * 40)
    print()
    print(f'Number variables for min: {probmin.numVariables()}')
    print(f'Number constraints for min: {probmin.numConstraints()}')
    print()
    print('Time:')
    print(f'- (real for min) {probmin.solutionTime}')
    print(f'- (CPU for min) {probmin.solutionCpuTime}')
    print()
    print(f'Solve status for min: {LpStatus[probmin.status]}')
    print(f'Objective value for min: {probmin.objective.value()}')

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

    print('Le chemin elementaire le plus leger de F est:')

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
