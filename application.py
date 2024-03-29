import sqlite3
import tkinter as tk
from tkinter import messagebox as tkmb
from tkinter import ttk, Toplevel
from tkinter import filedialog
from pathlib import Path, PurePath
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
import pdfkit
from dateutil.relativedelta import relativedelta
from jinja2 import Environment, FileSystemLoader
from configparser import ConfigParser

from markupsafe import re
import models
import views
import widgets


@dataclass
class Client:
    """Represents a selected client."""

    client_id: int
    first_name: str
    last_name: str
    date_of_birth: str
    email: str
    area_code: str
    phone_number: str
    street: str
    apt_bldg_ste: str
    city: str
    state: str
    zipcode: str
    diagnosis: str = None

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def last_first(self):
        return f"{self.last_name}_{self.first_name}"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def create_from_dict(cls, d):
        return Client(**d)


@dataclass
class Therapist:
    """Represents a selected therapist."""

    therapist_id: int
    first_name: str
    last_name: str
    license_type: str
    tax_id: str
    npi: str

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_name_and_license(self):
        return f"{self.first_name} {self.last_name}, {self.license_type}"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def create_from_dict(cls, d):
        return Therapist(**d)


@dataclass
class Service:
    """Represents details for therapeutic services."""

    new_or_update: str
    services_sought: tuple
    session_rate: str
    location: str
    services_sought: str
    full_address: tuple = field(default=None, init=False)
    service_code: str = field(default=None, init=False)
    session_count_low: int = 12
    session_count_high: int = 24
    registration_service_code: str = "None"
    registration_fee: int = 25
    registration_qty: int = 1
    intake_service_code: str = "90791"
    intake_qty: int = 1
    new_client_dx_code: str = "None"

    def __post_init__(self):
        self.service_code = self.services_sought.split()[1]

    def to_dict(self):
        return asdict(self)

    @classmethod
    def create_from_dict(cls, d):
        return Service(**d)

    def get_address(self):
        """Returns formatted address for where services will be provided."""

        location_city = ' '.join(self.location.split()[1:])

        if location_city == "Mount Pleasant":
            self.full_address = (
                "890 Johnnie Dodds Blvd.",
                "Bldg. 3 Ste. A",
                "Mount Pleasant, S.C. 29464",
            )
        elif location_city == "North Charleston":
            self.full_address = (
                "9263 Medical Plaza Dr.",
                "Ste. B",
                "North Charleston, S.C. 29406",
            )
        else:
            self.full_address = ("Telehealth",)

        return self.full_address

    def new_gfe_low_total_estimate(self):
        return (
            int(self.session_rate) * (self.session_count_low + self.intake_qty)
            + self.registration_fee
        )

    def new_gfe_high_total_estimate(self):
        return (
            int(self.session_rate)
            * (self.session_count_high + self.intake_qty)
            + self.registration_fee
        )

    def update_gfe_low_total_estimate(self):
        return int(self.session_rate) * self.session_count_low

    def update_gfe_high_total_estimate(self):
        return int(self.session_rate) * self.session_count_high

    def new_low_estimate_table_rows(self):
        service_total = int(self.session_rate) * self.session_count_low
        registration_row = (
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

        return (registration_row, intake_appt, service)

    def new_high_estimate_table_rows(self):
        service_total = int(self.session_rate) * self.session_count_high
        registration_row = (
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

        return (registration_row, intake_appt, service)

    def update_low_estimate_table_rows(self, client_obj):
        service_total = int(self.session_rate) * self.session_count_low
        service = (
            "Psychotherapy",
            self.service_code,
            client_obj.diagnosis,
            self.session_rate,
            self.session_count_low,
            service_total,
        )

        return service

    def update_high_estimate_table_rows(self, client_obj):
        service_total = int(self.session_rate) * self.session_count_high
        service = (
            "Psychotherapy",
            self.service_code,
            client_obj.diagnosis,
            self.session_rate,
            self.session_count_high,
            service_total,
        )

        return service


class Time:
    def __init__(self):
        self.timestamp = datetime.now(timezone.utc)
        self.timestamp_formatted = self.timestamp.strftime("%m-%d-%Y")
        self.months_until_renewal = relativedelta(months=+6)
        self.renewal_date = self.timestamp + self.months_until_renewal


class Text:
    def __init__(self, section1, section2):
        self.section1 = self.create_text_sections(section1)
        self.section2 = self.create_text_sections(section2)

    def create_text_sections(self, file: str) -> str:
        """Reads text from a file and uses to populate sections of a Good Faith Estimate"""
        section = []
        hold = []
        lines = []
        with open(file) as text:
            for line in text:
                section.append(line)

        for num, line in enumerate(section):
            if line == "\n" or num == (len(section) - 1):
                lines.append("".join(hold))
                hold = []
            else:
                hold.append(line.rstrip() + " ")

        return lines

@dataclass
class EstimateDetails:
    client: object
    therapist: object
    service_info: object
    time: object

    def get_data_for_database(self):
        most_recent_estimate = 1
        if self.service_info.new_or_update == "New":
            data = (
                self.client.client_id,
                self.therapist.therapist_id,
                self.time.timestamp,
                self.time.renewal_date,
                self.service_info.services_sought.split()[0],
                self.service_info.session_rate,
                self.service_info.new_gfe_low_total_estimate(),
                self.service_info.new_gfe_high_total_estimate(),
                self.service_info.location.split()[0],
                most_recent_estimate
            )
        else:
            data = (
                self.client.client_id,
                self.therapist.therapist_id,
                self.time.timestamp,
                self.time.renewal_date,
                self.service_info.services_sought.split()[0],
                self.service_info.session_rate,
                self.service_info.update_gfe_low_total_estimate(),
                self.service_info.update_gfe_high_total_estimate(),
                self.service_info.location.split()[0],
                most_recent_estimate
            )

        return data


class MainApplication:
    """Good Faith Estimate creator application."""

    def __init__(self, *args, **kwargs) -> None:
        self.root = tk.Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.geometry("300x300")
        self.database = self.check_for_database()
        self.search_window = views.ClientSelectionWindow(self.root)
        self.configuration = models.Configuration()
        self.save_directory = self.set_save_directory()
        self.new_client_window = None
        self.new_window = None
        self.estimate_window = None
        self.client = None
        self.therapist = None
        self.service_info = None
        self.time = None
        self.text = Text("first_section.txt", "second_section.txt")
        self.estimate_details = None
        self.filename = None
        self.new_window1 = None
        self.new_window2 = None

        self.search_window.bind("<<Search>>", self._get_client_from_db)
        self.search_window.bind(
            "<<CreateClient>>", self._show_new_client_window
        )
        self.search_window.bind(
            "<<CreateEstimate>>", self._show_estimate_window
        )


        self.life_resources_data = dict()
        therapist_query = """SELECT therapist_id, first_name, last_name,
        license_type FROM therapists WHERE therapist_status = 1"""
        self.database.search_and_return_tuple(therapist_query)
        therapist_values = []
        for therapist in self.database.get_search_results():
            therapist_values.append(
                f"{therapist[0]} {' '.join(therapist[1:3])}, {therapist[3]}"
            )
        self.life_resources_data["therapists"] = therapist_values

        services_query = """SELECT * FROM services"""
        self.database.search_and_return_tuple(services_query)
        service_values = []
        for service in self.database.get_search_results():
            service_values.append(f"{service[0]} {' '.join(service[1:])}")
        self.life_resources_data["services"] = service_values

        locations_query = """SELECT location_id, city FROM locations"""
        self.database.search_and_return_tuple(locations_query)
        location_values = []
        for location in self.database.get_search_results():
            location_values.append(
                f"{location[0]} {' '.join(location[1:])}")
        self.life_resources_data["location"] = location_values

        self.search_window.grid()
        self.root.mainloop()

    def check_for_database(self):
        """Checks if database exists and if not, creates appropriate database."""
        if not Path('gfe_db.db').exists():
            if tkmb.askyesno("Database not found",
                             "Do you want to create a database?"):
                db = models.Database('gfe_db.db')
                db.create_db_tables()
                return db

            else:
                instructions = ("Program will close now. Please move database"
                                " to the directory where the application"
                                " is located or run the program again to create"
                                " a database.")
                tkmb.showinfo(
                    "Database not found", instructions
                    )
                self.root.destroy()
                return None

        return models.Database('gfe_db.db')

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
            tkmb.showerror(
                "Error",
                """Please enter, at a minimum, the first or last name of the client you want to search for.""",
            )
            return None

        self.database.search_and_return_tuple(query, values)
        results = self.database.get_search_results()
        if results:
            self.search_window.search_results["values"] = results
        else:
            if tkmb.askyesno(
                "Create new client?",
                "No client was found. Would you like to create a new client?",
            ):
                self._show_new_client_window()
            else:
                return None

    def _show_new_client_window(self, *_) -> None:
        self.new_window1 = Toplevel(self.root)
        self.new_window1.columnconfigure(0, weight=1)
        self.new_window1.rowconfigure(0, weight=1)
        self.new_window1.geometry("400x700")
        self.new_client_window = views.NewClientWindow(self.new_window1)
        self.new_client_window.bind(
            "<<Submit>>", self._input_client_to_database
        )
        self.new_client_window.columnconfigure(0, weight=1)
        self.new_client_window.rowconfigure(0, weight=1)
        self.new_client_window.grid(sticky=tk.W + tk.E + tk.N + tk.S)

    def _input_client_to_database(self, *_):
        client_info = self.new_client_window.get()
        columns = [key for key in client_info.keys()]
        values = [value for value in client_info.values()]
        mark = "?"
        query = f"""INSERT INTO clients ({', '.join(columns)}) VALUES({', '.join(mark * len(columns))})"""
        self.database.update(query, tuple(values))
        tkmb.showinfo("Success", f"{client_info['first_name']} {client_info['last_name']} was created successfully.")
        self.new_window1.destroy()

    def _show_estimate_window(self, *_) -> None:
        self.client = self._get_client()
        self.new_window2 = Toplevel(self.root)
        self.new_window2.columnconfigure(0, weight=1)
        self.new_window2.rowconfigure(0, weight=1)
        self.new_window2.geometry("300x400")
        self.estimate_window = views.CreateEstimateWindow(
            self.new_window2, self.life_resources_data
        )
        self.estimate_window.bind("<<CreateEstimate>>", self._create_estimate)
        self.estimate_window.columnconfigure(0, weight=1)
        self.estimate_window.rowconfigure(0, weight=1)
        self.estimate_window.grid(sticky=tk.W + tk.E + tk.N + tk.S)

    def _input_estimate_to_database(self):
        self.estimate_details = EstimateDetails(
            self.client, self.therapist, self.service_info, self.time
        )
        query = """INSERT INTO estimate_details (client_id, therapist_id,
        date_of_estimate, renewal_date, service_id, session_rate,
        low_estimate, high_estimate, location_id, most_recent_estimate)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        self.database.update(
            query,
            self.estimate_details.get_data_for_database(),
        )

    def _get_client(self) -> object:
        query = """SELECT * FROM clients WHERE client_id = (?)"""
        window_data = self.search_window.get()
        selected_client_id = window_data["search_results"].split()[0]
        self.database.search(query, (selected_client_id,))
        results = self.database.get_search_results()
        return Client.create_from_dict(results[0])

    def _get_therapist(self, data: dict) -> object:
        query = """SELECT therapist_id, first_name, last_name, license_type, npi, tax_id
        FROM therapists WHERE therapist_id = (?)"""
        selected_therapist_id = data["therapist"].split()[0]
        self.database.search(query, (selected_therapist_id,))
        results = self.database.get_search_results()
        return Therapist.create_from_dict(results[0])

    def _reset_most_recent_estimate(self):
        """Sets most_recent_estimate in database to 0 (which is False)."""
        query = """UPDATE estimate_details SET most_recent_estimate = 0
        WHERE client_id = (?)"""
        values = (self.client.client_id,)
        self.database.update(query, values)

    def _create_estimate(self, *_):
        estimate_window_data = self.estimate_window.get()
        self.therapist = self._get_therapist(estimate_window_data)
        estimate_window_data.pop("therapist")
        self.service_info = Service.create_from_dict(estimate_window_data)
        self.time = Time()
        self.service_info.date_of_estimate = self.time.timestamp
        self._reset_most_recent_estimate()
        self._input_estimate_to_database()
        self.create_html()
        self.convert_to_pdf()
        self.remove_html(self.filename)
        tkmb.showinfo(
            "GFE Created",
            f"The Good Faith Estimate for {self.client.full_name()} was successfully created.",
        )
        if tkmb.askyesno(
            "Return to client search window?",
            "Would you like to create another estimate?",
        ):
            self.new_window2.destroy()
        else:
            self.root.destroy()

    def generate_filename(self):
        return f"{self.client.last_first()}_{self.time.timestamp.strftime('%Y-%m-%d-%H-%M-%S')}.html"

    def create_html(self):
        """Creates html file that will be converted to pdf."""
        self.filename = self.generate_filename()
        environment = Environment(loader=FileSystemLoader("templates/"))
        template = environment.get_template("html_prototype.html")

        with open(self.filename, mode="w", encoding="utf-8") as html:
            html.write(
                template.render(
                    client=self.client,
                    therapist=self.therapist,
                    service=self.service_info,
                    time=self.time,
                    text=self.text,
                )
            )

    def remove_html(self, file):
        """Removes html file."""
        if Path(file).exists():
            file_to_remove = Path(file)
            file_to_remove.unlink()
        else:
            raise Exception("File does not exist.")

    def set_save_directory(self):
        """Sets directory to save estimate PDFs to."""
        if self.configuration.save_directory:
            save_directory = self.configuration.get_save_directory()

        else:
            if tkmb.askyesno("Choose save directory", "Would you like to choose the directory to save estimate PDFs to?"):
                save_directory = self.configuration.set_save_directory(tk.filedialog.askdirectory())
            else:
                tkmb.showinfo("Save to default directory", "Your estimate PDF will save to the home directory.")
                save_directory = Path.home()

        return PurePath(save_directory)

    def convert_to_pdf(self):
        """Converts html to pdf."""
        css = "style.css"
        pdf_file = f"{self.filename[:-5]}.pdf"
        save_filepath = self.save_directory / pdf_file
        # config = filepath to wkhtmltopdf executable (needed on Windows systems)
        pdfkit.from_file(
            f"{self.filename}",
            save_filepath,
            options={"enable-local-file-access": ""},
            css=css,
            verbose=True
        )

if __name__ == "__main__":
    app = MainApplication()
