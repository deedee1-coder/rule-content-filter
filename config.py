import os

# Database file lives next to this file, no matter where the app is started from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "rules.db")

# Allowed values
MATCH_TYPES = ["contains", "startsWith", "exact"]
ACTION_TYPES = ["highlight", "tooltip"]

# Preset highlight colors (light shades so text stays readable)
HIGHLIGHT_COLORS = {
    "red": "#fca5a5",
    "blue": "#93c5fd",
    "green": "#86efac",
    "yellow": "#fde047",
    "purple": "#d8b4fe",
    "orange": "#fdba74",
}

# Limits
MAX_KEYWORD_LENGTH = 50
MAX_LABEL_LENGTH = 30
MAX_TEXT_LENGTH = 5000