import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, date
import pandas as pd

# Note: this code was strongly borrowed from http://www.danielforsyth.me/exploring_nba_data_in_python/


year = 2015
teamsFile = './teams.csv'
BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/seasontype/2/{2}'
BASE_GAME_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'

csvfile = open(teamsFile, 'rb')
reader = csv.reader(csvfile)
teamsList = list(reader)

game_id = []
dates = []
home_team = []
home_team_score = []
visit_team = []
visit_team_score = []
home_team_wins = []
home_team_losses = []
away_team_wins = []
away_team_losses = []

gamesCount = 0

for i in xrange(1, len(teamsList)):
  currRow = teamsList[i]
  _team = currRow[0]
  print "%s %s %s" % (_team, currRow[1], currRow[2])
  websiteText = requests.get(BASE_URL.format(currRow[1], year, currRow[2]))
  table = BeautifulSoup(websiteText.text).table
  # print table.prettify()
  for row in table.find_all('tr')[1:]:
    # print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    columns = row.find_all('td')
    try:
      _id = columns[2].a['href'].split('?id=')[1]
      # print _id
      _home = True if columns[1].li.text == 'vs' else False
      # print _home
      _other_team = columns[1].find_all('a')[1]['href']
      _other_team = _other_team.split('/')[-1:][0]
      for j in xrange(1, len(teamsList)):
        aRow = teamsList[j]
        if aRow[2] == _other_team:
          _other_team = aRow[0]
          break
      
      _score = columns[2].a.text.split(' ')[0].split('-')
      # print _score
      _won = True if columns[2].span.text == 'W' else False
      # print _won
      game_id.append(_id)

      boxScoreText = requests.get(BASE_GAME_URL.format(_id))
      # print _id
      boxScoreTable = BeautifulSoup(boxScoreText.text).find_all('div', class_='team-info')
      # Counting on the fact that away is first in data, only 2 entries
      away = True
      for element in boxScoreTable:
        recordData = element.find('p').text.split(',')[0][1:]
        # print recordData
        winsAndLosses = recordData.split('-')
        wins, losses = (winsAndLosses[0], winsAndLosses[1])
        if away:
          away_team_wins.append(wins)
          away_team_losses.append(losses)
          away = False
        else:
          home_team_wins.append(wins)
          home_team_losses.append(losses)


      # print "hello"
      # print boxScoreTable.find_all('p')
      # print "#############################################################################"

      home_team.append(_team if _home else _other_team)
      visit_team.append(_team if not _home else _other_team)

      d = datetime.strptime(columns[0].text, '%a, %b %d')
      theYear = year
      if d.month in (10, 11, 12):
        theYear = year - 1
      dates.append(date(theYear, d.month, d.day))
      print dates[-1]

      if _home:
        if _won:
          home_team_score.append(_score[0])
          visit_team_score.append(_score[1])
        else:
          home_team_score.append(_score[1])
          visit_team_score.append(_score[0])
      else:
        if _won:
          home_team_score.append(_score[1])
          visit_team_score.append(_score[0])
        else:
          home_team_score.append(_score[0])
          visit_team_score.append(_score[1])

      gamesCount += 1
      print gamesCount


      # Note that some items in columns will not actually be games
    except:
      pass

 
dic = {'id': game_id, 'date': dates, 'home_team': home_team, 'visit_team': visit_team, 
        'home_team_score': home_team_score, 'visit_team_score': visit_team_score, 'game_id': game_id, 
        'home_team_wins': home_team_wins, 'home_team_losses': home_team_losses, 'away_team_wins': away_team_wins, 
        'away_team_losses': away_team_losses}
        
games = pd.DataFrame(dic).drop_duplicates(cols='id').set_index('id')
print(games)
games.to_csv('./games.csv')
