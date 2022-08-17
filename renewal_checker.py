import sys
import os
import sqlite3
from datetime import datetime
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtG
import PyQt5. QtCore as qtc
from GoodFaithEstimate import resource_path, DatabaseConnection


class MainWindow(qtw.QMainWindow):
    """Creates a window to display all upcoming GFE renewals."""

    def __init__(self, *args, **kwarsg):
        super(MainWindow, self).__init__(*args, **kwarsg)

        self.database = DatabaseConnection(resource_path('gfe_db.db'))

        self.setWindowTitle("Upcoming GFE Renewals")
        widget = qtw.QWidget()
        layout = qtw.QVBoxLayout()
        listWidget = qtw.QListWidget()
        
        query = """SELECT clients.client_id, first_name, last_name, 
        date_of_estimate, renewal_date FROM clients INNER JOIN estimate_details
        on clients.client_id = estimate_details.client_id WHERE renewal_date 
        < DATETIME('now', '1 month')"""

        self.database.cur.execute(query)
        results = self.database.cur.fetchall()
        tableWidget = qtw.QTableWidget()
        tableWidget.setRowCount(len(results)+1)
        tableWidget.setColumnCount(4)

        tableWidget.setItem(0, 0, qtw.QTableWidgetItem('Client ID'))
        tableWidget.setItem(0, 1, qtw.QTableWidgetItem('Client Name'))
        tableWidget.setItem(0, 2, qtw.QTableWidgetItem('Date of Estiamte'))
        tableWidget.setItem(0, 3, qtw.QTableWidgetItem('Renewal Date'))

        for index, record in enumerate(results, 1):
            client_id, first, last, date_of_estimate, renewal = record
            formatted_date_of_estimate = datetime.strptime(date_of_estimate, "%Y-%m-%d %H:%M:%S.%f")
            formatted_date_of_estimate = formatted_date_of_estimate.strftime('%m-%d-%Y')
            formatted_renewal_date = datetime.strptime(renewal, "%Y-%m-%d %H:%M:%S.%f")
            formatted_renewal_date = formatted_renewal_date.strftime("%m-%d-%Y")

            tableWidget.setItem(index, 0, qtw.QTableWidgetItem(str(client_id)))
            tableWidget.setItem(index, 1, qtw.QTableWidgetItem(f'{first} {last}'))
            tableWidget.setItem(index, 2, qtw.QTableWidgetItem(formatted_date_of_estimate))
            tableWidget.setItem(index, 3, qtw.QTableWidgetItem(formatted_renewal_date))


        layout.addWidget(tableWidget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.resize(500,500)

if __name__ == "__main__":
    app = qtw.QApplication([])

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
