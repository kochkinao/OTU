import os
import pprint
import sys
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from settings import SOURCE_DIR

if __name__ == '__main__':
    response = requests.get('https://spmi.ru/raspisanie-zanyatiy')
    soup = BeautifulSoup(response.text, 'lxml')
    body = soup.find('body')
    div = body.find(class_='field__item')
    uls = div.find_all('ul')
    links = []
    for ul in uls:
        for li in ul.find_all('li'):
            links.append(li.find('a'))
    files = ['https://spmi.ru'+link['href'] for link in links]
    pprint.pp(files)
    for file in tqdm(files, file=sys.stdout):
        response = requests.get(file)
        with open(os.path.join(SOURCE_DIR, file.split('/')[-1]), 'wb') as file:
            file.write(response.content)