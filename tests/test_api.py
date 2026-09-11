import os
import tempfile
import unittest

import database
from app import app
from config import HIGHLIGHT_COLORS, MAX_KEYWORD_LENGTH, MAX_TEXT_LENGTH


class ApiTests(unittest.TestCase):
    def setUp(self):
        # Every test gets its own empty, temporary database, so real rules are never touched
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_path = database.DATABASE_PATH
        database.DATABASE_PATH = os.path.join(self.temp_dir.name, "test.db")
        database.init_db()
        self.client = app.test_client()

    def tearDown(self):
        database.DATABASE_PATH = self.original_path
        self.temp_dir.cleanup()

    def add_rule(self, **changes):
        """Send a valid highlight rule, with any fields replaced by `changes`."""
        rule = {
            "keyword": "urgent",
            "match_type": "contains",
            "action_type": "highlight",
            "color": HIGHLIGHT_COLORS["red"],
        }
        rule.update(changes)
        return self.client.post("/api/rules", json=rule)

    def process(self, text):
        return self.client.post("/api/process", json={"text": text})

    # ---------- Creating and listing rules ----------
    def test_new_database_has_no_rules(self):
        response = self.client.get("/api/rules")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_create_highlight_rule(self):
        response = self.add_rule()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["keyword"], "urgent")
        self.assertTrue(response.get_json()["enabled"])
        self.assertEqual(len(self.client.get("/api/rules").get_json()), 1)

    def test_create_tooltip_rule(self):
        response = self.add_rule(keyword="deadline", action_type="tooltip", color=None, label="IMPORTANT")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["label"], "IMPORTANT")
        self.assertIsNone(response.get_json()["color"])

    # ---------- Rule validation ----------
    def test_keyword_is_required(self):
        response = self.add_rule(keyword="   ")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Keyword is required.")

    def test_keyword_must_be_single_word(self):
        self.assertEqual(self.add_rule(keyword="finance team").status_code, 400)

    def test_keyword_length_limit(self):
        self.assertEqual(self.add_rule(keyword="a" * (MAX_KEYWORD_LENGTH + 1)).status_code, 400)

    def test_invalid_match_type_is_rejected(self):
        self.assertEqual(self.add_rule(match_type="regex").status_code, 400)

    def test_color_must_come_from_palette(self):
        self.assertEqual(self.add_rule(color="#000000").status_code, 400)

    def test_tooltip_rule_requires_label(self):
        response = self.add_rule(action_type="tooltip", color=None, label="")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Label is required for tooltip rules.")

    def test_duplicate_rule_is_blocked_ignoring_case(self):
        self.add_rule(keyword="urgent")
        response = self.add_rule(keyword="URGENT")
        self.assertEqual(response.status_code, 409)

    def test_same_keyword_with_different_action_is_allowed(self):
        self.add_rule(keyword="urgent")
        response = self.add_rule(keyword="urgent", action_type="tooltip", color=None, label="ASAP")
        self.assertEqual(response.status_code, 201)

    # ---------- Processing text ----------
    def test_process_requires_text(self):
        response = self.process("   ")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Please enter some text to process.")

    def test_process_text_length_limit(self):
        self.assertEqual(self.process("a" * (MAX_TEXT_LENGTH + 1)).status_code, 400)

    def test_process_uses_saved_rules(self):
        self.add_rule(keyword="urgent")
        data = self.process("This is URGENT.").get_json()
        matched = [piece["text"] for piece in data["pieces"] if piece["rules"]]
        self.assertEqual(matched, ["URGENT"])
        self.assertEqual(data["summary"]["matched_words"], 1)

    # ---------- Enable/disable ----------
    def test_disabled_rules_are_ignored_when_processing(self):
        rule_id = self.add_rule(keyword="urgent").get_json()["id"]
        response = self.client.patch(f"/api/rules/{rule_id}", json={"enabled": False})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["enabled"])

        data = self.process("This is urgent.").get_json()
        self.assertEqual(data["summary"]["rules_checked"], 0)
        self.assertTrue(all(piece["rules"] == [] for piece in data["pieces"]))

    def test_enabled_must_be_true_or_false(self):
        rule_id = self.add_rule().get_json()["id"]
        response = self.client.patch(f"/api/rules/{rule_id}", json={"enabled": "no"})
        self.assertEqual(response.status_code, 400)

    def test_enable_missing_rule_returns_404(self):
        response = self.client.patch("/api/rules/999", json={"enabled": True})
        self.assertEqual(response.status_code, 404)

    # ---------- Delete ----------
    def test_delete_rule(self):
        rule_id = self.add_rule().get_json()["id"]
        self.assertEqual(self.client.delete(f"/api/rules/{rule_id}").status_code, 200)
        self.assertEqual(self.client.get("/api/rules").get_json(), [])

    def test_delete_missing_rule_returns_404(self):
        self.assertEqual(self.client.delete("/api/rules/999").status_code, 404)


if __name__ == "__main__":
    unittest.main()