import re

# A word is a run of letters/digits. An apostrophe or hyphen INSIDE a word keeps it
# as one word ("don't", "follow-up"). Punctuation at the edges is not part of the word.
WORD_PATTERN = re.compile(r"\w+(?:['’-]\w+)*")


def split_into_pieces(text):
    """
    Split text into (piece, is_word) pairs.
    Example: "Hi, team!" -> [("Hi", True), (", ", False), ("team", True), ("!", False)]
    Joining all pieces gives back the original text exactly.
    """
    pieces = []
    position = 0

    for match in WORD_PATTERN.finditer(text):
        if match.start() > position:
            pieces.append((text[position:match.start()], False))  # spaces/punctuation before the word
        pieces.append((match.group(), True))
        position = match.end()

    if position < len(text):
        pieces.append((text[position:], False))  # anything after the last word

    return pieces


def word_matches_rule(word, rule):
    """Check one word against one rule. Matching ignores upper/lower case."""
    word = word.lower()
    keyword = rule["keyword"].lower()

    if not keyword:
        return False  # an empty keyword must never match everything

    if rule["match_type"] == "contains":
        return keyword in word
    if rule["match_type"] == "startsWith":
        return word.startswith(keyword)
    if rule["match_type"] == "exact":
        return word == keyword

    return False


def process_text(text, rules):
    """
    Check every word against every rule.
    Returns a list of pieces in the original order, each with the rules it matched:
    [{"text": "The ", "rules": []}, {"text": "meeting", "rules": [rule]}, ...]
    Matched rules keep the order they were given in (oldest first).
    """
    result = []

    for piece, is_word in split_into_pieces(text):
        matched_rules = []

        if is_word:
            for rule in rules:
                if word_matches_rule(piece, rule):
                    matched_rules.append(rule)

        result.append({"text": piece, "rules": matched_rules})

    return result


def build_summary(pieces, rules):
    """Count how many words matched, and how many words each rule matched."""
    counts = {rule["id"]: 0 for rule in rules}
    matched_words = 0

    for piece in pieces:
        if piece["rules"]:
            matched_words += 1
        for rule in piece["rules"]:
            counts[rule["id"]] += 1

    return {
        "matched_words": matched_words,
        "rules_checked": len(rules),
        "rules_matched": sum(1 for count in counts.values() if count > 0),
        "rule_counts": [{"rule": rule, "count": counts[rule["id"]]} for rule in rules],
    }