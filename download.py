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
import os
import zipfile

def login(username, token, url):
  login_args = {'user': config['user']['username'], 'token': config['user']['token'], 'script': 'true'}
  response = requests.post(config['kattis']['loginurl'], data=login_args)

  if response.status_code != 200:
    print('Bad login')
    exit(1)
  return response

# Check all pages until table length == 0 with page option
def get_solved(problems_url, cookies):
  solved = []
  problems_options = {'order': 'problem_difficulty', 'show_solved': 'on',
      'show_tried': 'off', 'show_untried': 'off', 'page': 0, 'script': 'true'}
  
  while True:
    print(f'Gathering names of solved from page {problems_options["page"]}...')
    problems = requests.get(problems_url, cookies=cookies, params=problems_options)
    if problems.status_code != 200:
      print('Failed to load solved problems')
      exit(1)
    
    problems_soup = bs4.BeautifulSoup(problems.text, 'lxml')
    table = problems_soup.find_all('td', {'class': 'name_column'})

    if len(table) == 0:
      break
    for t in table:
      solved.append(t.find('a').get('href').split('/')[-1])
    problems_options['page'] += 1
  return solved

def mkdir(dirname, relpath=None):
  if not os.path.exists(dirname):
    os.mkdir(dirname)
    return True
  return False

def download(base_url, user_url, sub_url, problem_name, cookies):
  problem_url = user_url + f'/{problem_name}'
  response = requests.get(problem_url, cookies=cookies)
  sub_soup = bs4.BeautifulSoup(response.text, 'lxml')
  table = sub_soup.find('tbody').find_all('tr')
  ids = []
  for row in table:
    if row.find('span', {'class': 'accepted'}):
      ids.append(row.find('td', {'class': 'submission_id'}).find('a').get('href').split('/')[-1])
  
  for i in ids:
    sub_response = requests.get(f'{sub_url}/{i}', cookies=cookies)
    button_soup = bs4.BeautifulSoup(sub_response.text, 'lxml')
    download_url = button_soup.find_all('a', {'class': 'btn'})[-2].get('href')
    mkdir(i)
    print(f'Downloading submission {i}: {download_url.split("/")[-1]}...')
    with open(os.path.join(i, download_url.split('/')[-1]), 'wb') as f:
      f.write(requests.get(base_url + download_url, cookies=cookies, allow_redirects=True).content)
  print(f'Finished with {problem_name}')
if __name__ == '__main__':
  # Open config file
  config = configparser.ConfigParser()
  config.read('.kattisrc')

  # Login to kattis using post request
  username = config['user']['username']
  token = config['user']['token']
  login_url = config['kattis']['loginurl']
  login_response = login(username, token, login_url)
  print('Successful login')

  base_url = f'https://{config["kattis"]["hostname"]}' 
  
  problems_url = f'{base_url}/problems'
  solved = get_solved(problems_url, login_response.cookies)
  
  submissions_url = f'{base_url}/users/{username}/submissions'
  single_sub_url = f'{base_url}/submissions'
  
  mkdir('solved')
  os.chdir(os.path.join('solved'))
  for s in solved:
    if mkdir(s):
      print(f'"{s}" directory created')
    else:
      print(f'"{s}" directory exists. Skipping')
      continue
    os.chdir(os.path.join(s))
    download(base_url, submissions_url, single_sub_url, s, login_response.cookies)
    os.chdir('..')

