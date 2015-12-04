#!/usr/bin/env python
import csv
import ipdb
import util
import backtracking
player_filename = "./SalariesData/DKSalaries11.02.2015.csv"
positions = ['PG', 'PF', 'SG','SF', 'C', 'Util', 'G', 'F']
TOTAL_SALARY_LIMIT = 50000

def make_player_dict():
    with open(player_filename) as f:
        headers = f.readline().split(',')
        headers = [''.join(e for e in header if e.isalnum()) for header in headers]
        reader = csv.DictReader(f, fieldnames=headers)
        result = {}
        i = 40
        for row in reader:
            if i == 0: break
            i -= 1
            if row["AvgPointsPerGame"] < 10:
                continue
            row["Position"] = get_possible_positions(row["Position"])
            row["Salary"] = int(row["Salary"])
            row["Points"] = float(row["AvgPointsPerGame"])
            print "salary for {} was:{}".format(row["Name"], row["Salary"])
            result[row["Name"]] = row
        return result

def get_possible_positions(pos):
    result = [pos, 'Util']
    if pos == 'C':
        return result
    else:
        result.append(pos[1])
        return result

def get_players_who_can_fill_position(pos, players):
    result = []
    for player_name in players.keys():
        if pos in players[player_name]["Position"]:
            result.append(player_name)
    return result

def add_position_variables(csp, players):
    for position in positions:
        domain = get_players_who_can_fill_position(position, players)
        csp.add_variable(position, domain)
    print "Finished adding position variables"

def add_same_player_constraints(csp, players):
    for pos1 in positions:
        for pos2 in positions:
            if pos1 != pos2:
                csp.add_binary_factor(pos1, pos2, lambda p1, p2: p1 != p2)
    print "Finished adding player constraints"

def add_salary_constraints(csp, players):
    sum_var = util.get_sum_variable(csp, "salary", positions, TOTAL_SALARY_LIMIT + 1, players)
    csp.add_unary_factor(sum_var, lambda x: x <= TOTAL_SALARY_LIMIT)
    print "Finished adding salary constraints"

def add_weights(csp, players):
    for position in positions:
        csp.add_unary_factor(position, lambda player_name: players[player_name]["Points"])

def main():
    csp = util.CSP()
    #Read in players
    players = make_player_dict()
    #Make a variable for each position
    add_position_variables(csp, players)
    #Ensure no position chooses the same player as another
    add_same_player_constraints(csp, players)
    #Ensure that total salary is under the limit
    add_salary_constraints(csp, players)
    #Add assignment weights
    add_weights(csp, players)

    search = backtracking.BacktrackingSearch()
    best_team = search.solve(csp, True, True) # TODO check that these work :  MCV and AC3
    total_cost = 0
    #ipdb.set_trace()
    print "Best Team was:"
    for variable in best_team:
        if not isinstance(variable, str): continue
        print players[best_team[variable]]
        total_cost += players[best_team[variable]]["Salary"]

    print "Total cost was: {}".format(total_cost)
"""
def add_team_size_factors(csp, players):
    # Constrain team size to range(5, 9)
     sum_var = util.get_sum_variable(csp, "team_size", players.keys(), len(players.keys()))
   csp.add_unary_factor(sum_var, lambda x: x <= 8 and x >= 8)

def add_player_variables(csp, players):
    for player_name in players.keys():
        print "adding variable for player {}".format(player_name)
        domain = [(x, pos) for pos in players[player_name]["Position"] for x in (0,1)]
        csp.add_variable(player_name, domain)

def add_weights(csp, players):
    for player in players.keys():
        player_weight = float(players[player]["AvgPointsPerGame"]) #TODO maybe log this?
        def weight_factor(val):
            return player_weight #TODO multiply by val[0]
        #csp.add_unary_factor(player, weight_factor) #TODO should this be times the val?

def add_position_factors(csp, players):
    def chosen_and_not_same_pos(val1, val2):
        if val1[0] and val2[0]: # then both chosen
            return val1[1] != val2[1] # check that positions not equal
        return True

    for i, player1 in enumerate(players.keys()):
        for j, player2 in enumerate(players.keys()):
            if j > i:
                csp.add_binary_factor(player1, player2, chosen_and_not_same_pos)
"""
if __name__ == "__main__":
    main()
