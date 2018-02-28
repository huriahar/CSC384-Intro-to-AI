'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = kenken_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the KenKen puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only 
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only n-ary 
      all-different constraints for both the row and column constraints. 

3. kenken_csp_model (worth 20/100 marks) 
    - A model built using your choice of (1) binary binary not-equal, or (2) 
      n-ary all-different constraints for the grid.
    - Together with KenKen cage constraints.

'''

from operator import mul
from cspbase import *
import itertools, functools

def binary_ne_grid(kenken_grid):
    N = kenken_grid[0][0]
    # Generate the domain
    domain = list(range(1, N+1))

    # Generate a list of variables
    variables = []
    for i in range(1, N+1):
        var_row = []
        for j in range(1, N+1):
            var_row.append(Variable('Var{}{}'.format(i, j), domain))
        variables.append(var_row)

    constraints = []

    # Add satisfying tuples
    satisfying_tuples = []
    for tup in itertools.product(domain, domain):
        if tup[0] != tup[1]:
            satisfying_tuples.append(tup)

    # Add row constraints Ex. 11 != 12 11 != 13 12 != 13 for row1
    for i in range(1, N+1):
        for j in range(1, N+1):
            for k in range(2, N+1):
                if j < k:
                    constraint = Constraint("C(Var{}{},Var{}{})".format(i, j, i, k), [variables[i-1][j-1], variables[i-1][k-1]])
                    constraint.add_satisfying_tuples(satisfying_tuples)
                    constraints.append(constraint)


    # Add col constraints Ex. 11 != 21 11 != 31 21 != 31 for col1
    for i in range(1, N+1):
        for j in range(1, N+1):
            for k in range(2, N+1):
                if i < k:
                    constraint = Constraint("C(Var{}{},Var{}{})".format(i, j, k, j), [variables[i-1][j-1], variables[k-1][j-1]])
                    constraint.add_satisfying_tuples(satisfying_tuples)
                    constraints.append(constraint)

    # Flatten the 2-D variables matrix to a list
    variables = list(itertools.chain(*variables))

    # Create CSP
    csp = CSP("binaryNEKenKen", variables)
    for con in constraints:
        csp.add_constraint(con)

    return csp, variables


def nary_ad_grid(kenken_grid):
    N = kenken_grid[0][0]
    # Generate the domain
    domain = list(range(1, N+1))

    # Generate a list of variables
    variables = []
    for i in range(1, N+1):
        var_row = []
        for j in range(1, N+1):
            var_row.append(Variable('Var{}{}'.format(i, j), domain))
        variables.append(var_row)

    constraints = []

    # Add satisfying tuples
    satisfying_tuples = []
    for tup in itertools.permutations(domain, N):
        satisfying_tuples.append(tup)

    # Add row constraints i.e. 11 != 12 != 13
    for row in range(1, N+1):
        constraint = Constraint("Row{}Con".format(row), variables[row-1])
        constraint.add_satisfying_tuples(satisfying_tuples)
        constraints.append(constraint)

    # Add col constraints i.e. 11 != 21 != 31
    for col in range(1, N+1):
        constraint = Constraint("Col{}Con".format(col), [row[col-1] for row in variables])
        constraint.add_satisfying_tuples(satisfying_tuples)
        constraints.append(constraint)

    # Flatten the 2-D variables matrix to a list
    variables = list(itertools.chain(*variables))

    # Create CSP
    csp = CSP("naryNEKenKen", variables)
    for con in constraints:
        csp.add_constraint(con)

    return csp, variables

def kenken_csp_model(kenken_grid):
    N = kenken_grid[0][0]
    # Generate the domain
    domain = list(range(1, N+1))

    # Generate a matrix of variables
    variables = []
    for i in range(1, N+1):
        var_row = []
        for j in range(1, N+1):
            var_row.append(Variable('Var{}{}'.format(i, j), domain))
        variables.append(var_row)

    constraints = []
    # Operation constraints
    for cageIdx in range(1, len(kenken_grid)):
        cage = kenken_grid[cageIdx]
        if len(cage) > 2:
            operator = cage[-1]
            target = cage[-2]
            cageVariables = []
            cageVariablesDomain = []
            for cageVar in cage[:-2]:
                i = cageVar//10
                j = cageVar%10
                cageVariables.append(variables[i-1][j-1])
                cageVariablesDomain.append(domain)

            constraint = Constraint('Cage{}'.format(cageIdx), cageVariables)

            satisfying_tuples = []
            for tup in itertools.product(*cageVariablesDomain):
                # Addition
                if operator == 0:
                    if sum(tup) == target and tup not in satisfying_tuples:
                        satisfying_tuples.append(tup)

                # Subtraction
                elif operator == 1:
                    for perm in itertools.permutations(tup):
                        diff = perm[0]
                        for i in range(1, len(perm)):
                            diff -= perm[i]
                        if diff == target and tup not in satisfying_tuples:
                            satisfying_tuples.append(tup)

                # Division
                elif operator == 2:
                    for perm in itertools.permutations(tup):
                        quotient = perm[0]
                        for i in range(1, len(perm)):
                            quotient //= perm[i]
                        if quotient == target and tup not in satisfying_tuples:
                            satisfying_tuples.append(tup)

                # Multiplication
                elif operator == 3:
                    if functools.reduce(mul, tup) == target and tup not in satisfying_tuples:
                        satisfying_tuples.append(tup)

            constraint.add_satisfying_tuples(satisfying_tuples)
            constraints.append(constraint)

        # len(cage) <= 2
        else:
            # First element of cage = Variable
            # Second element = value on the variable
            target = cage[-1]
            i = cage[0]//10
            j = cage[0]%10
            variables[i-1][j-1] = Variable('Var{}{}'.format(i, j), [target])

    satisfying_tuples = []
    for tup in itertools.permutations(domain, N):
        satisfying_tuples.append(tup)

    # Add row constraints i.e. 11 != 12 != 13
    for row in range(1, N+1):
        constraint = Constraint("Row{}Con".format(row), variables[row-1])
        constraint.add_satisfying_tuples(satisfying_tuples)
        constraints.append(constraint)

    # Add col constraints i.e. 11 != 21 != 31
    for col in range(1, N+1):
        constraint = Constraint("Col{}Con".format(col), [row[col-1] for row in variables])
        constraint.add_satisfying_tuples(satisfying_tuples)
        constraints.append(constraint)

    # Flatten the 2-D variables matrix to a list
    variablesList = list(itertools.chain(*variables))

    # Create CSP
    csp = CSP("KenKenModel", variablesList)
    for con in constraints:
        csp.add_constraint(con)

    return csp, variables
