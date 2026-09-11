from flask import Flask, jsonify, render_template, request

from database import create_rule, get_all_rules, init_db

app = Flask(__name__)

# Create the database table on startup (safe to run every time)
init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/rules", methods=["GET"])
def list_rules():
    return jsonify(get_all_rules())


@app.route("/api/rules", methods=["POST"])
def add_rule():
    data = request.get_json(silent=True) or {}
    # Validation is added in Stage 10
    rule = create_rule(
        keyword=data.get("keyword"),
        match_type=data.get("match_type"),
        action_type=data.get("action_type"),
        color=data.get("color"),
        label=data.get("label"),
    )
    return jsonify(rule), 201


if __name__ == "__main__":
    app.run(debug=True)