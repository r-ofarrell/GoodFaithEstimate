import sqlite3
from pathlib import Path
import os


class Database:
    def __init__(self, database):
        self._database = self.resource_path(database)
        self._conn = self.create_connection()
        self._cur = self.create_cursor()
        self._data = None

    def resource_path(self, relative_path):
        """Get the absolute path to a given resource."""

        return os.path.join(
            os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
            ),
            relative_path
        )

    def create_connection(self):
        """Creates connection to a specified database."""
        conn = sqlite3.connect(self._database)
        conn.row_factory = sqlite3.Row
        return conn

    def create_cursor(self):
        """Creates database cursor."""
        return self._conn.cursor()

    def search(self, query, values=None):
        """Searches database."""
        if values:
            self._cur.execute(query, values)
        else:
            self._cur.execute(query)
        results = self._cur.fetchall()
        self._data = results

    def get_data(self):
        """Retrieve data."""
        return self._data

    def update(self, query, values=None):
        """Updates database."""
        if values:
            self._cur.execute(query, values)
        else:
            self._cur.execute(query)
        self._conn.commit()

    def close(self):
        """Closes connection to database."""
        self._conn.close()
