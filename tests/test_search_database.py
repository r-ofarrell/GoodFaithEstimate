import pytest
import sqlite3
import textwrap
from pathlib import Path, PurePath
from ..models import Database


@pytest.fixture()
def database():
    test_directory = PurePath('.')
    db = Database(test_directory.joinpath('test.db'))

    yield db
    db.close()


@pytest.fixture()
def clean_database(database):
    clear_db = "DROP TABLE IF EXISTS clients"
    database.update(clear_db)
    query = textwrap.dedent("""CREATE TABLE IF NOT EXISTS clients (
    client_id int NOT NULL PRIMARY KEY,
    first_name text NOT NULL,
    last_name text NOT NULL,
    date_of_birth text NOT NULL,
    email text NOT NULL,
    area_code text NOT NULL,
    phone_number text NOT NULL,
    street text NOT NULL,
    apt_bldg_ste text,
    city text NOT NULL,
    state text NOT NULL,
    zipcode text NOT NULL
    );""")
    database.update(query)


def test_no_db():
    assert not Path('test.db').exists()


def test_db_exists(database):
    assert Path('test.db').exists()


def test_db_empty(database, clean_database):
    database.search("SELECT * FROM clients")
    results = database.get_search_results()
    assert not results


def test_db_search_and_return_tuple_returns_tuple(database):
    query = textwrap.dedent("""INSERT INTO clients (
                        client_id,
                        first_name,
                        last_name,
                        date_of_birth,
                        email,
                        area_code,
                        phone_number,
                        street,
                        city,
                        state,
                        zipcode
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""")

    values = (
            1,
            'Tony',
            'Starks',
            '1974-06-06',
            'tstarks@starks.com',
            '555',
            '5555555',
            '123 Starks Dr.',
            'New York City',
            'New York',
            '10101'
            )
    database.update(query, values)
    database.search_and_return_tuple("SELECT * FROM clients")
    results = database.get_search_results()

    assert isinstance(results[0], tuple)


def test_update_db(database):
    database.search_and_return_tuple("SELECT * FROM clients")
    results = database.get_search_results()
    exp_value = (
            1,
            'Tony',
            'Starks',
            '1974-06-06',
            'tstarks@starks.com',
            '555',
            '5555555',
            '123 Starks Dr.',
            None,
            'New York City',
            'New York',
            '10101'
            )

    assert results[0] == exp_value


def test_search_db_returns_sqlite3_row_obj(database):
    query = textwrap.dedent("""SELECT client_id, first_name, last_name,
    date_of_birth, area_code, phone_number, street, apt_bldg_ste,
    city, state, zipcode FROM clients WHERE client_id = (?)""")
    value = (1,)
    database.search(query, value)
    results = database.get_search_results()
    assert isinstance(results[0], sqlite3.Row)


def test_search_db_returns_dict_with_correct_values(database):
    query = textwrap.dedent("""SELECT client_id, first_name, last_name,
    date_of_birth, area_code, phone_number, street, apt_bldg_ste,
    city, state, zipcode FROM clients WHERE client_id = (?)""")
    value = (1,)
    database.search(query, value)
    results = database.get_search_results()
    exp_value = {
        'client_id': 1,
        'first_name': 'Tony',
        'last_name': 'Starks',
        'date_of_birth': '1974-06-06',
        'area_code': '555',
        'phone_number': '5555555',
        'street': '123 Starks Dr.',
        'apt_bldg_ste': None,
        'city': 'New York City',
        'state': 'New York',
        'zipcode': '10101'
    }

    for key, value in exp_value.items():
        assert exp_value[key] == results[0][key]


def test_remove_db_after_tests():
    test_directory = PurePath('.')
    filepath = test_directory.joinpath('test.db')
    file_to_remove = Path(filepath)
    file_to_remove.unlink()
    assert not Path(filepath).exists()
