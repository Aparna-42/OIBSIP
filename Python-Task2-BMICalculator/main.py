import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk
from bmi_logic import calculate_bmi, get_bmi_category
from database import create_database, save_record, get_records
from datetime import datetime



def handle_calculate():
    name = name_entry.get().strip()

    if not name:
        result_label.config(text="Please enter your name.")
        return

    try:
        weight = float(weight_entry.get())
        height_cm = float(height_entry.get())
    except ValueError:
        result_label.config(text="Please enter valid numbers.")
        return

    if weight <= 0 or height_cm <= 0:
        result_label.config(
            text="Weight and height must be greater than zero."
        )
        return

    if weight > 300 or height_cm > 250:
        result_label.config(
            text="Please enter realistic weight and height values."
        )
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
        result_label.config(
            text="Could not save BMI record.\nPlease try again."
        )
        return

    if category == "Underweight":
        result_color = "blue"
    elif category == "Normal weight":
        result_color = "green"
    elif category == "Overweight":
        result_color = "orange"
    else:
        result_color = "red"

    result_label.config(
        text=f"BMI: {bmi}\nCategory: {category}",
        fg=result_color
    )

def show_history():
    history_window = tk.Toplevel(window)
    history_window.title("BMI History")
    history_window.geometry("800x450")

    filter_frame = tk.Frame(history_window)
    filter_frame.pack(pady=10)

    name_label = tk.Label(
        filter_frame,
        text="Enter name:"
    )
    name_label.grid(row=0, column=0, padx=5)

    name_entry = tk.Entry(filter_frame, width=25)
    name_entry.grid(row=0, column=1, padx=5)

    columns = (
        "Name",
        "Weight",
        "Height",
        "BMI",
        "Category",
        "Date"
    )

    history_table = ttk.Treeview(
        history_window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        history_table.heading(column, text=column)

    history_table.column("Name", width=120)
    history_table.column("Weight", width=90)
    history_table.column("Height", width=90)
    history_table.column("BMI", width=80)
    history_table.column("Category", width=130)
    history_table.column("Date", width=180)

    history_table.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

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
        name = name_entry.get().strip()

        if name:
            load_records(name)
        else:
            load_records()

    search_button = tk.Button(
        filter_frame,
        text="Search",
        command=search_records
    )
    search_button.grid(row=0, column=2, padx=5)

    show_all_button = tk.Button(
        filter_frame,
        text="Show All",
        command=load_records
    )
    show_all_button.grid(row=0, column=3, padx=5)

    message_label = tk.Label(
    history_window,
    text=""
    )
    message_label.pack(pady=5)

    load_records()

def show_bmi_trend():
    trend_window = tk.Toplevel(window)
    trend_window.title("BMI Trend")
    trend_window.geometry("400x180")

    name_label = tk.Label(
        trend_window,
        text="Enter name:"
    )
    name_label.pack(pady=(20, 5))

    name_entry = tk.Entry(
        trend_window,
        width=25
    )
    name_entry.pack()

    def display_trend():
        name = name_entry.get().strip()

        if not name:
            trend_message.config(
                text="Please enter a name."
            )
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

    trend_button = tk.Button(
        trend_window,
        text="View Trend",
        command=display_trend
    )
    trend_button.pack(pady=10)

    trend_message = tk.Label(
        trend_window,
        text=""
    )
    trend_message.pack()
    
window = tk.Tk()
create_database()

window.title("Smart BMI Tracker")
window.geometry("550x600")
window.resizable(False, False)

# Main heading
title_label = tk.Label(
    window,
    text="Smart BMI Tracker",
    font=("Arial", 22, "bold")
)
title_label.pack(pady=(25, 5))

subtitle_label = tk.Label(
    window,
    text="Calculate and track your BMI",
    font=("Arial", 11)
)
subtitle_label.pack(pady=(0, 20))


# Input section
input_frame = tk.Frame(window)
input_frame.pack(pady=10)

name_label = tk.Label(
    input_frame,
    text="Name:",
    font=("Arial", 11)
)
name_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

name_entry = tk.Entry(
    input_frame,
    width=28,
    font=("Arial", 11)
)
name_entry.grid(row=0, column=1, padx=10, pady=10)

weight_label = tk.Label(
    input_frame,
    text="Weight (kg):",
    font=("Arial", 11)
)
weight_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

weight_entry = tk.Entry(
    input_frame,
    width=28,
    font=("Arial", 11)
)
weight_entry.grid(row=1, column=1, padx=10, pady=10)

height_label = tk.Label(
    input_frame,
    text="Height (cm):",
    font=("Arial", 11)
)
height_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

height_entry = tk.Entry(
    input_frame,
    width=28,
    font=("Arial", 11)
)
height_entry.grid(row=2, column=1, padx=10, pady=10)


# Calculate button
calculate_button = tk.Button(
    window,
    text="Calculate BMI",
    font=("Arial", 11, "bold"),
    width=20,
    command=handle_calculate
)
calculate_button.pack(pady=15)


# Result section
result_label = tk.Label(
    window,
    text="",
    font=("Arial", 13, "bold"),
    width=35,
    height=3
)
result_label.pack(pady=10)


# Additional buttons
history_button = tk.Button(
    window,
    text="View History",
    font=("Arial", 10),
    width=20,
    command=show_history
)
history_button.pack(pady=5)

trend_button = tk.Button(
    window,
    text="View BMI Trend",
    font=("Arial", 10),
    width=20,
    command=show_bmi_trend
)
trend_button.pack(pady=5)


window.mainloop()