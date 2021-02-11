import sqlite3
import datetime
import os


class DataBaseSQLITE:
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
        self.cursor.execute('CREATE TABLE institute (id integer primary key, name text NOT NULL UNIQUE);')
        self.cursor.execute('CREATE TABLE educational_program (id integer primary key, name text NOT NULL UNIQUE);')
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
        return last[-1]

    def need_to_update(self):
        last_date = self.last_changes()
        print(last_date)
        date_in_db = datetime.date(int(last_date.split('-')[0]), int(last_date.split('-')[1]), int(last_date.split('-')[2]))
        print(date_in_db)
        delta = datetime.date.today() - date_in_db
        if delta >= datetime.timedelta(days=1):
            print('Разница 1 день или более')
            return True
        else:
            print('Разница менее 1 дня')
            return False

    def close_conn(self):
        self.cursor.close()
        self.conn.close()
        print('Connection closed')


db_obj = DataBaseSQLITE()

# if db_obj.need_to_update():
#     print('Пора обновлять')
# else:
#     print('Еще можно подождать')
db_obj.need_to_update()

db_obj.close_conn()
