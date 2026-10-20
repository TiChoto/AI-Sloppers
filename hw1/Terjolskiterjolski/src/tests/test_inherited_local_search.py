from dataclasses import dataclass
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unimarket.assistants.local_search import LocalKeywordSearch


@dataclass
class Listing:
    id: str
    title: str
    description: str
    category: str = "Other"
    condition: str = "good"


class TestLocalKeywordSearch(unittest.TestCase):
    def setUp(self):
        self.search = LocalKeywordSearch()
        for listing in (
            Listing("calc-1", "Scientific calculator", "Reliable for engineering exams", "Electronics"),
            Listing("bike-blue", "Commuter bicycle", "Blue frame, recently serviced", "Transport"),
            Listing("bike-red", "Red bicycle", "Recently serviced", "Transport"),
            Listing("book-chem", "Chemistry textbook", "Introductory chemistry for first year", "Books"),
            Listing("book-physics", "Physics textbook", "Mechanics and waves", "Books"),
            Listing("laptop-1", "Lightweight laptop", "Good battery for study", "Electronics"),
        ):
            self.search.index_listing(listing)

    def test_engineering_calculator_query(self):
        results = self.search.query("I need a calculator for engineering exams")
        self.assertEqual([result.listing_id for result in results], ["calc-1"])
        self.assertEqual(
            results[0].reason,
            "Matched title terms: calculator; description terms: engineering, exams.",
        )

    def test_blue_bicycle_ranks_color_evidence(self):
        results = self.search.query("blue bicycle")
        self.assertEqual([result.listing_id for result in results], ["bike-blue", "bike-red"])
        self.assertEqual(results[0].reason, "Matched title terms: bicycle; description terms: blue.")
        self.assertEqual(results[1].reason, "Matched title terms: bicycle.")

    def test_textbook_query_ranks_specific_match(self):
        results = self.search.query("looking for a chemistry textbook")
        self.assertEqual([result.listing_id for result in results], ["book-chem", "book-physics"])
        self.assertEqual(results[0].reason, "Matched title terms: chemistry, textbook.")
        self.assertEqual(results[1].reason, "Matched title terms: textbook.")

    def test_query_is_case_and_punctuation_insensitive(self):
        results = self.search.query("CALCULATOR!!! engineering")
        self.assertEqual([result.listing_id for result in results], ["calc-1"])

    def test_blank_and_unmatched_queries_return_empty(self):
        self.assertEqual(self.search.query("  !!! "), [])
        self.assertEqual(self.search.query("I am looking for a"), [])
        self.assertEqual(self.search.query("microscope"), [])

    def test_reindex_replaces_the_listing_snapshot(self):
        self.search.index_listing(Listing("calc-1", "Desk lamp", "Warm light", "Home"))
        self.assertEqual(self.search.query("calculator"), [])
        self.assertEqual([r.listing_id for r in self.search.query("desk lamp")], ["calc-1"])

    def test_remove_and_unknown_remove(self):
        self.search.remove_listing("calc-1")
        self.search.remove_listing("not-indexed")
        self.assertEqual(self.search.query("calculator"), [])

    def test_results_are_unique_and_ties_are_deterministic(self):
        search = LocalKeywordSearch()
        search.index_listing(Listing("z-id", "Notebook", "Paper pages"))
        search.index_listing(Listing("a-id", "Notebook", "Paper pages"))
        self.assertEqual([r.listing_id for r in search.query("notebook")], ["a-id", "z-id"])

    def test_index_requires_nonempty_id_and_string_text(self):
        search = LocalKeywordSearch()
        with self.assertRaisesRegex(ValueError, "listing id"):
            search.index_listing(Listing(" ", "Book", "Description"))
        with self.assertRaisesRegex(ValueError, "text fields"):
            search.index_listing(Listing("bad", None, "Description"))

    def test_query_requires_text(self):
        with self.assertRaisesRegex(TypeError, "query text"):
            self.search.query(None)
