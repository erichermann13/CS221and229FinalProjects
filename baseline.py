import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import html5lib

playersFile = './players.csv'
players =  pd.read_csv(playersFile)

PaulPierce = players.loc[players['player'] == 'Paul Pierce']
# PaulPierce = PaulPierce.transpose()
mean = PaulPierce.mean()
scorePrediction = mean.loc['AST']*1.5 + mean.loc['PTS']*1 + mean.loc['REB']*1.25 + mean.loc['STL']*2 - mean.loc['TO']*0.5
print scorePrediction