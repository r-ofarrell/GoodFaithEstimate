import pytest
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ..widget import DobEntry, AreaCodeEntry, PhoneNumberEntry, ZipcodeEntry


@pytest.fixture()
def create_window():
    root = tk.Tk()
    return root


@pytest.fixture()
def dob(create_window):
    dob_entry = DobEntry(create_window)
    return dob_entry


def test_DobEntry_valid_inputs(dob):
    valid = True
    num_indexes = [0, 1, 2, 3, 5, 6, 8, 9]
    for index in range(0, 10):
        if index in num_indexes:
            if not dob._validate("1", str(index), "key", "1"):
                valid = False
        else:
            if not dob._validate("-", str(index), "key", "1"):
                valid = False

    assert valid


def test_DobEntry_invalid_inputs(dob):
    invalid = True
    num_indexes = [0, 1, 2, 3, 5, 6, 8, 9]
    for index in range(0, 10):
        if index in num_indexes:
            if dob._validate("/", str(index), "key", "1"):
                invalid = False
        else:
            if dob._validate("1", str(index), "key", "1"):
                invalid = False

    assert invalid


def test_DobEntry_focusout_valid_input(dob):
    date = "2000-01-01"
    for index, char in enumerate(date):
        dob.insert(index, char)
    assert dob._validate("0", "end", "focusout", "1")


def test_DobEntry_focusout_invalid_input(dob):
    date = "01-01-2000"
    for index, char in enumerate(date):
        dob.insert(index, char)
    assert not dob._validate("0", "end", "focusout", "1")


@pytest.fixture()
def area_code(create_window):
    area_code_entry = AreaCodeEntry(create_window)
    return area_code_entry


def test_AreaCodeEntry_valid_input(area_code):
    valid = True
    nums = range(0, 10)
    for num in nums:
        if not area_code._validate(str(num), "key", "1", str(num)):
            valid = False
        area_code.insert(0, "")
    assert valid


def test_AreaCodeEntry_invalid_input(area_code):
    invalid = True
    invalid_chars = ["a", "b", "c", "-", "/", "(", ")"]
    for char in invalid_chars:
        if area_code._validate(char, "key", "1", char):
            invalid = False
        area_code.insert(0, "")
    assert invalid


@pytest.fixture()
def phone_number(create_window):
    phone_number_entry = PhoneNumberEntry(create_window)
    return phone_number_entry


def test_PhoneNumberEntry_valid_input(phone_number):
    valid = True
    nums = range(0, 10)
    for num in nums:
        if not phone_number._validate(str(num), "key", "1", str(num)):
            valid = False
        phone_number.insert(0, "")
    assert valid


def test_PhoneNumberEntry_invalid_input(phone_number):
    invalid = True
    invalid_chars = ["a", "b", "c", "-", "/", "(", ")"]
    for char in invalid_chars:
        if phone_number._validate(char, "key", "1", char):
            invalid = False
        phone_number.insert(0, "")
    assert invalid


@pytest.fixture()
def zip_code(create_window):
    zip_code_entry = ZipcodeEntry(create_window)
    return zip_code_entry


def test_ZipcodeEntry_valid_input(zip_code):
    valid = True
    zip_codes = [29466, 29464, 95003, 94024, 97132]
    for num in zip_codes:
        if not zip_code._validate(str(num)):
            valid = False
    assert valid


def test_ZipcodeEntry_invalid_input(zip_code):
    invalid = True
    zip_codes = ["abcdef", "1234a", "a1234", "-----", "95003-1234", "29464-1234"]
    for num in zip_codes:
        if zip_code._validate(str(num)):
            invalid = False
    assert invalid
