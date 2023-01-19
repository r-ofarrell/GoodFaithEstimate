import tkinter as tk
from tkinter import ttk
import re
from tkinter import messagebox as tkmb

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
            "client_first": tk.StringVar(),
            "client_last": tk.StringVar(),
            "client_dob": tk.StringVar(),
            "client_area_code": tk.StringVar(),
            "client_phone": tk.StringVar(),
            "client_street": tk.StringVar(),
            "client_apt_bldg_ste": tk.StringVar(),
            "client_city": tk.StringVar(),
            "client_state": tk.StringVar(),
            "client_zip": tk.StringVar(),
        }

        new_client = self._add_frame("New client info", cols=1)
        LabelInput(new_client, "First name", self._vars["client_first"]).grid()
        LabelInput(new_client, "Last name", self._vars["client_last"]).grid()
        LabelInput(
            new_client, "Date of birth", self._vars["client_dob"], input_class=DobEntry
        ).grid()
        LabelInput(
            new_client, "Area code", self._vars["client_area_code"], input_class=AreaCodeEntry
        ).grid()
        LabelInput(
            new_client, "Phone number", self._vars["client_phone"], input_class=PhoneNumberEntry
        ).grid()
        LabelInput(new_client, "Street", self._vars["client_street"]).grid()
        LabelInput(
            new_client, "Apt/Bldg/Ste", self._vars["client_apt_bldg_ste"]
        ).grid()
        LabelInput(new_client, "City", self._vars["client_city"]).grid()
        LabelInput(new_client, "State", self._vars["client_state"]).grid()
        LabelInput(new_client, "Zip", self._vars["client_zip"], input_class=ZipcodeEntry).grid()
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
    client_selection = ClientSelectionWindow(root)
    client_selection.columnconfigure(0, weight=1)
    client_selection.grid(sticky=tk.W + tk.E)
    new_client = NewClientWindow(root)
    new_client.columnconfigure(0, weight=1)
    new_client.grid(sticky=tk.W + tk.E)
    estimate_info = CreateEstimateWindow(root, estimate_lists)
    estimate_info.columnconfigure(0, weight=1)
    estimate_info.grid(sticky=tk.W + tk.E)

    # first_var = tk.StringVar()
    # last_var = tk.StringVar()
    # LabelInput(client_selection, "First name:", first_var).grid()
    # LabelInput(client_selection, "Last name:", last_var).grid()

    root.mainloop()
