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

from cspbase import *
import itertools

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
    # Add row constraints i.e. 11 != 12 11 != 13 12 != 13 for row1
    for i in range(1, N+1):
        for j in range(1, N+1):
            for k in range(2, N+1):
                if j < k:
                    constraint = Constraint("C(Var{}{},Var{}{})".format(i, j, i, k), [variables[i-1][j-1], variables[i-1][k-1]])
                    constraints.append(constraint)


    # Add col constraints i.e. 11 != 21 11 != 31 21 != 31
    for i in range(1, N+1):
        for j in range(1, N+1):
            for k in range(2, N+1):
                if i < k:
                    constraint = Constraint("C(Var{}{},Var{}{})".format(i, j, k, j), [variables[i-1][j-1], variables[k-1][j-1]])
                    constraints.append(constraint)

    # Add satisfying tuples
    for con in constraints:
        satisfying_tuples = []
        for tup in itertools.product(domain, domain):
            if tup[0] != tup[1]:
                satisfying_tuples.append(tup)
        con.add_satisfying_tuples(satisfying_tuples)

    variables = list(itertools.chain(*variables))

    # Create CSP
    csp = CSP("binaryNEKenKen", variables)
    for con in constraints:
        csp.add_constraint(con)

    return csp, variables


def nary_ad_grid(kenken_grid):
    # TODO! IMPLEMENT THIS!
    pass

def kenken_csp_model(kenken_grid):
    # TODO! IMPLEMENT THIS!
    pass