import sqlite3
import datetime
import os


class DataBaseSQLITE:
    """
    Класс для работы с базой данных
    """
    def __init__(self):
        print('Start working with db')
        if os.path.exists('guu.sqlite3'):
            print('DB is exist')
            self.conn = sqlite3.connect('guu.sqlite3')
            self.cursor = self.conn.cursor()
        else:
            print('Creating new DB file')
            self.conn = sqlite3.connect('guu.sqlite3')
            self.cursor = self.conn.cursor()
            self.create_env()

    def create_env(self):
        self.cursor.execute('CREATE TABLE year (id integer primary key, number text NOT NULL UNIQUE);')
        self.cursor.execute("""
        CREATE TABLE institute (
        id integer primary key,
        year_id integer not null,
        name text NOT NULL,
        FOREIGN KEY (year_id) references year(id)
        );
        """)
        self.cursor.execute('CREATE TABLE educational_program (id integer primary key, name text NOT NULL);')
        self.cursor.execute("""
        CREATE TABLE couples (
        id integer primary key,
        year_id integer not null,
        institute_id integer not null,
        educational_program_id integer not null,
        day_of_week text not null,
        time text not null,
        FOREIGN KEY (year_id) references year(id),
        FOREIGN KEY (institute_id) references institute(id),
        FOREIGN KEY (educational_program_id) references educational_program(id)
        );
        """)
        self.cursor.execute('CREATE TABLE downloaded_file (id integer primary key, date text NOT NULL);')
        self.conn.commit()

    def last_changes(self):
        self.cursor.execute('SELECT * FROM downloaded_file WHERE id = (SELECT MAX(id) from downloaded_file);')
        last = self.cursor.fetchone()
        if last:
            return last[-1]
        else:
            return last

    def need_to_update(self):
        last_date = self.last_changes()
        print(last_date)
        if last_date:
            date_in_db = datetime.date(
                int(last_date.split('-')[0]), int(last_date.split('-')[1]), int(last_date.split('-')[2])
            )
            delta = datetime.date.today() - date_in_db
            if delta >= datetime.timedelta(days=1):
                print('Разница => 1 день')
                return True
            else:
                print('Ранзница < 1 день')
                return False
        else:
            return True

    def delete_years(self):
        self.cursor.execute('DELETE FROM year;')
        self.conn.commit()
        print('years deleted')

    def add_years(self, name):
        self.cursor.execute(f"INSERT INTO year (number) VALUES ('{name}');")
        self.conn.commit()

    def delete_institute(self):
        self.cursor.execute('DELETE FROM institute;')
        self.conn.commit()

    def add_institute(self, name, year_name):
        self.cursor.execute(
            f"""
            INSERT INTO institute(year_id, name) values ((select id from year where number = '{year_name}'), '{name}');
            """
        )
        self.conn.commit()

    def update_years(self, years_list: list):
        """
        Функция удаляет прошлые значения и добавляет новые названия курсов (пока что только ОЗФО) в БД

        :param years_list: Список новых названий курсов
        :return: Список внесенных новых названий курсов, отобранных по определенным правилам
        """
        if type(years_list) == list:
            # Чистим прошлые значения
            self.cursor.execute('DELETE FROM year;')
            self.conn.commit()

            # Проверяем листы файла и добавим в БД
            output = list()
            for i in years_list:
                if 'ОЗФО' in i:
                    self.cursor.execute(f"INSERT INTO year (number) VALUES ('{i}');")
                    output.append(i)
            self.conn.commit()
            print('Years updated')
            return output

    def get_years(self):
        self.cursor.execute("SELECT number FROM year;")
        output = []
        for i in self.cursor.fetchall():
            for j in i:
                output.append(j)
        return output

    def update_institute(self):
        return None

    def close_conn(self):
        self.cursor.close()
        self.conn.close()
        print('db connection closed')
