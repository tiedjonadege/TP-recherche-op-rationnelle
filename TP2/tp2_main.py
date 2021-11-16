# -*- coding=utf-8 -*-

"""TODO: DESCRIPTION."""

from pathlib import Path  # built-in usefull Path class

from pulp import *
#import pandas as pd
import numpy as np


from tp2_read_data_files import get_adm_cells_data

# ============================================================================ #
#                                  SET MODEL                                   #
# ============================================================================ #
def set_model_name(adm_cells, row_limits, col_limits):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Linear problem with maximization
    # ------------------------------------------------------------------------ #
    prob = LpProblem(name='set_model_name', sense=LpMaximize)
    # FIXME: it is not always a maximization problem ...

    # ------------------------------------------------------------------------ #
    # The variables
    # ------------------------------------------------------------------------ #
    # TODO: set variables
    variable_names = [str(i)+str(j) for j in range(len(col_limits))
     for i in range( len(row_limits)) ]
    variable_names.sort()
    print("Variable Indices:", variable_names)


    DV_variables = LpVariable.matrix("X", variable_names, cat = "Integer", lowBound= 0 )
    allocation = np.array(DV_variables).reshape(len(row_limits),len(col_limits))
    print("Decision Variable/Allocation Matrix: ")
    print(allocation)
    # ------------------------------------------------------------------------ #
    # The objective function
    # ------------------------------------------------------------------------ #
    # TODO: write the objective function
    obj_func=0
    for i in range(len(row_limits)):
        for j in range(len(col_limits)):
            if (i, j) in adm_cells:
                obj_func += lpSum(allocation[i][j])
    print (obj_func)
    prob += obj_func
    print(prob)

    # ------------------------------------------------------------------------ #
    # The constraints
    # ------------------------------------------------------------------------ #
    # TODO: write constraints
    for i in range(len(row_limits)):
        print(lpSum(allocation[i][j] for j in range(len(col_limits)) if (i,j) in adm_cells) <= row_limits[i] )
        prob += lpSum(allocation[i][j] for j in range(len(col_limits)) if (i, j) in adm_cells) <= row_limits[i] , "rows Constraints " + str(i)

    for j in range(len(col_limits)):
        print(lpSum(allocation[i][j] for i in range(len(row_limits)) if (i,j) in adm_cells) <= col_limits[j])
        prob += lpSum(allocation[i][j] for i in range(len(row_limits)) if (i, j) in adm_cells)  <= col_limits[j] , "col Constraints " + str(j)

    print(prob)
   
    #je veux ecrire sum des j allant jusqu a n des xij <= a li
    #Yt = (1.0/(M*N)) * sum([Y[i][j] for i in range(M) for j in range(N)])
    return prob,allocation


# ============================================================================ #
#                               SOLVE WITH DATA                                #
# ============================================================================ #
def solve_admissible_cells(adm_cells, row_limits, col_limits):
    """TODO: Description."""
    # ------------------------------------------------------------------------ #
    # Set data
    # ------------------------------------------------------------------------ #
    # TODO: set data

    # ------------------------------------------------------------------------ #
    # Solve the problem using the model
    # ------------------------------------------------------------------------ #
    prob, allocation = set_model_name(adm_cells, row_limits, col_limits)
    # Coin Branch and Cut solver is used to solve the instanced model
    # TODO: change the log path file
    prob.solve( PULP_CBC_CMD(msg=False, logPath=Path('tp2_all_results.log')))
    # ------------------------------------------------------------------------ #
    # Print the solver output
    # ------------------------------------------------------------------------ #
    print_log_output(prob,allocation)


# ============================================================================ #
#                                   UTILITIES                                  #
# ============================================================================ #
def print_log_output(prob: LpProblem,allocation):
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

    print(f'Solve status: {LpStatus[prob.status]}')
    print(f'Objective value: {prob.objective.value()}')

    print()
    print('-' * 40)
    print("Variables' values")
    print('-' * 40)
    print()
    # TODO: you can print variables value here

    print("Total Cost:", prob.objective.value())

# Decision Variables

    for v in prob.variables():
        try:
            print(v.name,"=", v.value())
        except:
            print("error couldnt find value")


    print("la total pour chaque ligne et colonne fera:")
    for i in range(len(ROW_LIMITS)):
        print("ligne ", str(i+1))
        print(lpSum(allocation[i][j].value() for j in range(len(COL_LIMITS)) if (i, j) in ADM_CELLS ))

    for j in range(len(COL_LIMITS)):
        print("colonne ", str(j + 1))
        print(lpSum(allocation[i][j].value() for i in range(len(ROW_LIMITS)) if (i, j) in ADM_CELLS))

if __name__ == '__main__':

    for ADM_CELLS, ROW_LIMITS, COL_LIMITS in get_adm_cells_data():
        # adm_cells: list of tuple (row_i, col_j)
        # corresponding to admissible cells
        # row_limits: list of row limits (int)
        # col_limits: list of column limits (int)
        solve_admissible_cells(ADM_CELLS, ROW_LIMITS, COL_LIMITS)



# ============================================================================ #
#                                   solution                                   #
# ============================================================================ #
#----------------------------------------
#Stats
#----------------------------------------

#set_model_name:
#MAXIMIZE
#1*X_00 + 1*X_01 + 1*X_10 + 1*X_12 + 1*X_13 + 1*X_21 + 1*X_24 + 1*X_32 + 1*X_34 + 0
#VARIABLES
#0 <= X_00 Integer
#0 <= X_01 Integer
#0 <= X_10 Integer
#0 <= X_12 Integer
#0 <= X_13 Integer
#0 <= X_21 Integer
#0 <= X_24 Integer
#0 <= X_32 Integer
#0 <= X_34 Integer

#X_00 + X_01 <= 9
#X_10 + X_12 + X_13 <= 10
#X_21 + X_24 <= 15
#X_32 + X_34 <= 2
#X_00 + X_10 <= 7
#X_01 + X_21 <= 5
#X_12 + X_32 <= 9
#X_13 <= 4
#X_24 + X_34 <= 8
#set_model_name:
#MAXIMIZE
#1*X_00 + 1*X_01 + 1*X_10 + 1*X_12 + 1*X_13 + 1*X_21 + 1*X_24 + 1*X_32 + 1*X_34 + 0
#SUBJECT TO
#rows_Constraints_0: X_00 + X_01 <= 9

#rows_Constraints_1: X_10 + X_12 + X_13 <= 10

#rows_Constraints_2: X_21 + X_24 <= 15

#rows_Constraints_3: X_32 + X_34 <= 2

#Demand_Constraints_0: X_00 + X_10 <= 7

#Demand_Constraints_1: X_01 + X_21 <= 5

#Demand_Constraints_2: X_12 + X_32 <= 9

#Demand_Constraints_3: X_13 <= 4

#Demand_Constraints_4: X_24 + X_34 <= 8


#Number variables: 9
#Number constraints: 9

#Time:
#- (real) 0.04389190673828125
#- (CPU) 0.0470000000204891

#Solve status: Optimal
#Objective value: 32.0

#la solution est:

#Total Cost: 32.0
#X_00 = 7.0
#X_01 = 2.0
#X_10 = 0.0
#X_12 = 6.0
#X_13 = 4.0
#X_21 = 3.0
#X_24 = 8.0
#X_32 = 2.0
#X_34 = 0.0

# ============================================================================ #
#== == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==  #


#MAXIMIZE
#1*X_110 + 1*X_112 + 1*X_113 + 1*X_12 + 1*X_13 + 1*X_15 + 1*X_16 + 1*X_17 + 1*X_18 + 1*X_19 + 1*X_29 + 1*X_40 + 1*X_41 + 1*X_412 + 1*X_413 + 1*X_414 + 1*X_42 + 1*X_43 + 1*X_45 + 1*X_46 + 1*X_47 + 1*X_49 + 1*X_51 + 1*X_511 + 1*X_514 + 1*X_54 + 1*X_55 + 1*X_810 + 1*X_811 + 1*X_813 + 1*X_814 + 1*X_85 + 1*X_86 + 1*X_87 + 1*X_88 + 1*X_89 + 1*X_90 + 1*X_91 + 1*X_910 + 1*X_911 + 1*X_912 + 1*X_914 + 1*X_92 + 1*X_95 + 1*X_96 + 1*X_97 + 1*X_98 + 0
#SUBJECT TO
#rows_Constraints_1: X_110 + X_112 + X_113 + X_12 + X_13 + X_15 + X_16 + X_17
# + X_18 + X_19 <= 19

#rows_Constraints_2: X_29 <= 32

#rows_Constraints_3:0 <= 37

#rows_Constraints_4: X_40 + X_41 + X_412 + X_413 + X_414 + X_42 + X_43 + X_45 + X_46 + X_47 + X_49 <= 42

#rows_Constraints_5: X_51 + X_511 + X_514 + X_54 + X_55 <= 24

#rows_Constraints_6:0 <= 38

#rows_Constraints_7:0 <= 40

#rows_Constraints_8: X_810 + X_811 + X_813 + X_814 + X_85 + X_86 + X_87 + X_88 + X_89 <= 29

#rows_Constraints_9: X_90 + X_91 + X_910 + X_911 + X_912 + X_914 + X_92 + X_95+ X_96 + X_97 + X_98 <= 16

#Demand_Constraints_0: X_40 + X_90 <= 3

#Demand_Constraints_1: X_41 + X_51 + X_91 <= 8

#Demand_Constraints_2: X_110 + X_810 + X_910 <= 17

#Demand_Constraints_3: X_511 + X_811 + X_911 <= 15

#Demand_Constraints_4: X_112 + X_412 + X_912 <= 12

#Demand_Constraints_5: X_113 + X_413 + X_813 <= 4

#Demand_Constraints_6: X_414 + X_514 + X_814 + X_914 <= 27

#Demand_Constraints_7: X_12 + X_42 + X_92 <= 17

#Demand_Constraints_8: X_13 + X_43 <= 10

#Demand_Constraints_9: X_54 <= 10

#Demand_Constraints_10: X_15 + X_45 + X_55 + X_85 + X_95 <= 17

#Demand_Constraints_11: X_16 + X_46 + X_86 + X_96 <= 8

#Demand_Constraints_12: X_17 + X_47 + X_87 + X_97 <= 19

#Demand_Constraints_13: X_18 + X_88 + X_98 <= 15

#Demand_Constraints_14: X_19 + X_29 + X_49 + X_89 <= 13

#VARIABLES
#0 <= X_110 Integer
#0 <= X_112 Integer
#0 <= X_113 Integer
#0 <= X_12 Integer
#0 <= X_13 Integer
#0 <= X_15 Integer
#0 <= X_16 Integer
#0 <= X_17 Integer
#0 <= X_18 Integer
#0 <= X_19 Integer
#0 <= X_29 Integer
#0 <= X_40 Integer
#0 <= X_41 Integer
#0 <= X_412 Integer
#0 <= X_413 Integer
#0 <= X_414 Integer
#0 <= X_42 Integer
#0 <= X_43 Integer
#0 <= X_45 Integer
#0 <= X_46 Integer
#0 <= X_47 Integer
#0 <= X_49 Integer
#0 <= X_51 Integer
#0 <= X_511 Integer
#0 <= X_514 Integer
#0 <= X_54 Integer
#0 <= X_55 Integer
#0 <= X_810 Integer
#0 <= X_811 Integer
#0 <= X_813 Integer
#0 <= X_814 Integer
#0 <= X_85 Integer
#0 <= X_86 Integer
#0 <= X_87 Integer
#0 <= X_88 Integer
#0 <= X_89 Integer
#0 <= X_90 Integer
#0 <= X_91 Integer
#0 <= X_910 Integer
#0 <= X_911 Integer
#0 <= X_912 Integer
#0 <= X_914 Integer
#0 <= X_92 Integer
#0 <= X_95 Integer
#0 <= X_96 Integer
#0 <= X_97 Integer
#0 <= X_98 Integer


#----------------------------------------
#Stats
#----------------------------------------

#Number variables: 47
#Number constraints: 25

#Time:
#- (real) 0.06582832336425781
#- (CPU) 0.062000000034458935

#Solve status: Optimal
#Objective value: 143.0

#----------------------------------------
#Variables' values
#----------------------------------------

#Total Cost: 143.0
#X_110 = 0.0 X_112 = 12.0 X_113 = 0.0 X_12 = 0.0 X_13 = 0.0 X_15 = 0.0 X_16 = 7.0 X_17 = 0.0 X_18 = 0.0 X_19 = 0.0 X_29 = 13.0 X_40 = 0.0
#X_41 = 2.0 X_412 = 0.0 X_413 = 4.0 X_414 = 0.0 X_42 = 17.0 X_43 = 0.0 X_45 = 0.0 X_46 = 0.0 X_47 = 19.0 X_49 = 0.0 X_51 = 0.0 X_511 = 14.0
#X_514 = 0.0 X_54 = 10.0 X_55 = 0.0 X_810 = 0.0 X_811 = 0.0 X_813 = 0.0 X_814 = 14.0 X_85 = 0.0 X_86 = 0.0X_87 = 0.0 X_88 = 15.0 X_89 = 0.0
#X_90 = 0.0 X_91 = 0.0 X_910 = 16.0 X_911 = 0.0 X_912 = 0.0 X_914 = 0.0 X_92 = 0.0 X_95 = 0.0 X_96 = 0.0 X_97 = 0.0 X_98 = 0.0
#
#
#
#
#
#
#



