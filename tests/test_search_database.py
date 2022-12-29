import pytest
import sqlite3
import os
import textwrap
from pathlib import PurePath
current_dir = PurePath(__file__)
import_dir = current_dir.parents[1].joinpath('good_faith_estimate')

import sys
sys.path.insert(0, str(import_dir))

from models import Database


@pytest.fixture()
def database():
    db = Database('test.db')
    yield db
    db.close()


def test_db_exists():
    assert os.path.exists('test.db')


def test_db_empty(database):
    clear_db = "DROP TABLE IF EXISTS clients"
    database.update(clear_db)
    query = textwrap.dedent("""CREATE TABLE IF NOT EXISTS clients (
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
    );""")
    database.update(query)
    database.search("SELECT * FROM clients")
    results = database.get_data()
    assert not results


def test_update_db(database):
    query = textwrap.dedent("""INSERT INTO clients (
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
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""")
    values = (
            1,
            'Tony',
            'Starks',
            '1974-06-06',
            '555',
            '5555555',
            '123 Starks Dr.',
            'New York City',
            'New York',
            '10101'
            )
    database.update(query, values)
    database.search("SELECT * FROM clients")
    results = database.get_data()
    exp_value = (
            1,
            'Tony',
            'Starks',
            '1974-06-06',
            '555',
            '5555555',
            '123 Starks Dr.',
            None,
            'New York City',
            'New York',
            '10101'
            )
    assert results[0] == exp_value
