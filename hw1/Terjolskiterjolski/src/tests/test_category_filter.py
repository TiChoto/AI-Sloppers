"""Tests for Nikolozi's category-filter extension, separate from inherited tests."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

from unimarket.assistants.local_search import LocalKeywordSearch

SRC = Path(__file__).resolve().parents[1]


class TestCategoryFilter(unittest.TestCase):
    def setUp(self):
        self.search = LocalKeywordSearch()
        for record in json.loads((SRC / "data/listings.json").read_text(encoding="utf-8")):
            self.search.index_listing(SimpleNamespace(**record))

    def ids(self, text, category=None):
        return [r.listing_id for r in self.search.query(text, category=category)]

    def test_golden_electronics_excludes_matching_book(self):
        self.assertEqual(self.ids("calculator", "Electronics"), ["calc-1"])
        self.assertEqual(self.search.query("calculator", category="Electronics")[0].reason,
                         "Matched title terms: calculator.")

    def test_golden_trimmed_case_insensitive_books_preserves_rank(self):
        results = self.search.query("chemistry textbook", category="  bOoKs  ")
        self.assertEqual([r.listing_id for r in results], ["book-chem", "book-physics"])
        self.assertEqual([r.reason for r in results], [
            "Matched title terms: chemistry, textbook.", "Matched title terms: textbook."])

    def test_golden_unknown_category_has_no_fallback(self):
        self.assertEqual(self.ids("calculator", "Transport"), [])

    def test_category_is_exact_not_substring(self):
        self.assertEqual(self.ids("textbook", "Book"), [])

    def test_category_does_not_create_keyword_matches(self):
        self.assertEqual(self.ids("microscope", "Books"), [])
        self.assertEqual(self.ids("   ", "Books"), [])

    def test_omitted_category_preserves_baseline(self):
        self.assertEqual(self.ids("calculator"), ["guide-1", "calc-1"])
        self.assertEqual(self.search.query("calculator"),
                         self.search.query("calculator", category=None))

    def test_invalid_category_is_rejected_even_with_blank_query(self):
        for category in ("", "  ", "\t"):
            with self.subTest(category=category), self.assertRaisesRegex(ValueError, "blank"):
                self.search.query("", category=category)
        for category in (5, False, []):
            with self.subTest(category=category), self.assertRaisesRegex(TypeError, "category"):
                self.search.query("calculator", category=category)

    def test_reindex_category_moves_listing_then_removal_hides_it(self):
        self.search.index_listing(SimpleNamespace(
            id="calc-1", title="Scientific calculator", description="Exam use",
            category=" Books ", condition="good"))
        self.assertEqual(self.ids("calculator", "Electronics"), [])
        self.assertEqual(self.ids("calculator", "Books"), ["guide-1", "calc-1"])
        self.search.remove_listing("calc-1")
        self.assertEqual(self.ids("calculator", "Books"), ["guide-1"])

    def test_filter_keeps_deterministic_ties(self):
        for listing_id in ("z", "a"):
            self.search.index_listing(SimpleNamespace(
                id=listing_id, title="Notebook", description="Paper",
                category="Books", condition="new"))
        self.assertEqual(self.ids("notebook", "books"), ["a", "z"])

    def test_cli_success_and_error(self):
        result = subprocess.run(
            [sys.executable, "-m", "unimarket", "calculator", "--category", "Books"],
            cwd=SRC, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [{
            "listing_id": "guide-1", "reason": "Matched title terms: calculator."}])
        result = subprocess.run(
            [sys.executable, "-m", "unimarket", "calculator", "--category", " "],
            cwd=SRC, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("category must not be blank", result.stderr)


if __name__ == "__main__":
    unittest.main()
