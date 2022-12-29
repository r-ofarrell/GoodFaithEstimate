#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk


class LabelInput(tk.Frame):
    """A widget with a label and an input together."""
    def __init__(self, parent, label, var, input_type=ttk.Entry,
                 input_args=None, label_args=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.input_args = input_args or {}
        self.label_args = label_args or {}
        self.variable = var

        # Setup label
        if input_type == ttk.Checkbutton:
            self.input_args['text'] = label
        else:
            self.label = ttk.Label(parent, text=label, **self.label_args)
            self.label.grid(row=0, column=0)

        # Setup the variable
        if input_type in (ttk.Checkbutton, ttk.Radiobutton):
            self.input_args['variable'] = self.variable
        else:
            self.input_args['textvariable'] = self.variable

        # Setup the input
        if input_type == ttk.Radiobutton:
            self.input = tk.Frame(self)
            for v in input_args.pop('values', []):
                button = ttk.Radiobutton(
                    self, value=v, text=v, **input_args
                )
            button.pack(side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x')
        else:
            self.input = input_type(self, **self.input_args)

        self.input.grid(row=1, column=0)
        self.columnconfigure(0, weight=1)

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        """Override grid to add default sticky values"""
        super().grid(sticky=sticky, **kwargs)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x300")
    input1 = LabelInput(root, 'User name', tk.StringVar(), ttk.Entry)
    input1.grid()
    root.mainloop()
