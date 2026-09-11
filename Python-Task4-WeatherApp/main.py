import io
from datetime import datetime, timedelta
import tkinter as tk

import requests
from PIL import Image, ImageTk

from weather_api import get_current_weather, get_forecast


class WeatherApp:
    def __init__(self, root):
        self.root = root

        # ---------- Window ----------
        self.root.title("Weather Forecast")
        self.root.geometry("1180x800")
        self.root.minsize(980, 650)

        # ---------- Modern dashboard colors ----------
        self.bg_color = "#F3F7FC"
        self.header_color = "#2563EB"
        self.card_color = "#FFFFFF"
        self.primary_color = "#2563EB"
        self.secondary_color = "#4F46E5"
        self.text_color = "#172554"
        self.muted_color = "#64748B"
        self.error_color = "#DC2626"
        self.sidebar_color = "#172554"
        self.sidebar_text = "#E2E8F0"
        self.soft_blue = "#EFF6FF"
        self.soft_green = "#ECFDF5"

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
        # MODERN DASHBOARD LAYOUT
        # ==================================================

        # Left navigation panel
        sidebar = tk.Frame(root, bg=self.sidebar_color, width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Weather icon
        weather_icon = Image.open("weather-app.png")
        weather_icon = weather_icon.resize((65, 65), Image.Resampling.LANCZOS)
        self.weather_icon_image = ImageTk.PhotoImage(weather_icon)

        tk.Label(
            sidebar,
            image=self.weather_icon_image,
            bg=self.sidebar_color
        ).pack(pady=(28, 0))

        tk.Label(
            sidebar,
            text="WEATHER",
            bg=self.sidebar_color,
            fg="white",
            font=("Segoe UI", 17, "bold")
        ).pack(pady=(0, 2))

        tk.Label(
            sidebar,
            text="Forecast Dashboard",
            bg=self.sidebar_color,
            fg="#A5B4FC",
            font=("Segoe UI", 9)
        ).pack()

        tk.Frame(sidebar, bg="#334155", height=1).pack(fill="x", padx=25, pady=28)

        nav_items = [
            ("⌂", "Home", self.scroll_to_top),
            ("◷", "Forecast", self.scroll_to_forecast),
            ("☀", "Conditions", self.scroll_to_conditions),
            ("⚙", "Settings", self.scroll_to_settings),
            ("ⓘ", "About", self.scroll_to_about),
        ]

        self.nav_items = {}
        for index, (icon, text, command) in enumerate(nav_items):
            item_bg = "#2563EB" if index == 0 else self.sidebar_color
            item = tk.Frame(sidebar, bg=item_bg, height=48, cursor="hand2")
            item.pack(fill="x", padx=12, pady=4)
            item.pack_propagate(False)

            icon_label = tk.Label(
                item, text=icon, bg=item_bg, fg="white",
                font=("Segoe UI Symbol", 17), cursor="hand2"
            )
            icon_label.pack(side="left", padx=(14, 12))

            text_label = tk.Label(
                item, text=text, bg=item_bg,
                fg="white" if index == 0 else self.sidebar_text,
                font=("Segoe UI", 11, "bold" if index == 0 else "normal"),
                cursor="hand2"
            )
            text_label.pack(side="left")

            for widget in (item, icon_label, text_label):
                widget.bind("<Button-1>", lambda event, cmd=command, name=text: self.handle_navigation(cmd, name))
                widget.bind("<Enter>", lambda event, frame=item: frame.config(bg="#1E40AF"))
                widget.bind("<Leave>", lambda event, frame=item, idx=index: frame.config(bg="#2563EB" if idx == 0 else self.sidebar_color))

            self.nav_items[text] = item

        tk.Label(
            sidebar,
            text=" Good weather \n brings a good mood ",
            bg=self.sidebar_color,
            fg="#94A3B8",
            font=("Segoe UI", 8),
            justify="left"
        ).pack(side="bottom", anchor="w", padx=22, pady=22)

        # Right side of dashboard.
        content = tk.Frame(root, bg=self.bg_color)
        content.pack(side="left", fill="both", expand=True)

        # ---------- Top header ----------
        header = tk.Frame(content, bg=self.header_color, height=105)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_left = tk.Frame(header, bg=self.header_color)
        header_left.pack(side="left", padx=28, pady=18)

        tk.Label(
            header_left,
            text="Weather Forecast",
            bg=self.header_color,
            fg="white",
            font=("Segoe UI", 26, "bold")
        ).pack(anchor="w")

        tk.Label(
            header_left,
            text="Real-time weather and forecast information",
            bg=self.header_color,
            fg="#DBEAFE",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(1, 0))

        header_right = tk.Frame(header, bg=self.header_color)
        header_right.pack(side="right", padx=24, pady=16)

        self.date_label = tk.Label(
            header_right,
            text="",
            bg=self.header_color,
            fg="white",
            font=("Segoe UI", 10, "bold")
        )
        self.date_label.pack(anchor="e")

        self.time_label = tk.Label(
            header_right,
            text="",
            bg=self.header_color,
            fg="#DBEAFE",
            font=("Segoe UI", 9)
        )
        self.time_label.pack(anchor="e", pady=(3, 0))

        self.update_date_time()

        # ==================================================
        # SCROLLABLE CONTENT
        # ==================================================
        main_area = tk.Frame(content, bg=self.bg_color)
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

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind("<Configure>", self.update_canvas_width)
        self.canvas.bind_all("<MouseWheel>", self.mouse_wheel_scroll)

        # ---------- Search card ----------
        search_card = tk.Frame(
            self.scrollable_frame,
            bg=self.card_color,
            highlightbackground="#D9E2F0",
            highlightthickness=1
        )
        search_card.pack(fill="x", padx=24, pady=20)

        tk.Label(
            search_card,
            text="Search location",
            bg=self.card_color,
            fg=self.text_color,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=20, pady=(14, 6))

        search_row = tk.Frame(search_card, bg=self.card_color)
        search_row.pack(fill="x", padx=20, pady=(0, 16))

        self.city_entry = tk.Entry(
            search_row,
            font=("Segoe UI", 12),
            relief="flat",
            bg="#F1F5F9",
            fg=self.text_color,
            insertbackground=self.text_color
        )
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 10))

        self.get_weather_button = tk.Button(
            search_row,
            text="Get Weather",
            command=self.fetch_weather,
            bg=self.primary_color,
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=22,
            pady=9
        )
        self.get_weather_button.pack(side="left")

        self.unit_button = tk.Button(
            search_row,
            text="°C / °F",
            command=self.toggle_unit,
            bg="#16A34A",
            fg="white",
            activebackground="#15803D",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=9
        )
        self.unit_button.pack(side="left", padx=(10, 0))

        self.city_entry.bind("<Return>", lambda event: self.fetch_weather())

        self.location_button = tk.Button(
            search_row,
            text="📍 My Location",
            command=self.use_current_location,
            bg="#0EA5E9",
            fg="white",
            activebackground="#0284C7",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=9
        )
        self.location_button.pack(side="left", padx=(10, 0))

        # ---------- Current weather card ----------
        self.current_card = tk.Frame(
            self.scrollable_frame,
            bg=self.card_color,
            highlightbackground="#D9E2F0",
            highlightthickness=1
        )
        self.current_card.pack(fill="x", padx=24, pady=(0, 14))
        current_card = self.current_card

        tk.Label(
            current_card,
            text="CURRENT WEATHER",
            bg=self.card_color,
            fg=self.primary_color,
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(16, 2))

        self.location_label = tk.Label(
            current_card,
            text="Search for a city",
            bg=self.card_color,
            fg=self.text_color,
            font=("Segoe UI", 21, "bold")
        )
        self.location_label.pack()

        self.icon_label = tk.Label(current_card, bg=self.card_color)
        self.icon_label.pack(pady=(2, 0))

        self.temperature_label = tk.Label(
            current_card,
            text="-- °C",
            bg=self.card_color,
            fg=self.primary_color,
            font=("Segoe UI", 32, "bold")
        )
        self.temperature_label.pack()

        self.condition_label = tk.Label(
            current_card,
            text="",
            bg=self.card_color,
            fg=self.muted_color,
            font=("Segoe UI", 13)
        )
        self.condition_label.pack(pady=(0, 8))

        details_frame = tk.Frame(current_card, bg=self.card_color)
        details_frame.pack(pady=(0, 18))

        self.humidity_label = tk.Label(
            details_frame,
            text="Humidity\n--%",
            bg=self.soft_blue,
            fg=self.text_color,
            font=("Segoe UI", 10, "bold"),
            padx=28,
            pady=8
        )
        self.humidity_label.pack(side="left", padx=5)

        self.wind_label = tk.Label(
            details_frame,
            text="Wind\n-- m/s",
            bg=self.soft_green,
            fg=self.text_color,
            font=("Segoe UI", 10, "bold"),
            padx=28,
            pady=8
        )
        self.wind_label.pack(side="left", padx=5)

        # ---------- Error message ----------
        self.error_label = tk.Label(
            self.scrollable_frame,
            text="",
            bg=self.bg_color,
            fg=self.error_color,
            font=("Segoe UI", 10, "bold")
        )
        self.error_label.pack(pady=(0, 3))

        # ---------- Next 6 hours ----------
        self.hourly_section = tk.Label(
            self.scrollable_frame,
            text="NEXT 6 HOURS",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI", 11, "bold")
        )
        self.hourly_section.pack(anchor="w", padx=26, pady=(8, 6))

        self.hourly_container = tk.Frame(
            self.scrollable_frame,
            bg=self.bg_color
        )
        self.hourly_container.pack(fill="x", padx=24)

        # ---------- 5-day forecast ----------
        self.daily_section = tk.Label(
            self.scrollable_frame,
            text="5-DAY FORECAST",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI", 11, "bold")
        )
        self.daily_section.pack(anchor="w", padx=26, pady=(18, 6))

        self.daily_container = tk.Frame(
            self.scrollable_frame,
            bg=self.bg_color
        )
        self.daily_container.pack(fill="x", padx=24, pady=(0, 24))

        # ---------- Settings section ----------
        self.settings_section = tk.Frame(
            self.scrollable_frame, bg=self.card_color,
            highlightbackground="#D9E2F0", highlightthickness=1
        )
        self.settings_section.pack(fill="x", padx=24, pady=(0, 14))
        tk.Label(
            self.settings_section, text="SETTINGS",
            bg=self.card_color, fg=self.primary_color,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=18, pady=(14, 4))
        tk.Label(
            self.settings_section,
            text="Temperature unit: use the °C / °F button above.\nLocation: My Location uses approximate IP-based detection.",
            bg=self.card_color, fg=self.muted_color,
            font=("Segoe UI", 9), justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 14))

        # ---------- About section ----------
        self.about_section = tk.Frame(
            self.scrollable_frame, bg=self.card_color,
            highlightbackground="#D9E2F0", highlightthickness=1
        )
        self.about_section.pack(fill="x", padx=24, pady=(0, 30))
        tk.Label(
            self.about_section, text="ABOUT",
            bg=self.card_color, fg=self.primary_color,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=18, pady=(14, 4))
        tk.Label(
            self.about_section,
            text="Weather Forecast\nA Python weather dashboard using OpenWeatherMap data.\nBuilt for the Oasis Infobyte Python Programming Internship – Task 4.",
            bg=self.card_color, fg=self.muted_color,
            font=("Segoe UI", 9), justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 14))

    # ======================================================
    # SIDEBAR NAVIGATION
    # ======================================================

    def handle_navigation(self, command, name):
        self.set_active_navigation(name)
        command()

    def set_active_navigation(self, name):
        for item_name, item in self.nav_items.items():
            active = item_name == name
            item.config(bg="#2563EB" if active else self.sidebar_color)
            for child in item.winfo_children():
                child.config(
                    bg="#2563EB" if active else self.sidebar_color,
                    fg="white" if active else self.sidebar_text,
                    font=("Segoe UI Symbol" if child is item.winfo_children()[0] else "Segoe UI",
                          17 if child is item.winfo_children()[0] else 11,
                          "bold" if active else "normal")
                )

    def scroll_to_widget(self, widget):
        self.root.update_idletasks()
        y = widget.winfo_y()
        total = max(1, self.scrollable_frame.winfo_height() - self.canvas.winfo_height())
        self.canvas.yview_moveto(max(0, min(1, y / total)))

    def scroll_to_top(self):
        self.canvas.yview_moveto(0)

    def scroll_to_forecast(self):
        self.scroll_to_widget(self.hourly_section)

    def scroll_to_conditions(self):
        self.scroll_to_widget(self.current_card)

    def scroll_to_settings(self):
        self.scroll_to_widget(self.settings_section)

    def scroll_to_about(self):
        self.scroll_to_widget(self.about_section)

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
    # CURRENT LOCATION
    # ======================================================

    def use_current_location(self):
        """Detect an approximate city from the current internet connection."""
        self.error_label.config(text="Detecting your location...")
        self.location_button.config(state="disabled")

        providers = [
            (
                "https://ipinfo.io/json",
                lambda data: data.get("city"),
            ),
            (
                "https://ipapi.co/json/",
                lambda data: data.get("city"),
            ),
            (
                "https://ipwho.is/",
                lambda data: data.get("city") if data.get("success", True) else None,
            ),
            (
                "http://ip-api.com/json/?fields=status,city",
                lambda data: data.get("city") if data.get("status") == "success" else None,
            ),
        ]

        detected_city = None

        try:
            for url, city_reader in providers:
                try:
                    response = requests.get(
                        url,
                        timeout=8,
                        headers={"User-Agent": "Smart Weather Forecast App/1.0"}
                    )
                    response.raise_for_status()
                    data = response.json()
                    detected_city = city_reader(data)
                    if detected_city:
                        break
                except (requests.exceptions.RequestException, ValueError):
                    continue

            if not detected_city:
                self.error_label.config(
                    text="Unable to detect your location. Please enter a city manually."
                )
                return

            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, detected_city)
            self.fetch_weather()

        finally:
            self.location_button.config(state="normal")

    def update_date_time(self):
        """Keep the current local date and time visible in the header."""
        now = datetime.now()
        self.date_label.config(text=now.strftime("%a, %d %b %Y"))
        self.time_label.config(text=now.strftime("%I:%M:%S %p"))
        self.root.after(1000, self.update_date_time)

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
        """Show the next six hours at one-hour intervals from the current time."""
        current_data = get_current_weather(city)
        if "error" in current_data or "coord" not in current_data:
            return

        latitude = current_data["coord"].get("lat")
        longitude = current_data["coord"].get("lon")
        if latitude is None or longitude is None:
            return

        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "hourly": "temperature_2m,weather_code",
                    "forecast_days": 2,
                    "timezone": "auto",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            return

        for widget in self.hourly_container.winfo_children():
            widget.destroy()

        self.forecast_icons = []
        self.hourly_temperature_labels = []
        self.hourly_temperatures_c = []

        times = data.get("hourly", {}).get("time", [])
        temperatures = data.get("hourly", {}).get("temperature_2m", [])
        weather_codes = data.get("hourly", {}).get("weather_code", [])

        if not times or not temperatures:
            return

        # The API provides hourly values on the hour. For a current time such
        # as 12:55 PM, show 1:55 PM, 2:55 PM, ... while using the corresponding
        # 1:00 PM, 2:00 PM, ... forecast values.
        now = datetime.now()
        hourly_lookup = {}
        for i, time_text in enumerate(times):
            try:
                forecast_time = datetime.fromisoformat(time_text)
                hourly_lookup[forecast_time] = (
                    temperatures[i],
                    weather_codes[i] if i < len(weather_codes) else 0
                )
            except (ValueError, IndexError):
                continue

        forecasts = []
        for hour_offset in range(1, 7):
            target_time = now + timedelta(hours=hour_offset)
            api_time = target_time.replace(minute=0, second=0, microsecond=0)
            if api_time in hourly_lookup:
                temp, weather_code = hourly_lookup[api_time]
                forecasts.append((target_time, temp, weather_code))

        self.hourly_temperatures_c = [item[1] for item in forecasts]

        for display_time_obj, temp, weather_code in forecasts:
            display_time = display_time_obj.strftime("%I:%M %p")
            condition = self.open_meteo_condition(weather_code)
            icon = self.load_forecast_icon(self.open_meteo_icon(weather_code))

            if icon:
                self.forecast_icons.append(icon)

            card = tk.Frame(
                self.hourly_container,
                bg=self.card_color,
                padx=6,
                pady=8,
                highlightbackground="#D9E2F0",
                highlightthickness=1
            )
            card.pack(side="left", expand=True, fill="both", padx=3)

            tk.Label(
                card, text=display_time, bg=self.card_color,
                fg=self.primary_color, font=("Segoe UI", 9, "bold")
            ).pack()

            if icon:
                tk.Label(card, image=icon, bg=self.card_color).pack()

            display_temp = temp if self.unit == "C" else (temp * 9 / 5) + 32
            temp_label = tk.Label(
                card, text=f"{display_temp:.1f} °{self.unit}",
                bg=self.card_color, fg=self.text_color,
                font=("Segoe UI", 12, "bold")
            )
            temp_label.pack(pady=3)
            self.hourly_temperature_labels.append(temp_label)

            tk.Label(
                card, text=condition, bg=self.card_color,
                fg=self.muted_color, font=("Segoe UI", 8),
                wraplength=90
            ).pack()

    def open_meteo_condition(self, code):
        conditions = {
            0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
            45: "Fog", 48: "Rime Fog", 51: "Light Drizzle", 53: "Drizzle",
            55: "Heavy Drizzle", 61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
            71: "Light Snow", 73: "Snow", 75: "Heavy Snow", 80: "Rain Showers",
            81: "Rain Showers", 82: "Heavy Showers", 95: "Thunderstorm",
            96: "Thunderstorm", 99: "Thunderstorm"
        }
        return conditions.get(code, "Weather Conditions")

    def open_meteo_icon(self, code):
        if code == 0:
            return "01d"
        if code in (1, 2):
            return "02d"
        if code in (3, 45, 48):
            return "03d"
        if code in (51, 53, 55):
            return "09d"
        if code in (61, 63, 65, 80, 81, 82):
            return "10d"
        if code in (71, 73, 75):
            return "13d"
        if code in (95, 96, 99):
            return "11d"
        return "03d"

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
        today = datetime.now().date()

        for forecast in data["list"]:
            date_text = forecast["dt_txt"].split(" ")[0]
            try:
                forecast_date = datetime.strptime(date_text, "%Y-%m-%d").date()
            except ValueError:
                continue

            if forecast_date >= today and date_text not in daily_data:
                daily_data[date_text] = forecast

        days = list(daily_data.items())[:5]

        self.daily_temperatures_c = [
            forecast["main"]["temp"]
            for date, forecast in days
        ]
        self.daily_temperature_labels = []

        for date, forecast in days:
            forecast_date = datetime.strptime(date, "%Y-%m-%d")
            day = forecast_date.strftime("%a")
            formatted_date = forecast_date.strftime("%d %b %Y")
            temp = forecast["main"]["temp"]
            condition = forecast["weather"][0]["description"].title()
            icon_code = forecast["weather"][0]["icon"]
            icon = self.load_forecast_icon(icon_code)

            if icon:
                self.forecast_icons.append(icon)

            card = tk.Frame(
                self.daily_container,
                bg=self.card_color,
                padx=8,
                pady=8,
                highlightbackground="#D9E2F0",
                highlightthickness=1
            )
            card.pack(side="left", expand=True, fill="both", padx=3)

            tk.Label(
                card, text=day, bg=self.card_color,
                fg=self.primary_color, font=("Segoe UI", 10, "bold")
            ).pack()

            if icon:
                tk.Label(card, image=icon, bg=self.card_color).pack()

            display_temp = temp if self.unit == "C" else (temp * 9 / 5) + 32
            temp_label = tk.Label(
                card, text=f"{display_temp:.1f} °{self.unit}",
                bg=self.card_color, fg=self.text_color,
                font=("Segoe UI", 12, "bold")
            )
            temp_label.pack(pady=2)
            self.daily_temperature_labels.append(temp_label)

            tk.Label(
                card, text=formatted_date, bg=self.card_color,
                fg=self.text_color, font=("Segoe UI", 8, "bold")
            ).pack(pady=(0, 2))

            tk.Label(
                card, text=condition, bg=self.card_color,
                fg=self.muted_color, font=("Segoe UI", 8),
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