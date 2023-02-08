# from os import wait
import tkinter as tk
import unittest
import sys

from pathlib import PurePath

current_dir = PurePath(__file__)
import_dir = current_dir.parents[1]

sys.path.insert(0, str(import_dir))

from views import ClientSelectionWindow, NewClientWindow, CreateEstimateWindow


class TestClientSelectionWindow(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        self.client_selection_window = ClientSelectionWindow(self.root)

    def tearDown(self) -> None:
        self.root.destroy()

    def test_window_exists(self):
        window = self.root.winfo_children()
        self.assertTrue(isinstance(window[0], ClientSelectionWindow))

    def test_window_get(self):
        client = (1, "Tony", "Stark", "1974-06-06")
        self.client_selection_window._vars["search_results"].set(client)
        data = self.client_selection_window.get()
        self.assertEqual(
            data["search_results"],
            self.client_selection_window._vars["search_results"].get(),
        )


class TestNewClientWindow(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        self.new_client_window = NewClientWindow(self.root)

    def tearDown(self) -> None:
        self.root.destroy()

    def test_window_exists(self):
        window = self.root.winfo_children()
        self.assertTrue(isinstance(window[0], NewClientWindow))

    def test_window_get(self):
        new_client_info = (
            "Star",
            "Lord",
            "1984-06-06",
            "555",
            "5555555",
            "999 Other Planet Ln.",
            "",
            "Unknown City",
            "Unknown Planet",
            "00000",
        )
        data = dict()
        for key, value in zip(
            self.new_client_window._vars.keys(), new_client_info
        ):
            self.new_client_window._vars[key].set(value)
            data[key] = value
        self.assertEqual(self.new_client_window.get(), data)


class TestCreateEstimateWindow(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        self.lr_data = {
            "services": ("90837", "90847"),
            "therapists": (
                "1 Ryan O'Farrell, Psy.D.",
                "2 Jacquie Atkins, LPC",
                "3 Sydney Reynolds, LPC",
            ),
            "location": ("Mount Pleasant", "North Charleston", "Telehealth"),
        }
        self.create_estimate_window = CreateEstimateWindow(
            self.root, self.lr_data
        )

    def tearDown(self) -> None:
        self.root.destroy()

    def test_window_exists(self):
        window = self.root.winfo_children()
        self.assertTrue(isinstance(window[0], CreateEstimateWindow))

    def test_window_get(self):
        data = dict()
        self.create_estimate_window._vars["services_sought"].set(
            self.lr_data["services"][0]
        )
        self.create_estimate_window._vars["session_rate"].set("165")
        self.create_estimate_window._vars["therapist"].set(
            self.lr_data["therapists"][0]
        )
        self.create_estimate_window._vars["location"].set(
            self.lr_data["location"][0]
        )
        for key, value in self.create_estimate_window._vars.items():
            data[key] = value.get()
        self.assertEqual(self.create_estimate_window.get(), data)


if __name__ == "__main__":
    unittest.main()
