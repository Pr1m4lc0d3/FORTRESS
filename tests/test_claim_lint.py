import contextlib
import io
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

    def test_number_not_sourced_by_bare_token_in_different_context(self):
        findings = claim_lint.lint_text(
            "Our platform serves 97 million requests a day.", self.register, self.config
        )
        self.assertTrue(
            [f for f in findings if f.category == "number"],
            "a cleared '97 downloads all-time' must not source '97 million requests'",
        )

    def test_unclosed_fence_does_not_blank_rest_of_document(self):
        text = "Here is code:\n\n```\nport = 8080\n\nWe have 4200 active users.\n"
        with contextlib.redirect_stderr(io.StringIO()) as err:
            findings = claim_lint.lint_text(text, self.register, self.config)
        spans = [f.span for f in findings if f.category == "number"]
        self.assertIn("4200", spans, "an unterminated fence must not disable the scan")
        self.assertIn("unterminated code fence", err.getvalue())

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


class TestRegisterSchema(unittest.TestCase):
    def test_cleared_entry_without_source_suffix_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            register_path = Path(tmp) / "truth.md"
            register_path.write_text(
                "# Truth Register\n\n## Cleared\n\n- 40,000 users\n", encoding="utf-8"
            )
            with contextlib.redirect_stderr(io.StringIO()) as err:
                register = claim_lint.load_register(register_path)
            self.assertEqual(set(), register)
            self.assertIn("malformed Cleared entry", err.getvalue())
            findings = claim_lint.lint_text(
                "We serve 40,000 users.", register, claim_lint.DEFAULT_CONFIG
            )
            self.assertTrue(
                [f for f in findings if f.category == "number"],
                "an unsourced register entry must not source anything",
            )

    def test_cleared_entry_with_source_suffix_is_accepted(self):
        register = claim_lint.load_register(FIXTURES / "truth.md")
        self.assertTrue(register)


class TestConfigGate(unittest.TestCase):
    def _run_with_config(self, body):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "truth.config.json"
            config_path.write_text(body, encoding="utf-8")
            draft = Path(tmp) / "draft.md"
            draft.write_text("We have 4200 users.\n", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()) as err:
                code = claim_lint.main(
                    [
                        str(draft),
                        "--register",
                        str(FIXTURES / "truth.md"),
                        "--config",
                        str(config_path),
                    ]
                )
            return code, err.getvalue()

    def test_catch_all_ignore_is_refused(self):
        code, err = self._run_with_config('{"ignore": [".*"]}')
        self.assertEqual(2, code)
        self.assertIn("catch-all ignore pattern", err)
        self.assertIn("may not disable detection", err)

    def test_all_warn_severity_is_refused(self):
        code, err = self._run_with_config(
            '{"severity": {"number": "warn", "superlative": "warn",'
            ' "comparative": "warn", "testimonial": "warn", "absolute": "warn"}}'
        )
        self.assertEqual(2, code)
        self.assertIn("never fail", err)

    def test_invalid_severity_value_is_refused(self):
        code, err = self._run_with_config('{"severity": {"number": "eror"}}')
        self.assertEqual(2, code)
        self.assertIn("invalid severity 'eror'", err)

    def test_shipped_config_is_accepted(self):
        shipped = (ASSETS / "truth.config.json").read_text(encoding="utf-8")
        code, err = self._run_with_config(shipped)
        self.assertEqual(1, code, err)

    def test_config_is_echoed_on_every_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text("All clear here.\n", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()) as err:
                code = claim_lint.main(
                    [str(draft), "--register", str(FIXTURES / "truth.md")]
                )
            self.assertEqual(0, code)
            echoed = err.getvalue()
            self.assertIn("claim-lint: config: built-in defaults", echoed)
            self.assertIn("number=error", echoed)
            self.assertIn("absolute=warn", echoed)
            self.assertIn("ignore patterns: 1", echoed)


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
