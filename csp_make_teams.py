#!/usr/bin/env python
import csv
import util
import backtracking
player_filename = "./DKSalaries11.2.2015.csv"

def make_player_dict():
    with open(player_filename) as f:
        headers = f.readline().split(',')
        headers = [''.join(e for e in header if e.isalnum()) for header in headers]
        reader = csv.DictReader(f, fieldnames=headers)
        result = {}
        for row in reader:
            row["Position"] = get_possible_positions(row["Position"])
            result[row["Name"]] = row
        return result

def get_possible_positions(pos):
    result = [pos, 'Util']
    if pos == 'C':
        return result
    else:
        result.append(pos[1])
        return result

def main():
    csp = util.CSP()
    players = make_player_dict()
    add_player_variables(csp, players)
    add_factors(csp, players)
    search = backtracking.BacktrackingSearch()
    search.solve(csp, True, True)

def add_factors(csp, players):
    #TODO maybe make maxsum lower
    #sum_var = util.get_sum_variable(csp, "team", players.keys(), 15)
    sum_var = util.get_sum_variable(csp, "test", players.keys(), 15)
    csp.add_unary_factor(sum_var, lambda x: x <= 10 and x >= 5)

def add_player_variables(csp, players):
    for player_name in players.keys():
        domain = [0, 1]#[(x, pos) for pos in players[player_name]["Position"] for x in (0,1)]
        csp.add_variable(player_name, domain)

if __name__ == "__main__":
    main()


