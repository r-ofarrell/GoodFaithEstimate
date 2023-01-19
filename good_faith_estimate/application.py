from sqlite3 import register_adapter
import tkinter as tk
from tkinter import Toplevel, messagebox as tkmb
from tkinter import ttk
from pathlib import Path
from dataclasses import dataclass, asdict, astuple

from markupsafe import re
import models
import views
import widget


@dataclass
class Client:
    """Represents a selected client."""
    client_id: int
    first_name: str
    last_name: str
    date_of_birth: str
    area_code: str
    phone_number: str
    street: str
    apt_ste_bldg: str
    city: str
    zipcode: str
    diagnosis: str = None

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def create_from_dict(cls, d):
        return Client(**d)



@dataclass
class Therapist:
    """Represents a selected therapist."""

    id: int
    first: str
    last: str
    license: str
    tax_id: str
    npi: str

    def full_name(self):
        return f"{self.first} {self.last}"

    def full_name_and_license(self):
        return f"{self.first} {self.last}, {self.license}"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def create_from_dict(cls, d):
        return Therapist(**d)

@dataclass
class Service:
    """Represents details for therapeutic services."""

    new_or_update: str
    service_code: str
    session_rate: str
    location: str
    session_count_low: int = 12
    session_count_high: int = 24
    registration_service_code: str = "None"
    registration_fee: int = 25
    registration_qty: int = 1
    intake_service_code: str = "90791"
    intake_qty: int = 1
    new_client_dx_code: str = "None"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def create_from_dict(cls, d):
        return Service(**d)

    def new_gfe_low_total_estimate(self):
        return (
            self.session_rate * (self.session_count_low + self.intake_qty)
            + self.registration_fee
        )

    def new_gfe_high_total_estimate(self):
        return (
            self.session_rate * (self.session_count_high + self.intake_qty)
            + self.registration_fee
        )

    def new_low_estimate_table_rows(self):
        service_total = self.session_rate * self.session_count_low
        self.registration_fee = (
            "Registration fee",
            self.registration_service_code,
            self.new_client_dx_code,
            self.registration_fee,
            self.registration_qty,
            self.registration_fee,
        )
        intake_appt = (
            "Intake assessment",
            self.intake_service_code,
            self.new_client_dx_code,
            self.session_rate,
            self.intake_qty,
            self.session_rate,
        )
        service = (
            "Psychotherapy",
            self.service_code,
            self.new_client_dx_code,
            self.session_rate,
            self.session_count_low,
            service_total,
        )

        return (self.registration_fee, intake_appt, service)

    def new_high_estimate_table_rows(self):
        service_total = self.session_rate * self.session_count_high
        self.registration_fee = (
            "Registration fee",
            self.registration_service_code,
            self.new_client_dx_code,
            self.registration_fee,
            self.registration_qty,
            self.registration_fee,
        )
        intake_appt = (
            "Intake assessment",
            self.intake_service_code,
            self.new_client_dx_code,
            self.session_rate,
            self.intake_qty,
            self.session_rate,
        )
        service = (
            "Psychotherapy",
            self.service_code,
            self.new_client_dx_code,
            self.session_rate,
            self.session_count_high,
            service_total,
        )

        return (self.registration_fee, intake_appt, service)

    def update_low_estimate_table_rows(self, client_obj):
        service_total = self.session_rate * self.session_count_low
        service = (
            "Psychotherapy",
            self.service_code,
            client_obj.dx,
            self.session_rate,
            self.session_count_low,
            service_total,
        )

        return service

    def update_high_estimate_table_rows(self, client_obj):
        service_total = self.session_rate * self.session_count_high
        service = (
            "Psychotherapy",
            self.service_code,
            client_obj.dx,
            self.session_rate,
            self.session_count_high,
            service_total,
        )

        return service


class MainApplication:
    """Good Faith Estimate creator application."""

    def __init__(self, *args, **kwargs) -> None:
        # super().__init__(*args, **kwargs)
        self.root = tk.Tk()
        self.file = Path(__file__)
        self.db_folder = self.file.parents[1]
        self.database = models.Database(str(Path.joinpath(self.db_folder, "gfe_db.db")))
        self.search_window = views.ClientSelectionWindow(self.root)
        self.new_client_window = None
        self.estimate_window = None
        self.estimate_info = dict()

        self.search_window.bind("<<Search>>", self._get_client_from_db)
        self.search_window.bind("<<CreateClient>>", self._show_new_client_window)
        self.search_window.bind("<<CreateEstimate>>", self._show_estimate_window)

        self.life_resources_data = dict()
        therapist_query = """SELECT therapist_id, first_name, last_name,
        license_type FROM therapists WHERE therapist_status = 1"""
        self.database.search(therapist_query)
        self.life_resources_data["therapists"] = self.database.get_data()

        services_query = """SELECT * FROM services"""
        self.database.search(services_query)
        self.life_resources_data["services"] = self.database.get_data()

        locations_query = """SELECT location_id, city FROM locations"""
        self.database.search(locations_query)
        self.life_resources_data["location"] = self.database.get_data()

        self.estimate_window = views.CreateEstimateWindow(
            self.root, self.life_resources_data
        )
        self.search_window.grid()
        self.root.mainloop()

    def _get_client_from_db(self, *_) -> None:
        """Searches for a given client in the database."""
        client = self.search_window.get()
        self.search_window._vars["search_results"].set("")
        self.search_window.search_results["values"] = [""]
        if client["first"] and client["last"]:
            # If both first and last name are present, search database using both.
            query = """SELECT client_id, first_name, last_name, date_of_birth FROM clients WHERE
            first_name=:first AND last_name=:last"""
            values = {"first": client["first"], "last": client["last"]}
        elif client["first"]:
            # If only first name is given, search only using first name.
            query = """SELECT client_id, first_name, last_name, date_of_birth FROM clients WHERE
            first_name=:first"""
            values = {"first": client["first"]}
        elif client["last"]:
            # If only last name is given, search only using last name.
            query = """SELECT client_id, first_name, last_name, date_of_birth FROM clients WHERE
            last_name=:last"""
            values = {"last": client["last"]}
        else:
            # If search fields are empty when search button is pressed, throw
            # an error.
            tkmb.showerror("Error",
                           """Please enter, at a minimum, the first or last name of the client you want to search for.""")
            return None

        self.database.search(query, values)
        results = self.database.get_data()
        if results:
            self.search_window.search_results["values"] = results
        else:
            if tkmb.askyesno("Create new client?",
                             "No client was found. Would you like to create a new client?"):
                self._new_client_window()
            else:
                return None

    def _show_new_client_window(self, *_) -> None:
        new_window = Toplevel(self.root)
        new_window.columnconfigure(0, weight=1)
        new_window.rowconfigure(0, weight=1)
        new_window.geometry("400x700")
        self.new_client_window = views.NewClientWindow(new_window)
        self.new_client_window.columnconfigure(0, weight=1)
        self.new_client_window.rowconfigure(0, weight=1)
        self.new_client_window.grid(sticky=tk.W + tk.E + tk.N + tk.S)

    def _show_estimate_window(self, *_) -> None:
        new_window = Toplevel(self.root)
        new_window.columnconfigure(0, weight=1)
        new_window.rowconfigure(0, weight=1)
        new_window.geometry("300x400")
        self.estimate_window = views.CreateEstimateWindow(new_window, self.life_resources_data)
        self.estimate_window.bind("<<CreateEstimate>>", self._create_estimate)
        self.estimate_window.columnconfigure(0, weight=1)
        self.estimate_window.rowconfigure(0, weight=1)
        self.estimate_window.grid(sticky=tk.W + tk.E + tk.N + tk.S)

    def _create_estimate(self, *_):
        estimate_window_data = self.estimate_window.get()
        therapist = self._get_therapist_info(estimate_window_data)
        # Fill in code to get rest of needed data here.


    def _get_therapist_info(self, data: dict) -> object:
        query = """SELECT therapist_id, first_name, last_name, license_type, npi, tax_id
        FROM therapists WHERE therapist_id = :therapist_id"""
        selected_therapist_id = data["therapist"][0:2].rstrip()
        value = {"therapist_id": selected_therapist_id}
        self.database.search(query, value)
        results = self.database.get_data()
        therapist = Therapist(results[0])
        print(therapist.full_name_and_license())
        return therapist

if __name__ == "__main__":
    app = MainApplication()
