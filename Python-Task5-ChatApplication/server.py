import socket
import threading

from database import (
    initialize_database,
    authenticate_user,
    register_user,
    get_rooms,
    create_room,
    get_room_id,
    save_message,
    get_message_history,
    hide_message_for_user,
    clear_chat_for_user
)

from chat_utils import (
    HOST,
    PORT,
    BUFFER_SIZE,
    encode_message,
    decode_message,
)


clients = {}
clients_lock = threading.Lock()


# ==========================================================
# SEND DATA
# ==========================================================

def send_data(client_socket, data):
    try:
        client_socket.sendall(encode_message(data))
        return True
    except (ConnectionResetError, BrokenPipeError, OSError):
        return False


# ==========================================================
# BROADCAST MESSAGE
# ==========================================================

def broadcast(room_name, data, exclude=None):
    with clients_lock:
        room_clients = [
            client_socket
            for client_socket, info in clients.items()
            if info["room"] == room_name
            and client_socket != exclude
        ]

    for client_socket in room_clients:
        if not send_data(client_socket, data):
            remove_client(client_socket)

# ==========================================================
# BROADCAST ROOM MEMBERS
# ==========================================================

def broadcast_room_members(room_name):
    with clients_lock:
        unique_members = {}

        for info in clients.values():
            if info["room"] == room_name:
                username = info["username"]
                unique_members[username] = {
                    "username": username,
                    "status": "online"
                }

        members = list(unique_members.values())

        room_clients = [
            client_socket
            for client_socket, info in clients.items()
            if info["room"] == room_name
        ]

    data = {
        "type": "room_members",
        "room": room_name,
        "members": members,
        "count": len(members)
    }

    for client_socket in room_clients:
        send_data(client_socket, data)
# ==========================================================
# SEND ROOM HISTORY
# ==========================================================

def send_history(client_socket, room_name, username):
    history = get_message_history(
        room_name,
        username
    )

    messages = []

    for message_id, msg_username, message, timestamp in history:
        messages.append({
            "id": message_id,
            "username": msg_username,
            "message": message,
            "timestamp": timestamp
        })

    send_data(
        client_socket,
        {
            "type": "history",
            "messages": messages
        }
    )
# ==========================================================
# REMOVE CLIENT
# ==========================================================

def remove_client(client_socket):
    with clients_lock:
        client_info = clients.pop(client_socket, None)

    try:
        client_socket.close()
    except OSError:
        pass

    if client_info:
        username = client_info["username"]
        room = client_info["room"]

        broadcast(
            room,
            {
                "type": "system",
                "message": f"{username} left the room."
            }
        )

        broadcast_room_members(room)

        print(f"{username} disconnected.")


# ==========================================================
# CLIENT HANDLER
# ==========================================================

def handle_client(client_socket, address):

    username = None
    current_room = "General"

    try:

        # --------------------------------------------------
        # LOGIN / REGISTRATION
        # --------------------------------------------------

        while True:

            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                return

            request = decode_message(data)

            action = request.get("action")

            # Registration
            if action == "register":
                username = request.get("username", "").strip()
                password = request.get("password", "")

                if not username or not password:
                    send_data(
                        client_socket,
                        {
                            "type": "auth",
                            "success": False,
                            "message": "Username and password are required."
                        }
                    )
                    continue

                success, message = register_user(
                    username,
                    password
                )

                if success:
                    current_room = "General"

                    with clients_lock:
                        clients[client_socket] = {
                            "username": username,
                            "room": current_room
                        }

                    send_data(
                        client_socket,
                        {
                            "type": "auth",
                            "success": True,
                            "message": "Registration successful.",
                            "username": username,
                            "room": current_room
                        }
                    )

                    # Load existing General room history
                    send_history(
                        client_socket,
                        current_room,
                        username

                    )

                    broadcast_room_members(current_room)

                    print(
                        f"{username} registered and connected from {address}"
                    )

                    break

                else:
                    send_data(
                        client_socket,
                        {
                            "type": "auth",
                            "success": False,
                            "message": message
                        }
                    )

            # Login
            elif action == "login":

                username = request.get("username", "").strip()
                password = request.get("password", "")

                if authenticate_user(username, password):

                    with clients_lock:
                        clients[client_socket] = {
                            "username": username,
                            "room": current_room
                        }

                    send_data(
                        client_socket,
                        {
                            "type": "auth",
                            "success": True,
                            "message": "Login successful.",
                            "username": username,
                            "room": current_room
                        }
                    )

                    send_history(
                        client_socket,
                        current_room,
                        username
                    )

                    broadcast(
                        current_room,
                        {
                            "type": "system",
                            "message": f"{username} joined the room."
                        },
                        exclude=client_socket
                    )
                    broadcast_room_members(current_room)
                    print(
                        f"{username} connected from {address}"
                    )

                    break

                else:

                    send_data(
                        client_socket,
                        {
                            "type": "auth",
                            "success": False,
                            "message": "Invalid username or password."
                        }
                    )

        # --------------------------------------------------
        # MAIN CHAT LOOP
        # --------------------------------------------------

        while True:

            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                break

            request = decode_message(data)

            action = request.get("action")

            # ------------------------------------------------
            # SEND MESSAGE
            # ------------------------------------------------

            if action == "message":

                message = request.get("message", "").strip()

                if not message:
                    continue

                message_id = save_message(
                    current_room,
                    username,
                    message
                )

                from datetime import datetime

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                broadcast(
                    current_room,
                    {
                        "type": "message",
                        "id": message_id,
                        "room": current_room,
                        "username": username,
                        "message": message,
                        "timestamp": timestamp
                    }
                )


            # ------------------------------------------------
            # LOGOUT
            # ------------------------------------------------

            elif action == "logout":

                remove_client(client_socket)

                break

            # ------------------------------------------------
            # DELETE MESSAGE
            # ------------------------------------------------

            elif action == "delete_message":

                message_id = request.get("message_id")

                if not message_id:
                    send_data(
                        client_socket,
                        {
                            "type": "delete_result",
                            "success": False,
                            "message": "No message selected."
                        }
                    )
                    continue

                success = hide_message_for_user(
                    username,
                    message_id
                )

                send_data(
                    client_socket,
                    {
                        "type": "delete_result",
                        "success": success,
                        "message": (
                            "Message deleted for you."
                            if success
                            else "Unable to delete message."
                        )
                    }
                )
            # ------------------------------------------------
            # CLEAR CHAT
            # ------------------------------------------------

            elif action == "clear_chat":

                success = clear_chat_for_user(
                    username,
                    current_room
                )

                send_data(
                    client_socket,
                    {
                        "type": "clear_result",
                        "success": success,
                        "message": (
                            "Chat cleared for you."
                            if success
                            else "Unable to clear chat."
                        )
                    }
                )

            
            # ------------------------------------------------
            # GET ROOMS
            # ------------------------------------------------

            elif action == "get_rooms":

                rooms = get_rooms()

                send_data(
                    client_socket,
                    {
                        "type": "rooms",
                        "rooms": rooms
                    }
                )

            # ------------------------------------------------
            # CREATE ROOM
            # ------------------------------------------------

            elif action == "create_room":

                room_name = request.get(
                    "room",
                    ""
                ).strip()

                if not room_name:
                    send_data(
                        client_socket,
                        {
                            "type": "room_result",
                            "success": False,
                            "message": "Room name cannot be empty."
                        }
                    )
                    continue

                success, message = create_room(
                    room_name
                )

                send_data(
                    client_socket,
                    {
                        "type": "room_result",
                        "success": success,
                        "message": message
                    }
                )

            # ------------------------------------------------
            # JOIN ROOM
            # ------------------------------------------------

            elif action == "join_room":

                room_name = request.get(
                    "room",
                    ""
                ).strip()

                if room_name not in get_rooms():

                    send_data(
                        client_socket,
                        {
                            "type": "room_result",
                            "success": False,
                            "message": "Room does not exist."
                        }
                    )

                    continue

                old_room = current_room

                broadcast(
                    old_room,
                    {
                        "type": "system",
                        "message": f"{username} left the room."
                    },
                    exclude=client_socket
                )

                current_room = room_name

                with clients_lock:
                    if client_socket in clients:
                        clients[client_socket]["room"] = current_room
                broadcast_room_members(old_room)
                send_data(
                    client_socket,
                    {
                        "type": "room_changed",
                        "room": current_room
                    }
                )

                send_history(
                    client_socket,
                    current_room,
                    username
                )

                broadcast(
                    current_room,
                    {
                        "type": "system",
                        "message": f"{username} joined the room."
                    },
                    exclude=client_socket
                )
                broadcast_room_members(current_room)
    except (
        ConnectionResetError,
        BrokenPipeError,
        ConnectionAbortedError,
        OSError,
        ValueError
    ):
        pass

    finally:
        remove_client(client_socket)


# ==========================================================
# START SERVER
# ==========================================================

def start_server():

    initialize_database()

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen(10)

    print("=" * 50)
    print("Oasis Infobyte - Chat Application Server")
    print("=" * 50)
    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for clients...")
    print("=" * 50)

    while True:

        client_socket, address = (
            server_socket.accept()
        )

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, address),
            daemon=True
        )

        thread.start()


if __name__ == "__main__":
    start_server()