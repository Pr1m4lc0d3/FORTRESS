import contextlib
import io
import json
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

    # Round 3: this class previously held test_ignores_four_digit_years, which
    # asserted that "Founded in 2024 and still going." produced no number
    # finding. It was REPLACED, not deleted. The ignore it encoded
    # (\b(?:19|20)\d{2}\b) exempted every integer from 1900 to 2099, so "Over
    # 2000 people signed up." passed clean — a false negative on exactly the
    # shape an invented marketing stat takes. A bare year is now treated as a
    # claim; only genuine date FORMATS are ignored. The four tests below encode
    # the replacement behaviour.

    def test_bare_year_is_a_claim_and_is_flagged(self):
        findings = claim_lint.lint_text(
            "Founded in 2024 and still going.", self.register, self.config
        )
        self.assertTrue(
            [f for f in findings if f.category == "number"],
            "a bare year is a factual assertion and belongs in the register",
        )

    def test_iso_date_is_ignored(self):
        findings = claim_lint.lint_text(
            "Released 2026-08-04.", self.register, self.config
        )
        self.assertEqual([], [f for f in findings if f.category == "number"])

    def test_written_date_is_ignored(self):
        for draft in (
            "Released January 2024 to the public.",
            "Released 12 March 2026 to the public.",
            "Released March 12, 2026 to the public.",
        ):
            with self.subTest(draft=draft):
                findings = claim_lint.lint_text(draft, self.register, self.config)
                self.assertEqual([], [f for f in findings if f.category == "number"])

    def test_round_number_in_year_range_is_flagged(self):
        for draft in ("Over 2000 people signed up.", "We processed 1999 orders."):
            with self.subTest(draft=draft):
                findings = claim_lint.lint_text(draft, self.register, self.config)
                self.assertTrue(
                    [f for f in findings if f.category == "number"],
                    "a round number is not exempt for landing in the year range",
                )

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

    def test_number_at_end_of_line_is_not_sourced_by_bare_token(self):
        register = {"pricing is 79 / 149 / 249 one-time — source: pricing page"}
        findings = claim_lint.lint_text(
            "Enterprise seats start at 79", register, self.config
        )
        self.assertTrue(
            [f for f in findings if f.category == "number"],
            "a span ending its line must not collapse to the bare token",
        )

    def test_number_at_end_of_line_falls_back_to_whole_line(self):
        for draft in (
            "Peak throughput, requests per second: 97",
            "Our concurrent connection ceiling is 97",
            "# 97",
            "- 97",
        ):
            with self.subTest(draft=draft):
                findings = claim_lint.lint_text(draft, self.register, self.config)
                self.assertTrue(
                    [f for f in findings if f.category == "number"],
                    "'97 downloads all-time' must not source a trailing bare 97",
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


class TestMagnitudeDetection(unittest.TestCase):
    """Spelled-out quantities. A stat does not stop being a stat in words."""

    def setUp(self):
        self.config = claim_lint.DEFAULT_CONFIG
        self.register = claim_lint.load_register(FIXTURES / "truth.md")

    def _magnitudes(self, text):
        return [
            f
            for f in claim_lint.lint_text(text, self.register, self.config)
            if f.category == "magnitude"
        ]

    def test_flags_spelled_out_quantity(self):
        self.assertTrue(self._magnitudes("We have forty thousand paying customers."))

    def test_spelled_out_quantity_is_one_span(self):
        findings = self._magnitudes("We have forty thousand paying customers.")
        self.assertIn("forty thousand", [f.span for f in findings])

    def test_flags_vague_magnitudes(self):
        for draft in (
            "Hundreds of teams rely on it.",
            "It serves millions of requests.",
            "Dozens of integrations ship with it.",
            "Scores of reviewers agree.",
            "A handful of teams tested it.",
            "Countless hours saved.",
            "Numerous customers renewed.",
        ):
            with self.subTest(draft=draft):
                self.assertTrue(self._magnitudes(draft), draft)

    def test_flags_number_word_quantifying_a_plural_noun(self):
        self.assertTrue(self._magnitudes("We have forty paying customers."))
        self.assertTrue(self._magnitudes("Twelve teams use it."))

    def test_magnitude_is_error_severity(self):
        findings = self._magnitudes("Hundreds of teams rely on it.")
        self.assertEqual("error", findings[0].severity)

    def test_magnitude_passes_when_sourced(self):
        register = {"forty thousand paying customers as of the last billing export"}
        findings = [
            f
            for f in claim_lint.lint_text(
                "We have forty thousand paying customers as of the last billing export.",
                register,
                self.config,
            )
            if f.category == "magnitude"
        ]
        self.assertEqual([], findings)

    def test_ordinary_prose_does_not_trip_magnitude(self):
        """A noisy linter gets disabled, which is itself a false negative."""
        for draft in (
            "There is one place to look.",
            "The two halves close into one circle.",
            "Pick one and move on.",
            "It does one thing well.",
        ):
            with self.subTest(draft=draft):
                self.assertEqual([], self._magnitudes(draft), draft)

    def test_one_and_two_still_flag_in_front_of_a_magnitude_word(self):
        for draft in ("We serve one million users.", "Two thousand teams signed up."):
            with self.subTest(draft=draft):
                self.assertTrue(self._magnitudes(draft), draft)


class TestTestimonialForms(unittest.TestCase):
    def setUp(self):
        self.config = claim_lint.DEFAULT_CONFIG
        self.register = claim_lint.load_register(FIXTURES / "truth.md")

    def _testimonials(self, text):
        return [
            f
            for f in claim_lint.lint_text(text, self.register, self.config)
            if f.category == "testimonial"
        ]

    def test_flags_markdown_blockquote(self):
        text = "> This tool completely changed how our team works.\n"
        self.assertTrue(self._testimonials(text))

    def test_flags_blockquote_below_other_lines(self):
        text = "Intro copy here.\n\n> This tool completely changed how our team works.\n"
        findings = self._testimonials(text)
        self.assertTrue(findings)
        self.assertEqual(3, findings[0].line)

    def test_short_blockquote_is_not_a_testimonial(self):
        self.assertEqual([], self._testimonials("> Note: see below.\n"))

    def test_flags_single_quoted_testimonial(self):
        text = "'This tool completely changed how our team works.'"
        self.assertTrue(self._testimonials(text))

    def test_flags_curly_single_quoted_testimonial(self):
        text = "‘This tool completely changed how our team works.’"
        self.assertTrue(self._testimonials(text))

    def test_apostrophes_do_not_form_a_testimonial(self):
        text = "It doesn't matter which editor you're using when you're building.\n"
        self.assertEqual([], self._testimonials(text))


class TestScanSuffixes(unittest.TestCase):
    def test_publish_formats_are_scanned(self):
        for name in ("page.html", "page.htm", "post.mdx", "doc.rst", "note.txt"):
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / name
                    path.write_text("We have 4200 users.\n", encoding="utf-8")
                    code = claim_lint.main(
                        [tmp, "--register", str(FIXTURES / "truth.md")]
                    )
                    self.assertEqual(1, code, name)

    def test_json_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.json"
            path.write_text('{"users": 4200}\n', encoding="utf-8")
            code = claim_lint.main([tmp, "--register", str(FIXTURES / "truth.md")])
            self.assertEqual(0, code)


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
        # Round 2: the old assertion here checked for "may not disable detection",
        # a claim the code could not enforce (a broad ignore CAN disable a
        # category). The sentence was removed as a false claim; this asserts the
        # true replacement. The refusal itself is unchanged and still asserted.
        self.assertIn("'severity' and 'ignore' only", err)

    def test_all_warn_severity_is_refused(self):
        # 'magnitude' is listed here for the same reason as every other
        # category: the assertion is that a map setting EVERY category to warn
        # is refused, so a newly added category has to appear in the map for it
        # to still be an all-warn map. The assertion itself is unchanged.
        code, err = self._run_with_config(
            '{"severity": {"number": "warn", "magnitude": "warn",'
            ' "superlative": "warn", "comparative": "warn",'
            ' "testimonial": "warn", "absolute": "warn"}}'
        )
        self.assertEqual(2, code)
        self.assertIn("never fail", err)

    def test_invalid_severity_value_is_refused(self):
        code, err = self._run_with_config('{"severity": {"number": "eror"}}')
        self.assertEqual(2, code)
        self.assertIn("invalid severity 'eror'", err)

    def test_patterns_override_is_refused(self):
        code, err = self._run_with_config('{"patterns": {"number": "$^"}}')
        self.assertEqual(2, code)
        self.assertIn("'patterns' is not user-overridable", err)

    def test_patterns_override_is_refused_even_when_harmless(self):
        code, err = self._run_with_config(
            '{"patterns": {"number": "\\\\b\\\\d+\\\\b"}}'
        )
        self.assertEqual(2, code)
        self.assertIn("'patterns' is not user-overridable", err)

    def test_ignore_patterns_are_echoed_in_full(self):
        code, err = self._run_with_config('{"ignore": ["\\\\b4471\\\\b"]}')
        self.assertEqual(1, code, err)
        self.assertIn("ignore patterns: 1: \\b4471\\b", err)

    def test_no_ignore_patterns_is_echoed_explicitly(self):
        code, err = self._run_with_config('{"ignore": []}')
        self.assertEqual(1, code, err)
        self.assertIn("ignore patterns: 0: (none)", err)

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


class TestSharedLintVectors(unittest.TestCase):
    """One spec file, answered by both implementations of "is this claim sourced?".

    console/src/lint.js is a second implementation of this linter, for the
    browser. Two implementations of one question is the duplication that drifts
    apart silently — and the drift shows up as a FALSE NEGATIVE, a claim one
    side passes as sourced when it is not. Twelve of those have already been
    found here, every one of them by somebody using or adversarially reading the
    tool rather than by the suite that was green at the time.

    console/tests/lint-vectors.json is the shared specification. The JS test
    runner asserts against the same file, so a vector added for a bug found on
    either side becomes a regression test for both. When the two disagree, one
    of them is wrong: find out which. Never edit a vector to make them agree.
    """

    VECTORS = (
        Path(__file__).resolve().parent.parent.parent
        / "console" / "tests" / "lint-vectors.json"
    )

    @staticmethod
    def _verdict(rows, with_lines):
        """Both runners reduce a result to this shape, so they compare like for like."""
        return sorted(
            json.dumps(
                [row["category"], row["span"], row["severity"],
                 row.get("line") if with_lines else None],
                ensure_ascii=False, separators=(",", ":"),
            )
            for row in rows
        )

    def test_python_agrees_with_every_shared_vector(self):
        self.assertTrue(
            self.VECTORS.exists(),
            f"the shared vector file is missing: {self.VECTORS}. It is the only thing "
            "holding claim_lint.py and console/src/lint.js to the same answer; a run "
            "without it proves nothing.",
        )
        vectors = json.loads(self.VECTORS.read_text(encoding="utf-8"))
        self.assertTrue(vectors, "the shared vector file is empty")

        for vector in vectors:
            with self.subTest(vector=vector["name"]):
                with tempfile.TemporaryDirectory() as tmp:
                    config = claim_lint.DEFAULT_CONFIG
                    if "config" in vector:
                        path = Path(tmp) / "truth.config.json"
                        path.write_text(json.dumps(vector["config"]), encoding="utf-8")
                        if vector.get("refused"):
                            with self.assertRaises(claim_lint.ConfigRefused) as caught:
                                claim_lint.load_config(str(path))
                            self.assertIn(vector["refused"], str(caught.exception))
                            continue
                        config, _ = claim_lint.load_config(str(path))

                    with_lines = any("line" in item for item in vector["expect"])
                    with contextlib.redirect_stderr(io.StringIO()):
                        findings = claim_lint.lint_text(
                            vector["text"], set(vector["register"]), config
                        )
                    actual = self._verdict(
                        [f._asdict() for f in findings], with_lines
                    )
                    self.assertEqual(
                        self._verdict(vector["expect"], with_lines), actual,
                        f"{vector['name']}: claim_lint.py disagrees with the shared "
                        "vector. Either this implementation or console/src/lint.js is "
                        "wrong — do not change the vector to settle it.",
                    )


if __name__ == "__main__":
    unittest.main()
