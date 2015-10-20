import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import html5lib
from collections import Counter

playersFile = './DKSalaries.csv'
players =  pd.read_csv(playersFile)
players = players.sort('AvgPointsPerGame', ascending=False)
bank = 50000
minCost = 4000
team = []


for n in range(2):
    for i, position in enumerate(pd.unique(players.Position.ravel())):
        currPosition = players.loc[players['Position'] == position]
        topPlayer = currPosition.iloc[n]
        if (bank - float(topPlayer['Salary'])) >= 0:
            team.append(topPlayer['Name'])
            bank -= float(topPlayer['Salary'])

print team
print 'Money Remaining: ',bank



