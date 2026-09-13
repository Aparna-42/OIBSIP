import json
from datetime import datetime


# ==========================================================
# EMOJI SUPPORT
# ==========================================================

EMOJI_MAP = {
    ":smile:": "😄",
    ":laugh:": "😂",
    ":heart:": "❤️",
    ":love:": "😍",
    ":thumbsup:": "👍",
    ":thumbsdown:": "👎",
    ":ok:": "👌",
    ":clap:": "👏",
    ":fire:": "🔥",
    ":rocket:": "🚀",
    ":wave:": "👋",
    ":sad:": "😢",
    ":angry:": "😠",
    ":cool:": "😎",
    ":party:": "🎉",
    ":check:": "✅",
}


def convert_emojis(message):
    """Convert emoji shortcodes into Unicode emojis."""

    for shortcode, emoji in EMOJI_MAP.items():
        message = message.replace(shortcode, emoji)

    return message


# ==========================================================
# TIMESTAMP
# ==========================================================

def get_timestamp():
    """Return the current time in HH:MM format."""

    return datetime.now().strftime("%H:%M")


def format_message(username, message):
    """Format a chat message with timestamp and username."""

    timestamp = get_timestamp()
    message = convert_emojis(message)

    return f"[{timestamp}] {username}: {message}"


# ==========================================================
# NETWORK MESSAGE HELPERS
# ==========================================================

def encode_message(data):
    """Convert a Python dictionary into JSON bytes."""

    return (
        json.dumps(data)
        .encode("utf-8")
    )


def decode_message(data):
    """Convert JSON bytes into a Python dictionary."""

    return json.loads(
        data.decode("utf-8")
    )


# ==========================================================
# NETWORK CONSTANTS
# ==========================================================

HOST = "127.0.0.1"
PORT = 5555


BUFFER_SIZE = 4096