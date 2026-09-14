import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

from chat_utils import (
    HOST,
    PORT,
    BUFFER_SIZE,
    encode_message,
    decode_message,
    convert_emojis,
)


class ChatClient:

    def __init__(self, root):
        self.root = root
        self.root.title("ChatNest")
        screen_width = self.root.winfo_screenwidth()
        window_width = max(680, min(1000, (screen_width // 2) - 10))
        self.root.geometry(f"{window_width}x650")
        self.root.minsize(680, 550)

        self.socket = None
        self.username = None
        self.current_room = "General"
        self.connected = False

        self.bg_color = "#F3F7FC"
        self.primary_color = "#2563EB"
        self.dark_color = "#172554"
        self.card_color = "#FFFFFF"
        self.text_color = "#172554"
        self.muted_color = "#64748B"
        self.success_color = "#16A34A"
        self.error_color = "#DC2626"
        self.selected_message_id = None
        self.show_login_screen()

    # ======================================================
    # CONNECTION
    # ======================================================

    def connect_to_server(self):

        try:
            self.socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.socket.connect(
                (HOST, PORT)
            )

            self.connected = True

            threading.Thread(
                target=self.receive_messages,
                daemon=True
            ).start()

            return True

        except ConnectionRefusedError:
            messagebox.showerror(
                "Connection Error",
                "Unable to connect to the server.\n\n"
                "Make sure server.py is running."
            )
            return False

        except OSError as error:
            messagebox.showerror(
                "Connection Error",
                str(error)
            )
            return False

    # ======================================================
    # SEND DATA
    # ======================================================

    def send_data(self, data):

        try:
            self.socket.sendall(
                encode_message(data)
            )
            return True

        except (ConnectionResetError, BrokenPipeError, OSError):
            self.connected = False

            messagebox.showerror(
                "Connection Lost",
                "Connection to the server was lost."
            )

            return False

    # ======================================================
    # RECEIVE DATA
    # ======================================================

    def receive_messages(self):

        while self.connected:

            try:
                data = self.socket.recv(
                    BUFFER_SIZE
                )

                if not data:
                    break

                message = decode_message(data)

                self.root.after(
                    0,
                    self.handle_server_message,
                    message
                )

            except (
                ConnectionResetError,
                ConnectionAbortedError,
                OSError,
                ValueError
            ):
                break

        self.connected = False

    # ======================================================
    # LOGIN SCREEN
    # ======================================================

    def show_login_screen(self):

        self.clear_window()

        self.root.configure(
            bg=self.bg_color
        )

        container = tk.Frame(
            self.root,
            bg=self.bg_color
        )

        container.pack(
            expand=True
        )

        card = tk.Frame(
            container,
            bg=self.card_color,
            padx=45,
            pady=35,
            highlightbackground="#D9E2F0",
            highlightthickness=1
        )

        card.pack()

        tk.Label(
            card,
            text="💬",
            bg=self.card_color,
            fg=self.primary_color,
            font=("Segoe UI Emoji", 40)
        ).pack()

        tk.Label(
            card,
            text="ChatNest",
            bg=self.card_color,
            fg=self.dark_color,
            font=("Segoe UI", 24, "bold")
        ).pack()

        tk.Label(
            card,
            text="Chat • Connect • Belong",
            bg=self.card_color,
            fg=self.muted_color,
            font=("Segoe UI", 10)
        ).pack(
            pady=(0, 25)
        )

        tk.Label(
            card,
            text="Username",
            bg=self.card_color,
            fg=self.text_color,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w"
        )

        self.username_entry = tk.Entry(
            card,
            width=32,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )

        self.username_entry.pack(
            pady=(5, 15),
            ipady=7
        )

        tk.Label(
            card,
            text="Password",
            bg=self.card_color,
            fg=self.text_color,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w"
        )

        self.password_entry = tk.Entry(
            card,
            width=32,
            show="*",
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )

        self.password_entry.pack(
            pady=(5, 20),
            ipady=7
        )

        button_frame = tk.Frame(
            card,
            bg=self.card_color
        )

        button_frame.pack()

        tk.Button(
            button_frame,
            text="Login",
            command=self.login,
            bg=self.primary_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=9
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            button_frame,
            text="Register",
            command=self.register,
            bg=self.success_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=9
        ).pack(
            side="left",
            padx=5
        )

        self.username_entry.focus()

    # ======================================================
    # REGISTER
    # ======================================================

    def register(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter username and password."
            )
            return

        if not self.connected:

            if not self.connect_to_server():
                return

        self.send_data({
            "action": "register",
            "username": username,
            "password": password
        })

    # ======================================================
    # LOGIN
    # ======================================================

    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter username and password."
            )
            return

        if not self.connected:

            if not self.connect_to_server():
                return

        self.send_data({
            "action": "login",
            "username": username,
            "password": password
        })

    # ======================================================
    # SERVER MESSAGE HANDLER
    # ======================================================

    def handle_server_message(self, data):

        message_type = data.get("type")

        # --------------------------------------------------
        # AUTHENTICATION
        # --------------------------------------------------

        if message_type == "auth":

            if data.get("success"):

                self.username = data.get(
                    "username"
                )

                self.current_room = data.get(
                    "room",
                    "General"
                )

                self.show_chat_screen()

            else:

                messagebox.showerror(
                    "Authentication",
                    data.get(
                        "message",
                        "Authentication failed."
                    )
                )

        # --------------------------------------------------
        # NORMAL MESSAGE
        # --------------------------------------------------

        elif message_type == "message":

            message_id = data.get("id")

            username = data.get(
                "username",
                "Unknown"
            )

            message = data.get(
                "message",
                ""
            )

            timestamp = data.get(
                "timestamp",
                ""
            )

            self.display_message(
                message_id,
                username,
                message,
                timestamp
            )

            if username != self.username:
                self.notify_new_message(
                    username,
                    message
                )
        # --------------------------------------------------
        # MESSAGE HISTORY
        # --------------------------------------------------

        elif message_type == "history":
            history = data.get("messages", [])

            if not hasattr(self, "chat_text"):
                return

            self.chat_text.config(state="normal")
            self.chat_text.delete("1.0", tk.END)

            for msg in history:
                message_id = msg.get("id")
                username = msg.get("username", "")
                message = convert_emojis(msg.get("message", ""))
                timestamp = msg.get("timestamp", "")

                self.chat_text.insert(
                    tk.END,
                    f"[{timestamp}] {username}: {message}\n",
                    f"message_{message_id}"
                )

            self.chat_text.config(state="disabled")
            self.chat_text.see(tk.END)
        # --------------------------------------------------
        # SYSTEM MESSAGE
        # --------------------------------------------------

        elif message_type == "system":

            self.display_system_message(
                data.get(
                    "message",
                    ""
                )
            )

        # --------------------------------------------------
        # ROOMS
        # --------------------------------------------------

        elif message_type == "rooms":

            rooms = data.get(
                "rooms",
                []
            )

            self.update_room_list(
                rooms
            )

        # --------------------------------------------------
        # ROOM MEMBERS
        # --------------------------------------------------

        elif message_type == "room_members":

            members = data.get("members", [])
            count = data.get("count", len(members))

            # Update member count
            if hasattr(self, "member_count_label"):
                member_text = (
                    f"{count} member"
                    if count == 1
                    else f"{count} members"
                )

                self.member_count_label.config(
                    text=member_text
                )

            # Clear old member cards
            if hasattr(self, "members_list_frame"):

                for widget in self.members_list_frame.winfo_children():
                    widget.destroy()

                # Create member cards
                for member in members:

                    username = member.get(
                        "username",
                        "Unknown"
                    )

                    status = member.get(
                        "status",
                        "online"
                    )

                    card = tk.Frame(
                        self.members_list_frame,
                        bg="#F0FDF4"
                    )

                    card.pack(
                        fill="x",
                        pady=4
                    )

                    # Avatar
                    tk.Label(
                        card,
                        text=username[:1].upper(),
                        bg=self.success_color,
                        fg="white",
                        font=("Segoe UI", 10, "bold"),
                        width=3
                    ).pack(
                        side="left",
                        padx=7,
                        pady=7
                    )

                    info = tk.Frame(
                        card,
                        bg="#F0FDF4"
                    )

                    info.pack(
                        side="left",
                        padx=(2, 5),
                        pady=5
                    )

                    tk.Label(
                        info,
                        text=username,
                        bg="#F0FDF4",
                        fg=self.dark_color,
                        font=("Segoe UI", 10, "bold")
                    ).pack(
                        anchor="w"
                    )

                    tk.Label(
                        info,
                        text="●  Online",
                        bg="#F0FDF4",
                        fg=self.success_color,
                        font=("Segoe UI", 8)
                    ).pack(
                        anchor="w"
                    )
        # --------------------------------------------------
        # ROOM RESULT
        # --------------------------------------------------

        elif message_type == "room_result":

            if data.get("success"):

                messagebox.showinfo(
                    "Room",
                    data.get(
                        "message",
                        "Success"
                    )
                )

                self.request_rooms()

            else:

                messagebox.showerror(
                    "Room",
                    data.get(
                        "message",
                        "Operation failed."
                    )
                )


        # --------------------------------------------------
        # DELETE ROOM RESULT
        # --------------------------------------------------

        elif message_type == "room_delete_result":
            messagebox.showerror(
                "Delete Room",
                data.get("message", "Unable to delete room.")
            )

        # --------------------------------------------------
        # DELETE MESSAGE RESULT
        # --------------------------------------------------

        elif message_type == "delete_result":

            if data.get("success"):

                self.selected_message_id = None

                messagebox.showinfo(
                    "Message Deleted",
                    "Message deleted for you."
                )

                message_id = data.get("message_id")
                if message_id and hasattr(self, "chat_text"):
                    tag = f"message_{message_id}"
                    ranges = self.chat_text.tag_ranges(tag)
                    if ranges:
                        self.chat_text.config(state="normal")
                        self.chat_text.delete(ranges[0], ranges[-1])
                        self.chat_text.config(state="disabled")

            else:

                messagebox.showerror(
                    "Delete Message",
                    data.get(
                        "message",
                        "Unable to delete message."
                    )
        )

        elif message_type == "clear_result":
            if data.get("success"):
                self.selected_message_id = None
                self.clear_chat()
                messagebox.showinfo(
                    "Chat Cleared",
                    "Chat cleared for you."
                )
            else:
                messagebox.showerror(
                    "Clear Chat",
                    data.get("message", "Unable to clear chat.")
                )       
        # --------------------------------------------------
        # ROOM DELETED
        # --------------------------------------------------

        elif message_type == "room_deleted":
            deleted_room = data.get("room", "")
            new_room = data.get("new_room", "General")
            rooms = data.get("rooms", [])

            # Update the room list from the same response instead of making
            # another request immediately. This keeps room deletion stable.
            if rooms:
                self.update_room_list(rooms)

            if data.get("notify"):
                messagebox.showinfo(
                    "Room Deleted",
                    data.get("message", "Room deleted successfully.")
                )

            # If this client was inside the deleted room, move it to General.
            if self.current_room == deleted_room:
                self.send_data({
                    "action": "join_room",
                    "room": new_room
                })

        # --------------------------------------------------
        # ROOM CHANGED
        # --------------------------------------------------

        elif message_type == "room_changed":

            self.current_room = data.get(
                "room",
                "General"
            )

            self.room_label.config(
                text=f"#{self.current_room}"
            )

            self.clear_chat()

    # ======================================================
    # CHAT SCREEN
    # ======================================================

    def show_chat_screen(self):
        self.clear_window()
        self.root.title("ChatNest")
        self.root.configure(bg=self.bg_color)

        # ==================================================
        # TOP HEADER
        # ==================================================

        header = tk.Frame(
            self.root,
            bg=self.dark_color,
            height=72
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        # --------------------------------------------------
        # Left: App Logo + Name
        # --------------------------------------------------

        logo_frame = tk.Frame(
            header,
            bg=self.dark_color
        )
        logo_frame.pack(side="left", padx=25)

        tk.Label(
            logo_frame,
            text="◯",
            bg=self.dark_color,
            fg="white",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            logo_frame,
            text="ChatNest",
            bg=self.dark_color,
            fg="white",
            font=("Segoe UI", 21, "bold")
        ).pack(side="left")


        # --------------------------------------------------
        # Right: Online Status + Username + Profile
        # --------------------------------------------------

        profile = tk.Frame(
            header,
            bg=self.dark_color
        )
        profile.pack(
            side="right",
            padx=22
        )

        # Green online indicator
        tk.Label(
            profile,
            text="●",
            bg=self.dark_color,
            fg="#22C55E",
            font=("Segoe UI", 13)
        ).pack(
            side="left",
            padx=(0, 6)
        )

        # Username
        tk.Label(
            profile,
            text=self.username,
            bg=self.dark_color,
            fg="white",
            font=("Segoe UI", 11, "bold")
        ).pack(
            side="left",
            padx=5
        )

        # Profile button
        tk.Button(
            profile,
            text="👤",
            command=self.show_profile_menu,
            bg=self.dark_color,
            fg="white",
            activebackground=self.dark_color,
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI Emoji", 13),
            cursor="hand2"
        ).pack(
            side="left",
            padx=(10, 0)
        )
        # ==================================================
        # MAIN CONTAINER
        # ==================================================

        main = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        main.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        # ==================================================
        # LEFT SIDEBAR
        # ==================================================

        sidebar = tk.Frame(
            main,
            bg=self.card_color,
            width=270,
            highlightbackground="#D9E2F0",
            highlightthickness=1
        )
        sidebar.pack(
            side="left",
            fill="y",
            padx=(0, 10)
        )
        sidebar.pack_propagate(False)

        # Create room
        tk.Button(
            sidebar,
            text="+  Create Room",
            command=self.create_new_room,
            bg=self.primary_color,
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            pady=10
        ).pack(
            fill="x",
            padx=14,
            pady=(15, 6)
        )

        tk.Button(
            sidebar,
            text="🗑  Delete Room",
            command=self.delete_current_room,
            bg="#FEE2E2",
            fg="#DC2626",
            activebackground="#FECACA",
            activeforeground="#B91C1C",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            pady=8
        ).pack(
            fill="x",
            padx=14,
            pady=(0, 12)
        )

        # Search
        search_frame = tk.Frame(
            sidebar,
            bg="#F1F5F9"
        )
        search_frame.pack(
            fill="x",
            padx=14,
            pady=(0, 15)
        )

        tk.Label(
            search_frame,
            text="🔍",
            bg="#F1F5F9",
            fg=self.muted_color,
            font=("Segoe UI", 11)
        ).pack(side="left", padx=(8, 3))

        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 10),
            bg="#F1F5F9",
            fg=self.text_color,
            relief="flat",
            bd=0
        )
        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=7
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.search_rooms
        )

        # Rooms title
        tk.Label(
            sidebar,
            text="CHAT ROOMS",
            bg=self.card_color,
            fg=self.muted_color,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w",
            padx=16,
            pady=(0, 8)
        )

        # Room list
        self.room_listbox = tk.Listbox(
            sidebar,
            font=("Segoe UI", 11),
            bg=self.card_color,
            fg=self.text_color,
            selectbackground="#DBEAFE",
            selectforeground=self.primary_color,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activestyle="none"
        )

        self.room_listbox.pack(
            fill="both",
            expand=True,
            padx=10
        )

        self.room_listbox.bind(
            "<Double-Button-1>",
            self.join_selected_room
        )

        # Bottom navigation
        nav = tk.Frame(
            sidebar,
            bg=self.card_color
        )
        nav.pack(
            fill="x",
            padx=10,
            pady=10
        )

        tk.Button(
            nav,
            text="⌂  Home",
            command=self.show_chat_screen,
            bg="#EFF6FF",
            fg=self.primary_color,
            relief="flat",
            bd=0,
            anchor="w",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            pady=7
        ).pack(fill="x")

        tk.Button(
            nav,
            text="👤  Profile",
            command=self.show_profile,
            bg=self.card_color,
            fg=self.text_color,
            relief="flat",
            bd=0,
            anchor="w",
            font=("Segoe UI", 10),
            cursor="hand2",
            pady=7
        ).pack(fill="x")

        tk.Button(
            nav,
            text="⚙  Settings",
            command=self.show_settings,
            bg=self.card_color,
            fg=self.text_color,
            relief="flat",
            bd=0,
            anchor="w",
            font=("Segoe UI", 10),
            cursor="hand2",
            pady=7
        ).pack(fill="x")

        tk.Button(
            nav,
            text="ⓘ  About ChatNest",
            command=self.show_about,
            bg=self.card_color,
            fg=self.text_color,
            relief="flat",
            bd=0,
            anchor="w",
            font=("Segoe UI", 10),
            cursor="hand2",
            pady=7
        ).pack(fill="x")

        # ==================================================
        # CENTER CHAT AREA
        # ==================================================

        chat_frame = tk.Frame(
            main,
            bg=self.card_color,
            highlightbackground="#D9E2F0",
            highlightthickness=1
        )
        chat_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Room header
        room_header = tk.Frame(
            chat_frame,
            bg=self.card_color,
            height=72
        )
        room_header.pack(fill="x")
        room_header.pack_propagate(False)

        room_info = tk.Frame(
            room_header,
            bg=self.card_color
        )
        room_info.pack(
            side="left",
            padx=20
        )

        self.room_label = tk.Label(
            room_info,
            text=f"#  {self.current_room}",
            bg=self.card_color,
            fg=self.dark_color,
            font=("Segoe UI", 17, "bold")
        )
        self.room_label.pack(anchor="w", pady=(12, 0))

        self.room_description = tk.Label(
            room_info,
            text="Chat with everyone",
            bg=self.card_color,
            fg=self.muted_color,
            font=("Segoe UI", 9)
        )
        self.room_description.pack(anchor="w")

        # Delete selected message
        tk.Button(
            room_header,
            text="🗑  Delete",
            command=self.delete_selected_message,
            bg="#FEE2E2",
            fg="#DC2626",
            relief="flat",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        ).pack(
            side="right",
            padx=(5, 0)
        )

        tk.Button(
            room_header,
            text="🧹  Clear Chat",
            command=self.clear_chat_for_user,
            bg="#FEF3C7",
            fg="#92400E",
            relief="flat",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        ).pack(side="right", padx=(5, 0))
        # Refresh
        tk.Button(
            room_header,
            text="↻  Refresh",
            command=self.request_rooms,
            bg="#EFF6FF",
            fg=self.primary_color,
            relief="flat",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        ).pack(
            side="right",
            padx=18
        )

        # Message area
        message_frame = tk.Frame(
            chat_frame,
            bg="#F8FAFC"
        )
        message_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 8)
        )

        scrollbar = tk.Scrollbar(
            message_frame
        )
        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.chat_text = tk.Text(
            message_frame,
            wrap="word",
            font=("Segoe UI", 10),
            bg="#F8FAFC",
            fg=self.text_color,
            relief="flat",
            bd=0,
            state="disabled",
            yscrollcommand=scrollbar.set,
            padx=12,
            pady=10
        )

        self.chat_text.pack(
            fill="both",
            expand=True
        )
        self.chat_text.bind(
            "<Button-1>",
            self.select_message
        )

        scrollbar.config(
            command=self.chat_text.yview
        )

        self.chat_text.tag_config(
            "system",
            foreground=self.muted_color,
            font=("Segoe UI", 9, "italic")
        )

        self.chat_text.tag_config(
            "own",
            foreground=self.primary_color,
            font=("Segoe UI", 10, "bold")
        )

        self.chat_text.tag_config(
            "other",
            foreground=self.success_color,
            font=("Segoe UI", 10, "bold")
        )

        # ==================================================
        # MESSAGE INPUT
        # ==================================================

        input_area = tk.Frame(
            chat_frame,
            bg=self.card_color
        )
        input_area.pack(
            fill="x",
            padx=12,
            pady=(0, 12)
        )

        tk.Label(
            input_area,
            text="😊",
            bg=self.card_color,
            fg=self.muted_color,
            font=("Segoe UI Emoji", 15)
        ).pack(
            side="left",
            padx=(5, 8)
        )

        self.message_entry = tk.Entry(
            input_area,
            font=("Segoe UI", 11),
            bg="#F8FAFC",
            fg=self.text_color,
            relief="flat",
            bd=0
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=11
        )

        self.message_entry.bind(
            "<Return>",
            lambda event: self.send_chat_message()
        )

        tk.Button(
            input_area,
            text="➤",
            command=self.send_chat_message,
            bg=self.primary_color,
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 16, "bold"),
            cursor="hand2",
            width=4,
            pady=5
        ).pack(
            side="right",
            padx=(8, 0)
        )

        # ==================================================
        # RIGHT MEMBER PANEL
        # ==================================================

        members_panel = tk.Frame(
            main,
            bg=self.card_color,
            width=235,
            highlightbackground="#D9E2F0",
            highlightthickness=1
        )
        members_panel.pack(
            side="right",
            fill="y",
            padx=(10, 0)
        )
        members_panel.pack_propagate(False)

        # Member heading
        tk.Label(
            members_panel,
            text="♧  Room Members",
            bg=self.card_color,
            fg=self.dark_color,
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(22, 4)
        )

        self.member_count_label = tk.Label(
            members_panel,
            text="1 member",
            bg=self.card_color,
            fg=self.muted_color,
            font=("Segoe UI", 9)
        )
        self.member_count_label.pack(
            anchor="w",
            padx=18,
            pady=(0, 12)
        )

        # Members container
        self.members_list_frame = tk.Frame(
            members_panel,
            bg=self.card_color
        )
        self.members_list_frame.pack(
            fill="x",
            padx=12,
            pady=(0, 10)
        )

        # About card
        about_card = tk.Frame(
            members_panel,
            bg="#EFF6FF"
        )
        about_card.pack(
            side="bottom",
            fill="x",
            padx=12,
            pady=15
        )

        tk.Label(
            about_card,
            text="💬",
            bg="#EFF6FF",
            fg=self.primary_color,
            font=("Segoe UI Emoji", 24)
        ).pack(pady=(12, 2))

        tk.Label(
            about_card,
            text="ChatNest",
            bg="#EFF6FF",
            fg=self.dark_color,
            font=("Segoe UI", 12, "bold")
        ).pack()

        tk.Label(
            about_card,
            text="Connect. Chat. Share.",
            bg="#EFF6FF",
            fg=self.muted_color,
            font=("Segoe UI", 9)
        ).pack(pady=(0, 12))

        self.request_rooms()
        self.message_entry.focus()

    def search_rooms(self, event=None):
        search_text = self.search_entry.get().strip().lower()

        self.room_listbox.delete(0, "end")

        for room in getattr(self, "all_rooms", []):
            if search_text in room.lower():
                self.room_listbox.insert(
                    "end",
                    f"#  {room}"
                )

    def show_profile(self):
        messagebox.showinfo(
            "ChatNest Profile",
            f"👤  Username: {self.username}\n\n"
            f"🟢  Status: Online\n\n"
            f"💬  Current room: #{self.current_room}"
        )

    def show_settings(self):
        messagebox.showinfo(
            "Settings",
            "ChatNest Settings\n\n"
            "• Notifications: Enabled\n"
            "• Emoji support: Enabled\n"
            "• Message history: Enabled"
        )


    def show_about(self):
        messagebox.showinfo(
            "About ChatNest",
            "ChatNest\n\n"
            "A real-time Python chat application.\n\n"
            "Built with:\n"
            "• Python\n"
            "• Tkinter\n"
            "• Socket Programming\n"
            "• SQLite\n\n"
            "Oasis Infobyte – Python Programming Internship"
        )


    def show_profile_menu(self):
        menu = tk.Menu(
            self.root,
            tearoff=0
        )
        menu.add_command(
            label="Logout",
            command=self.logout
        )

        try:
            menu.tk_popup(
                self.root.winfo_pointerx(),
                self.root.winfo_pointery()
            )
        finally:
            menu.grab_release()

    def logout(self):
        try:
            if self.connected:
                self.send_data({
                    "action": "logout"
                })
        except:
            pass

        self.connected = False

        self.show_login_screen()

    def display_message(
        self,
        message_id,
        username,
        message,
        timestamp
    ):
        message = convert_emojis(message)

        self.chat_text.config(
            state="normal"
        )

        message_tag = f"message_{message_id}"

        self.chat_text.insert(
            "end",
            f"[{timestamp}] ",
            message_tag
        )

        self.chat_text.insert(
            "end",
            f"{username}: ",
            message_tag
        )

        self.chat_text.insert(
            "end",
            f"{message}\n",
            message_tag
        )

        self.chat_text.config(
            state="disabled"
        )

        self.chat_text.see(
            "end"
        )
    # ======================================================
    # DISPLAY MESSAGE
    # ======================================================

    def select_message(self, event):
        index = self.chat_text.index(f"@{event.x},{event.y}")

        tags = self.chat_text.tag_names(index)

        for tag in tags:
            if tag.startswith("message_"):
                self.selected_message_id = int(
                    tag.replace("message_", "")
                )

                self.chat_text.tag_remove(
                    "selected",
                    "1.0",
                    tk.END
                )

                self.chat_text.tag_add(
                    "selected",
                    f"{index} linestart",
                    f"{index} lineend"
                )

                return
    
        self.selected_message_id = None

    def delete_selected_message(self):
        if not self.selected_message_id:
            messagebox.showwarning(
                "No Message Selected",
                "Please select a message first."
            )
            return

        confirm = messagebox.askyesno(
            "Delete Message",
            "Delete this message for you?"
        )

        if not confirm:
            return

        self.send_data({
            "action": "delete_message",
            "message_id": self.selected_message_id
        })
    # ======================================================
    # SYSTEM MESSAGE
    # ======================================================

    def display_system_message(self, message):

        self.chat_text.config(
            state="normal"
        )

        self.chat_text.insert(
            "end",
            f"• {message}\n",
            "system"
        )

        self.chat_text.config(
            state="disabled"
        )

        self.chat_text.see(
            "end"
        )

    # ======================================================
    # CLEAR CHAT
    # ======================================================

    def clear_chat(self):

        self.chat_text.config(
            state="normal"
        )

        self.chat_text.delete(
            "1.0",
            "end"
        )

        self.chat_text.config(
            state="disabled"
        )
    def clear_chat_for_user(self):
        confirm = messagebox.askyesno(
            "Clear Chat",
            "Clear all messages in this room for you?"
        )

        if not confirm:
            return

        self.send_data({
            "action": "clear_chat"
        })
    # ======================================================
    # SEND CHAT MESSAGE
    # ======================================================

    def send_chat_message(self):

        message = self.message_entry.get().strip()

        if not message:
            return

        if self.send_data({
            "action": "message",
            "message": message
        }):

            self.message_entry.delete(
                0,
                "end"
            )

    # ======================================================
    # REQUEST ROOMS
    # ======================================================

    def request_rooms(self):

        self.send_data({
            "action": "get_rooms"
        })

    # ======================================================
    # UPDATE ROOM LIST
    # ======================================================

    def update_room_list(self, rooms):
        self.all_rooms = rooms

        if hasattr(self, "search_entry"):
            self.search_rooms()
        else:
            self.room_listbox.delete(0, "end")

            for room in rooms:
                self.room_listbox.insert(
                    "end",
                    f"#  {room}"
                )

    # ======================================================
    # CREATE ROOM
    # ======================================================

    def create_new_room(self):

        room_name = simpledialog.askstring(
            "Create Room",
            "Enter room name:",
            parent=self.root
        )

        if not room_name:
            return

        room_name = room_name.strip()

        if not room_name:
            return

        self.send_data({
            "action": "create_room",
            "room": room_name
        })

    # ======================================================
    # DELETE ROOM
    # ======================================================

    def delete_current_room(self):
        if self.current_room == "General":
            messagebox.showwarning(
                "Delete Room",
                "The General room cannot be deleted."
            )
            return

        confirm = messagebox.askyesno(
            "Delete Room",
            f"Delete #{self.current_room} and all its messages?"
        )

        if not confirm:
            return

        self.send_data({
            "action": "delete_room",
            "room": self.current_room
        })

    # ======================================================
    # JOIN ROOM
    # ======================================================

    def join_selected_room(self, event=None):

        selection = self.room_listbox.curselection()

        if not selection:
            return

        room_text = self.room_listbox.get(
            selection[0]
        )

        room_name = room_text.replace(
            "#",
            ""
        ).strip()

        if room_name == self.current_room:
            return

        self.send_data({
            "action": "join_room",
            "room": room_name
        })

    # ======================================================
    # NOTIFICATION
    # ======================================================

    def notify_new_message(self, username, message):
        try:
            import ctypes

            # Get the currently active Windows window
            foreground_window = ctypes.windll.user32.GetForegroundWindow()

            # Get this application's window handle
            current_window = self.root.winfo_id()

            # Show notification only when this chat is NOT the active window
            if foreground_window != current_window:

                self.root.bell()

                notification = tk.Toplevel(self.root)
                notification.title("New Message")
                notification.geometry("350x150")
                notification.resizable(False, False)
                notification.configure(bg="white")

                notification.attributes("-topmost", True)

                tk.Label(
                    notification,
                    text="🔔 New Message",
                    bg="white",
                    fg=self.dark_color,
                    font=("Segoe UI", 14, "bold")
                ).pack(pady=(18, 5))

                tk.Label(
                    notification,
                    text=f"From: {username}",
                    bg="white",
                    fg=self.primary_color,
                    font=("Segoe UI", 10, "bold")
                ).pack()

                tk.Label(
                    notification,
                    text=convert_emojis(message),
                    bg="white",
                    fg=self.text_color,
                    font=("Segoe UI", 10),
                    wraplength=310
                ).pack(pady=5)

                notification.after(4000, notification.destroy)

        except tk.TclError:
            pass
    # ======================================================
    # CLEAR WINDOW
    # ======================================================

    def clear_window(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    # ======================================================
    # CLOSE APPLICATION
    # ======================================================

    def on_close(self):

        self.connected = False

        try:
            self.socket.shutdown(
                socket.SHUT_RDWR
            )
        except (OSError, AttributeError):
            pass

        try:
            self.socket.close()
        except (OSError, AttributeError):
            pass

        self.root.destroy()


# ==========================================================
# APPLICATION START
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ChatClient(root)

    root.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )

    root.mainloop()