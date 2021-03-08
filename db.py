import sqlite3
import datetime
import os


class DataBaseSQLITE:
    """
    Класс для работы с базой данных.
    """
    def __init__(self):
        if os.path.exists('guu.sqlite3'):
            self.conn = sqlite3.connect('guu.sqlite3')
            self.cursor = self.conn.cursor()
        else:
            print('Создание файла с БД')
            self.conn = sqlite3.connect('guu.sqlite3')
            self.cursor = self.conn.cursor()
            self.create_env()

    def create_env(self):
        """
        Метод для создания таблиц в пустой БД.
        """
        self.cursor.execute('CREATE TABLE year (id integer primary key, number text NOT NULL UNIQUE);')
        self.cursor.execute("""
        CREATE TABLE institute (
        id integer primary key,
        year_id integer not null,
        name text NOT NULL,
        FOREIGN KEY (year_id) references year(id)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE educational_program (
        id integer primary key,
        institute_id integer not null,
        name text NOT NULL,
        coordinates text,
        FOREIGN KEY (institute_id) references institute(id)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE couples (
        id integer primary key,
        educational_program_id integer not null,
        number_of_week text not null,
        day_of_week text not null,
        time text not null,
        teacher text not null,
        subject text not null,
        FOREIGN KEY (educational_program_id) references educational_program(id)
        );
        """)
        self.cursor.execute('CREATE TABLE downloaded_file (id integer primary key, date text NOT NULL);')
        self.conn.commit()

    def last_changes(self):
        """
        Метод возвращает дату последнего обновления БД или None, если записей нет.
        """
        self.cursor.execute('SELECT * FROM downloaded_file WHERE id = (SELECT MAX(id) from downloaded_file);')
        last = self.cursor.fetchone()
        if last:
            date_str = last[-1]
            return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        else:
            return last

    def need_to_update(self):
        """
        Возвращает значение, нужно ли обновлять БД
        """
        last_date = self.last_changes()
        print('Дата последнего обновления БД:', last_date)
        if last_date:
            delta = datetime.datetime.now() - last_date
            if delta >= datetime.timedelta(days=1):
                print('БД нужно обновить в связи с датой последнего обновления')
                return True
            else:
                print('БД обновлять не нужно, прошло меньше суток')
                return False
        else:
            print('БД нуужно обновить, нет записей о последнем обновлении')
            return True

    def add_year(self, name):
        self.cursor.execute(f"INSERT INTO year (number) VALUES ('{name}');")
        self.conn.commit()

    def add_institute(self, name, year_name):
        self.cursor.execute(
            f"""
            INSERT INTO institute(year_id, name) values ((select id from year where number = '{year_name}'), '{name}');
            """
        )
        self.conn.commit()

    def delete_all_data(self):
        self.cursor.executescript("""
        DELETE FROM year;
        DELETE FROM institute;
        DELETE FROM educational_program;
        DELETE FROM couples;
        """)
        self.conn.commit()

    def add_inst_prog(self, year, institute, program, coordinates):
        self.cursor.executescript(f"""
        BEGIN TRANSACTION;
        INSERT INTO institute (year_id, name) VALUES ((SELECT id FROM year WHERE number = '{year}'), '{institute}');
        INSERT INTO educational_program (institute_id, name, coordinates) VALUES (
            (SELECT id FROM institute WHERE name = '{institute}' AND year_id = (
                SELECT id FROM year WHERE number = '{year}'
                )
            ), '{program}', '{coordinates}'
        );
        COMMIT;
        """)
        self.conn.commit()

    def add_prog(self, year, institute, program, coordinates):
        self.cursor.executescript(f"""
        INSERT INTO educational_program (institute_id, name, coordinates) VALUES (
            (SELECT id FROM institute WHERE institute.name = '{institute}' AND year_id=(
                SELECT id FROM year WHERE number = '{year}'
                )
            ), '{program}', '{coordinates}'
        );
        """)
        self.conn.commit()

    def get_years(self):
        self.cursor.execute("SELECT number FROM year;")
        output = []
        for i in self.cursor.fetchall():
            for j in i:
                output.append(j)
        return output

    def get_progs_by_year(self, year):
        self.cursor.execute(f"""
        SELECT name, coordinates FROM educational_program WHERE institute_id IN (
            SELECT id FROM institute WHERE year_id = (select id from year where number = '{year}')
        );
        """)
        output = []
        for program in self.cursor.fetchall():
            output.append(program)
        return output

    def get_program_by_col(self, year, column):
        self.cursor.execute(f"""
        SELECT educational_program.id, educational_program.name FROM educational_program JOIN institute ON
        educational_program.institute_id = institute.id
        WHERE institute.year_id=(SELECT id FROM year WHERE number='{year}') AND 
        educational_program.coordinates='{column}';
        """)
        return self.cursor.fetchone()

    def add_couple(self, program_id, number_of_week, day, time, subject):
        self.cursor.execute(f"""
        INSERT INTO couples (educational_program_id, number_of_week, day_of_week, time, teacher, subject)
        VALUES ('{program_id}', '{number_of_week}', '{day}', '{time}', 'nothing', '{subject}');
        """)
        self.conn.commit()

    def updated(self):
        """
        Метод для занесения даты обновления в БД
        """
        self.cursor.execute(f"""
        INSERT INTO downloaded_file (date) VALUES ('{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');
        """)
        self.conn.commit()

    def close_conn(self):
        """
        Метод для закрытия соединения с БД
        """
        self.cursor.close()
        self.conn.close()
        print('Соединение с БД закрыто')
