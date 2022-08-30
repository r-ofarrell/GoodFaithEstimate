import sys
import sqlite3
import os
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
from PyQt5.QtCore import QDate
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from docx import Document
from location_of_services import address
from document_creator import GfeDocument


def resource_path(relative_path):
    """Get absolute path to a file/database."""

    base_path = getattr(
        sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))
    )

    return os.path.join(base_path, relative_path)


class DatabaseConnection:
    """Establishes a connection with a specified database."""

    def __init__(self, database):
        self.database = database
        self.conn, self.cur = self.create_connection()

    def create_connection(self):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()

        return (conn, cur)

    def close(self):
        self.conn.close()


class MainWindow(qtw.QMainWindow):
    """Creates a window to search for a client in a specified database"""

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.database = DatabaseConnection(resource_path("gfe_db.db"))
        self.new_estimate_window = None
        self.new_client_window = None
        self.client_info = None

        self.first_name_entry = qtw.QLineEdit()
        self.last_name_entry = qtw.QLineEdit()
        self.birth_date = qtw.QDateEdit()
        self.birth_date.setDisplayFormat("MM/dd/yyyy")

        layout = qtw.QFormLayout()
        layout.addRow("First name:", self.first_name_entry)
        layout.addRow("Last name:", self.last_name_entry)
        layout.addRow("Date of birth:", self.birth_date)

        close_button = qtw.QPushButton("Close")
        close_button.clicked.connect(self.close)
        submit = qtw.QPushButton("Submit")
        submit.clicked.connect(
            lambda: self.estimate_info_window()
            if self.client_search()
            else self.client_not_found_dialogue()
        )

        layout.addWidget(submit)
        layout.addWidget(close_button)

        widget = qtw.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def client_search(self):
        "Searches for a client in the specified database."
        query = (
            "SELECT client_id, first_name, last_name, date_of_birth "
            "FROM clients WHERE first_name=:FirstName and "
            "last_name=:LastName and date_of_birth=:DOB"
        )
        search_parameters = {
            "FirstName": self.first_name_entry.text().rstrip(),
            "LastName": self.last_name_entry.text().rstrip(),
            "DOB": self.birth_date.text().rstrip(),
        }

        self.database.cur.execute(query, search_parameters)
        results = self.database.cur.fetchall()

        if results:
            self.client_info = results[0]

            return results[0]

        self.client_info = (
            self.first_name_entry.text(),
            self.last_name_entry.text(),
            self.birth_date.text(),
        )

        return None

    def estimate_info_window(self):
        """Opens a window for inputting information for a Good Faith Estimate."""
        if self.new_estimate_window is None:
            self.new_estimate_window = GoodFaithEstimate(
                self.client_info, self
            )
        self.new_estimate_window.show()

    def client_not_found_dialogue(self):
        """Opens a window when a client is not found in the database."""
        message = (
            "The entered client was not found in the database.\n\n"
            "Would you like to enter the client as a new client?"
        )
        enter_new_client = qtw.QMessageBox.question(
            self, "Client not found", message
        )
        if enter_new_client == qtw.QMessageBox.Yes:
            self.show_new_client_window()
        else:
            self.show()

    def show_new_client_window(self):
        """Opens a window for inputting a new client's information."""
        if self.new_client_window is None:
            self.new_client_window = ClientInfoEntry(self.client_info, self)
        self.new_client_window.show()


class GoodFaithEstimate(qtw.QWidget):
    """A GUI for obtaining information to make a Good Faith Estimate."""

    def __init__(self, client_info, parent_window=None):
        super(qtw.QWidget, self).__init__()

        self.parent_window = parent_window
        self.database = DatabaseConnection(resource_path("gfe_db.db"))
        self.client_id = client_info[0]
        self.first_name = client_info[1]
        self.last_name = client_info[2]
        self.date_of_birth = client_info[3]

        self.setWindowTitle("Good Faith Estimate Details")

        self.client_name_label = qtw.QLabel(
            f"Client ID: {self.client_id}\n"
            f"Name: {self.first_name} {self.last_name}\n"
            f"Date of Birth: {self.date_of_birth}"
        )

        self.first_or_additional = qtw.QComboBox()
        self.first_or_additional.addItems(["First year", "Additional year"])
        self.therapists = qtw.QComboBox()

        query = """SELECT first_name, last_name FROM therapists WHERE 
        therapist_status = 1;"""
        self.database.cur.execute(query)
        results = self.database.cur.fetchall()
        for therapist in results:
            self.therapists.addItem(f"{therapist[0]} {therapist[1]}")

        self.services_sought = qtw.QComboBox()
        self.services_sought.addItems(["90837", "90847"])
        self.session_rate = qtw.QLineEdit()
        self.session_rate.setValidator(qtg.QIntValidator(0, 5000, self))
        self.location = qtw.QComboBox()
        self.location.addItems(
            ["Mount Pleasant", "North Charleston", "Telehealth"]
        )

        layout = qtw.QFormLayout()
        layout.addWidget(self.client_name_label)
        layout.addRow(
            "GFE within first year \nor GFE for additional year",
            self.first_or_additional,
        )
        layout.addRow("Therapist:", self.therapists)
        layout.addRow("Services sought:", self.services_sought)
        layout.addRow("Session rate:", self.session_rate)
        layout.addRow("Location for services:", self.location)

        submit = qtw.QPushButton("Submit")
        submit.clicked.connect(self.create_document)
        submit.clicked.connect(lambda: self.insert_estimate_details())
        submit.clicked.connect(qtw.QApplication.closeAllWindows)

        layout.addWidget(submit)

        self.setLayout(layout)

    def create_document(self):
        """Creates a Good Faith Estimate docx file."""
        GfeDocument(
        resource_path("first_section.txt"),
        resource_path("second_section.txt"),
        self.information_for_estimate(),
        )

    def information_for_estimate(self):
        """Creates a dictionary of information needed for a GFE."""
        (
            therapist_id,
            therapist_first,
            therapist_last,
            license_type,
            tax_id,
            npi,
        ) = self.therapist_info()
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth,
            "date": datetime.now(),
            "services_sought": self.services_sought.currentText(),
            "rate": self.session_rate.text(),
            "therapist_first": therapist_first,
            "therapist_last": therapist_last,
            "license_type": license_type,
            "tax_id": tax_id,
            "npi": npi,
            "first_or_additional_year": self.first_or_additional.currentText(),
            "location": self.location.currentText(),
        }

    def therapist_info(self):
        """Pulls information about a specified therapist from database."""
        full_name = self.therapists.currentText().split()
        first_name = full_name[0]
        last_name = full_name[1]

        query = """SELECT therapist_id, license_type, tax_id, npi FROM therapists WHERE 
        first_name = (?) and last_name = (?)"""
        values = (first_name, last_name)
        self.database.cur.execute(query, values)
        therapist_id, license_type, tax_id, npi = self.database.cur.fetchone()

        return (therapist_id, first_name, last_name, license_type, tax_id, npi)


    def insert_estimate_details(self):
        """Inserts data obtained from GUI into the specified database."""
        query = """INSERT INTO estimate_details (client_id, therapist_id, 
        date_of_estimate, renewal_date, services_sought, session_rate, 
        low_estimate, high_estimate, location) VALUES (?, ?, ?, ?, ?, ?, ?, 
        ?, ?);"""

        therapist_id = self.therapist_info()[0]
        date_of_estimate = datetime.now()
        months_until_renewal = relativedelta(months=+6)
        renewal_date = date_of_estimate + months_until_renewal
        session_count_low = 12
        session_count_high = 24

        values_tuple = (
            self.client_id,
            therapist_id,
            str(date_of_estimate),
            str(renewal_date),
            self.services_sought.currentText(),
            self.session_rate.text(),
            int(self.session_rate.text()) * session_count_low,
            int(self.session_rate.text()) * session_count_high,
            self.location.currentText(),
        )

        self.database.cur.execute(query, values_tuple)
        self.database.conn.commit()
        self.database.close()


class ClientInfoEntry(qtw.QWidget):
    """Creates GUI for inputting information about a new client."""

    def __init__(self, client_info, parent):
        super(qtw.QWidget, self).__init__()

        self.first_name, self.last_name, self.date_of_birth = client_info
        self.parent = parent
        self.new_estimate_window = None
        self.client_info = None
        self.database = DatabaseConnection(resource_path("gfe_db.db"))

        self.setWindowTitle("Enter New Client Information")

        self.first_name_label = qtw.QLabel(self.first_name)
        self.last_name_label = qtw.QLabel(self.last_name)
        self.date_of_birth_label = qtw.QLabel(self.date_of_birth)

        self.email = qtw.QLineEdit()

        self.area_code = qtw.QLineEdit()
        area_code_regx = qtc.QRegExp(r"\d{3}")
        self.area_code_validator = qtg.QRegExpValidator(
            area_code_regx, self.area_code
        )
        self.area_code.setValidator(self.area_code_validator)

        self.phone = qtw.QLineEdit()
        phone_regx = qtc.QRegExp(r"\d{7}")
        self.phone_validator = qtg.QRegExpValidator(phone_regx, self.phone)
        self.phone.setValidator(self.phone_validator)

        self.street = qtw.QLineEdit()
        self.apt_ste_bldg = qtw.QLineEdit()
        self.city = qtw.QLineEdit()
        self.state = qtw.QLineEdit()
        self.zip = qtw.QLineEdit()
        zip_regx = qtc.QRegExp(r"\d{5}")
        self.zip_validator = qtg.QRegExpValidator(zip_regx, self.zip)
        self.zip.setValidator(self.zip_validator)

        layout = qtw.QFormLayout()
        layout.addWidget(self.first_name_label)
        layout.addWidget(self.last_name_label)
        layout.addWidget(self.date_of_birth_label)
        layout.addRow("Email:", self.email)
        layout.addRow("Area code:", self.area_code)
        layout.addRow("Phone number:", self.phone)
        layout.addRow("Street:", self.street)
        layout.addRow("Apt/Ste/Bldg:", self.apt_ste_bldg)
        layout.addRow("City:", self.city)
        layout.addRow("State:", self.state)
        layout.addRow("Zip:", self.zip)

        submit = qtw.QPushButton("Submit")
        cancel = qtw.QPushButton("Cancel")
        submit.clicked.connect(lambda: self.enter_into_database())
        submit.clicked.connect(lambda: self.pull_from_database())
        submit.clicked.connect(self.close)
        submit.clicked.connect(self.estimate_info_window)
        cancel.clicked.connect(self.close)
        cancel.clicked.connect(parent.show)

        layout.addWidget(submit)
        layout.addWidget(cancel)

        self.setLayout((layout))

    def enter_into_database(self):
        """Inserts data obtained from GUI into the specified database."""
        query = """INSERT INTO clients (first_name, last_name, date_of_birth, 
        email, area_code, phone_number, street, apt_ste_bldg, city, state, zip) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

        values_tuple = (
            self.first_name,
            self.last_name,
            self.date_of_birth,
            self.email.text(),
            self.area_code.text(),
            self.phone.text(),
            self.street.text(),
            self.apt_ste_bldg.text(),
            self.city.text(),
            self.state.text(),
            self.zip.text(),
        )

        self.database.cur.execute(query, values_tuple)
        self.database.conn.commit()

        print("Success")

    def pull_from_database(self):
        """Retrieves data from specified database to populate a new window."""
        query = (
            "SELECT client_id, first_name, last_name, date_of_birth "
            "FROM clients WHERE first_name=:FirstName and "
            "last_name=:LastName and date_of_birth=:DOB"
        )

        search_parameters = {
            "FirstName": self.first_name.rstrip(),
            "LastName": self.last_name.rstrip(),
            "DOB": self.date_of_birth.rstrip(),
        }

        self.database.cur.execute(query, search_parameters)
        results = self.database.cur.fetchall()

        self.client_info = results[0]

    def estimate_info_window(self):
        """Opens a window for inputting data for a Good Faith Estimate."""
        if self.new_estimate_window is None:
            self.new_estimate_window = GoodFaithEstimate(
                self.client_info, self
            )
        self.new_estimate_window.show()


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
