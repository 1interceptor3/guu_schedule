import sqlite3
import os


class DataBaseSQLITE:
    def __init__(self):
        if os.path.exists('guu.sqlite3'):
            self.conn = sqlite3.connect('guu.sqlite3')
            self.cursor = self.conn.cursor()
        else:
            conn = sqlite3.connect('guu.sqlite3')
            cursor = conn.cursor()

    def create_env(self):
        return None

    def __del__(self):
        self.conn.close()
        self.cursor.close()
        print('Connection closed')
