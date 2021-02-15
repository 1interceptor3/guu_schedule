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
            # Если нужно обновление или файла нету, проходим по каталогу и удаляем лишние файлы excel
            for i in os.listdir():
                if '.xlsx' in i:
                    os.remove(i)
            # Получаем новое название скачанного файла
            self.excel_file_name = self.download_file()
            print('New file', self.excel_file_name)
            self.work_with_excel(new=True, file_name=self.excel_file_name)
        else:
            self.excel_file_name = get_excel_file()
            print('Old file', self.excel_file_name)
            self.work_with_excel(new=False, file_name=self.excel_file_name)

    def download_file(self):
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

    def work_with_excel(self, new: bool, file_name=None):
        wb = openpyxl.load_workbook(filename=file_name)
        if new:
            sheets = self.db_obj.update_years(wb.sheetnames)
        else:
            sheets = self.db_obj.get_years()

        # Перебираем листы и выбираем институты
        for sheet in sheets:
            ws = wb[sheet]
            institute_coordinate, program_coordinate, arrow_coordinate = None, None, None
            institute_list, program_list = list(), list()

            for row in ws.rows:
                for cell in row:
                    if cell.value == 'ИНСТИТУТ':
                        institute_coordinate = cell.coordinate
                        continue
                    if cell.value == 'НАПРАВЛЕНИЕ':
                        arrow_coordinate = cell.coordinate
                        continue
                    if cell.value == 'ОБРАЗОВАТЕЛЬНАЯ ПРОГРАММА':
                        program_coordinate = cell.coordinate
                        continue
            print('--------------------')
            print(ws.title)
            # Перебор строки институтов
            for i in range(column_index_from_string(institute_coordinate[0]) + 1, ws.max_column + 1):
                if ws.cell(row=int(institute_coordinate[1]), column=i).value:
                    institute_list.append(ws.cell(row=int(institute_coordinate[1]), column=i).value)

            print(institute_list)
            print(len(institute_list))

            # Перебор строки программ обучения

            for col in ws.iter_cols(
                    min_row=int(arrow_coordinate[1]), max_row=int(program_coordinate[1]),
                    min_col=column_index_from_string('E'), values_only=True):
                if col[1]:
                    program_list.append(col[1])
                else:
                    program_list.append(col[0])

            print(program_list)
            print(len(program_list))

            print('--------------------')
            break  # Проверяем пока только 1 лист

        wb.close()

    def __del__(self):
        self.db_obj.close_conn()


guu_obj = Guu()
