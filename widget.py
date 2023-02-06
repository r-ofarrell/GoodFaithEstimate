import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmb
from datetime import datetime
import re


# Why the commented code doesn't work as expected is beyond me. I'm leaving
# it here with the hopes that I'll figure it out one day.
# But when I create two LabelInputs, it leads to one label and two inputs,
# with the second label overriding the first. No idea why.
#
# class LabelInput(tk.Frame):
#     """A widget with a label and an input together."""
#     def __init__(self, parent, label, var, input_type=ttk.Entry,
#                  input_args=None, label_args=None, **kwargs):
#         super().__init__(parent, **kwargs)
#         self.input_args = input_args or {}
#         self.label_args = label_args or {}
#         self.variable = var

#         # Setup label
#         if input_type == ttk.Checkbutton:
#             self.input_args['text'] = label
#         else:
#             self.label = ttk.Label(parent, text=label, **self.label_args)
#             self.label.grid(row=0, column=0, sticky=tk.W + tk.E)

#         # Setup the variable
#         if input_type in (ttk.Checkbutton, ttk.Radiobutton):
#             self.input_args['variable'] = self.variable
#         else:
#             self.input_args['textvariable'] = self.variable

#         # Setup the input
#         if input_type == ttk.Radiobutton:
#             self.input = tk.Frame(self)
#             for v in input_args.pop('values', []):
#                 button = ttk.Radiobutton(
#                     self, value=v, text=v, **input_args
#                 )
#             button.pack(side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x')
#         else:
#             self.input = input_type(self, **self.input_args)

#         self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
#         self.columnconfigure(0, weight=1)

#     def grid(self, sticky=(tk.E + tk.W), **kwargs):
#         """Override grid to add default sticky values"""
#         super().grid(sticky=sticky, **kwargs)
#


class DobEntry(ttk.Entry):
    """An Entry widget enforcing dates in yyyy-mm-dd format."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.error = tk.StringVar()
        self.configure(
            validate="all",
            validatecommand=(
                self.register(self._validate),
                "%S",
                "%i",
                "%V",
                "%d",
            ),
            invalidcommand=(self.register(self._invalid), "%V"),
        )

    def _validate(self, char, index, event, action):
        self._toggle_error()
        valid = True

        if event == "key":
            if action == "0":
                valid = True
            elif index in ("0", "1", "3", "4", "6", "7", "8", "9"):
                valid = char.isdigit()
            elif index in ("2", "5"):
                valid = char == "-"
            else:
                valid = False
        elif event == "focusout":
            try:
                datetime.strptime(self.get(), "%m-%d-%Y")
            except ValueError:
                valid = False

        return valid

    def _invalid(self, event):
        self._toggle_error("Please enter date of birth as mm-dd-yyyy")

    def _toggle_error(self, error=""):
        self.error.set(error)
        self.config(foreground="red" if error else "black")


class AreaCodeEntry(ttk.Entry):
    """An Entry widget that accepts a 3 digit area code."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.error = tk.StringVar()
        self.configure(
            validate="all",
            validatecommand=(
                self.register(self._validate),
                "%S",
                "%V",
                "%d",
                "%P",
            ),
            invalidcommand=(self.register(self._invalid), "%V"),
        )

    def _validate(self, char, event, action, proposed):
        self._toggle_error()
        valid = True
        if event == "key":
            if action == "0":
                valid = True
            elif not char.isdigit():
                valid = False
        elif event == "focusout":
            valid = len(self.get()) == 3

        return valid

    def _invalid(self, event):
        self._toggle_error("Please enter a 3 digit area code")

    def _toggle_error(self, error=""):
        self.error.set(error)
        self.config(foreground="red" if error else "black")


class PhoneNumberEntry(ttk.Entry):
    """An Entry widget that accepts 7 digits (no '-()')."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.error = tk.StringVar()
        self.configure(
            validate="all",
            validatecommand=(
                self.register(self._validate),
                "%S",
                "%V",
                "%d",
                "%P",
            ),
            invalidcommand=(self.register(self._invalid), "%V"),
        )

    def _validate(self, char, event, action, proposed):
        self._toggle_error()
        valid = True
        if event == "key":
            if action == "0":
                valid = True
            elif not char.isdigit():
                valid = False
        elif event == "focusout":
            valid = len(self.get()) == 7

        return valid

    def _invalid(self, event):
        newline = "\n"
        self._toggle_error(
            f"Please enter a 7 digit phone number{newline}with no special characters or spaces"
        )

    def _toggle_error(self, error=""):
        self.error.set(error)
        self.config(foreground="red" if error else "black")


class ZipcodeEntry(ttk.Entry):
    """An Entry widget that accepts a 5 digit zipcode."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.error = tk.StringVar()
        self.configure(
            validate="focusout",
            validatecommand=(self.register(self._validate), "%s"),
            invalidcommand=(self.register(self._invalid), "%s"),
        )

    def _validate(self, value):
        self._toggle_error()
        return len(value) == 5 and value.isdigit()

    def _invalid(self, value):
        self._toggle_error("Please enter a 5 digit zipcode")

    def _toggle_error(self, error=""):
        self.error.set(error)
        self.config(foreground="red" if error else "black")


class LabelInput(tk.Frame):
    """A widget containing a label and input together."""

    def __init__(
        self,
        parent,
        label,
        var,
        input_class=ttk.Entry,
        input_args=None,
        label_args=None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = var
        self.variable.label_widget = self

        # setup the label
        if input_class in (ttk.Checkbutton, ttk.Button):
            # Buttons don't need labels, they're built-in
            input_args["text"] = label
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # setup the variable
        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args["variable"] = self.variable
        else:
            input_args["textvariable"] = self.variable

        # Setup the input
        if input_class == ttk.Radiobutton:
            # for Radiobutton, create one input per value
            self.input = tk.Frame(self)
            for v in input_args.pop("values", []):
                button = ttk.Radiobutton(
                    self.input, value=v, text=v, **input_args
                )
                button.pack(
                    side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill="x"
                )
        else:
            self.input = input_class(self, **input_args)

        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))

        if input_class in (
            DobEntry,
            AreaCodeEntry,
            PhoneNumberEntry,
            ZipcodeEntry,
        ):
            self.error_label = ttk.Label(
                self, textvariable=self.input.error, foreground="red"
            )
            self.error_label.grid(row=2, column=0, sticky=(tk.W + tk.E))
        else:
            self.space = ttk.Label(self, text="")
            self.space.grid(row=2, column=0, sticky=(tk.W + tk.E))

        self.columnconfigure(0, weight=1)

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        """Override grid to add default sticky values"""
        super().grid(sticky=sticky, **kwargs)

if __name__ == "__main__":
    root = tk.Tk()
    phone = PhoneNumberEntry(root)
    phone.pack()
    label = ttk.Label(root, text="Phone number")
    label.pack()
    entry = ttk.Entry()
    entry.pack()
    root.mainloop()
