# Rule-Based Content Filter

A small web application for creating text-matching rules and applying them to a block of text. Matching words are highlighted in a chosen color or tagged with a label, and a summary shows which rules matched.

Built as an internship assignment for AnchorzUp.

## Features

**Required by the assignment**

- Create rules and view saved rules
- Match types: `contains`, `startsWith`, `exact`
- Actions: `highlight` (with a selected color) and `tooltip` (a label shown next to the word)
- Rules are stored in a SQL database (SQLite) and reused
- Text is sent to the backend, processed against all rules, and displayed with highlights, labels, and a per-rule match summary
- Multiple rules can apply to the same word

**Optional improvements implemented**

- Delete rules
- Enable/disable rules (disabled rules are ignored when processing)
- Validation with clear error messages on both frontend and backend
- Automated tests for the matching logic and the API

## Tech stack

| Part | Technology |
|---|---|
| Frontend | HTML, CSS, vanilla JavaScript |
| Backend | Python 3, Flask |
| Database | SQLite (through Python's built-in `sqlite3`, plain parameterized SQL) |
| Tests | Python's built-in `unittest` |

## Project structure

```
rule-content-filter/
├── app.py              Flask app: page route and API endpoints
├── config.py           Settings: limits, match/action types, color palette, database path
├── database.py         SQLite connection, table setup, and all SQL queries
├── matcher.py          Text matching logic (no Flask or database code)
├── validation.py       Input validation for rules and text
├── requirements.txt    Python dependencies
├── templates/
│   └── index.html      The single page
├── static/
│   ├── app.js          Frontend logic: loads rules, sends requests, renders results
│   └── style.css       Styles
└── tests/
    ├── test_matcher.py Tests for the matching rules
    └── test_api.py     Tests for the API (uses a temporary database)
```

## Getting started

**Requirements:** Python 3.10 or newer, Git.

1. Clone the repository:

   ```
   git clone https://github.com/deedee1-coder/rule-content-filter.git
   cd rule-content-filter
   ```

2. Create and activate a virtual environment:

   Windows (PowerShell):
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell says running scripts is disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

   macOS / Linux:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```
   python -m pip install -r requirements.txt
   ```

4. Start the app:

   ```
   python app.py
   ```

5. Open **http://127.0.0.1:5000** in a browser.

The SQLite database file (`rules.db`) is created automatically on first start. It is not committed to Git, so a fresh clone starts with no rules.

## Running the tests

```
python -m unittest discover -s tests -v
```

The API tests use a temporary database, so they never change your saved rules.

## How it works

1. The browser loads the page from Flask. `app.js` requests the saved rules from `GET /api/rules` and shows them in the table.
2. Creating a rule sends the form data to `POST /api/rules`. The backend validates it, saves it with a parameterized `INSERT`, and returns the new rule.
3. Clicking **Process text** sends the text to `POST /api/process`. The backend loads the enabled rules (oldest first), splits the text into words and non-word pieces, checks every word against every rule, and returns JSON.
4. `app.js` builds the result from that JSON using DOM elements and `textContent`. The backend never returns HTML, so user text can never be run as code in the page.

## Matching behavior

The assignment does not define every edge case. The following are **implementation decisions made for this project**, not requirements stated in the assignment.

| Decision | Behavior |
|---|---|
| Case | Matching ignores upper/lower case. `urgent` matches `Urgent` and `URGENT`. The original capitalization is always kept in the output. |
| Whole words | Rules are checked against individual words, and whole words are marked in the output. |
| Single-word keywords | Keywords must be a single word (no spaces). This keeps the first version simple and reliable; phrases like `finance team` are not supported. |
| Keyword characters | Keywords may contain letters and numbers, with an apostrophe or hyphen inside the word (`don't`, `follow-up`). A keyword like `urgent!` is rejected, because words in the text never include edge punctuation, so it could never match. |
| Punctuation | Punctuation at the edges of a word is ignored: `urgent.` matches `urgent`. Apostrophes and hyphens inside a word keep it as one word: `don't`, `follow-up`. |
| Multiple rules on one word | All enabled matching rules apply. Every tooltip label is shown. If several highlight rules match, the **oldest** highlight rule's color is used. Hovering a word lists every rule that matched it. |
| Disabled rules | Ignored completely during processing. |
| Duplicates | A rule is rejected if a rule with the same keyword (ignoring case), match type, and action already exists. |

**Match types**, checked against each word:

| Match type | Meaning | Keyword `dead` vs word `deadline` |
|---|---|---|
| `contains` | The keyword appears anywhere inside the word | matches |
| `startsWith` | The word begins with the keyword | matches |
| `exact` | The whole word equals the keyword | no match |

## Validation and limits

Limits are defined once in `config.py` and passed to the page, so they only need to be changed in one place.

| Field | Rule |
|---|---|
| Keyword | Required, one word (letters and numbers, with an optional inner apostrophe or hyphen), at most 50 characters |
| Label (tooltip rules) | Required, at most 30 characters |
| Color (highlight rules) | Must be one of the preset palette colors |
| Input text | Required, at most 5,000 characters |

The frontend performs quick checks for immediate feedback. The backend validates every request again, because the API can be called without the UI.

## API

All endpoints accept and return JSON. Errors are returned as `{"error": "message"}`.

| Method | Endpoint | Purpose | Success | Errors |
|---|---|---|---|---|
| `GET` | `/api/rules` | List all rules (oldest first) | 200 | |
| `POST` | `/api/rules` | Create a rule | 201 | 400 invalid, 409 duplicate |
| `PATCH` | `/api/rules/<id>` | Enable or disable a rule | 200 | 400 invalid, 404 not found |
| `DELETE` | `/api/rules/<id>` | Delete a rule | 200 | 404 not found |
| `POST` | `/api/process` | Process text with the enabled rules | 200 | 400 invalid |

**Create a rule** (`POST /api/rules`):

```json
{ "keyword": "urgent", "match_type": "contains", "action_type": "highlight", "color": "#fca5a5" }
```

```json
{ "keyword": "deadline", "match_type": "contains", "action_type": "tooltip", "label": "IMPORTANT" }
```

**Enable or disable** (`PATCH /api/rules/<id>`):

```json
{ "enabled": false }
```

**Process text** (`POST /api/process`):

Request:
```json
{ "text": "The deadline is urgent." }
```

Response, with saved rules `urgent` (id 1), `meeting` (id 2), and `deadline` (id 3). Rule objects are shortened here; the API returns all rule fields.
```json
{
  "pieces": [
    { "text": "The", "rules": [] },
    { "text": " ", "rules": [] },
    { "text": "deadline", "rules": [{ "id": 3, "keyword": "deadline", "action_type": "tooltip", "label": "IMPORTANT" }] },
    { "text": " ", "rules": [] },
    { "text": "is", "rules": [] },
    { "text": " ", "rules": [] },
    { "text": "urgent", "rules": [{ "id": 1, "keyword": "urgent", "action_type": "highlight", "color": "#fca5a5" }] },
    { "text": ".", "rules": [] }
  ],
  "summary": {
    "matched_words": 2,
    "rules_checked": 3,
    "rules_matched": 2,
    "rule_counts": [
      { "rule": { "id": 1, "keyword": "urgent" }, "count": 1 },
      { "rule": { "id": 2, "keyword": "meeting" }, "count": 0 },
      { "rule": { "id": 3, "keyword": "deadline" }, "count": 1 }
    ]
  }
}
```

Joining the `text` of all pieces gives back the original input exactly.

## Database

Table `rules`:

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER, primary key | Unique rule id. A lower id means an older rule. |
| `keyword` | TEXT, not null | The word to match |
| `match_type` | TEXT, not null | `contains`, `startsWith`, or `exact` |
| `action_type` | TEXT, not null | `highlight` or `tooltip` |
| `color` | TEXT | Highlight color (highlight rules only) |
| `label` | TEXT | Label text (tooltip rules only) |
| `enabled` | INTEGER, not null, default 1 | `1` = enabled, `0` = disabled |

All queries use parameterized SQL (`?` placeholders) so user input is never inserted directly into SQL strings.

## Limitations and possible improvements

- Keywords are single words; matching phrases would need a different matching approach.
- Rules cannot be edited yet (delete and re-create instead).
- No rule priority setting; highlight conflicts are resolved by rule age.
- Flask's built-in development server is used; a production deployment would use a WSGI server such as Waitress or Gunicorn.
- No authentication; all users share the same rules.
