import enum
import unittest
import tkinter as tk
from tkinter import ttk
from ..widget import DobEntry


class TestDobEntry(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        self.dob = DobEntry(self.root)

    def tearDown(self) -> None:
        self.root.destroy()

    def test_dob_entry(self):
        valid_date = "2000-01-01"
        for index, char in enumerate(valid_date):
            self.dob.insert(index, char)
            self.assertEqual(self.dob._validate("0", "0", "key", "1"), True)

    def test_dob_entry_invalid_input(self):
        invalid_date = "01-01-2000"
        for index, char in enumerate(invalid_date):
            self.dob.insert(index, char)
            self.assertEqual(self.dob._validate("0", "0", "focusout", "1"), False)


if __name__ == "__main__":
    unittest.main()
