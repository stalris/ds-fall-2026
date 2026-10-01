"""Run with python validate_app.py. No extra test dependencies required."""

import csv
import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from app import DATA_PATH, UNKNOWN_GENRE, prepare_data, select_years, split_genres, summarize, top_movies


class DashboardChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = pd.read_csv(DATA_PATH)
        cls.data, cls.notes = prepare_data(cls.raw)
        cls.counts, cls.means, cls.years, cls.movies = summarize(cls.data)

    def test_supplied_data_against_independent_csv_calculation(self):
        # An independent row-by-row calculation checks the pandas aggregation.
        movie_genres, rating_genres, yearly, movie_ratings = {}, {}, {}, {}
        with DATA_PATH.open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                movie_id, rating = int(row["movie_id"]), int(row["rating"])
                genres = row["genres"].split("|")
                movie_genres[movie_id] = genres
                movie_ratings.setdefault(movie_id, []).append(rating)
                for genre in genres:
                    label = UNKNOWN_GENRE if genre == "unknown" else genre
                    rating_genres.setdefault(label, []).append(rating)
                if row["year"]:
                    yearly.setdefault(int(float(row["year"])), []).append(rating)
        for row in self.counts.itertuples():
            source_label = "unknown" if row.genre == UNKNOWN_GENRE else row.genre
            self.assertEqual(row.movie_count, sum(source_label in genres for genres in movie_genres.values()))
        for row in self.means.itertuples():
            values = rating_genres[row.genre]
            self.assertEqual(row.rating_count, len(values))
            self.assertAlmostEqual(row.mean_rating, sum(values) / len(values))
        for row in self.years.itertuples():
            values = yearly[row.year]
            self.assertEqual(row.rating_count, len(values))
            self.assertAlmostEqual(row.mean_rating, sum(values) / len(values))
        for row in self.movies.itertuples():
            values = movie_ratings[row.movie_id]
            self.assertEqual(row.rating_count, len(values))
            self.assertAlmostEqual(row.mean_rating, sum(values) / len(values))
        self.assertEqual(len(self.data), 100_000)
        self.assertEqual(len(movie_genres), 1682)
        self.assertEqual(self.years.rating_count.sum(), 99_970)
        self.assertEqual(top_movies(self.movies, 50).movie_id.tolist(), [408, 318, 169, 483, 114])
        self.assertEqual(top_movies(self.movies, 150).movie_id.tolist(), [318, 483, 64, 603, 12])

    def test_cleaning_and_multigenre_weighting(self):
        rows = pd.DataFrame([
            [1, 1, 5, "2005-01-01", "Alpha", 2000, " Drama ||Comedy|Drama "],
            [2, 1, 1, "2006-01-01", "Alpha", 2000, "Drama|Comedy"],
            [3, 2, 3, "2006-01-01", "Beta", "bad", None],
            [4, 3, 99, "2006-01-01", "Gamma", 9999, "Drama"],
        ], columns=["user_id", "movie_id", "rating", "timestamp", "title", "year", "genres"])
        data, notes = prepare_data(pd.concat([rows, rows.iloc[[0]]], ignore_index=True))
        counts, means, years, movies = summarize(data)
        self.assertEqual(len(data), 4)
        self.assertEqual(counts.set_index("genre").loc["Drama", "movie_count"], 2)
        self.assertEqual(means.set_index("genre").loc["Drama", "mean_rating"], 3)
        self.assertEqual(years.year.tolist(), [2000])  # Not the rating timestamp's year.
        self.assertEqual(years.rating_count.tolist(), [2])
        self.assertTrue(top_movies(movies, 50).empty)
        self.assertTrue(select_years(years, (2001, 2002)).empty)
        self.assertTrue(any("Removed 1" in note for note in notes))
        self.assertEqual(split_genres(" | | "), [UNKNOWN_GENRE])
        self.assertEqual(split_genres("Drama,Comedy"), ["Drama,Comedy"])
        fractional = rows.copy()
        fractional["year"] = [2000.5, 2000.5, 1887, None]
        self.assertTrue(prepare_data(fractional)[0].year.isna().all())

    def test_schema_and_conflicting_metadata(self):
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            prepare_data(self.raw.drop(columns="year"))
        conflict = self.raw.iloc[[0, 0]].copy()
        conflict.iloc[1, conflict.columns.get_loc("genres")] = "Drama"
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            prepare_data(conflict)
        aliases = self.raw.head(3).rename(columns={"user_id": "userId", "movie_id": "movieId"})
        self.assertIn("movie_id", prepare_data(aliases)[0])

    def test_unrounded_sort_and_tie_breaking(self):
        stats = pd.DataFrame({"movie_id": [4, 3, 2, 1, 5], "title": ["B", "A", "A", "Z", "Higher"],
                              "mean_rating": [4, 4, 4, 4, 4.00001], "rating_count": [50, 50, 50, 51, 50]})
        self.assertEqual(top_movies(stats, 50).movie_id.tolist(), [5, 1, 2, 3, 4])

    def test_streamlit_controls_and_chart_specs(self):
        at = AppTest.from_file(Path(__file__).with_name("app.py"), default_timeout=30).run()
        self.assertFalse(at.exception)
        self.assertFalse(at.error)
        self.assertEqual(len(at.header), 4)
        self.assertEqual(len(at.get("vega_lite_chart")), 4)
        for chart in at.get("vega_lite_chart"):
            spec = json.loads(chart.proto.spec)
            self.assertTrue(spec["title"])
            self.assertTrue(spec["encoding"]["x"]["title"])
            self.assertTrue(spec["encoding"]["y"]["title"])
        original = at.dataframe[0].value.Movie.tolist()
        at.radio(key="minimum_ratings").set_value(150).run()
        self.assertFalse(at.exception)
        self.assertNotEqual(original, at.dataframe[0].value.Movie.tolist())
        self.assertEqual(at.dataframe[0].value.Movie.tolist(), at.dataframe[2].value.Movie.tolist())
        full_chart = at.get("vega_lite_chart")[2].proto.spec
        at.slider(key="release_year_range").set_value((1990, 1998)).run()
        self.assertFalse(at.exception)
        self.assertNotEqual(full_chart, at.get("vega_lite_chart")[2].proto.spec)
        self.assertTrue(any("69,452 ratings across 9" in x.value for x in at.caption))
        at.radio(key="minimum_ratings").set_value(50).run()
        self.assertEqual(at.dataframe[0].value.Movie.tolist(), original)

    def test_streamlit_empty_range_and_no_qualifying_movies(self):
        fixture = self.raw.head(2).copy()
        fixture["year"] = [2000, 2002]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.csv"
            fixture.to_csv(path, index=False)
            script = f"import app\nfrom pathlib import Path\napp.DATA_PATH = Path({str(path)!r})\napp.main()"
            at = AppTest.from_string(script, default_timeout=30).run()
            self.assertFalse(at.exception)
            self.assertTrue(any("No movies have at least 50" in x.value for x in at.info))
            at.slider(key="release_year_range").set_value((2001, 2001)).run()
            self.assertFalse(at.exception)
            self.assertTrue(any("No ratings fall" in x.value for x in at.info))

    def test_streamlit_all_missing_years_and_bad_ratings(self):
        fixture = self.raw.head(2).copy()
        fixture["year"] = None
        fixture["rating"] = "bad"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.csv"
            fixture.to_csv(path, index=False)
            script = f"import app\nfrom pathlib import Path\napp.DATA_PATH = Path({str(path)!r})\napp.main()"
            at = AppTest.from_string(script, default_timeout=30).run()
            self.assertFalse(at.exception)
            self.assertTrue(any("No valid release-year" in x.value for x in at.info))


if __name__ == "__main__":
    unittest.main(verbosity=2)
