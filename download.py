'''
	Filename:    download.py
	Author:      Sean Malloy
	Description: Submission downloader for solved problems on open.kattis.com

	TODO:
	- Authenticator
	- lxml and BeautifulSoup parsing/downloading
	- Might need another module for actually downloading the zip files with the
		source code...
'''

import configparser
import requests
import bs4

# Check all pages until table length == 0 with page option
def get_solved(problems_url):
	problems_options = {'order': 'problem_difficulty', 'show_solved': 'on',
			'show_tried': 'off', 'show_untried': 'off', 'page': 0}
	problems = requests.get(problems_url, data=problems_options)

	if problems.status_code == 200:
		print('Loaded solved problems page OK')
	else:
		print('Failed to load solved problems')
		exit(1)


	problems_soup = bs4.BeautifulSoup(problems.text, 'lxml')
	table = problems_soup.find_all('td', {'class': 'name_column'})

	solved = []
	for t in table:
		solved.append(t.find('a').get('href').split('/')[-1])
		print(solved[-1])

if __name__ == '__main__':
	# Open config file
	config = configparser.ConfigParser()
	config.read('.kattisrc')

	# Login to kattis using post request
	login_args = {'user': config['user']['username'], 'token': config['user']['token'], 'script': 'true'}
	login = requests.post(config['kattis']['loginurl'], data=login_args)

	if login.status_code == 200:
		print('Login OK!')
	else:
		print('Login failed')
		exit(1)

	problems_url = f'https://{config["kattis"]["hostname"]}/problems'
