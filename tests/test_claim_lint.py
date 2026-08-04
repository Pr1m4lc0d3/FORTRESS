import sys
import tempfile
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

    def test_sourced_fragment_does_not_vouch_for_rest_of_line(self):
        register = {"we are the fastest option"}
        findings = claim_lint.lint_text(
            "We are the fastest option, and it never loses your data.",
            register,
            self.config,
        )
        self.assertTrue(
            [f for f in findings if f.category == "absolute"],
            "a cleared fragment must not suppress an unsourced claim on the same line",
        )

    def test_flags_hash_one_superlative(self):
        self.assertIn("superlative", self._categories("We are #1 in the market."))


class TestCli(unittest.TestCase):
    def _write(self, directory, name, body):
        path = Path(directory) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def test_exit_zero_when_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = self._write(tmp, "draft.md", "We have 97 downloads all-time.\n")
            code = claim_lint.main([str(draft), "--register", str(FIXTURES / "truth.md")])
            self.assertEqual(0, code)

    def test_exit_one_on_error_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = self._write(tmp, "draft.md", "We have 4200 users.\n")
            code = claim_lint.main([str(draft), "--register", str(FIXTURES / "truth.md")])
            self.assertEqual(1, code)

    def test_report_mode_exits_zero_despite_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = self._write(tmp, "draft.md", "We have 4200 users.\n")
            code = claim_lint.main(
                [str(draft), "--register", str(FIXTURES / "truth.md"), "--report"]
            )
            self.assertEqual(0, code)

    def test_warn_only_findings_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = self._write(tmp, "draft.md", "It never breaks.\n")
            code = claim_lint.main([str(draft), "--register", str(FIXTURES / "truth.md")])
            self.assertEqual(0, code)

    def test_missing_register_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = self._write(tmp, "draft.md", "Anything.\n")
            code = claim_lint.main([str(draft), "--register", str(Path(tmp) / "nope.md")])
            self.assertEqual(2, code)

    def test_directory_target_scans_markdown_recursively(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "posts/a.md", "Clean: 97 downloads all-time.\n")
            self._write(tmp, "posts/b.md", "We have 4200 users.\n")
            code = claim_lint.main([tmp, "--register", str(FIXTURES / "truth.md")])
            self.assertEqual(1, code)


if __name__ == "__main__":
    unittest.main()
