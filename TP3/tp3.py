# -*- coding=utf-8 -*-

"""TODO: DESCRIPTION."""

# from pathlib import Path  # built-in usefull Path class

from pulp import PULP_CBC_CMD, LpMinimize, LpProblem, LpVariable, LpBinary, lpSum


# ============================================================================ #
#                                  SET MODEL                                   #
# ============================================================================ #


def set_parking_optimal(n, lamda, L ):
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
    # TODO: set variables
    variable_x = {i: LpVariable(f'voiture{i}_cote_gauche', lowBound=0, cat=LpBinary)  for i in N}
    variable_G = LpVariable(f'cote_gauche', lowBound=0)
    variable_D = LpVariable(f'cote_droit', lowBound=0)
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


    prob += (T >= variable_G), f'minmax_G',
    prob += (T >= variable_D), f'minmax_D',
    prob += (variable_G == lpSum(lamda[i] * variable_x[i] for i in N)), f'cote_G',
    prob += (L - variable_G== variable_D), f'cote_D',


    return prob, T, variable_G, variable_D, variable_x


# ============================================================================ #
#                               SOLVE WITH DATA                                #
# ============================================================================ #
def solve_parking(n, lamda, L):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Set data
    # ------------------------------------------------------------------------ #
    # TODO: set data

    # ------------------------------------------------------------------------ #
    # Solve the problem using the model
    # ------------------------------------------------------------------------ #
    prob, T, variable_G, variable_D, variable_x = set_parking_optimal(n, lamda, L)

    # Coin Branch and Cut solver is used to solve the instanced model
    # TODO: change the log path file
    prob.solve(
        PULP_CBC_CMD(
            msg=False, logPath=str('./CBC_parking_u.log'),
        ),
    )
    # ------------------------------------------------------------------------ #
    # Print the solver output
    # ------------------------------------------------------------------------ #
    print_log_output(prob, variable_x, T)


# ============================================================================ #
#                                   UTILITIES                                  #
# ============================================================================ #
def print_log_output(prob: LpProblem, variable_x, T ):
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


    print( 'cote_droit' )
    for i in range (15):
      if variable_x[i].value() == 0:
         print(i + 1)

    print('cote_gauche')
    for i in range(15):
        if variable_x[i].value() == 1:
            print(i + 1)


if __name__ == '__main__':

    lamda = {0: 4.0, 1: 4.5, 2: 3.0, 3: 4.1, 4: 2.4, 5: 4.2, 6: 3.7, 8: 3.2, 7: 3.5, 9: 4.5, 10: 2.3, 11: 3.3, 12: 3.8, 13: 4.6, 14: 3.0}
    m = 2
    n = 15
    L= sum(lamda[i] for i in lamda)
    solve_parking(n, lamda, L)
