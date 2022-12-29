from sqlite3 import register_adapter
import tkinter as tk
from tkinter import Toplevel, messagebox as tkmb
from tkinter import ttk
from pathlib import Path

from markupsafe import re
import models
import views
import widget


class Client:
    """Represents a selected client."""

    def __init__(self, client: tuple) -> None:
        self.id, self.first, self.last, self.dob, self.dx = client


class Therapist:
    """Represents a selected therapist."""

    def __init__(self, therapist: tuple) -> None:
        (
            self.id,
            self.first,
            self.last,
            self.license,
            self.tax_id,
            self.npi,
        ) = therapist


class Service:
    """Represents details for therapeutic services."""

    def __init__(self, service) -> None:
        (
            self.new_or_update,
            self.service_code,
            self.session_rate,
            self.location,
        ) = service
        self.session_count_low = 12
        self.session_count_high = 24
        self.registration_service_code = "None"
        self.registration_fee = 25
        self.registration_qty = 1
        self.intake_service_code = "90791"
        self.intake_qty = 1
        self.new_client_dx_code = "None"

    def new_gfe_total_estimate_low(self):
        return (
            self.session_rate * (self.session_count_low + self.intake_qty)
            + self.registration_fee
        )

    def new_gfe_total_estimate_high(self):
        return (
            self.session_rate * (self.session_count_high + self.intake_qty)
            + self.registration_fee
        )

    def new_estimate_low_table_rows(self):
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

    def new_estimate_high_table_rows(self):
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

    def update_estimate_low_table_rows(self, client_obj):
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

    def update_estimate_high_table_rows(self, client_obj):
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
        self.estimate_info = dict()

        self.search_window.bind("<<Search>>", self._client_from_db)
        self.search_window.bind("<<CreateClient>>", self._new_client_window)
        self.search_window.bind("<<CreateEstimate>>", self._gfe_estimate_window)

        # life_resources_data = dict()
        # therapist_query = """SELECT * FROM therapists"""
        # self.database.search(therapist_query)
        # life_resources_data["therapists"] = self.database.get_data()
        #
        # services_query = """SELECT * FROM services"""
        # self.database.search(services_query)
        # life_resources_data["services"] = self.database.get_data()
        #
        # locations_query = """SELECT city FROM locations"""
        # self.database.search(locations_query)
        # life_resources_data["locations"] = self.database.get_data()
        #
        # self.estimate_window = views.CreateEstimateWindow(
        #     self.root, life_resources_data
        # )
        self.search_window.grid()
        self.root.mainloop()

    def _client_from_db(self, *_) -> None:
        """Searches for a given client in the database."""
        client = self.search_window.get()
        self.search_window._vars["search_results"].set("")
        self.search_window.search_results["values"] = [""]
        if client["first"] and client["last"]:
            query = """SELECT client_id, first_name, last_name, date_of_birth FROM clients WHERE
            first_name=:first AND last_name=:last"""
            values = {"first": client["first"], "last": client["last"]}
        elif client["first"]:
            query = """SELECT client_id, first_name, last_name, date_of_birth FROM clients WHERE
            first_name=:first"""
            values = {"first": client["first"]}
        elif client["last"]:
            query = """SELECT client_id, first_name, last_name, date_of_birth FROM clients WHERE
            last_name=:last"""
            values = {"last": client["last"]}
        else:
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


    def _new_client_window(self, *_):
        new_window = Toplevel(self.root)
        new_window.columnconfigure(0, weight=1)
        new_window.rowconfigure(0, weight=1)
        new_window.geometry("400x700")
        self.new_client_window = views.NewClientWindow(new_window)
        self.new_client_window.columnconfigure(0, weight=1)
        self.new_client_window.rowconfigure(0, weight=1)
        self.new_client_window.grid(sticky=tk.W + tk.E + tk.N + tk.S)

    def _gfe_estimate_window(self):
        pass

if __name__ == "__main__":
    app = MainApplication()
