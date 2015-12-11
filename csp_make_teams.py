#!/usr/bin/env python
import csv
import ipdb
import util
#import backtracking
import beamsearch
import time
player_filename = "./PredictionsData/12.8.2015.csv"
#player_filename = "./SalariesData/DKSalaries11.02.2015.csv"
positions = ['PG', 'PF', 'SG','SF', 'C', 'Util', 'G', 'F']
TOTAL_SALARY_LIMIT = 50000
BEAM_SIZE = 10000


def make_player_dict(player_filename):
    with open(player_filename) as f:
        headers = f.readline().split(',')
        headers = [''.join(e for e in header if e.isalnum()) for header in headers]
        reader = csv.DictReader(f, fieldnames=headers)
        result = {}
        for row in reader:
            if row["AvgPointsPerGame"] < 10:
                continue
            row["Position"] = get_possible_positions(row["Position"])
            row["Salary"] = util.round_up(int(row["Salary"]), 200)
            #row["Salary"] = int(row["Salary"])
            row["Points"] = float(row["AvgPointsPerGame"])
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

def make_teams(player_filename = "./PredictionsData/12.8.2015.csv"):
    csp = util.CSP()
    #Read in players
    players = make_player_dict(player_filename)
    #Make a variable for each position
    add_position_variables(csp, players)
    #Ensure no position chooses the same player as another
    add_same_player_constraints(csp, players)
    #Ensure that total salary is under the limit
    add_salary_constraints(csp, players)
    #Add assignment weights
    add_weights(csp, players)
    #ipdb.set_trace()
    return get_beamsearch_results(csp, players)


def get_beamsearch_results(csp, players):
    search = beamsearch.BeamSearch(players, k = BEAM_SIZE)
    start = time.time()
    best_teams = search.solve(csp) # TODO check that these work :  MCV and AC3
    for best_team in best_teams:
        total_cost = 0
        best_team = best_team[0]

        print "\n one optimal team was:"
        for variable in best_team.keys():
            if not isinstance(variable, str): continue
            print players[best_team[variable]]
            total_cost += players[best_team[variable]]["Salary"]
            print "Total cost was: {}".format(total_cost)
    if best_teams:
        return best_teams[0]
    else:
        return []

if __name__ == "__main__":
    make_teams()
