# -*- coding=utf-8 -*-

"""TODO: DESCRIPTION."""

# from pathlib import Path  # built-in usefull Path class

from pulp import PULP_CBC_CMD, LpMinimize, LpProblem, LpVariable, LpBinary, lpSum


# ============================================================================ #
#                                  SET MODEL                                   #
# ============================================================================ #


def set_parking_optimal(n, m, lamda, epsilon, bigM ):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Linear problem with maximization
    # ------------------------------------------------------------------------ #
    prob = LpProblem(name='Parking_Optimal', sense=LpMinimize)
    # FIXME: it is not always a maximization problem ...

    # ------------------------------------------------------------------------ #
    # The variables
    # ------------------------------------------------------------------------ #
    N = [i for i in range(n)]
    M = [j for j in range(m)]
    # TODO: set variables
    variable_x = {(i, j): LpVariable(f'voiture{i}_cote_{j}', lowBound=0, cat=LpBinary) for j in M for i in N}
    variable_t = {i: LpVariable(f'cote_{i}', lowBound=0) for i in M}
    variable_y = {j: LpVariable(f'cote_y_{j}', lowBound=0, cat=LpBinary) for j in M}
    variable_z = {j: LpVariable(f'cote_Z_{j}', lowBound=0, cat=LpBinary) for j in M}
    T = LpVariable('max', lowBound=0)

    # ------------------------------------------------------------------------ #
    # The objective function
    # ------------------------------------------------------------------------ #
    # TODO: write the objective function

    prob += T, 'maximum'

    # ------------------------------------------------------------------------ #
    # The constraints
    # ------------------------------------------------------------------------ #
    # TODO: write constraints
    # Question1
    for j in M:
        prob += (T >= variable_t[j]), f'minmax_{j}',

    for j in M:
        prob += (variable_t[j] == lpSum(lamda[i] * variable_x[(i, j)] for i in N)), f'cote_{j}',


     # Question2-a

    prob += (variable_t[1] <= 20.0), f'coteborne',

    # Question2-b
    for j in M:
        prob += (variable_t[j] <= 16 - epsilon + (bigM * (1 - variable_z[j]))), f'const_z_{j}',
        prob += (lpSum(variable_z[j]) == 1.0), f'const_z_i_{j}',

    # Question2-c
    for i in N:
        prob += (lamda[i] * variable_x[(i, 0)] <= 4.0), f'voiture_D_con_{i}',

    # Question2-d
    for j in M:
        prob += 10 + epsilon - (bigM * variable_y[j]) <= variable_t[1], f'BigMun_{j}'
        prob += 10 + (bigM * (1 - variable_y[j])) >= variable_t[1], f'BigMdeux_{j}'
        prob += 13 - epsilon - (bigM * variable_y[j]) >= variable_t[0], f'BigMtrois_{j}'

    return prob, T, variable_t, variable_y, variable_x, variable_z


# ============================================================================ #
#                               SOLVE WITH DATA                                #
# ============================================================================ #
def solve_parking(n, m, lamda, epsilon, bigM, cote):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Set data
    # ------------------------------------------------------------------------ #
    # TODO: set data

    # ------------------------------------------------------------------------ #
    # Solve the problem using the model
    # ------------------------------------------------------------------------ #
    prob, T, variable_t, variable_y, variable_x, variable_z = \
        set_parking_optimal(n, m, lamda, epsilon, bigM )

    # Coin Branch and Cut solver is used to solve the instanced model
    # TODO: change the log path file
    prob.solve(
        PULP_CBC_CMD(
            msg=False, logPath=str('./CBC_parking.log'),
        ),
    )
    # ------------------------------------------------------------------------ #
    # Print the solver output
    # ------------------------------------------------------------------------ #
    print_log_output(prob, variable_x, T, cote)


# ============================================================================ #
#                                   UTILITIES                                  #
# ============================================================================ #
def print_log_output(prob: LpProblem, variable_x, T, cote):
    """Print the log output and problem solutions."""
    print()
    print('-' * 40)
    print('Stats')
    print('-' * 40)
    print()
    print(f'Number variables: {prob.numVariables()}')
    print(f'Number constraints: {prob.numConstraints()}')
    print()
    print('Time:')
    print(f'- (real) {prob.solutionTime}')
    print(f'- (CPU) {prob.solutionCpuTime}')
    print()

    print(f'Objective value: {prob.objective.value()}')

    print()
    print('-' * 40)
    print("Variables' values")
    print('-' * 40)
    print()
    # TODO: you can print variables value here

    print('-' * 40)
    print(f'minmaxobj={T.value()}')
    print('-' * 40)

    u=0
    for j in range(m):

        if (j == 0):
            print( cote[u] )
            u= u+1
        else:
            print( cote[u] )

        for i in range(n):
            if variable_x[(i, j)].value() == 1:
                print(i + 1)


if __name__ == '__main__':

    epsilon = 0.000001
    bigM = 1000000
    lamda = {0: 4.0, 1: 4.5, 2: 3.0, 3: 4.1, 4: 2.4, 5: 4.2, 6: 3.7, 8: 3.2, 7: 3.5, 9: 4.5, 10: 2.3, 11: 3.3, 12: 3.8, 13: 4.6, 14: 3.0}
    cote = ['cote_droit','cote_gauche']
    m = len(cote)
    n = len(lamda)
    solve_parking(n, m, lamda , epsilon, bigM, cote)
