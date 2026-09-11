from config import (
    ACTION_TYPES,
    HIGHLIGHT_COLORS,
    MATCH_TYPES,
    MAX_KEYWORD_LENGTH,
    MAX_LABEL_LENGTH,
    MAX_TEXT_LENGTH,
)
from matcher import WORD_PATTERN


def validate_rule(data):
    """
    Check the data sent for a new rule.
    Returns (rule, None) when valid, or (None, error_message) when not.
    """
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    keyword = data.get("keyword")
    match_type = data.get("match_type")
    action_type = data.get("action_type")

    # Keyword
    if not isinstance(keyword, str) or not keyword.strip():
        return None, "Keyword is required."
    keyword = keyword.strip()

    if len(keyword) > MAX_KEYWORD_LENGTH:
        return None, f"Keyword can be at most {MAX_KEYWORD_LENGTH} characters."
    if any(character.isspace() for character in keyword):
        return None, "Keyword must be a single word."
    if not WORD_PATTERN.fullmatch(keyword):
        return None, "Keyword can only contain letters and numbers, with an apostrophe or hyphen inside the word."

    # Match type and action
    if match_type not in MATCH_TYPES:
        return None, "Match type must be contains, startsWith, or exact."
    if action_type not in ACTION_TYPES:
        return None, "Action must be highlight or tooltip."

    # Color for highlight rules, label for tooltip rules
    color = None
    label = None

    if action_type == "highlight":
        color = data.get("color")
        if color not in HIGHLIGHT_COLORS.values():
            return None, "Please choose a color."
    else:
        label = data.get("label")
        if not isinstance(label, str) or not label.strip():
            return None, "Label is required for tooltip rules."
        label = label.strip()
        if len(label) > MAX_LABEL_LENGTH:
            return None, f"Label can be at most {MAX_LABEL_LENGTH} characters."

    rule = {
        "keyword": keyword,
        "match_type": match_type,
        "action_type": action_type,
        "color": color,
        "label": label,
    }
    return rule, None


def validate_text(data):
    """
    Check the data sent for processing.
    Returns (text, None) when valid, or (None, error_message) when not.
    """
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    text = data.get("text")

    if not isinstance(text, str) or not text.strip():
        return None, "Please enter some text to process."
    if len(text) > MAX_TEXT_LENGTH:
        return None, f"Text can be at most {MAX_TEXT_LENGTH:,} characters."

    return text, None