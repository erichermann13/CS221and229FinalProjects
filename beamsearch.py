#!/usr/bin/python
import collections, util, copy, random
from sets import Set
MAX_BANK = 50000
NUM_PLAYERS = 8
AVG_SALARY = 3000
#AVG_SALARY = 4300

class BeamSearch():

    def __init__(self, players_info, k = 10, num_to_return = 3):
        # keeps track of all the optimal assignments
        self.k = k
        self.players_info = players_info
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0
        self.optimalCost = 0
        self.num_to_return = num_to_return

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        # List of all solutions found.
        self.allAssignments = []


    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w


    def solve(self, csp):
        # CSP to be solved.
        self.csp = csp
        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}
        # perform beam search
        self.beam_search()
        #print "optimal assignment", self.optimalAssignment
        return self.optimalAssignments


    def beam_search(self):
        # initialize set of assignments
        results = [ ({}, 0, 0) ]
        positions = ['SG','SF','PG', 'PF', 'C', 'Util', 'G', 'F']

        for n, var in enumerate(positions):
            num_results = len(results)

            for _ in range(num_results):
                # pop last assignment
                partialAssignment, old_weight, old_cost= results.pop(0)

    	   # extend assignments
                for val in self.domains[var]:
                    weight = self.get_delta_weight(partialAssignment, var, val)
                    cost = self.players_info[val]["Salary"]
                    valid_cost = MAX_BANK - (old_cost + cost ) >= (NUM_PLAYERS - (n+1)) * AVG_SALARY

                    # check is salary is valid
                    if weight  > 0 and valid_cost:
                        newAssignment = copy.copy(partialAssignment)
                        newAssignment[var] = val
                        results.append((newAssignment, old_weight + weight, old_cost + cost))

    	    # prune
            #print "pruning from", len(results), "results"
            if len(results) > self.k:
                 results = sorted(results, key=lambda x: x[1]) [ : self.k]

        print "number of optimal results", len(results)
        self.numOptimalAssignments = len(results)
        self.allAssignments = results
        self.optimalAssignment , self.optimalWeight, self.optimalCost = self.allAssignments[0]
        indices = [(i*self.numOptimalAssignments)/self.num_to_return for i in range(self.num_to_return)]
        self.optimalAssignments = [self.allAssignments[i] for i in indices]

