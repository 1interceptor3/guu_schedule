from bs4 import BeautifulSoup
import requests

html = requests.request('GET', 'https://guu.ru/%d1%81%d1%82%d1%83%d0%b4%d0%b5%d0%bd%d1%82%d0%b0%d0%bc/%d1%80%d0%b0%d1%81%d0%bf%d0%b8%d1%81%d0%b0%d0%bd%d0%b8%d0%b5-%d1%81%d0%b5%d1%81%d1%81%d0%b8%d0%b9/schedule').text
bs_obj = BeautifulSoup(html, 'html.parser')

for i in bs_obj.findAll('span', attrs={'class': 'doc-unit-title'}):
    if 'ОЗФО' in i.get_text():
        print(i)
