import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from bmi_logic import calculate_bmi, get_bmi_category
from database import create_database, save_record, get_records
from datetime import datetime


# -----------------------------
# Theme
# -----------------------------
BG = "#F2FBF7"
CARD = "#FFFFFF"
PRIMARY = "#188A68"
PRIMARY_DARK = "#116B52"
PRIMARY_LIGHT = "#DDF4EA"
TEXT = "#163B34"
MUTED = "#607A73"
BORDER = "#D6E8E1"
BLUE_LIGHT = "#EEF7FF"
ORANGE_LIGHT = "#FFF4E8"
SUCCESS = "#159447"
WARNING = "#F59E0B"
DANGER = "#DC3C3C"
INFO = "#318CE7"


# -----------------------------
# Reusable UI helpers
# -----------------------------
def rounded_card(parent, bg=CARD, padx=1):
    return tk.Frame(
        parent,
        bg=bg,
        highlightbackground=BORDER,
        highlightthickness=1,
        bd=0
    )


def create_entry(parent, width=28):
    return tk.Entry(
        parent,
        width=width,
        font=("Segoe UI", 11),
        relief="flat",
        bd=0,
        bg="#FAFCFB",
        fg=TEXT,
        insertbackground=TEXT,
        highlightthickness=1,
        highlightbackground="#C9DCD5",
        highlightcolor=PRIMARY
    )


def button(parent, text, command, primary=False, width=18):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Segoe UI", 10, "bold" if primary else "normal"),
        width=width,
        height=2,
        relief="flat",
        bd=0,
        cursor="hand2",
        bg=PRIMARY if primary else "#EAF7F1",
        fg="white" if primary else PRIMARY_DARK,
        activebackground=PRIMARY_DARK if primary else PRIMARY_LIGHT,
        activeforeground="white" if primary else PRIMARY_DARK
    )


def clear_content():
    for widget in content_area.winfo_children():
        widget.destroy()


def show_page(page_builder, active):
    clear_content()
    page_builder()
    set_active_nav(active)


def set_active_nav(active):
    nav_items = {
        "calculator": calculator_nav,
        "history": history_nav,
        "trend": trend_nav,
        "about": about_nav
    }

    for key, nav_button in nav_items.items():
        if key == active:
            nav_button.config(bg=PRIMARY, fg="white",
                              font=("Segoe UI", 10, "bold"))
        else:
            nav_button.config(bg="#EAF7F1", fg=TEXT,
                              font=("Segoe UI", 10))


# -----------------------------
# BMI calculation
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
        name, weight, height_cm, bmi, category, recorded_at
    )

    if not success:
        show_result("Could not save BMI record.\nPlease try again.", DANGER)
        return

    if category == "Underweight":
        result_color = INFO
        message = "Below the healthy weight range."
    elif category == "Normal weight":
        result_color = SUCCESS
        message = "You are in the healthy weight range. Keep it up!"
    elif category == "Overweight":
        result_color = WARNING
        message = "Consider healthy lifestyle habits and regular activity."
    else:
        result_color = DANGER
        message = "Consider discussing your BMI with a healthcare professional."

    result_bmi.config(text=f"BMI: {bmi:.2f}", fg=result_color)
    result_category.config(text=f"Category: {category}", fg=result_color)
    result_message.config(text=message)
    result_saved.config(text="✓ Record saved successfully")


def show_result(message, color):
    result_bmi.config(text="BMI: —", fg=color)
    result_category.config(text=message, fg=color)
    result_message.config(text="")
    result_saved.config(text="")


# -----------------------------
# Calculator page
# -----------------------------
def build_calculator_page():
    global name_entry, weight_entry, height_entry
    global result_bmi, result_category, result_message, result_saved

    page = tk.Frame(content_area, bg=BG)
    page.pack(fill="both", expand=True)

    top = tk.Frame(page, bg=BG)
    top.pack(fill="x", padx=28, pady=(22, 14))

    tk.Label(
        top, text="▣", font=("Segoe UI", 30, "bold"),
        bg=BG, fg=PRIMARY
    ).pack(side="left", padx=(0, 14))

    title_box = tk.Frame(top, bg=BG)
    title_box.pack(side="left")

    tk.Label(
        title_box, text="BMI Calculator",
        font=("Segoe UI", 22, "bold"),
        bg=BG, fg="#101B3B"
    ).pack(anchor="w")

    tk.Label(
        title_box,
        text="Enter your details to calculate your Body Mass Index (BMI)",
        font=("Segoe UI", 11),
        bg=BG, fg=MUTED
    ).pack(anchor="w")

    body = tk.Frame(page, bg=BG)
    body.pack(fill="both", expand=True, padx=28)

    left = tk.Frame(body, bg=BG)
    left.pack(side="left", fill="both", expand=True, padx=(0, 14))

    right = tk.Frame(body, bg=BG, width=310)
    right.pack(side="right", fill="y")
    right.pack_propagate(False)

    # Input card
    input_card = rounded_card(left)
    input_card.pack(fill="x", pady=(0, 14))

    tk.Label(
        input_card, text="Enter Your Details",
        font=("Segoe UI", 14, "bold"),
        bg=CARD, fg=TEXT
    ).grid(row=0, column=0, columnspan=2,
           sticky="w", padx=25, pady=(22, 15))

    fields = [
        ("Name", 1),
        ("Weight (kg)", 2),
        ("Height (cm)", 3)
    ]

    for label_text, row in fields:
        tk.Label(
            input_card, text=label_text,
            font=("Segoe UI", 10, "bold"),
            bg=CARD, fg=MUTED
        ).grid(row=row, column=0, sticky="w",
               padx=(25, 18), pady=9)

    name_entry = create_entry(input_card)
    weight_entry = create_entry(input_card)
    height_entry = create_entry(input_card)

    name_entry.grid(row=1, column=1, sticky="ew",
                    padx=(0, 25), pady=8, ipady=7)
    weight_entry.grid(row=2, column=1, sticky="ew",
                      padx=(0, 25), pady=8, ipady=7)
    height_entry.grid(row=3, column=1, sticky="ew",
                      padx=(0, 25), pady=8, ipady=7)

    input_card.columnconfigure(1, weight=1)

    button(
        input_card, "▣   Calculate BMI",
        handle_calculate, primary=True, width=22
    ).grid(row=4, column=0, columnspan=2,
           sticky="ew", padx=25, pady=(18, 24))

    # Result card
    result_card = tk.Frame(
        left, bg=PRIMARY_LIGHT,
        highlightbackground="#CBE8DA",
        highlightthickness=1
    )
    result_card.pack(fill="x")

    tk.Label(
        result_card, text="Your BMI Result",
        font=("Segoe UI", 14, "bold"),
        bg=PRIMARY_LIGHT, fg=TEXT
    ).pack(pady=(20, 4))

    result_bmi = tk.Label(
        result_card, text="BMI: —",
        font=("Segoe UI", 23, "bold"),
        bg=PRIMARY_LIGHT, fg=TEXT
    )
    result_bmi.pack()

    result_category = tk.Label(
        result_card,
        text="Enter your details and calculate",
        font=("Segoe UI", 12, "bold"),
        bg=PRIMARY_LIGHT, fg=MUTED,
        wraplength=560
    )
    result_category.pack(pady=(3, 5))

    result_message = tk.Label(
        result_card, text="",
        font=("Segoe UI", 9),
        bg=PRIMARY_LIGHT, fg=MUTED,
        wraplength=560
    )
    result_message.pack()

    result_saved = tk.Label(
        result_card, text="",
        font=("Segoe UI", 9, "bold"),
        bg=PRIMARY_LIGHT, fg=SUCCESS
    )
    result_saved.pack(pady=(3, 18))

    # BMI categories card
    category_card = tk.Frame(
        right, bg=BLUE_LIGHT,
        highlightbackground="#CDE2F5",
        highlightthickness=1
    )
    category_card.pack(fill="x", pady=(0, 14))

    tk.Label(
        category_card, text="BMI Categories",
        font=("Segoe UI", 14, "bold"),
        bg=BLUE_LIGHT, fg="#153D78"
    ).pack(anchor="w", padx=22, pady=(20, 13))

    category_rows = [
        ("●", "Underweight", "BMI below 18.5", INFO),
        ("●", "Normal weight", "18.5 – 24.9", SUCCESS),
        ("●", "Overweight", "25 – 29.9", WARNING),
        ("●", "Obesity", "30 or above", DANGER)
    ]

    for dot, name, range_text, color in category_rows:
        row = tk.Frame(category_card, bg=BLUE_LIGHT)
        row.pack(fill="x", padx=22, pady=5)

        tk.Label(row, text=dot, font=("Segoe UI", 18),
                 bg=BLUE_LIGHT, fg=color).pack(side="left")
        tk.Label(row, text=name, font=("Segoe UI", 10),
                 bg=BLUE_LIGHT, fg=TEXT, width=16,
                 anchor="w").pack(side="left")
        tk.Label(row, text=range_text, font=("Segoe UI", 10),
                 bg=BLUE_LIGHT, fg=MUTED).pack(side="left")

    tk.Label(
        category_card, text="",
        bg=BLUE_LIGHT
    ).pack(pady=5)

    # Tips card
    tips_card = tk.Frame(
        right, bg=ORANGE_LIGHT,
        highlightbackground="#F6D9BA",
        highlightthickness=1
    )
    tips_card.pack(fill="x")

    tk.Label(
        tips_card, text="💡  Tips for a Healthy Life",
        font=("Segoe UI", 13, "bold"),
        bg=ORANGE_LIGHT, fg="#A94A15"
    ).pack(anchor="w", padx=22, pady=(20, 10))

    tips = [
        "Maintain a balanced diet",
        "Exercise regularly",
        "Stay hydrated",
        "Get enough sleep",
        "Monitor your BMI regularly"
    ]

    for tip in tips:
        tk.Label(
            tips_card, text=f"•  {tip}",
            font=("Segoe UI", 10),
            bg=ORANGE_LIGHT, fg=TEXT,
            anchor="w"
        ).pack(fill="x", padx=22, pady=4)

    tk.Label(tips_card, text="", bg=ORANGE_LIGHT).pack(pady=5)

    name_entry.focus_set()


# -----------------------------
# History page
# -----------------------------
def build_history_page():
    page = tk.Frame(content_area, bg=BG)
    page.pack(fill="both", expand=True)

    top = tk.Frame(page, bg=BG)
    top.pack(fill="x", padx=28, pady=(22, 14))

    tk.Label(
        top, text="▤", font=("Segoe UI", 30, "bold"),
        bg=BG, fg=PRIMARY
    ).pack(side="left", padx=(0, 14))

    heading = tk.Frame(top, bg=BG)
    heading.pack(side="left")

    tk.Label(
        heading, text="BMI History",
        font=("Segoe UI", 22, "bold"),
        bg=BG, fg="#101B3B"
    ).pack(anchor="w")

    tk.Label(
        heading, text="View and search your saved BMI records",
        font=("Segoe UI", 11),
        bg=BG, fg=MUTED
    ).pack(anchor="w")

    search_card = rounded_card(page)
    search_card.pack(fill="x", padx=28, pady=(0, 14))

    tk.Label(
        search_card, text="Search by name:",
        font=("Segoe UI", 10, "bold"),
        bg=CARD, fg=TEXT
    ).pack(side="left", padx=(18, 10), pady=15)

    search_entry = create_entry(search_card, 25)
    search_entry.pack(side="left", ipady=7, padx=5, pady=10)

    table_frame = tk.Frame(page, bg=CARD,
                           highlightbackground=BORDER,
                           highlightthickness=1)
    table_frame.pack(fill="both", expand=True, padx=28, pady=(0, 14))

    columns = ("Name", "Weight", "Height", "BMI", "Category", "Date")

    style = ttk.Style(window)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "BMI.Treeview",
        background="white",
        foreground=TEXT,
        fieldbackground="white",
        rowheight=34,
        font=("Segoe UI", 10),
        borderwidth=0
    )
    style.configure(
        "BMI.Treeview.Heading",
        background=PRIMARY,
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        padding=9
    )
    style.map(
        "BMI.Treeview",
        background=[("selected", "#DDF4EA")],
        foreground=[("selected", TEXT)]
    )

    table = ttk.Treeview(
        table_frame, columns=columns,
        show="headings", style="BMI.Treeview"
    )

    widths = {
        "Name": 140, "Weight": 100, "Height": 100,
        "BMI": 90, "Category": 150, "Date": 220
    }

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=widths[col], anchor="center")

    scroll = ttk.Scrollbar(
        table_frame, orient="vertical", command=table.yview
    )
    table.configure(yscrollcommand=scroll.set)

    table.pack(side="left", fill="both", expand=True,
               padx=(10, 0), pady=10)
    scroll.pack(side="right", fill="y", padx=(0, 10), pady=10)

    message = tk.Label(
        page, text="", font=("Segoe UI", 9),
        bg=BG, fg=DANGER
    )
    message.pack()

    def load_records(name=None):
        for item in table.get_children():
            table.delete(item)

        records = get_records(name)

        if records is None:
            message.config(
                text="Could not read BMI history from the database."
            )
            return

        message.config(text="")

        for record in records:
            table.insert(
                "", tk.END,
                values=(
                    record[0], record[1], record[2],
                    record[3], record[4], record[5]
                )
            )

    def search_records():
        value = search_entry.get().strip()
        load_records(value if value else None)

    def delete_selected():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a BMI record to delete."
            )
            return

        values = table.item(selected[0], "values")

        confirm = messagebox.askyesno(
            "Delete Record",
            f"Delete the selected BMI record for '{values[0]}'?"
        )

        if not confirm:
            return

        try:
            connection = sqlite3.connect("bmi_tracker.db")
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM bmi_records
                WHERE id = (
                    SELECT id FROM bmi_records
                    WHERE name = ?
                      AND weight = ?
                      AND height = ?
                      AND bmi = ?
                      AND category = ?
                      AND recorded_at = ?
                    ORDER BY id DESC
                    LIMIT 1
                )
                """,
                (
                    values[0],
                    float(values[1]),
                    float(values[2]),
                    float(values[3]),
                    values[4],
                    values[5]
                )
            )

            connection.commit()
            connection.close()

            load_records(
                search_entry.get().strip() or None
            )

            messagebox.showinfo(
                "Record Deleted",
                "The selected BMI record was deleted successfully."
            )

        except (sqlite3.Error, ValueError):
            messagebox.showerror(
                "Delete Error",
                "Could not delete the selected BMI record."
            )

    button(
        search_card, "Search", search_records,
        primary=True, width=10
    ).pack(side="left", padx=8, pady=10)

    button(
        search_card, "Show All", lambda: load_records(),
        width=10
    ).pack(side="left", padx=(0, 8), pady=10)

    button(
        search_card, "Delete Selected", delete_selected,
        width=15
    ).pack(side="left", padx=(0, 15), pady=10)

    search_entry.bind("<Return>", lambda event: search_records())

    load_records()


# -----------------------------
# Trend page
# -----------------------------
def build_trend_page():
    page = tk.Frame(content_area, bg=BG)
    page.pack(fill="both", expand=True)

    top = tk.Frame(page, bg=BG)
    top.pack(fill="x", padx=28, pady=(22, 14))

    tk.Label(
        top, text="▥", font=("Segoe UI", 30, "bold"),
        bg=BG, fg=PRIMARY
    ).pack(side="left", padx=(0, 14))

    heading = tk.Frame(top, bg=BG)
    heading.pack(side="left")

    tk.Label(
        heading, text="BMI Trend",
        font=("Segoe UI", 22, "bold"),
        bg=BG, fg="#101B3B"
    ).pack(anchor="w")

    tk.Label(
        heading, text="Track BMI measurements over time",
        font=("Segoe UI", 11),
        bg=BG, fg=MUTED
    ).pack(anchor="w")

    control = rounded_card(page)
    control.pack(fill="x", padx=28, pady=(0, 14))

    tk.Label(
        control, text="Enter user name:",
        font=("Segoe UI", 10, "bold"),
        bg=CARD, fg=TEXT
    ).pack(side="left", padx=(18, 10), pady=15)

    trend_entry = create_entry(control, 25)
    trend_entry.pack(side="left", ipady=7, padx=5, pady=10)

    message = tk.Label(
        control, text="", font=("Segoe UI", 9),
        bg=CARD, fg=DANGER
    )
    message.pack(side="left", padx=10)

    chart_card = tk.Frame(
        page, bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    chart_card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

    def display_trend():
        name = trend_entry.get().strip()

        if not name:
            message.config(text="Please enter a name.")
            return

        records = get_records(name)

        if records is None:
            message.config(
                text="Could not read BMI records from the database."
            )
            return

        if not records:
            message.config(
                text="No BMI records found for this user."
            )
            return

        message.config(text="")

        for widget in chart_card.winfo_children():
            widget.destroy()

        records.reverse()

        dates = [record[5] for record in records]
        bmi_values = [record[3] for record in records]

        figure = plt.Figure(figsize=(8.5, 4.8), dpi=100)
        axis = figure.add_subplot(111)

        axis.plot(dates, bmi_values, marker="o")
        axis.set_title(f"BMI Trend - {name}", fontsize=14)
        axis.set_xlabel("Date and Time")
        axis.set_ylabel("BMI")
        axis.tick_params(axis="x", rotation=45)
        axis.grid(True, alpha=0.3)
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=12, pady=12
        )

    button(
        control, "View Trend",
        display_trend, primary=True, width=12
    ).pack(side="right", padx=(5, 15), pady=10)

    trend_entry.bind("<Return>", lambda event: display_trend())


# -----------------------------
# About page
# -----------------------------
def build_about_page():
    page = tk.Frame(content_area, bg=BG)
    page.pack(fill="both", expand=True)

    card = rounded_card(page)
    card.pack(fill="both", expand=True, padx=60, pady=45)

    tk.Label(
        card, text="About Smart BMI Tracker",
        font=("Segoe UI", 24, "bold"),
        bg=CARD, fg=TEXT
    ).pack(pady=(45, 15))

    tk.Label(
        card,
        text=(
            "A desktop BMI calculator and tracking application built with "
            "Python and Tkinter.\n\n"
            "It calculates BMI, classifies the result, stores records in "
            "SQLite, supports history search,\nand visualizes BMI progress "
            "using Matplotlib."
        ),
        font=("Segoe UI", 11),
        bg=CARD, fg=MUTED,
        justify="center"
    ).pack(pady=10)

    tk.Label(
        card,
        text="Oasis Infobyte • Python Programming Internship • Task 2",
        font=("Segoe UI", 10, "bold"),
        bg=CARD, fg=PRIMARY
    ).pack(pady=20)

    tk.Label(
        card,
        text="Developed by Aparna Sunil T P",
        font=("Segoe UI", 10),
        bg=CARD, fg=MUTED
    ).pack()


# -----------------------------
# Application window
# -----------------------------
window = tk.Tk()
create_database()

window.title("Smart BMI Tracker")
window.geometry("1200x780")
window.configure(bg=BG)
window.minsize(1050, 700)

# Header
header = tk.Frame(window, bg="#F7FFFB", height=125,
                  highlightbackground=BORDER,
                  highlightthickness=1)
header.pack(fill="x")
header.pack_propagate(False)

brand = tk.Frame(header, bg="#F7FFFB")
brand.pack(side="left", padx=38, pady=18)

tk.Label(
    brand, text="◉", font=("Segoe UI", 42, "bold"),
    bg="#F7FFFB", fg=PRIMARY
).pack(side="left", padx=(0, 16))

brand_text = tk.Frame(brand, bg="#F7FFFB")
brand_text.pack(side="left")

tk.Label(
    brand_text, text="Smart BMI Tracker",
    font=("Segoe UI", 26, "bold"),
    bg="#F7FFFB", fg="#07563F"
).pack(anchor="w")

tk.Label(
    brand_text, text="Track Today for a Healthier Tomorrow",
    font=("Segoe UI", 11),
    bg="#F7FFFB", fg="#64808B"
).pack(anchor="w")

info = tk.Frame(header, bg="#F7FFFB")
info.pack(side="right", padx=38, pady=28)

date_text = datetime.now().strftime("%d %b %Y    %I:%M %p")

tk.Label(
    info, text=date_text,
    font=("Segoe UI", 10, "bold"),
    bg="#F7FFFB", fg=TEXT
).pack(anchor="e")

tk.Label(
    info, text='"A healthier you, a brighter tomorrow!"',
    font=("Segoe UI", 10, "italic"),
    bg="#F7FFFB", fg=MUTED
).pack(anchor="e", pady=(7, 0))

# Main body
body = tk.Frame(window, bg=BG)
body.pack(fill="both", expand=True)

# Sidebar
sidebar = tk.Frame(body, bg="#E8F8F1", width=245)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar, text="",
    bg="#E8F8F1"
).pack(pady=7)

calculator_nav = tk.Button(
    sidebar, text="⌂   BMI Calculator",
    command=lambda: show_page(build_calculator_page, "calculator"),
    font=("Segoe UI", 10, "bold"),
    relief="flat", bd=0, cursor="hand2",
    bg=PRIMARY, fg="white",
    anchor="w", padx=22
)
calculator_nav.pack(fill="x", padx=12, pady=7, ipady=12)

history_nav = tk.Button(
    sidebar, text="▤   History",
    command=lambda: show_page(build_history_page, "history"),
    font=("Segoe UI", 10),
    relief="flat", bd=0, cursor="hand2",
    bg="#EAF7F1", fg=TEXT,
    anchor="w", padx=22
)
history_nav.pack(fill="x", padx=12, pady=7, ipady=12)

trend_nav = tk.Button(
    sidebar, text="▥   BMI Trend",
    command=lambda: show_page(build_trend_page, "trend"),
    font=("Segoe UI", 10),
    relief="flat", bd=0, cursor="hand2",
    bg="#EAF7F1", fg=TEXT,
    anchor="w", padx=22
)
trend_nav.pack(fill="x", padx=12, pady=7, ipady=12)

# Push About to bottom
tk.Label(sidebar, text="", bg="#E8F8F1").pack(expand=True)

about_nav = tk.Button(
    sidebar, text="ⓘ   About",
    command=lambda: show_page(build_about_page, "about"),
    font=("Segoe UI", 10),
    relief="flat", bd=0, cursor="hand2",
    bg="#EAF7F1", fg=TEXT,
    anchor="w", padx=22
)
about_nav.pack(fill="x", padx=12, pady=(7, 22), ipady=12)

# Content
content_area = tk.Frame(body, bg=BG)
content_area.pack(side="left", fill="both", expand=True)

# Footer
footer = tk.Frame(window, bg="#F7FFFB", height=42,
                  highlightbackground=BORDER,
                  highlightthickness=1)
footer.pack(fill="x")
footer.pack_propagate(False)

tk.Label(
    footer,
    text="© 2026 Smart BMI Tracker",
    font=("Segoe UI", 9),
    bg="#F7FFFB", fg=MUTED
).pack(side="left", padx=25)



show_page(build_calculator_page, "calculator")

window.mainloop()
