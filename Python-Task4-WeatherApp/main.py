import io
from datetime import datetime
import tkinter as tk

import requests
from PIL import Image, ImageTk

from weather_api import get_current_weather, get_forecast


class WeatherApp:
    def __init__(self, root):
        self.root = root

        # ---------- Window ----------
        self.root.title("Weather Forecast")
        self.root.geometry("1050x760")
        self.root.minsize(850, 600)

        # ---------- Colors ----------
        self.bg_color = "#EAF4FF"
        self.header_color = "#1976D2"
        self.card_color = "#FFFFFF"
        self.primary_color = "#1565C0"
        self.secondary_color = "#42A5F5"
        self.text_color = "#17324D"
        self.muted_color = "#607D8B"
        self.error_color = "#D32F2F"

        self.root.configure(bg=self.bg_color)
        self.current_icon = None
        self.forecast_icons = []

        self.unit = "C"
        self.current_temperature_c = None
        self.hourly_temperature_labels = []
        self.hourly_temperatures_c = []
        self.daily_temperature_labels = []
        self.daily_temperatures_c = []

        # ==================================================
        # HEADER - Fixed (does not scroll)
        # ==================================================

        header = tk.Frame(
            root,
            bg=self.header_color,
            height=105
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Weather Forecast",
            bg=self.header_color,
            fg="white",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=(18, 2))

        tk.Label(
            header,
            text="Real-time weather and forecast information",
            bg=self.header_color,
            fg="#E3F2FD",
            font=("Segoe UI", 10)
        ).pack()

        # ==================================================
        # SCROLLABLE AREA
        # ==================================================

        main_area = tk.Frame(
            root,
            bg=self.bg_color
        )
        main_area.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            main_area,
            bg=self.bg_color,
            highlightthickness=0
        )

        self.scrollbar = tk.Scrollbar(
            main_area,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(
            self.canvas,
            bg=self.bg_color
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        # Update scroll area when content changes
        self.scrollable_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # Make content width match window width
        self.canvas.bind(
            "<Configure>",
            self.update_canvas_width
        )

        # Mouse wheel scrolling
        self.canvas.bind_all(
            "<MouseWheel>",
            self.mouse_wheel_scroll
        )

        # ==================================================
        # SEARCH CARD
        # ==================================================

        search_card = tk.Frame(
            self.scrollable_frame,
            bg=self.card_color,
            padx=20,
            pady=15
        )
        search_card.pack(
            fill="x",
            padx=25,
            pady=15
        )

        self.city_entry = tk.Entry(
            search_card,
            font=("Segoe UI", 12),
            width=35,
            relief="flat",
            bg="#F1F7FC",
            fg=self.text_color,
            insertbackground=self.text_color
        )
        self.city_entry.pack(
            side="left",
            padx=(5, 12),
            ipady=8
        )

        self.get_weather_button = tk.Button(
            search_card,
            text="Get Weather",
            command=self.fetch_weather,
            bg=self.primary_color,
            fg="white",
            activebackground=self.secondary_color,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.get_weather_button.pack(side="left")

        self.unit_button = tk.Button(
            search_card,
            text="°C / °F",
            command=self.toggle_unit,
            bg="#43A047",
            fg="white",
            activebackground="#66BB6A",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        )
        self.unit_button.pack(side="left", padx=10)


        self.city_entry.bind(
            "<Return>",
            lambda event: self.fetch_weather()
        )

        # ==================================================
        # CURRENT WEATHER CARD
        # ==================================================

        current_card = tk.Frame(
            self.scrollable_frame,
            bg=self.card_color,
            padx=20,
            pady=10
        )
        current_card.pack(
            fill="x",
            padx=25,
            pady=5
        )

        tk.Label(
            current_card,
            text="CURRENT WEATHER",
            bg=self.card_color,
            fg=self.primary_color,
            font=("Segoe UI", 11, "bold")
        ).pack()

        self.location_label = tk.Label(
            current_card,
            text="Search for a city",
            bg=self.card_color,
            fg=self.text_color,
            font=("Segoe UI", 20, "bold")
        )
        self.location_label.pack(pady=(3, 0))

        self.icon_label = tk.Label(
            current_card,
            bg=self.card_color
        )
        self.icon_label.pack()

        self.temperature_label = tk.Label(
            current_card,
            text="-- °C",
            bg=self.card_color,
            fg=self.primary_color,
            font=("Segoe UI", 30, "bold")
        )
        self.temperature_label.pack()

        self.condition_label = tk.Label(
            current_card,
            text="",
            bg=self.card_color,
            fg=self.text_color,
            font=("Segoe UI", 14)
        )
        self.condition_label.pack()

        # Weather details
        details_frame = tk.Frame(
            current_card,
            bg=self.card_color
        )
        details_frame.pack(pady=5)

        self.humidity_label = tk.Label(
            details_frame,
            text="Humidity\n--%",
            bg="#E3F2FD",
            fg=self.text_color,
            font=("Segoe UI", 10, "bold"),
            padx=22,
            pady=7
        )
        self.humidity_label.pack(
            side="left",
            padx=5
        )

        self.wind_label = tk.Label(
            details_frame,
            text="Wind\n-- m/s",
            bg="#E8F5E9",
            fg=self.text_color,
            font=("Segoe UI", 10, "bold"),
            padx=22,
            pady=7
        )
        self.wind_label.pack(
            side="left",
            padx=5
        )

        # ==================================================
        # ERROR MESSAGE
        # ==================================================

        self.error_label = tk.Label(
            self.scrollable_frame,
            text="",
            bg=self.bg_color,
            fg=self.error_color,
            font=("Segoe UI", 10, "bold")
        )
        self.error_label.pack(pady=3)

        # ==================================================
        # NEXT 6 HOURS
        # ==================================================

        tk.Label(
            self.scrollable_frame,
            text="NEXT 6 HOURS",
            bg=self.bg_color,
            fg=self.primary_color,
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=(10, 5)
        )

        self.hourly_container = tk.Frame(
            self.scrollable_frame,
            bg=self.bg_color
        )
        self.hourly_container.pack(
            fill="x",
            padx=25
        )

        # ==================================================
        # 5-DAY FORECAST
        # ==================================================

        tk.Label(
            self.scrollable_frame,
            text="5-DAY FORECAST",
            bg=self.bg_color,
            fg=self.primary_color,
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=(15, 5)
        )

        self.daily_container = tk.Frame(
            self.scrollable_frame,
            bg=self.bg_color
        )
        self.daily_container.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

    # ======================================================
    # SCROLL FUNCTIONS
    # ======================================================

    def update_canvas_width(self, event):
        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )

    def mouse_wheel_scroll(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # ======================================================
    # FETCH WEATHER
    # ======================================================

    def fetch_weather(self):
        city = self.city_entry.get().strip()

        if not city:
            self.error_label.config(
                text="Please enter a city name."
            )
            return

        # Clear previous weather data
        self.location_label.config(
            text="Search for a city"
        )

        self.temperature_label.config(
            text=f"-- °{self.unit}"
        )

        self.condition_label.config(
            text=""
        )

        self.humidity_label.config(
            text="Humidity\n--%"
        )

        self.wind_label.config(
            text="Wind\n-- m/s"
        )

        self.current_temperature_c = None

        # Clear hourly forecast
        for widget in self.hourly_container.winfo_children():
            widget.destroy()

        self.hourly_temperature_labels = []
        self.hourly_temperatures_c = []

        # Clear 5-day forecast
        for widget in self.daily_container.winfo_children():
            widget.destroy()

        self.daily_temperature_labels = []
        self.daily_temperatures_c = []

        self.error_label.config(text="")

        # Get current weather
        data = get_current_weather(city)

        if "error" in data:
            self.error_label.config(
                text=data["error"]
            )
            return

        location = f"{data['name']}, {data['sys']['country']}"
        temperature = data["main"]["temp"]

        self.current_temperature_c = temperature

        condition = data["weather"][0]["description"].title()
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        self.location_label.config(
            text=location
        )

        display_temperature = temperature

        if self.unit == "F":
            display_temperature = (
                temperature * 9 / 5
            ) + 32

        self.temperature_label.config(
            text=f"{display_temperature:.1f} °{self.unit}"
        )

        self.condition_label.config(
            text=condition
        )

        self.humidity_label.config(
            text=f"Humidity\n{humidity}%"
        )

        self.wind_label.config(
            text=f"Wind\n{wind_speed:.1f} m/s"
        )

        self.load_weather_icon(
            data["weather"][0]["icon"]
        )

        self.load_hourly_forecast(city)
        self.load_daily_forecast(city)
        
    # ======================================================
    # WEATHER ICON
    # ======================================================

    def load_weather_icon(self, icon_code):
        icon_url = (
            f"https://openweathermap.org/img/wn/"
            f"{icon_code}@2x.png"
        )

        try:
            response = requests.get(
                icon_url,
                timeout=10
            )
            response.raise_for_status()

            image = Image.open(
                io.BytesIO(response.content)
            )

            image = image.resize(
                (70, 70),
                Image.Resampling.LANCZOS
            )

            self.current_icon = ImageTk.PhotoImage(
                image
            )

            self.icon_label.config(
                image=self.current_icon
            )

        except requests.exceptions.RequestException:
            self.icon_label.config(
                image=""
            )

    def load_forecast_icon(self, icon_code):
        icon_url = (
            f"https://openweathermap.org/img/wn/"
            f"{icon_code}@2x.png"
        )

        try:
            response = requests.get(
                icon_url,
                timeout=10
            )
            response.raise_for_status()

            image = Image.open(
                io.BytesIO(response.content)
            )

            image = image.resize(
                (50, 50),
                Image.Resampling.LANCZOS
            )

            return ImageTk.PhotoImage(image)

        except requests.exceptions.RequestException:
            return None 
        

    # ======================================================
    # 6-HOUR FORECAST
    # ======================================================

    def load_hourly_forecast(self, city):
        data = get_forecast(city)

        if "error" in data:
            return

        for widget in self.hourly_container.winfo_children():
            widget.destroy()

        self.forecast_icons = []

        forecasts = data["list"][:2]

        self.hourly_temperatures_c = [
            forecast["main"]["temp"]
            for forecast in forecasts
        ]

        self.hourly_temperature_labels = []

        for forecast in forecasts:

            time = datetime.fromtimestamp(
                forecast["dt"]
            ).strftime("%I:%M %p")

            temp = forecast["main"]["temp"]

            condition = (
                forecast["weather"][0]["description"]
                .title()
            )

            icon_code = forecast["weather"][0]["icon"]
            icon = self.load_forecast_icon(icon_code)

            if icon:
                self.forecast_icons.append(icon)

            card = tk.Frame(
                self.hourly_container,
                bg=self.card_color,
                padx=15,
                pady=8
            )

            card.pack(
                side="left",
                expand=True,
                fill="x",
                padx=5
            )

            tk.Label(
                card,
                text=time,
                bg=self.card_color,
                fg=self.primary_color,
                font=("Segoe UI", 11, "bold")
            ).pack()

            if icon:
                tk.Label(
                    card,
                    image=icon,
                    bg=self.card_color
                ).pack()

            temp_label = tk.Label(
                card,
                text=f"{temp:.1f} °{self.unit}",
                bg=self.card_color,
                fg=self.text_color,
                font=("Segoe UI", 15, "bold")
            )

            temp_label.pack(pady=3)

            self.hourly_temperature_labels.append(
                temp_label
            )

            tk.Label(
                card,
                text=condition,
                bg=self.card_color,
                fg=self.muted_color,
                font=("Segoe UI", 9)
            ).pack()

    # ======================================================
    # 5-DAY FORECAST
    # ======================================================

    def load_daily_forecast(self, city):
        data = get_forecast(city)

        if "error" in data:
            return

        for widget in self.daily_container.winfo_children():
            widget.destroy()

        daily_data = {}

        for forecast in data["list"]:

            date = forecast["dt_txt"].split(" ")[0]

            if date not in daily_data:
                daily_data[date] = forecast

        days = list(daily_data.items())[:5]

        self.daily_temperatures_c = [
            forecast["main"]["temp"]
            for date, forecast in days
        ]

        self.daily_temperature_labels = []

        for date, forecast in days:

            day = datetime.strptime(
                date,
                "%Y-%m-%d"
            ).strftime("%a")

            temp = forecast["main"]["temp"]

            condition = (
                forecast["weather"][0]
                ["description"]
                .title()
            )

            icon_code = forecast["weather"][0]["icon"]
            icon = self.load_forecast_icon(icon_code)

            if icon:
                self.forecast_icons.append(icon)

            card = tk.Frame(
                self.daily_container,
                bg=self.card_color,
                padx=10,
                pady=8
            )

            card.pack(
                side="left",
                expand=True,
                fill="x",
                padx=4
            )

            if icon:
                tk.Label(
                    card,
                    image=icon,
                    bg=self.card_color
                ).pack()

            temp_label = tk.Label(
                card,
                text=f"{temp:.1f} °{self.unit}",
                bg=self.card_color,
                fg=self.text_color,
                font=("Segoe UI", 13, "bold")
            )

            temp_label.pack(pady=3)

            self.daily_temperature_labels.append(temp_label)

            tk.Label(
                card,
                text=condition,
                bg=self.card_color,
                fg=self.muted_color,
                font=("Segoe UI", 8),
                wraplength=100
            ).pack()

    def toggle_unit(self):
        if self.unit == "C":
            self.unit = "F"
        else:
            self.unit = "C"

        # Current weather
        if self.current_temperature_c is not None:
            temp = self.current_temperature_c

            if self.unit == "F":
                temp = (temp * 9 / 5) + 32

            self.temperature_label.config(
                text=f"{temp:.1f} °{self.unit}"
            )

        # 6-hour forecast
        for label, temp_c in zip(
            self.hourly_temperature_labels,
            self.hourly_temperatures_c
        ):
            temp = temp_c

            if self.unit == "F":
                temp = (temp * 9 / 5) + 32

            label.config(
                text=f"{temp:.1f} °{self.unit}"
            )

        # 5-day forecast
        for label, temp_c in zip(
            self.daily_temperature_labels,
            self.daily_temperatures_c
        ):
            temp = temp_c

            if self.unit == "F":
                temp = (temp * 9 / 5) + 32

            label.config(
                text=f"{temp:.1f} °{self.unit}"
            )


# ==========================================================
# APPLICATION START
# ==========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()