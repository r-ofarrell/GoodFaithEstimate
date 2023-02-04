import tkinter as tk
from tkinter import ttk
import re
from tkinter import messagebox as tkmb
from tkinter import filedialog
from pathlib import Path

from widget import AreaCodeEntry, DobEntry, PhoneNumberEntry, LabelInput, ZipcodeEntry


class ClientSelectionWindow(ttk.Frame):
    """Window for searching and selecting a client."""

    def _add_frame(self, label, cols=2):
        """Add a labelframe to the window."""

        frame = ttk.LabelFrame(self, text=label)
        frame.grid(sticky=tk.W + tk.E)
        for i in range(cols):
            frame.columnconfigure(i, weight=1)
        return frame

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._vars = {
            "first": tk.StringVar(),
            "last": tk.StringVar(),
            "search_results": tk.StringVar(),
        }

        self.add_or_search = self._add_frame("Add or search for a client")
        self.first_name = LabelInput(
            self.add_or_search, "First name:", self._vars["first"]
        )
        self.last_name = LabelInput(
            self.add_or_search, "Last name:", self._vars["last"]
        )
        self.search_btn = ttk.Button(
            self.add_or_search, text="Search", command=self._on_search
        )
        self.create_new_btn = ttk.Button(
            self.add_or_search, text="Create new client", command=self._on_create
        )
        self.search_results_label = ttk.Label(self.add_or_search, text="Search results")
        self.search_results = ttk.Combobox(
            self.add_or_search, textvariable=self._vars["search_results"]
        )
        self.search_results["state"] = "readonly"
        self.create_estimate_btn = ttk.Button(
            self.add_or_search,
            text="Create estimate",
            command=self._on_create_estimate,
        )

        self.first_name.grid(row=0, column=0, columnspan=2)
        self.last_name.grid(row=1, column=0, columnspan=2)
        self.search_btn.grid(row=2, column=0, sticky=tk.W)
        self.create_new_btn.grid(row=2, column=1, sticky=tk.E)
        self.search_results_label.grid(row=3, column=0, columnspan=2)
        self.search_results.grid(row=4, column=0, columnspan=2)
        self.create_estimate_btn.grid(row=5, column=0, columnspan=2)

    def _on_search(self):
        self.event_generate("<<Search>>")

    def _on_create(self):
        self.event_generate("<<CreateClient>>")

    def _on_create_estimate(self):
        self.event_generate("<<CreateEstimate>>")

    def get(self):
        data = dict()
        for key, var in self._vars.items():
            try:
                data[key] = var.get()
            except tk.TclError:
                message = f"Errror in {key}: {key} not found."
                raise ValueError(message)

        return data


class NewClientWindow(ttk.Frame):
    """Window for inputting a new client's information."""

    def _add_frame(self, label, cols=2):
        """Add a labelframe to the window."""

        frame = ttk.LabelFrame(self, text=label)
        frame.grid(sticky=tk.W + tk.E)
        for i in range(cols):
            frame.columnconfigure(i, weight=1)
        return frame

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._vars = {
            "first_name": tk.StringVar(),
            "last_name": tk.StringVar(),
            "date_of_birth": tk.StringVar(),
            "area_code": tk.StringVar(),
            "phone_number": tk.StringVar(),
            "street": tk.StringVar(),
            "apt_bldg_ste": tk.StringVar(),
            "city": tk.StringVar(),
            "state": tk.StringVar(),
            "zipcode": tk.StringVar(),
        }

        new_client = self._add_frame("New client info", cols=1)
        LabelInput(new_client, "First name", self._vars["first_name"]).grid()
        LabelInput(new_client, "Last name", self._vars["last_name"]).grid()
        LabelInput(
            new_client, "Date of birth", self._vars["date_of_birth"], input_class=DobEntry
        ).grid()
        LabelInput(
            new_client, "Area code", self._vars["area_code"], input_class=AreaCodeEntry
        ).grid()
        LabelInput(
            new_client, "Phone number", self._vars["phone_number"], input_class=PhoneNumberEntry
        ).grid()
        LabelInput(new_client, "Street", self._vars["street"]).grid()
        LabelInput(
            new_client, "Apt/Bldg/Ste", self._vars["apt_bldg_ste"]
        ).grid()
        LabelInput(new_client, "City", self._vars["city"]).grid()
        LabelInput(new_client, "State", self._vars["state"]).grid()
        LabelInput(new_client, "Zip", self._vars["zipcode"], input_class=ZipcodeEntry).grid()
        submit_btn = ttk.Button(
            new_client, text="Submit", command=self._on_submit
        )
        submit_btn.grid()

    def _on_submit(self):
        self.event_generate("<<Submit>>")

    def get(self):
        data = dict()
        for key, variable in self._vars.items():
            try:
                data[key] = variable.get()
            except tk.TclError:
                message = f"Errror in {key}: {key} not found."
                raise ValueError(message)

        return data


class CreateEstimateWindow(ttk.Frame):
    """Window for inputting information for a Good Faith Estimate."""

    def _add_frame(self, label, cols=2):
        """Add a labelframe to the window."""

        frame = ttk.LabelFrame(self, text=label)
        frame.grid(sticky=tk.W + tk.E)
        for i in range(cols):
            frame.columnconfigure(i, weight=1)
        return frame

    def __init__(self, parent, lr_data, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._vars = {
            "new_or_update": tk.StringVar(),
            "services_sought": tk.StringVar(),
            "therapist": tk.StringVar(),
            "session_rate": tk.StringVar(),
            "location": tk.StringVar(),
        }

        estimate_info = self._add_frame("Estimate information", cols=1)
        new_or_update = LabelInput(
            estimate_info,
            "New or updated estimate?",
            self._vars["new_or_update"],
            ttk.Combobox
        )
        new_or_update.input["state"] = "readonly"
        new_or_update.input["values"] = ["New", "Update"]
        services_sought = LabelInput(
            estimate_info,
            "Services sought",
            self._vars["services_sought"],
            ttk.Combobox
        )
        services_sought.input["state"] = "readonly"
        services_sought.input["values"] = lr_data["services"]
        therapist_selection = LabelInput(
            estimate_info, "Therapist", self._vars["therapist"], ttk.Combobox
        )
        therapist_selection.input["state"] = "readonly"
        therapist_selection.input["values"] = lr_data["therapists"]
        session_rate = LabelInput(
            estimate_info, "Session rate", self._vars["session_rate"]
        )
        location = LabelInput(
            estimate_info,
            "Location of services",
            self._vars["location"],
            ttk.Combobox,
        )
        location.input["state"] = "readonly"
        location.input["values"] = lr_data["location"]
        create_estimate_btn = ttk.Button(
            estimate_info,
            text="Create Estimate",
            command=self._on_create_estimate,
        )

        new_or_update.grid(sticky=tk.W + tk.E)
        services_sought.grid(sticky=tk.W + tk.E)
        therapist_selection.grid(sticky=tk.W + tk.E)
        session_rate.grid(sticky=tk.W + tk.E)
        location.grid(sticky=tk.W + tk.E)
        create_estimate_btn.grid(sticky=tk.W + tk.E)

    def _on_create_estimate(self):
        self.event_generate("<<CreateEstimate>>")

    def get(self):
        data = dict()
        for key, variable in self._vars.items():
            try:
                data[key] = variable.get()
            except tk.TclError:
                message = f"Errror in {key}: {key} not found."
                raise ValueError(message)

        return data


class databaseDialog(ttk.Frame):
    """Dialog window for finding or creating a file."""
    def _add_frame(self, label, cols=2):
        """Add a labelframe to the window."""

        frame = ttk.LabelFrame(self, text=label)
        frame.grid(sticky=tk.W + tk.E)
        for i in range(cols):
            frame.columnconfigure(i, weight=1)
        return frame

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        database_dialog = self._add_frame("Good Faith Estimate Database", cols=1)
        no_database_message = (f'If you already have a database, click "Search" to find it,\n'
                               f'otherwise click "Create" to make a new database.')
        ttk.Label(database_dialog, text=no_database_message).pack()
        search_btn = ttk.Button(database_dialog, text="Search", command=self.search_db_option)
        create_btn = ttk.Button(database_dialog, text="Create", command=self.create_db_option)
        cancel_btn = ttk.Button(database_dialog, text="Cancel", command=self.close)

        search_btn.pack()
        create_btn.pack()


    @classmethod
    def check_if_db_exists(self, filepath):
        return Path(filepath).exists()

    def create_db_option(self):
        filedialog.asksaveasfile()

    def search_db_option(self):
        filedialog.askopenfile()

    def close(self):
        pass


if __name__ == "__main__":
    estimate_lists = {
        "services_sought": ("90837", "90847"),
        "therapists": (
            "Ryan O'Farrell, Psy.D.",
            "Jacquie Atkins, LPC",
            "Sydney Reynolds, LPC",
        ),
        "location": ("Mount Pleasant", "North Charleston", "Telehealth"),
    }
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    database = databaseDialog(root)
    database.pack()
    # client_selection = ClientSelectionWindow(root)
    # client_selection.columnconfigure(0, weight=1)
    # client_selection.grid(sticky=tk.W + tk.E)
    # new_client = NewClientWindow(root)
    # new_client.columnconfigure(0, weight=1)
    # new_client.grid(sticky=tk.W + tk.E)
    # estimate_info = CreateEstimateWindow(root, estimate_lists)
    # estimate_info.columnconfigure(0, weight=1)
    # estimate_info.grid(sticky=tk.W + tk.E)

    # first_var = tk.StringVar()
    # last_var = tk.StringVar()
    # LabelInput(client_selection, "First name:", first_var).grid()
    # LabelInput(client_selection, "Last name:", last_var).grid()

    root.mainloop()
