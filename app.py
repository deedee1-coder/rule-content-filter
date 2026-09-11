from flask import Flask, jsonify, render_template, request

from config import HIGHLIGHT_COLORS, MAX_KEYWORD_LENGTH, MAX_LABEL_LENGTH, MAX_TEXT_LENGTH
from database import create_rule, get_all_rules, get_enabled_rules, init_db, rule_exists
from matcher import build_summary, process_text
from validation import validate_rule, validate_text

app = Flask(__name__)

# Create the database table on startup (safe to run every time)
init_db()


@app.route("/")
def home():
    return render_template(
        "index.html",
        colors=HIGHLIGHT_COLORS,
        max_keyword_length=MAX_KEYWORD_LENGTH,
        max_label_length=MAX_LABEL_LENGTH,
        max_text_length=MAX_TEXT_LENGTH,
    )


@app.route("/api/rules", methods=["GET"])
def list_rules():
    return jsonify(get_all_rules())


@app.route("/api/rules", methods=["POST"])
def add_rule():
    rule, error = validate_rule(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    if rule_exists(rule["keyword"], rule["match_type"], rule["action_type"]):
        return jsonify({"error": "This rule already exists."}), 409

    new_rule = create_rule(
        keyword=rule["keyword"],
        match_type=rule["match_type"],
        action_type=rule["action_type"],
        color=rule["color"],
        label=rule["label"],
    )
    return jsonify(new_rule), 201


@app.route("/api/process", methods=["POST"])
def process():
    text, error = validate_text(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    rules = get_enabled_rules()
    pieces = process_text(text, rules)
    return jsonify({"pieces": pieces, "summary": build_summary(pieces, rules)})


if __name__ == "__main__":
    app.run(debug=True)