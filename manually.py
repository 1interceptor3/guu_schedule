from bs4 import BeautifulSoup
import openpyxl
from openpyxl.worksheet.merge import MergeCell
from openpyxl.utils import get_column_letter, column_index_from_string
import requests
import os
from db import DataBaseSQLITE


def make_obj(url):
    html = requests.request('GET', url)
    bs_obj = BeautifulSoup(html.text, 'html.parser')
    return bs_obj


def get_excel_file():
    """
    Функция ищет в текущей директории файлы с расширением .xlsx.
    В приоритете вернет которые не начинаются с символа '~', так как это временные файлы, которые создаются при
    открытии.

    :return: строка с названием excel файла в текущей директории
    """
    memory = None
    for i in os.listdir():
        if '.xlsx' in i and not i.startswith('~'):
            return i
        elif '.xlsx' in i:
            memory = i
    return memory


class Guu:
    link_schedule = 'https://guu.ru/%d1%81%d1%82%d1%83%d0%b4%d0%b5%d0%bd%d1%82%d0%b0%d0%bc/%d1%80%d0%b0%d1%81%d0%bf' \
                    '%d0%b8%d1%81%d0%b0%d0%bd%d0%b8%d0%b5-%d1%81%d0%b5%d1%81%d1%81%d0%b8%d0%b9/schedule'
    base_url = 'https://guu.ru'

    def __init__(self):
        self.db_obj = DataBaseSQLITE()

        # Проверка на необходимость обновления файла и на наличие файла
        if self.db_obj.need_to_update() or not get_excel_file():
            # Получаем новое название скачанного файла
            self.excel_file_name = self.download_file()
            print('New file', self.excel_file_name)
            # self.work_with_excel(new=True, file_name=self.excel_file_name)
        else:
            self.excel_file_name = get_excel_file()
            print('Old file', self.excel_file_name)
            # self.work_with_excel(new=False, file_name=self.excel_file_name)
            self.update_from_excel(self.excel_file_name)

    def download_file(self):
        # Удаляем старый файл
        for i in os.listdir():
            if '.xlsx' in i:
                os.remove(i)
        obj = make_obj(self.link_schedule)
        print('start downloading xlsx file')
        for i in obj.findAll('span', attrs={'class': 'doc-unit-title'}):
            if 'ОЗФО' in i.get_text():
                relative_path = i.parent.attrs['href']
                file_name = relative_path.split('/')[-1]
                html_file = requests.request('GET', self.base_url + relative_path)
                with open(file_name, 'wb') as file:
                    file.write(html_file.content)
                    print('xlsx file is downloaded')
                return file_name

    def update_from_excel(self, file_name):
        self.db_obj.delete_all_data()
        global inst_col, inst_row, prog_row
        wb = openpyxl.load_workbook(filename=file_name)
        output = dict()
        print('------------------')

        for sheet_name in [i for i in wb.sheetnames if 'ОЗФО' in i]:
            print(sheet_name)
            ws = wb[sheet_name]
            output[sheet_name] = {}
            self.db_obj.add_year(sheet_name)

            for row in ws.iter_rows():
                for cell in row:
                    if cell.value == 'ИНСТИТУТ':
                        inst_col, inst_row = cell.column, cell.row
                    elif cell.value == 'ОБРАЗОВАТЕЛЬНАЯ ПРОГРАММА':
                        prog_row = cell.row

            inst_mem = None
            for col in ws.iter_cols(min_col=inst_col+1, min_row=inst_row, max_row=prog_row, values_only=True):
                if col[0]:
                    inst_mem = col[0].replace('\n', '').capitalize()
                    if col[2]:
                        program = col[2].replace('\n', '').capitalize()
                    else:
                        program = col[1].replace('\n', '').capitalize()
                    print(sheet_name, inst_mem, program)
                    self.db_obj.add_inst_prog(sheet_name, inst_mem, program)
                    output[sheet_name].update({inst_mem: {program, }})

                elif not col[0] and (col[1] or col[2]):
                    if col[2]:
                        program = col[2].replace('\n', '').capitalize()
                    else:
                        program = col[1].replace('\n', '').capitalize()
                    print(sheet_name, inst_mem, program)
                    output[sheet_name][inst_mem].update({program, })
                    self.db_obj.add_prog(sheet_name, inst_mem, program)

                else:
                    continue

            print('------------------')
        print(output)

    def __del__(self):
        self.db_obj.close_conn()


guu_obj = Guu()
