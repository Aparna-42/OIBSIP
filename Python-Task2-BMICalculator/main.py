import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from bmi_logic import calculate_bmi, get_bmi_category
from database import create_database, save_record, get_records
from datetime import datetime


# -----------------------------
# Theme
# -----------------------------
BG = "#F4F7FB"
CARD = "#FFFFFF"
PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"
TEXT = "#172033"
MUTED = "#64748B"
BORDER = "#E2E8F0"
SUCCESS = "#16A34A"
WARNING = "#F59E0B"
DANGER = "#DC2626"
INFO = "#2563EB"


def style_button(parent, text, command, primary=False, width=18):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Segoe UI", 10, "bold" if primary else "normal"),
        width=width,
        height=2,
        relief="flat",
        bd=0,
        cursor="hand2",
        bg=PRIMARY if primary else "#EEF2FF",
        fg="white" if primary else PRIMARY,
        activebackground=PRIMARY_DARK if primary else "#E0E7FF",
        activeforeground="white" if primary else PRIMARY,
    )
    return button


def create_entry(parent, width=28):
    return tk.Entry(
        parent,
        width=width,
        font=("Segoe UI", 11),
        relief="flat",
        bd=0,
        bg="#F8FAFC",
        fg=TEXT,
        insertbackground=TEXT,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=PRIMARY,
    )


# -----------------------------
# Main calculation
# -----------------------------
def handle_calculate():
    name = name_entry.get().strip()

    if not name:
        show_result("Please enter your name.", DANGER)
        return

    try:
        weight = float(weight_entry.get())
        height_cm = float(height_entry.get())
    except ValueError:
        show_result("Please enter valid numbers.", WARNING)
        return

    if weight <= 0 or height_cm <= 0:
        show_result("Weight and height must be greater than zero.", WARNING)
        return

    if weight > 300 or height_cm > 250:
        show_result("Please enter realistic weight and height values.", WARNING)
        return

    bmi = calculate_bmi(weight, height_cm)
    category = get_bmi_category(bmi)
    recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    success = save_record(
        name,
        weight,
        height_cm,
        bmi,
        category,
        recorded_at
    )

    if not success:
        show_result(
            "Could not save BMI record.\nPlease try again.",
            DANGER
        )
        return

    if category == "Underweight":
        result_color = INFO
        badge_text = "UNDERWEIGHT"
    elif category == "Normal weight":
        result_color = SUCCESS
        badge_text = "NORMAL WEIGHT"
    elif category == "Overweight":
        result_color = WARNING
        badge_text = "OVERWEIGHT"
    else:
        result_color = DANGER
        badge_text = "OBESITY"

    result_title.config(
        text=f"{bmi:.2f}",
        fg=result_color
    )
    result_category.config(
        text=badge_text,
        fg=result_color
    )
    result_status.config(
        text="BMI record saved successfully",
        fg=MUTED
    )


def show_result(message, color):
    result_title.config(text="—", fg=color)
    result_category.config(text=message, fg=color)
    result_status.config(text="")


# -----------------------------
# History window
# -----------------------------
def show_history():
    history_window = tk.Toplevel(window)
    history_window.title("BMI History")
    history_window.geometry("1050x620")
    history_window.configure(bg=BG)
    history_window.minsize(900, 520)

    header = tk.Frame(history_window, bg=PRIMARY, height=90)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="BMI History",
        font=("Segoe UI", 20, "bold"),
        bg=PRIMARY,
        fg="white"
    ).pack(anchor="w", padx=28, pady=(18, 0))

    tk.Label(
        header,
        text="Search and review saved BMI records",
        font=("Segoe UI", 10),
        bg=PRIMARY,
        fg="#DBEAFE"
    ).pack(anchor="w", padx=30, pady=(2, 0))

    content = tk.Frame(history_window, bg=BG)
    content.pack(fill="both", expand=True, padx=24, pady=20)

    filter_card = tk.Frame(
        content,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    filter_card.pack(fill="x", pady=(0, 15))

    tk.Label(
        filter_card,
        text="Search by name",
        font=("Segoe UI", 10, "bold"),
        bg=CARD,
        fg=TEXT
    ).pack(side="left", padx=(18, 8), pady=16)

    search_entry = tk.Entry(
        filter_card,
        width=25,
        font=("Segoe UI", 10),
        relief="flat",
        bd=0,
        bg="#F8FAFC",
        fg=TEXT,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=PRIMARY
    )
    search_entry.pack(side="left", ipady=7, padx=5, pady=12)

    table_frame = tk.Frame(content, bg=CARD)
    table_frame.pack(fill="both", expand=True)

    columns = ("Name", "Weight", "Height", "BMI", "Category", "Date")

    table_style = ttk.Style(history_window)
    try:
        table_style.theme_use("clam")
    except tk.TclError:
        pass

    table_style.configure(
        "History.Treeview",
        background="white",
        foreground=TEXT,
        fieldbackground="white",
        rowheight=34,
        font=("Segoe UI", 10),
        borderwidth=0
    )
    table_style.configure(
        "History.Treeview.Heading",
        background="#EFF6FF",
        foreground=TEXT,
        font=("Segoe UI", 10, "bold"),
        padding=9
    )
    table_style.map(
        "History.Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", TEXT)]
    )

    history_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="History.Treeview"
    )

    widths = {
        "Name": 140,
        "Weight": 100,
        "Height": 100,
        "BMI": 90,
        "Category": 150,
        "Date": 220
    }

    for column in columns:
        history_table.heading(column, text=column)
        history_table.column(
            column,
            width=widths[column],
            anchor="center"
        )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=history_table.yview
    )
    history_table.configure(yscrollcommand=scrollbar.set)

    history_table.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(12, 0),
        pady=12
    )
    scrollbar.pack(side="right", fill="y", padx=(0, 12), pady=12)

    message_label = tk.Label(
        content,
        text="",
        font=("Segoe UI", 9),
        bg=BG,
        fg=DANGER
    )
    message_label.pack(pady=(8, 0))

    def load_records(name=None):
        for item in history_table.get_children():
            history_table.delete(item)

        records = get_records(name)

        if records is None:
            message_label.config(
                text="Could not read BMI history from the database."
            )
            return

        message_label.config(text="")

        for record in records:
            history_table.insert(
                "",
                tk.END,
                values=(
                    record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5]
                )
            )

    def search_records():
        name = search_entry.get().strip()
        load_records(name if name else None)

    search_button = style_button(
        filter_card,
        "Search",
        search_records,
        primary=True,
        width=10
    )
    search_button.pack(side="left", padx=8, pady=10)

    show_all_button = style_button(
        filter_card,
        "Show All",
        lambda: load_records(),
        primary=False,
        width=10
    )
    show_all_button.pack(side="left", padx=(0, 15), pady=10)

    search_entry.bind("<Return>", lambda event: search_records())

    load_records()


# -----------------------------
# BMI trend window
# -----------------------------
def show_bmi_trend():
    trend_window = tk.Toplevel(window)
    trend_window.title("BMI Trend")
    trend_window.geometry("480x330")
    trend_window.configure(bg=BG)
    trend_window.resizable(False, False)

    header = tk.Frame(trend_window, bg=PRIMARY, height=92)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="BMI Trend",
        font=("Segoe UI", 20, "bold"),
        bg=PRIMARY,
        fg="white"
    ).pack(anchor="w", padx=26, pady=(18, 0))

    tk.Label(
        header,
        text="View BMI progress over time",
        font=("Segoe UI", 10),
        bg=PRIMARY,
        fg="#DBEAFE"
    ).pack(anchor="w", padx=28, pady=(2, 0))

    card = tk.Frame(
        trend_window,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    card.pack(fill="both", expand=True, padx=24, pady=22)

    tk.Label(
        card,
        text="Enter user name",
        font=("Segoe UI", 10, "bold"),
        bg=CARD,
        fg=TEXT
    ).pack(pady=(22, 7))

    trend_name_entry = tk.Entry(
        card,
        width=28,
        font=("Segoe UI", 11),
        relief="flat",
        bd=0,
        bg="#F8FAFC",
        fg=TEXT,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=PRIMARY
    )
    trend_name_entry.pack(ipady=8)

    trend_message = tk.Label(
        card,
        text="",
        font=("Segoe UI", 9),
        bg=CARD,
        fg=DANGER
    )
    trend_message.pack(pady=(10, 2))

    def display_trend():
        name = trend_name_entry.get().strip()

        if not name:
            trend_message.config(text="Please enter a name.")
            return

        records = get_records(name)

        if records is None:
            trend_message.config(
                text="Could not read BMI records from the database."
            )
            return

        if not records:
            trend_message.config(
                text="No BMI records found for this user."
            )
            return

        records.reverse()

        dates = [record[5] for record in records]
        bmi_values = [record[3] for record in records]

        plt.figure(figsize=(8, 5))
        plt.plot(
            dates,
            bmi_values,
            marker="o"
        )
        plt.title(f"BMI Trend - {name}")
        plt.xlabel("Date and Time")
        plt.ylabel("BMI")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    trend_button = style_button(
        card,
        "View Trend",
        display_trend,
        primary=True,
        width=18
    )
    trend_button.pack(pady=(12, 20))

    trend_name_entry.bind("<Return>", lambda event: display_trend())


# -----------------------------
# Main window
# -----------------------------
window = tk.Tk()
create_database()

window.title("Smart BMI Tracker")
window.geometry("680x760")
window.configure(bg=BG)
window.resizable(False, False)

# Header
header = tk.Frame(window, bg=PRIMARY, height=150)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="Smart BMI Tracker",
    font=("Segoe UI", 26, "bold"),
    bg=PRIMARY,
    fg="white"
).pack(pady=(28, 3))

tk.Label(
    header,
    text="Calculate, save and track your BMI",
    font=("Segoe UI", 11),
    bg=PRIMARY,
    fg="#DBEAFE"
).pack()

# Main content
main = tk.Frame(window, bg=BG)
main.pack(fill="both", expand=True, padx=55, pady=24)

# Input card
input_card = tk.Frame(
    main,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=1
)
input_card.pack(fill="x")

tk.Label(
    input_card,
    text="Enter Your Details",
    font=("Segoe UI", 14, "bold"),
    bg=CARD,
    fg=TEXT
).grid(row=0, column=0, columnspan=2, sticky="w", padx=25, pady=(22, 16))

labels = [
    ("Name", 1),
    ("Weight (kg)", 2),
    ("Height (cm)", 3)
]

for text, row in labels:
    tk.Label(
        input_card,
        text=text,
        font=("Segoe UI", 10, "bold"),
        bg=CARD,
        fg=MUTED
    ).grid(row=row, column=0, sticky="w", padx=(25, 15), pady=9)

name_entry = create_entry(input_card)
weight_entry = create_entry(input_card)
height_entry = create_entry(input_card)

name_entry.grid(row=1, column=1, sticky="ew", padx=(0, 25), pady=8, ipady=7)
weight_entry.grid(row=2, column=1, sticky="ew", padx=(0, 25), pady=8, ipady=7)
height_entry.grid(row=3, column=1, sticky="ew", padx=(0, 25), pady=8, ipady=7)

input_card.columnconfigure(1, weight=1)

calculate_button = style_button(
    input_card,
    "Calculate BMI",
    handle_calculate,
    primary=True,
    width=22
)
calculate_button.grid(
    row=4,
    column=0,
    columnspan=2,
    pady=(18, 24)
)

# Result card
result_card = tk.Frame(
    main,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=1
)
result_card.pack(fill="x", pady=18)

tk.Label(
    result_card,
    text="YOUR BMI RESULT",
    font=("Segoe UI", 9, "bold"),
    bg=CARD,
    fg=MUTED
).pack(pady=(18, 2))

result_title = tk.Label(
    result_card,
    text="—",
    font=("Segoe UI", 28, "bold"),
    bg=CARD,
    fg=TEXT
)
result_title.pack()

result_category = tk.Label(
    result_card,
    text="Enter your details and calculate",
    font=("Segoe UI", 12, "bold"),
    bg=CARD,
    fg=MUTED,
    wraplength=520
)
result_category.pack(pady=(0, 2))

result_status = tk.Label(
    result_card,
    text="",
    font=("Segoe UI", 9),
    bg=CARD,
    fg=MUTED
)
result_status.pack(pady=(0, 18))

# Bottom actions
actions = tk.Frame(main, bg=BG)
actions.pack(fill="x")

history_button = style_button(
    actions,
    "View History",
    show_history,
    primary=False,
    width=18
)
history_button.pack(side="left", padx=(0, 8), expand=True)

trend_button = style_button(
    actions,
    "View BMI Trend",
    show_bmi_trend,
    primary=False,
    width=18
)
trend_button.pack(side="left", padx=(8, 0), expand=True)

# Footer
tk.Label(
    main,
    text="Your BMI records are stored locally in SQLite.",
    font=("Segoe UI", 9),
    bg=BG,
    fg=MUTED
).pack(pady=(20, 0))

name_entry.focus_set()

window.mainloop()
