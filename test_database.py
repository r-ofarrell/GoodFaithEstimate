import unittest
from pathlib import PurePath

current_dir = PurePath(__file__)
import_dir = current_dir.parents[0].joinpath('good_faith_estimate')
import sys

sys.path.insert(0, str(import_dir))

from models import Database


class TestSearchDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.db = Database("test.db")
        clear_db = "DROP TABLE IF EXISTS clients"
        self.db.update(clear_db)
        query = """CREATE TABLE IF NOT EXISTS clients (
            client_id int NOT NULL PRIMARY KEY,
            first_name text NOT NULL,
            last_name text NOT NULL,
            date_of_birth text NOT NULL,
            area_code text NOT NULL,
            phone_number text NOT NULL,
            street text NOT NULL,
            apt_bldg_ste text,
            city text NOT NULL,
            state text NOT NULL,
            zip text NOT NULL
            );"""
        self.db.update(query)
        insert_query = """INSERT INTO clients (
                            client_id,
                            first_name,
                            last_name,
                            date_of_birth,
                            area_code,
                            phone_number,
                            street,
                            city,
                            state,
                            zip
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        values = [
            (
                2,
                "Peter",
                "Parker",
                "2000-01-01",
                "555",
                "5555555",
                "987 Spidey Ln.",
                "New York City",
                "New York",
                "10101",
            ),
            (
                1,
                "Tony",
                "Starks",
                "1974-06-06",
                "555",
                "5555555",
                "123 Starks Dr.",
                "New York City",
                "New York",
                "10101",
            ),
        ]

        for value in values:
            self.db.update(insert_query, value)

    @classmethod
    def tearDownClass(self) -> None:
        clear_db = "DROP TABLE IF EXISTS clients"
        self.db.update(clear_db)
        self.db.close()

    def test_update_db(self):
        query = """INSERT INTO clients (
                            client_id,
                            first_name,
                            last_name,
                            date_of_birth,
                            area_code,
                            phone_number,
                            street,
                            city,
                            state,
                            zip
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        values = (
            3,
            "Bruce",
            "Banner",
            "1975-07-07",
            "555",
            "5555555",
            "000 Unknown",
            "Unknown City",
            "Unknown",
            "00000",
        )
        self.db.update(query, values)
        self.db.search("SELECT * FROM clients WHERE client_id=3")
        results = self.db.get_data()
        exp_value = (
            3,
            "Bruce",
            "Banner",
            "1975-07-07",
            "555",
            "5555555",
            "000 Unknown",
            None,
            "Unknown City",
            "Unknown",
            "00000",
        )
        self.assertEqual(results[0], exp_value)

    def test_multiple_search_results(self):
        select_all_query = """SELECT * FROM clients"""
        self.db.search(select_all_query)
        results = self.db.get_data()
        exp_value = [
            (
                2,
                "Peter",
                "Parker",
                "2000-01-01",
                "555",
                "5555555",
                "987 Spidey Ln.",
                None,
                "New York City",
                "New York",
                "10101",
            ),
            (
                1,
                "Tony",
                "Starks",
                "1974-06-06",
                "555",
                "5555555",
                "123 Starks Dr.",
                None,
                "New York City",
                "New York",
                "10101",
            ),
        ]
        self.assertEqual(results, exp_value)


if __name__ == "__main__":
    unittest.main()
