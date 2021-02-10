from bs4 import BeautifulSoup
from openpyxl import load_workbook
import requests


# html = requests.request(
#     'GET', 'https://guu.ru/%d1%81%d1%82%d1%83%d0%b4%d0%b5%d0%bd%d1%82%d0%b0%d0%bc/%d1%80%d0%b0%d1%81%d0%bf%d0%b8%d1%81%d0%b0%d0%bd%d0%b8%d0%b5-%d1%81%d0%b5%d1%81%d1%81%d0%b8%d0%b9/schedule'
# )
# bs_obj = BeautifulSoup(html.text, 'html.parser')
# base_url = 'https://guu.ru'
#
# for i in bs_obj.findAll('span', attrs={'class': 'doc-unit-title'}):
#     if 'ОЗФО' in i.get_text():
#         relative_path = i.parent.attrs['href']
#         file_name = relative_path.split('/')[-1]
#         html_file = requests.request('GET', base_url + relative_path)
#         with open(file_name, 'wb') as file:
#             file.write(html_file.content)
#         break


def make_obj(url):
    html = requests.request('GET', url)
    bs_obj = BeautifulSoup(html.text, 'html.parser')
    return bs_obj


class Guu:
    link_schedule = 'https://guu.ru/%d1%81%d1%82%d1%83%d0%b4%d0%b5%d0%bd%d1%82%d0%b0%d0%bc/%d1%80%d0%b0%d1%81%d0%bf' \
                    '%d0%b8%d1%81%d0%b0%d0%bd%d0%b8%d0%b5-%d1%81%d0%b5%d1%81%d1%81%d0%b8%d0%b9/schedule'
    base_url = 'https://guu.ru'

    def download_file(self):
        obj = make_obj(self.link_schedule)
        for i in obj.findAll('span', attrs={'class': 'doc-unit-title'}):
            if 'ОЗФО' in i.get_text():
                relative_path = i.parent.attrs['href']
                file_name = relative_path.split('/')[-1]
                html_file = requests.request('GET', self.base_url + relative_path)
                with open(file_name, 'wb') as file:
                    file.write(html_file.content)
                return file_name

    def load_excel(self, file_name=None):
        wb = load_workbook(file_name)
        return wb.sheetnames


guu_obj = Guu()
excel = guu_obj.download_file()
print(guu_obj.load_excel(excel))
