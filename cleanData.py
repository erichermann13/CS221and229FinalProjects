import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd
import numpy as np

playersFile = './players.csv'

players = pd.read_csv(playersFile)

players['date'] = pd.to_datetime(players.date)

players = players.sort('date')

# Home column will be 1 if the player was on the home team, 0 otherwise
players['Home'] = np.where(players['team'] == players['home_team'], 1, 0)

del players['id']

players.to_csv('./players_clean.csv')