import unittest

from matcher import build_summary, process_text, split_into_pieces, word_matches_rule


def make_rule(keyword, match_type, rule_id=1):
    """Build a rule dictionary shaped like the ones from the database."""
    return {
        "id": rule_id,
        "keyword": keyword,
        "match_type": match_type,
        "action_type": "highlight",
        "color": "#fca5a5",
        "label": None,
        "enabled": True,
    }


def matched_words(text, rules):
    """Return only the pieces of text that matched at least one rule."""
    return [piece["text"] for piece in process_text(text, rules) if piece["rules"]]


class MatchTypeTests(unittest.TestCase):
    def test_keyword_line_only_matches_deadline_with_contains(self):
        self.assertTrue(word_matches_rule("deadline", make_rule("line", "contains")))
        self.assertFalse(word_matches_rule("deadline", make_rule("line", "startsWith")))
        self.assertFalse(word_matches_rule("deadline", make_rule("line", "exact")))

    def test_keyword_dead_matches_deadline_with_contains_and_starts_with(self):
        self.assertTrue(word_matches_rule("deadline", make_rule("dead", "contains")))
        self.assertTrue(word_matches_rule("deadline", make_rule("dead", "startsWith")))
        self.assertFalse(word_matches_rule("deadline", make_rule("dead", "exact")))

    def test_keyword_deadline_matches_deadline_with_all_types(self):
        for match_type in ["contains", "startsWith", "exact"]:
            self.assertTrue(word_matches_rule("Deadline", make_rule("deadline", match_type)))

    def test_matching_ignores_case(self):
        self.assertTrue(word_matches_rule("Urgent", make_rule("urgent", "exact")))
        self.assertTrue(word_matches_rule("urgent", make_rule("URGENT", "exact")))

    def test_empty_keyword_never_matches(self):
        self.assertFalse(word_matches_rule("anything", make_rule("", "contains")))


class TextProcessingTests(unittest.TestCase):
    def test_pieces_join_back_to_original_text(self):
        text = "The deadline is urgent.\n\nFollow-up: don't wait!"
        joined = "".join(piece for piece, is_word in split_into_pieces(text))
        self.assertEqual(joined, text)

    def test_punctuation_at_word_edges_is_ignored(self):
        self.assertEqual(matched_words("The deadline is urgent.", [make_rule("urgent", "exact")]), ["urgent"])

    def test_apostrophes_and_hyphens_stay_inside_words(self):
        pieces = split_into_pieces("don't follow-up")
        words = [piece for piece, is_word in pieces if is_word]
        self.assertEqual(words, ["don't", "follow-up"])

    def test_original_capitalization_is_kept(self):
        self.assertEqual(matched_words("URGENT: reply now", [make_rule("urgent", "exact")]), ["URGENT"])

    def test_multiple_rules_on_same_word_are_all_kept_in_order(self):
        older = make_rule("dead", "startsWith", rule_id=1)
        newer = make_rule("deadline", "exact", rule_id=2)
        result = process_text("deadline", [older, newer])
        self.assertEqual([rule["id"] for rule in result[0]["rules"]], [1, 2])

    def test_no_matches_returns_text_without_rules(self):
        result = process_text("Nothing to see here.", [make_rule("urgent", "contains")])
        self.assertTrue(all(piece["rules"] == [] for piece in result))

    def test_assignment_example(self):
        rules = [
            make_rule("urgent", "contains", rule_id=1),
            make_rule("meeting", "contains", rule_id=2),
            make_rule("deadline", "contains", rule_id=3),
        ]
        text = "The meeting with the finance team is tomorrow. The deadline is urgent."
        self.assertEqual(matched_words(text, rules), ["meeting", "deadline", "urgent"])

    def test_summary_counts_words_and_rules(self):
        rules = [make_rule("dead", "startsWith", rule_id=1), make_rule("urgent", "exact", rule_id=2)]
        pieces = process_text("deadline deadlines urgent", rules)
        summary = build_summary(pieces, rules)
        self.assertEqual(summary["matched_words"], 3)
        self.assertEqual(summary["rules_matched"], 2)
        self.assertEqual([item["count"] for item in summary["rule_counts"]], [2, 1])


if __name__ == "__main__":
    unittest.main()