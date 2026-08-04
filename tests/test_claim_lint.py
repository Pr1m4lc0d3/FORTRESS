import sys
import unittest
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "skills" / "fortress-truth" / "assets"
sys.path.insert(0, str(ASSETS))

import claim_lint  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestNumberDetection(unittest.TestCase):
    def setUp(self):
        self.config = claim_lint.DEFAULT_CONFIG
        self.register = claim_lint.load_register(FIXTURES / "truth.md")

    def test_flags_number_not_in_register(self):
        findings = claim_lint.lint_text(
            "We have 4200 active users.", self.register, self.config
        )
        categories = [f.category for f in findings]
        self.assertIn("number", categories)

    def test_passes_number_present_in_register(self):
        findings = claim_lint.lint_text(
            "We have 97 downloads all-time.", self.register, self.config
        )
        self.assertEqual([], [f for f in findings if f.category == "number"])

    def test_ignores_four_digit_years(self):
        findings = claim_lint.lint_text(
            "Founded in 2024 and still going.", self.register, self.config
        )
        self.assertEqual([], [f for f in findings if f.category == "number"])

    def test_ignores_numbers_inside_fenced_code(self):
        text = "Here is code:\n\n```\nport = 8080\n```\n"
        findings = claim_lint.lint_text(text, self.register, self.config)
        self.assertEqual([], [f for f in findings if f.category == "number"])

    def test_ignores_numbers_inside_urls(self):
        findings = claim_lint.lint_text(
            "See https://example.com/report/2311 for detail.",
            self.register,
            self.config,
        )
        self.assertEqual([], [f for f in findings if f.category == "number"])

    def test_reports_correct_line_number(self):
        text = "First line is clean.\nSecond line claims 5000 users.\n"
        findings = [
            f
            for f in claim_lint.lint_text(text, self.register, self.config)
            if f.category == "number"
        ]
        self.assertEqual(1, len(findings))
        self.assertEqual(2, findings[0].line)

    def test_number_does_not_match_inside_larger_number(self):
        register = {"pricing is 79 / 149 / 249 one-time"}
        findings = claim_lint.lint_text("It costs 49 dollars.", register, self.config)
        self.assertTrue(
            [f for f in findings if f.category == "number"],
            "49 must not be considered sourced by 149 or 249",
        )


class TestClaimCategories(unittest.TestCase):
    def setUp(self):
        self.config = claim_lint.DEFAULT_CONFIG
        self.register = claim_lint.load_register(FIXTURES / "truth.md")

    def _categories(self, text):
        return [f.category for f in claim_lint.lint_text(text, self.register, self.config)]

    def test_flags_superlative(self):
        self.assertIn("superlative", self._categories("We are the fastest option."))

    def test_flags_comparative(self):
        self.assertIn("comparative", self._categories("It is better than the rest."))

    def test_flags_testimonial_quote(self):
        text = '"This product completely changed how our team works."'
        self.assertIn("testimonial", self._categories(text))

    def test_absolute_is_warning_not_error(self):
        findings = claim_lint.lint_text(
            "It never loses your data.", self.register, self.config
        )
        absolutes = [f for f in findings if f.category == "absolute"]
        self.assertTrue(absolutes)
        self.assertEqual("warn", absolutes[0].severity)

    def test_superlative_passes_when_sourced(self):
        register = {"we are the only tool with a signed record"}
        findings = claim_lint.lint_text(
            "We are the only tool with a signed record.", register, self.config
        )
        self.assertEqual([], [f for f in findings if f.category == "superlative"])


if __name__ == "__main__":
    unittest.main()
