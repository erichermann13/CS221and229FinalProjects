import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np
import html5lib
from collections import Counter

playersFile = './players.csv'
players =  pd.read_csv(playersFile)

new_df = pd.DataFrame()

for player_name in pd.unique(players.player.ravel()):
    curr_player = players.loc[players['player'] == player_name]
    mean = curr_player.mean()
    # curr_player_price = curr_player[0]['price']
    # curr_player_pos = curr_player[0]['pos']
    scorePrediction = mean.loc['AST']*1.5 + mean.loc['PTS']*1 + mean.loc['REB']*1.25 + mean.loc['STL']*2 - mean.loc['TO']*0.5

    print player_name, scorePrediction


