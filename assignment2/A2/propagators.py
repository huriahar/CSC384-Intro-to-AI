'''
This file will contain different constraint propagators to be used within 
bt_search.

---
A propagator is a function with the following header
    propagator(csp, newly_instantiated_variable=None)

csp is a CSP object---the propagator can use this to get access to the variables 
and constraints of the problem. The assigned variables can be accessed via 
methods, the values assigned can also be accessed.

newly_instantiated_variable is an optional argument. SEE ``PROCESSING REQUIRED''
if newly_instantiated_variable is not None:
    then newly_instantiated_variable is the most
    recently assigned variable of the search.
else:
    propagator is called before any assignments are made
    in which case it must decide what processing to do
    prior to any variables being assigned. 

The propagator returns True/False and a list of (Variable, Value) pairs, like so
    (True/False, [(Variable, Value), (Variable, Value) ...]

Propagators will return False if they detect a dead-end. In this case, bt_search 
will backtrack. Propagators will return true if we can continue.

The list of variable value pairs are all of the values that the propagator 
pruned (using the variable's prune_value method). bt_search NEEDS to know this 
in order to correctly restore these values when it undoes a variable assignment.

Propagators SHOULD NOT prune a value that has already been pruned! Nor should 
they prune a value twice.

---

PROCESSING REQUIRED:
When a propagator is called with newly_instantiated_variable = None:

1. For plain backtracking (where we only check fully instantiated constraints)
we do nothing...return true, []

2. For FC (where we only check constraints with one remaining 
variable) we look for unary constraints of the csp (constraints whose scope 
contains only one variable) and we forward_check these constraints.

3. For GAC we initialize the GAC queue with all constaints of the csp.

When a propagator is called with newly_instantiated_variable = a variable V

1. For plain backtracking we check all constraints with V (see csp method
get_cons_with_var) that are fully assigned.

2. For forward checking we forward check all constraints with V that have one 
unassigned variable left

3. For GAC we initialize the GAC queue with all constraints containing V.

'''

from collections import deque

def prop_BT(csp, newVar=None):
    '''
    Do plain backtracking propagation. That is, do no propagation at all. Just 
    check fully instantiated constraints.
    '''
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []

def prop_FC(csp, newVar=None):
    constraintsToCheck = []
    valuesToPrune = []
    if not newVar:
        # Check all the constraints which have only 1 variable in their scope
        constraintsToCheck = [constraint for constraint in csp.get_all_cons() if (len(constraint.get_scope()) == 1)]
    else:
        # Check for constraints with 1 unassigned variable which have newVar in them
        constraintsToCheck = csp.get_cons_with_var(newVar)

    for constraint in constraintsToCheck:
        if constraint.get_n_unasgn() == 1:
            unassignedVariable = constraint.get_unasgn_vars()[0]
            for val in unassignedVariable.cur_domain():
                # If setting unassignedVariable to val together with previous
                # assignments to variables in scope constraint falsifies the constraint
                # then remove val from curDom[unassignedVariable]
                if not constraint.has_support(unassignedVariable, val):
                    toPrunePair = (unassignedVariable, val)
                    if toPrunePair not in valuesToPrune:
                        valuesToPrune.append(toPrunePair)
                        unassignedVariable.prune_value(val)

            # If curDom[unassignedVariable] = {} -> DWO
            if unassignedVariable.cur_domain_size() == 0:
                return False, valuesToPrune

    return True, valuesToPrune

def prop_GAC(csp, newVar=None):
    '''
    Do GAC propagation. If newVar is None we do initial GAC enforce processing 
    all constraints. Otherwise we do GAC enforce with constraints containing 
    newVar on GAC Queue.
    '''
    constraintsToCheck = []
    valuesToPrune = []
    if not newVar:
        constraintsToCheck = csp.get_all_cons()
    else:
        constraintsToCheck = csp.get_cons_with_var(newVar)

    GACQueue = deque(constraintsToCheck)

    while len(GACQueue):
        constraint = GACQueue.popleft()
        for variable in constraint.get_scope():
            for val in variable.cur_domain():
                if not constraint.has_support(variable, val):
                    toPrunePair = (variable, val)
                    if toPrunePair not in valuesToPrune:
                        valuesToPrune.append(toPrunePair)
                        variable.prune_value(val)

                    if variable.cur_domain_size() == 0:
                        # DWO
                        GACQueue.clear()
                        return False, valuesToPrune
                    else:
                        # Add dependent constaints in GACQueue
                        for dependentConstraint in csp.get_cons_with_var(variable):
                            if dependentConstraint not in GACQueue:
                                GACQueue.append(dependentConstraint)

    return True, valuesToPrune
