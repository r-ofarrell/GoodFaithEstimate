import sqlite3
from pathlib import Path
import os


class Database:
    def __init__(self, database):
        self._database = self.resource_path(database)
        self._conn = self.create_connection()
        self._cur = self.create_cursor()
        self._cur_dict = self.create_cursor()
        self._cur_dict.row_factory = sqlite3.Row
        self._search_results = None
        self.database_tables = [
            {
                "table": "clients",
                "columns": {
                    "client_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "first_name": "TEXT NOT NULL",
                    "last_name": "TEXT NOT NULL",
                    "date_of_birth": "TEXT",
                    "email": "TEXT",
                    "area_code": "TEXT",
                    "phone_number": "TEXT",
                    "street": "TEXT",
                    "apt_bldg_ste": "TEXT",
                    "city": "TEXT",
                    "state": "TEXT",
                    "zipcode": "TEXT",
                    "diagnosis": "TEXT",
                },
            },
            {
                "table": "therapists",
                "columns": {
                    "therapist_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "first_name": "TEXT NOT NULL",
                    "last_name": "TEXT NOT NULL",
                    "license_type": "TEXT NOT NULL",
                    "date_of_birth": "TEXT",
                    "email": "TEXT",
                    "area_code": "TEXT",
                    "phone_number": "TEXT",
                    "tax_id": "TEXT",
                    "npi": "TEXT",
                    "street": "TEXT",
                    "apt_bldg_ste": "TEXT",
                    "city": "TEXT",
                    "state": "TEXT",
                    "zipcode": "TEXT",
                    "therapist_status": "INTEGER",
                },
            },
            {
                "table": "locations",
                "columns": {
                    "location_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "street": "TEXT",
                    "apt_bldg_ste": "TEXT",
                    "city": "TEXT",
                    "state": "TEXT",
                    "zipcode": "TEXT",
                }
            },
            {
                "table": "services",
                "columns": {
                    "service_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "cpt_code": "TEXT",
                    "description": "TEXT",
                }
            },
            {
                "table": "estimate_details",
                "columns": {
                    "estimate_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "client_id": "INTEGER",
                    "therapist_id": "INTEGER",
                    "date_of_service": "TEXT NOT NULL",
                    "renewal_date": "TEXT NOT NULL",
                    "service_id": "INTEGER",
                    "session_rate": "TEXT NOT NULL",
                    "low_estimate": "TEXT NOT NULL",
                    "high_estimate": "TEXT NOT NULL",
                    "location_id": "INTEGER",
                }
            },
        ]

    def create_db_tables(self):
        """Creates tables for GFE database."""
        foreign_keys = """FOREIGN KEY (client_id) REFERENCES clients (client_id) ON UPDATE CASCADE ON DELETE SET NULL,
        FOREIGN KEY (therapist_id) REFERENCES services (service_id) ON UPDATE CASCADE ON DELETE SET NULL,
        FOREIGN KEY (service_id) REFERENCES therapists (therapist_id) ON UPDATE CASCADE ON DELETE SET NULL,
        FOREIGN KEY (location_id) REFERENCES locations (location_id) ON UPDATE CASCADE ON DELETE SET NULL"""
        last_table = len(self.database_tables) - 1

        for index, item in enumerate(self.database_tables):
            if index == last_table: # Adds foreign keys for estimate_table
                table = item["table"]
                columns = [
                    f"{key} {value}" for key, value in item["columns"].items()
                ]
                query = (
                    f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)}, {foreign_keys});"
                )
                self.update(query)

            else:
                table = item["table"]
                columns = [
                    f"{key} {value}" for key, value in item["columns"].items()
                ]
                query = (
                    f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)});"
                )
                self.update(query)

    def resource_path(self, relative_path):
        """Get the absolute path to a given resource."""

        return os.path.join(
            os.environ.get("_MEIPASS2", os.path.abspath(".")), relative_path
        )

    def create_connection(self):
        """Creates connection to a specified database."""
        conn = sqlite3.connect(self._database)
        return conn

    def create_cursor(self):
        """Creates database cursor."""
        return self._conn.cursor()

    def search(self, query, values=None):
        """Searches database."""
        if values:
            self._cur_dict.execute(query, values)
        else:
            self._cur_dict.execute(query)
        results = self._cur_dict.fetchall()
        self._search_results = results

    def search_and_return_tuple(self, query, values=None):
        """Searches database."""
        if values:
            self._cur.execute(query, values)
        else:
            self._cur.execute(query)
        results = self._cur.fetchall()
        self._search_results = results

    def get_search_results(self):
        """Retrieve data."""
        return self._search_results

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
