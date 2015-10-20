import requests
from bs4 import BeautifulSoup
import csv

# Note: this script was inspired by https://first-web-scraper.readthedocs.org/en/latest/ 
# and http://www.danielforsyth.me/exploring_nba_data_in_python/

url = 'http://espn.go.com/nba/teams'
response = requests.get(url)
html = response.content
soup = BeautifulSoup(html)

teams = []
prefix_1 = []
prefix_2 = []


tables = soup.find_all('ul', attrs={'class': 'medium-logos'})

for table in tables:
	lis = table.find_all('li')
	for li in lis:
		info = li.h5.a
		teams.append(info.text)
		url = info['href']
		prefix_1.append(url.split('/')[-2])
		prefix_2.append(url.split('/')[-1])

list_of_rows = []
for i in xrange(0, len(teams)):
	list_of_rows.append([teams[i], prefix_1[i], prefix_2[i]])

print list_of_rows

outfile = open('./teams.csv', 'wb')
writer = csv.writer(outfile)
writer.writerow(['team', 'prefix_1', 'prefix_2'])
writer.writerows(list_of_rows)

# print teams
# print len(teams)
# print prefix_1
# print prefix_2




