import tkinter as tk
from tkinter import ttk, messagebox, font
import csv, os
from datetime import datetime
from collections import defaultdict
import locale

locale.setlocale(locale.LC_ALL, '')

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_PATH, 'expenses.csv')

EXPENSE_TYPES = ["Food", "Transport", "Entertainment", "Housing", "Utilities", "Shopping", "Health", "Other"]

# ------------- File Handling -------------
def setup_file():
    if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
        with open(CSV_FILE, 'w', newline='') as f:
            csv.writer(f).writerow(['Date', 'Category', 'Amount'])

def save_expense(date, category, amount):
    try:
        with open(CSV_FILE, 'a', newline='') as f:
            csv.writer(f).writerow([date, category, amount])
        return True
    except Exception as err:
        messagebox.showerror("Write Error", f"Error saving entry: {err}")
        return False

def fetch_expenses():
    entries = []
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and len(row) >= 3:
                    entries.append(row)
    except:
        pass
    return entries

# ------------- UI Functions -------------
def log_expense():
    cat, amt, dt = cat_var.get(), amt_entry.get(), date_entry.get()
    if not (cat and amt and dt):
        messagebox.showwarning("Input Missing", "Please complete all fields.")
        return
    try:
        float(amt)
        datetime.strptime(dt, "%d-%m-%Y")
    except:
        messagebox.showwarning("Invalid Input", "Enter a valid amount and date.")
        return
    if save_expense(dt, cat, amt):
        amt_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        insert_today()
        update_display()
        status.config(text=f"Added: ₹{amt} under {cat}")

def update_display():
    for row in table.get_children():
        table.delete(row)
    total = 0
    cat_totals = defaultdict(float)
    month_totals = defaultdict(float)
    for d, c, a in fetch_expenses():
        try:
            f_amt = float(a)
            table.insert('', 'end', values=(d, c, f"₹{f_amt:,.2f}"))
            total += f_amt
            cat_totals[c] += f_amt
            month = datetime.strptime(d, "%d-%m-%Y").strftime("%b %Y")
            month_totals[month] += f_amt
        except:
            continue
    total_lbl.config(text=f"Total: ₹{total:,.2f}")
    for w in cat_summary.winfo_children(): w.destroy()
    for idx, (k, v) in enumerate(sorted(cat_totals.items(), key=lambda x: -x[1])):
        ttk.Label(cat_summary, text=f"{k}", foreground="#2c3e50").grid(row=idx, column=0, sticky='w')
        ttk.Label(cat_summary, text=f"₹{v:,.2f}", foreground="#2c3e50").grid(row=idx, column=1)
    for w in month_summary.winfo_children(): w.destroy()
    for idx, (k, v) in enumerate(sorted(month_totals.items(), key=lambda x: datetime.strptime(x[0], "%b %Y"), reverse=True)):
        ttk.Label(month_summary, text=f"{k}", foreground="#2c3e50").grid(row=idx, column=0, sticky='w')
        ttk.Label(month_summary, text=f"₹{v:,.2f}", foreground="#2c3e50").grid(row=idx, column=1)

def insert_today():
    date_entry.delete(0, tk.END)
    date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))

# ------------- App Initialization -------------
root = tk.Tk()
root.title("EXPENZO")
root.geometry("800x650")
root.configure(bg="#f0f4f8")

style = ttk.Style()
style.theme_use('clam')
style.configure("TFrame", background="#f0f4f8")
style.configure("TLabel", background="#f0f4f8", font=("Segoe UI", 10), foreground="#2c3e50")
style.configure("TButton", font=("Segoe UI", 10), padding=5, foreground="#2c3e50")
style.configure("TEntry", foreground="#2c3e50")
style.configure("TCombobox", foreground="#2c3e50")
style.configure("Treeview", background="white", fieldbackground="white", font=("Segoe UI", 10), rowheight=24)
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#2c3e50", foreground="white")
style.map("Treeview.Heading", background=[("active", "#2c3e50")], foreground=[("active", "white")])
style.map("TButton", background=[("active", "#d1e0e0")])

setup_file()

frame = ttk.Frame(root, padding=15)
frame.pack(fill='both', expand=True)

header_frame = ttk.Frame(frame)
header_frame.pack(fill='x', pady=(0, 15))

# Centered logo and heading using an inner frame
centered_header = ttk.Frame(header_frame)
centered_header.pack(anchor='center')

logo_path = os.path.join(BASE_PATH, 'logo.png')
logo_img = tk.PhotoImage(file=logo_path)
logo_label = tk.Label(centered_header, image=logo_img, bg="#f0f4f8")
logo_label.image = logo_img
logo_label.pack(side="left")

header = ttk.Label(centered_header, text="EXPENZO", font=('Segoe UI', 18, 'bold'), foreground="#2c3e50")
header.pack(side="left", padx=10)

form = ttk.Frame(frame)
form.pack(pady=10)

cat_var = tk.StringVar()
ttk.Label(form, text="Category:").grid(row=0, column=0, padx=5, pady=5)
ttk.Combobox(form, textvariable=cat_var, values=EXPENSE_TYPES, width=15).grid(row=0, column=1, padx=5, pady=5)

ttk.Label(form, text="Amount:").grid(row=0, column=2, padx=5, pady=5)
amt_entry = ttk.Entry(form, width=12)
amt_entry.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(form, text="Date:").grid(row=0, column=4, padx=5, pady=5)
date_entry = ttk.Entry(form, width=12)
date_entry.grid(row=0, column=5, padx=5, pady=5)
ttk.Button(form, text="Today", command=insert_today).grid(row=0, column=6, padx=5)

btns = ttk.Frame(frame)
btns.pack(pady=10, fill='x')
ttk.Button(btns, text="Log Expense", command=log_expense).pack(side='right', padx=10)

status = ttk.Label(frame, text="", font=('Segoe UI', 9), foreground="#333")
status.pack()

tabs = ttk.Notebook(frame)
tabs.pack(fill='both', expand=True)

# Table Tab
tab1 = ttk.Frame(tabs)
tabs.add(tab1, text="Expenses")
columns = ("Date", "Category", "Amount")
table = ttk.Treeview(tab1, columns=columns, show='headings', height=15)
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center")
table.pack(fill='both', expand=True)

# Summary Tab
tab2 = ttk.Frame(tabs)
tabs.add(tab2, text="Summary")
total_lbl = ttk.Label(tab2, text="Total: ₹0.00", font=('Segoe UI', 12, 'bold'), foreground="#2c3e50")
total_lbl.pack(pady=10)
summary_cont = ttk.Frame(tab2)
summary_cont.pack(fill='both', expand=True)

cat_summary = ttk.LabelFrame(summary_cont, text="By Category")
cat_summary.pack(side='left', fill='both', expand=True, padx=10)

month_summary = ttk.LabelFrame(summary_cont, text="By Month")
month_summary.pack(side='right', fill='both', expand=True, padx=10)

insert_today()
update_display()

root.mainloop()
