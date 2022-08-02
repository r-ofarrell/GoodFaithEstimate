import sys
import sqlite3
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import datetime as dt
from docx import Document
from estimate_details import Client, Therapist, Estimate
from location_of_services import address
from document_creator import GfeDocument
from PyQt5.QtCore import QDate


class MainWindow(qtw.QMainWindow):
    def __init__(self, database, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.database = database
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

        button_layout = qtw.QHBoxLayout()
        close_button = qtw.QPushButton('Close')
        close_button.clicked.connect(self.close)
        submit = qtw.QPushButton("Submit")
        submit.clicked.connect(
                            lambda: self.estimate_info_window()
                            if self.client_search(self.database_connection())
                            else self.client_not_found_dialogue()
                        )

        layout.addWidget(submit)
        layout.addWidget(close_button)

        widget = qtw.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def database_connection(self):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        return cur

    def client_search(self, database_cursor):
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

        database_cursor.execute(query, search_parameters)
        results = database_cursor.fetchall()

        if results:
            print(
                f"I found {results} {self.first_name_entry.text()} "
                f"{self.last_name_entry.text()} in the database!"
            )

            self.client_info = results[0]

            return results[0]

        else:
            print(
                f"This is stupid and does not work. Date of birth: "
                f"{self.birth_date.text()}"
            )

    def estimate_info_window(self):
        if self.new_estimate_window is None:
            self.new_estimate_window = GoodFaithEstimate(self.client_info, self)
        self.new_estimate_window.show()

    def client_not_found_dialogue(self):
        message = (
                "The entered client was not found in the database.\n\n"
                "Would you like to enter the client as a new client?"
                )
        enter_new_client = qtw.QMessageBox.question(self, 'Client note found', message)
        if enter_new_client == qtw.QMessageBox.Yes:
            self.show_new_client_window()
        else:
            self.show()

    def show_new_client_window(self):
        if self.new_client_window is None:
            self.new_client_window = ClientInfoEntry(self) 
        self.new_client_window.show()


class GoodFaithEstimate(qtw.QWidget):
    def __init__(self, client_info, parent_window=None):
        super(qtw.QWidget, self).__init__()

        self.parent_window = parent_window
        self.client_id = client_info[0]
        self.first_name = client_info[1]
        self.last_name = client_info[2]
        self.date_of_birth = client_info[3]

        self.client_info = None
        self.therapist_info = None
        self.estimate_info = None

        self.setWindowTitle("Good Faith Estimate Details")

        self.client_name_label = qtw.QLabel(
            f"Client ID: {self.client_id}\n"
            f"Name: {self.first_name} {self.last_name}\n"
            f"Date of Birth: {self.date_of_birth}"
        )

        self.new_updated = qtw.QComboBox()
        self.new_updated.addItems(["New", "Updated"])
        self.therapists = qtw.QComboBox()
        self.therapists.addItems(
            [
                "Jacquie Atkins, LPC",
                "Carol Conway, LISW-CL",
                "Robin Delaney, Ph.D.",
                "Audrey Godfrey, LPC",
                "Delores Hollen, LPC",
                "Elena Layton, LISW-CL",
                "Ryan O'Farrell, Psy.D.",
                "Sydney Reynolds, LPC",
                "Abbi Russo, LPC-A",
                "Shannon Scott, LPC",
                "Breanne Stevens, LPC",
                "Chris Wells, LPC-A",
                "Carolyn Wenner, LPC",
            ]
        )
        self.services_sought = qtw.QComboBox()
        self.services_sought.addItems(["90837", "90847"])
        self.session_rate = qtw.QLineEdit()
        self.session_rate.setValidator(qtg.QIntValidator(0, 300, self))
        self.location = qtw.QComboBox()
        self.location.addItems(["Mount Pleasant", "North Charleston", "Telehealth"])

        layout = qtw.QFormLayout()
        layout.addWidget(self.client_name_label)
        layout.addRow("New or updated GFE:", self.new_updated)
        layout.addRow("Therapist:", self.therapists)
        layout.addRow("Services sought:", self.services_sought)
        layout.addRow("Session rate:", self.session_rate)
        layout.addRow("Location for services:", self.location)

        submit = qtw.QPushButton("Submit")
        submit.clicked.connect(self.create_client)
        submit.clicked.connect(self.create_therapist)
        submit.clicked.connect(self.create_estimate)
        submit.clicked.connect(self.create_document)
        submit.clicked.connect(self.close)
        submit.clicked.connect(self.parent_window.close)

        layout.addWidget(submit)

        self.setLayout(layout)

    def create_document(self):
        gfe = GfeDocument(
                'gfe_introduction.txt', 'dispute.txt', self.client_info, 
                self.therapist_info, self.estimate_info)

    def create_client(self):
        self.client_info = Client(
                self.first_name,
                self.last_name,
                self.date_of_birth,
                self.services_sought.currentText()
                )

    def create_therapist(self):
        self.therapist_info = Therapist(
                self.therapists.currentText(),
                self.session_rate.text(),
                self.location.currentText()
                )

    def create_estimate(self):
        self.estimate_info = Estimate(
            self.session_rate.text(),
            dt.datetime.now(),
            self.new_updated.currentText()
        )


class ClientInfoEntry(qtw.QWidget):
    def __init__(self, parent):
        super(qtw.QWidget, self).__init__()

        self.parent = parent
        self.new_estimate_window = None
        self.client_info = None
        self.dbconn, self.dbcur = self.database_connection('gfe_db.db')

        self.setWindowTitle("Enter New Client Information")

        self.first_name = qtw.QLineEdit()
        self.last_name = qtw.QLineEdit()
        self.date_of_birth = qtw.QDateEdit()
        self.date_of_birth.setDisplayFormat("MM/dd/yyyy")
        self.email = qtw.QLineEdit()
        self.area_code = qtw.QLineEdit()
        self.phone = qtw.QLineEdit()
        self.street = qtw.QLineEdit()
        self.apt = qtw.QLineEdit()
        self.city = qtw.QLineEdit()
        self.state = qtw.QLineEdit()
        self.zip = qtw.QLineEdit()


        layout = qtw.QFormLayout()
        layout.addRow("First name:", self.first_name)
        layout.addRow("Last name:", self.last_name)
        layout.addRow("Date of Birth:", self.date_of_birth)
        layout.addRow("Email:", self.email)
        layout.addRow("Area code:", self.area_code)
        layout.addRow("Phone number:", self.phone)
        layout.addRow("Street:", self.street)
        layout.addRow("Apt/Ste/Bldg:", self.apt)
        layout.addRow("City:", self.city)
        layout.addRow("State:", self.state)
        layout.addRow("Zip:", self.zip)

        submit = qtw.QPushButton("Submit")
        cancel = qtw.QPushButton("Cancel")
        submit.clicked.connect(lambda: self.enter_into_database(self.dbconn, self.dbcur))
        submit.clicked.connect(lambda: self.pull_from_database(self.dbconn, self.dbcur))
        submit.clicked.connect(self.close)
        submit.clicked.connect(self.estimate_info_window)
        cancel.clicked.connect(self.close)
        cancel.clicked.connect(parent.show)

        layout.addWidget(submit)
        layout.addWidget(cancel)

        self.setLayout((layout))

    def database_connection(self, database):
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        return (conn, cur)


    def enter_into_database(self, conn, cur):
        query = (
                "INSERT INTO clients (first_name, last_name, date_of_birth) "
                "VALUES (?, ?, ?);"
                )

        values_tuple = (
                self.first_name.text(), 
                self.last_name.text(),
                self.date_of_birth.text()
                #                    "Email": self.email.text(),
                #                    "AreaCode": self.area_code.text(),
                #                    "PhoneNumber": self.phone_number.text(),
                #                    "Street": self.street.text(),
                #                    "AptSteBldg": self.apt_ste_bldg.text(),
                #                    "City": self.city.text(),
                #                    "State": self.state.text(),
                #                    "Zip": self.zip.text()
                )

        cur.execute(query, values_tuple)
        conn.commit()

        print("Success")

    def pull_from_database(self, conn, cur):
        query = (
                "SELECT client_id, first_name, last_name, date_of_birth " 
                "FROM clients WHERE first_name=:FirstName and "
                "last_name=:LastName and date_of_birth=:DOB"
        )

        search_parameters = {
            "FirstName": self.first_name.text().rstrip(),
            "LastName": self.last_name.text().rstrip(),
            "DOB": self.date_of_birth.text().rstrip(),
        }

        cur.execute(query, search_parameters)
        results = cur.fetchall()

        self.client_info = results[0]

    def estimate_info_window(self):
        if self.new_estimate_window is None:
            self.new_estimate_window = GoodFaithEstimate(self.client_info)
        self.new_estimate_window.show()




if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    main = MainWindow("gfe_db.db")
    main.show()

    sys.exit(app.exec_())

                #":Email, :AreaCode, :PhoneNumber, :Street, :AptSteBldg, :City, "
                #":State, :Zip"

