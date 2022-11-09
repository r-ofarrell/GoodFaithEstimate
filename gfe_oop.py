import tkinter as tk
import sys
import sqlite3
import os
import re
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from tkinter import ttk
from tkinter import messagebox as tkmb
from docx import Document
from location_of_services import address
from document_creator import GfeDocument
# from docx2pdf import convert


# Model
class SearchDatabase:
    def __init__(self, database):
        self.database = self.resource_path(database)
        self.conn, self.cur = self.create_connection()

    def resource_path(self, relative_path):
        """Get the absolute path to a given resource."""

        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(base_path, relative_path)

    def create_connection(self):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()

        return (conn, cur)

    def search(self, query, values):
        self.cur.execute(query, values)
        results = self.cur.fetchall()
        return results

    def update(self, query, values):
        self.cur.execute(query, values)
        self.conn.commit()

    def close(self):
        self.conn.close()


class Therapists(SearchDatabase):
    def __init__(self, database):
        super().__init__(database)
        self.therapists = self.therapist_list()

    def therapist_list(self):
        query = """SELECT therapist_id, first_name, last_name, license_type,
        tax_id, npi FROM therapists WHERE therapist_status = :value"""
        values = {"value": 1}

        return self.search(query, values)


class EstimateInfo:
    def __init__(self):
        self.session_count_low = 12
        self.session_count_high = 24
        self.date_of_estimate = datetime.now(timezone.utc)
        self.months_until_renewal = relativedelta(months=+6)
        self.renewal_date = self.date_of_estimate + self.months_until_renewal

    def client_info(self, client_id, first, last, dob):
        self.client_id = client_id
        self.client_first_name = first
        self.client_last_name = last
        self.client_dob = dob

    def therapist_info(
        self, therapist_id, first, last, license_type, tax_id, npi
    ):
        self.therapist_id = therapist_id
        self.therapist_first_name = first
        self.therapist_last_name = last
        self.therapist_license_type = license_type
        self.therapist_tax_id = tax_id
        self.therapist_npi = npi

    def estimate_info(
        self, estimate_type, services_sought, session_rate, location
    ):
        self.estimate_type = estimate_type
        self.services_sought = services_sought
        self.session_rate = session_rate
        self.location = location

    def values(self):
        return (
            self.client_id,
            self.therapist_id,
            str(self.date_of_estimate),
            str(self.renewal_date),
            self.services_sought,
            self.session_rate,
            (int(self.session_rate) * self.session_count_low),
            (int(self.session_rate) * self.session_count_high),
            self.location,
        )


# View
class firstWindow:
    """First window where user can search for whether client is in database."""

    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.columnconfigure(1, weight=1)

        self.first_name_var = tk.StringVar()
        self.first_name_label = tk.Label(self.frame, text="First name:").grid(
            row=0, column=0
        )
        self.first_name_entry = tk.Entry(self.frame)
        self.first_name_entry.grid(
            row=0, column=1, sticky=tk.E + tk.W, padx=10
        )

        self.last_name_var = tk.StringVar()
        self.last_name_label = tk.Label(self.frame, text="Last name:").grid(
            row=1, column=0
        )
        self.last_name_entry = tk.Entry(
            self.frame, textvariable=self.last_name_var
        )
        self.last_name_entry.grid(row=1, column=1, sticky=tk.E + tk.W, padx=10)

        self.results_combobox_var = tk.StringVar()
        self.results_combobox = ttk.Combobox(
            self.frame, textvariable=self.results_combobox_var
        )
        self.results_combobox.state(["readonly"])
        self.results_combobox.grid(row=3, column=1)

        # Buttons frame
        self.buttons_frame = tk.Frame(self.frame)
        self.button = tk.Button(self.buttons_frame, text="Search for client")
        self.button.grid(row=0, column=0, padx=5, ipadx=10)

        self.new_client_button = tk.Button(
            self.buttons_frame, text="Create new client"
        )
        self.new_client_button.grid(row=0, column=1, padx=5, ipadx=10)
        self.buttons_frame.grid(row=2, column=1)

        self.create_gfe_label = tk.Label(
            self.frame, text="Create Good Faith Estimate for selected client?"
        )
        self.create_gfe_label.grid(row=4, column=1)
        self.create_gfe_button = tk.Button(
            self.frame, text="Ok"
        )  # Add command to button
        self.create_gfe_button.grid(row=5, column=1, ipadx=10)

        self.frame.grid(row=0, column=0)


class clientInfoInput:
    """Window for inputting new client information."""

    def __init__(self):
        self.client_info_input = tk.Toplevel()
        self.client_info_input.geometry("400x400")
        self.client_info_input.title("Client information")
        self.client_info_input.columnconfigure(1, weight=1)

        self.firstNameVar = tk.StringVar(self.client_info_input)
        self.firstNameLabel = tk.Label(
            self.client_info_input, text="First name:"
        ).grid(row=0, column=0)
        self.firstNameEntry = tk.Entry(
            self.client_info_input, textvariable=self.firstNameVar
        )
        self.firstNameEntry = self.firstNameEntry.grid(
            row=0, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.lastNameVar = tk.StringVar(self.client_info_input)
        self.lastNameLabel = tk.Label(
            self.client_info_input, text="Last name:"
        ).grid(row=1, column=0)
        self.lastNameEntry = tk.Entry(
            self.client_info_input, textvariable=self.lastNameVar
        )
        self.lastNameEntry = self.lastNameEntry.grid(
            row=1, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.dobVar = tk.StringVar(self.client_info_input)
        self.dobLabel = tk.Label(
            self.client_info_input, text="Date of birth:"
        ).grid(row=2, column=0)
        self.dobEntry = tk.Entry(
            self.client_info_input, textvariable=self.dobVar
        )
        self.dobEntry = self.dobEntry.grid(
            row=2, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.emailVar = tk.StringVar(self.client_info_input)
        self.emailLabel = tk.Label(self.client_info_input, text="Email:").grid(
            row=3, column=0
        )
        self.emailEntry = tk.Entry(
            self.client_info_input, textvariable=self.emailVar
        )
        self.emailEntry = self.emailEntry.grid(
            row=3, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.areaCodeVar = tk.StringVar(self.client_info_input)
        self.areaCodeLabel = tk.Label(
            self.client_info_input, text="Area code:"
        ).grid(row=4, column=0)
        self.areaCodeEntry = tk.Entry(
            self.client_info_input, textvariable=self.areaCodeVar
        )
        self.areaCodeEntry = self.areaCodeEntry.grid(
            row=4, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.phoneNumberVar = tk.StringVar(self.client_info_input)
        self.phoneNumberLabel = tk.Label(
            self.client_info_input, text="Phone number:"
        ).grid(row=5, column=0)
        self.phoneNumberEntry = tk.Entry(
            self.client_info_input, textvariable=self.phoneNumberVar
        )
        self.phoneNumberEntry = self.phoneNumberEntry.grid(
            row=5, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.streetAddressVar = tk.StringVar(self.client_info_input)
        self.streetAddressLabel = tk.Label(
            self.client_info_input, text="Street address"
        ).grid(row=6, column=0)
        self.streetAddressEntry = tk.Entry(
            self.client_info_input, textvariable=self.streetAddressVar
        )
        self.streetAddressEntry = self.streetAddressEntry.grid(
            row=6, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.aptBldgSteVar = tk.StringVar(self.client_info_input)
        self.aptBldgSteLabel = tk.Label(
            self.client_info_input, text="Apt./Bldg/Ste.:"
        ).grid(row=7, column=0)
        self.aptBldgSteEntry = tk.Entry(
            self.client_info_input, textvariable=self.aptBldgSteVar
        )
        self.aptBldgSteEntry = self.aptBldgSteEntry.grid(
            row=7, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.cityVar = tk.StringVar(self.client_info_input)
        self.cityLabel = tk.Label(self.client_info_input, text="City:").grid(
            row=8, column=0
        )
        self.cityEntry = tk.Entry(
            self.client_info_input, textvariable=self.cityVar
        )
        self.cityEntry = self.cityEntry.grid(
            row=8, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.stateVar = tk.StringVar(self.client_info_input)
        self.stateLabel = tk.Label(self.client_info_input, text="State:").grid(
            row=9, column=0
        )
        self.stateEntry = tk.Entry(
            self.client_info_input, textvariable=self.stateVar
        )
        self.stateEntry = self.stateEntry.grid(
            row=9, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.zipVar = tk.StringVar(self.client_info_input)
        self.zipLabel = tk.Label(self.client_info_input, text="Zip:").grid(
            row=10, column=0
        )
        self.zipEntry = tk.Entry(
            self.client_info_input, textvariable=self.zipVar
        )
        self.zipEntry = self.zipEntry.grid(
            row=10, column=1, padx=10, sticky=tk.E + tk.W
        )

        self.enter_button = tk.Button(self.client_info_input, text="Enter")
        self.enter_button.grid(row=11, column=1, ipadx=10)

    def close(self):
        self.client_info_input.destroy()


class GoodFaithEstimateWindow:
    def __init__(self, client_info_tuple, therapist_list):
        self.therapist_list = therapist_list
        self.gfe_window = tk.Toplevel()
        self.gfe_window.geometry("400x400")
        self.gfe_window.title("Create Good Faith Estimate")

        self.client_id, self.first, self.last, self.dob = client_info_tuple

        self.frame = tk.Frame(self.gfe_window)
        self.client_id_label = tk.Label(
            self.frame, text=f"Client ID: {self.client_id}"
        )
        self.client_id_label.grid(row=0, column=0)
        self.full_name_label = tk.Label(
            self.frame, text=f"Client name: {self.first} {self.last}"
        )
        self.full_name_label.grid(row=1, column=0)
        self.dob_label = tk.Label(
            self.frame, text=f"Date of Birth: {self.dob}"
        )
        self.dob_label.grid(row=2, column=0)
        self.frame.grid(row=0, column=1)

        self.estimate_type_label = tk.Label(
            self.gfe_window, text="Initial estimate or renewal:"
        )
        self.estimate_type_label.grid(row=2, column=0)
        self.estimate_types = ("Initial Estimate", "Renewal")
        self.estimate_type_menu_var = tk.StringVar()
        self.estimate_type_menu = ttk.Combobox(
            self.gfe_window, textvariable=self.estimate_type_menu_var
        )
        self.estimate_type_menu["state"] = "readonly"
        self.estimate_type_menu["values"] = self.estimate_types
        self.estimate_type_menu.grid(row=2, column=1)

        self.therapist_label = tk.Label(self.gfe_window, text="Therapist:")
        self.therapist_label.grid(row=3, column=0)
        self.therapist_selection_var = tk.StringVar()
        self.therapist_selection = ttk.Combobox(
            self.gfe_window, textvariable=self.therapist_selection_var
        )
        self.therapist_selection["values"] = self.therapist_list
        self.therapist_selection['state'] = 'readonly'
        self.therapist_selection.grid(row=3, column=1)

        self.services_sought_label = tk.Label(
            self.gfe_window, text="Services sought:"
        )
        self.services_sought_label.grid(row=4, column=0)
        services = ("90837", "90847")
        self.services_sought_var = tk.StringVar()
        self.services_sought_menu = ttk.Combobox(
            self.gfe_window, textvariable=self.services_sought_var
        )
        self.services_sought_menu["values"] = services
        self.services_sought_menu["state"] = "readonly"
        self.services_sought_menu.grid(row=4, column=1)

        self.session_rate_label = tk.Label(
            self.gfe_window, text="Session rate:"
        )
        self.session_rate_label.grid(row=5, column=0)
        self.session_rate_entry = tk.Entry(self.gfe_window)
        self.session_rate_entry.grid(row=5, column=1)

        self.location_label = tk.Label(
            self.gfe_window, text="Primary location for services:"
        )
        self.location_label.grid(row=6, column=0)
        locations = ("Mount Pleasant", "North Charleston", "Telehealth")
        self.location_var = tk.StringVar()
        self.location_menu = ttk.Combobox(
            self.gfe_window, textvariable=self.location_var
        )
        self.location_menu["values"] = locations
        self.location_menu["state"] = "readonly"
        self.location_menu.grid(row=6, column=1)

        self.submit_button = tk.Button(self.gfe_window, text="Submit")
        self.submit_button.grid(row=7, column=1)

    def close(self):
        self.gfe_window.destroy()


# Controller
class mainApplication:
    """Controller for Good Faith Estimate creator."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Good Faith Estimate")
        self.root.geometry("500x200")
        self.root.columnconfigure(0, weight=1)
        self.window = firstWindow(self.root)
        self.database = SearchDatabase("gfe_db.db")
        self.therapist_data = Therapists("gfe_db.db")
        self.estimate_info = EstimateInfo()

        self.window.button.configure(
            command=lambda: self.display_search_results(self.client_search())
        )
        self.window.new_client_button.configure(
            command=self.show_client_input_window
        )
        self.window.create_gfe_button.configure(
            command=self.show_gfe_input_window
        )

    def num_validator(self, number, length):
        number_regex = re.compile(rf"^[0-9]{{{length}}}$")
        return number_regex.match(number)

    def client_search(self):
        if (
            self.window.first_name_entry.get()
            and self.window.last_name_entry.get()
        ):
            query = (
                "SELECT client_id, first_name, last_name, date_of_birth "
                "FROM clients WHERE first_name=:FirstName and "
                "last_name=:LastName"
            )

            search_parameters = {
                "FirstName": self.window.first_name_entry.get(),
                "LastName": self.window.last_name_entry.get(),
            }

            return self.database.search(query=query, values=search_parameters)

        elif (
            self.window.first_name_entry.get()
            or self.window.last_name_entry.get()
        ):
            query = (
                "SELECT client_id, first_name, last_name, date_of_birth "
                "FROM clients WHERE first_name=:FirstName or "
                "last_name=:LastName"
            )

            search_parameters = {
                "FirstName": self.window.first_name_entry.get(),
                "LastName": self.window.last_name_entry.get(),
            }

            return self.database.search(query=query, values=search_parameters)

        else:
            self.window.results_combobox.set("")

    def display_search_results(self, results):
        if results:
            self.window.results_combobox["values"] = results

        else:
            self.window.results_combobox["values"] = ""
            response = tkmb.askyesno(
                "No results found",
                "Do you want to input a new client into the database?",
            )
            if response:
                self.show_client_input_window()

    def show_client_input_window(self):
        self.client_input_window = clientInfoInput()
        self.client_input_window.enter_button.configure(
            command=self.enter_into_database
        )

    def enter_into_database(self):
        """Inserts data obtained from GUI into the specified database."""
        if (
            self.num_validator(self.client_input_window.areaCodeVar.get(), "3")
            and self.num_validator(
                self.client_input_window.phoneNumberVar.get(), "7"
            )
            and self.num_validator(self.client_input_window.zipVar.get(), "5")
        ):
            query = """INSERT INTO clients (first_name, last_name, date_of_birth,
            email, area_code, phone_number, street, apt_ste_bldg, city, state, zip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

            client_info_tuple = (
                self.client_input_window.firstNameVar.get().rstrip(),
                self.client_input_window.lastNameVar.get().rstrip(),
                self.client_input_window.dobVar.get().rstrip(),
                self.client_input_window.emailVar.get().rstrip(),
                self.client_input_window.areaCodeVar.get().rstrip(),
                self.client_input_window.phoneNumberVar.get().rstrip(),
                self.client_input_window.streetAddressVar.get().rstrip(),
                self.client_input_window.aptBldgSteVar.get().rstrip(),
                self.client_input_window.cityVar.get().rstrip(),
                self.client_input_window.stateVar.get().rstrip(),
                self.client_input_window.zipVar.get().rstrip(),
            )

            self.database.update(query=query, values=client_info_tuple)

            self.client_input_window.close()

        if not self.num_validator(
            self.client_input_window.areaCodeVar.get(), "3"
        ):
            tkmb.showerror("Error", "Please enter a 3 digit areacode.")

        if not self.num_validator(
            self.client_input_window.phoneNumberVar.get(), "7"
        ):
            tkmb.showerror(
                "Error",
                "Please enter a 7 digit phone number with no spaces or other characters (e.g., '-').",
            )

        if not self.num_validator(self.client_input_window.zipVar.get(), "5"):
            tkmb.showerror("Error", "Please enter a 5 digit zip code.")

    def show_gfe_input_window(self):
        """Show and populate window for Good Faith Estimate."""
        if self.window.results_combobox_var.get():
            results_tuple = tuple(
                self.window.results_combobox_var.get().split()
            )
            self.estimate_info.client_info(*results_tuple)
            therapist_options = []
            for therapist in self.therapist_data.therapists:
                therapist_options.append(therapist[0:4])
            self.gfe_input_window = GoodFaithEstimateWindow(
                results_tuple, therapist_options
            )
            self.gfe_input_window.submit_button.configure(
                command=self.create_estimate
            )

    def get_therapist_selection(self):
        query = """SELECT therapist_id, first_name, last_name, license_type,
        tax_id, npi FROM therapists WHERE therapist_id = (?)"""

        therapist = self.gfe_input_window.therapist_selection_var.get()[0]

        return self.database.search(query, therapist)

    def create_estimate(self):
        if not self.num_validator(
            self.gfe_input_window.session_rate_entry.get(), "1,3"
        ):
            tkmb.showerror(
                "Error",
                "Please enter the session rate using only digits and ensure the entry is 999 or below.",
            )
        else:
            self.estimate_info.therapist_info(
                *self.get_therapist_selection()[0]
            )
            self.estimate_info.estimate_info(
                self.gfe_input_window.estimate_type_menu_var.get(),
                self.gfe_input_window.services_sought_var.get(),
                self.gfe_input_window.session_rate_entry.get(),
                self.gfe_input_window.location_var.get(),
            )

            query = """INSERT INTO estimate_details (client_id, therapist_id,
            date_of_estimate, renewal_date, services_sought, session_rate,
            low_estimate, high_estimate, location) VALUES (?, ?, ?, ?, ?, ?, ?,
            ?, ?);"""

            self.database.update(query, self.estimate_info.values())

            gfe_document = GfeDocument(
                "first_section.txt", "second_section.txt", self.estimate_info
            )

            # convert(gfe_document.filename)

            tkmb.showinfo(
                "GFE Created",
                f"The Good Faith Estimate for {self.estimate_info.client_first_name} {self.estimate_info.client_last_name} was successfully created.",
            )

            self.gfe_input_window.close()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    t = mainApplication()
    t.run()
