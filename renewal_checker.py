#!/usr/bin/env python3

import tkinter as tk
from models import Database
from datetime import datetime

db = Database('gfe_db.db')

query2 = """SELECT renewal_date, clients.client_id, first_name, last_name FROM clients INNER JOIN estimate_details on clients.client_id = estimate_details.client_id WHERE renewal_date
< DATETIME('now', '1 month') and most_recent_estimate = 1"""

db.search_and_return_tuple(query2)
results = db.get_search_results()
results.sort()

root = tk.Tk()
root.geometry('300x300')
tk.Label(root, text="Client").grid(column=0, row=0)
tk.Label(root, text="Renewal Date").grid(column=2, row=0)
for index, result in enumerate(results):
    renewal_date, client_id, first, last = results[index]
    client_info = f"{client_id} {first} {last}"
    renewal_datetime = datetime.fromisoformat(renewal_date)
    formatted_renewal = renewal_datetime.strftime('%m-%d-%Y')
    tk.Label(root, text=client_info).grid(column=0, row=(index + 1))
    tk.Label(root, text="\t").grid(column=1, row=(index + 1))
    tk.Label(root, text=formatted_renewal).grid(column=2, row=(index + 1))

root.mainloop()
