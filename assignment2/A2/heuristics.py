'''
This file will contain different variable ordering heuristics to be used within
bt_search.

1. ord_dh(csp)
    - Takes in a CSP object (csp).
    - Returns the next Variable to be assigned as per the DH heuristic.
2. ord_mrv(csp)
    - Takes in a CSP object (csp).
    - Returns the next Variable to be assigned as per the MRV heuristic.
3. val_lcv(csp, var)
    - Takes in a CSP object (csp), and a Variable object (var)
    - Returns a list of all of var's potential values, ordered from best value 
      choice to worst value choice according to the LCV heuristic.

The heuristics can use the csp argument (CSP object) to get access to the 
variables and constraints of the problem. The assigned variables and values can 
be accessed via methods.
'''

import random
from copy import deepcopy

def ord_dh(csp):
    # Returns the variable that is involved in the largest number of
    # constraints on other unassigned variables
    constraints = csp.get_all_cons()
    degreesOfVariables = dict()
    for constraint in constraints:
        for variable in constraint.get_unasgn_vars():
            if variable not in degreesOfVariables:
                degreesOfVariables[variable] = constraint.get_n_unasgn()
            else:
                degreesOfVariables[variable] += constraint.get_n_unasgn()

    # Return key with maximum value
    return max(degreesOfVariables, key=degreesOfVariables.get)

def ord_mrv(csp):
    # Returns the variable with the most constrained current domain
    # (i.e. the variable with the fewest legal values)
    unassignedVariables = csp.get_all_unasgn_vars()
    return min(unassignedVariables, key=lambda var: var.cur_domain_size())
    
def val_lcv(csp, var):
    # A value heuristic, that given a variable, chooses the value to be assigned
    # according to the Least Constraining Value heuristic
    # The list is ordered by the value that rules out the fewest values in the
    # remaining variables (i.e. the variable that gives the most flexibility later on)
    # to the value that rules out the most
    varRuleOutCount = dict()
    constraints = csp.get_cons_with_var(var)
    for value in var.cur_domain():
        ruleOutCount = 0
        var.assign(value)
        for constraint in constraints:
            for unassignedVariable in constraint.get_unasgn_vars():
                for unassignedValue in unassignedVariable.cur_domain():
                    if not constraint.has_support(unassignedVariable, unassignedValue):
                        varRuleOutCount += 1
        var.unassign()
        varRuleOutCount[value] = ruleOutCount
    return sorted(varRuleOutCount, key=varRuleOutCount.get)