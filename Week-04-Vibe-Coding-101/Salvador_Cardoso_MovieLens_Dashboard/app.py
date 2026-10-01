"""Four MovieLens analyses. Run with: python -m streamlit run app.py"""

from datetime import date
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).parent / "movie_ratings.csv"
UNKNOWN_GENRE = "Unknown / unlisted"
KNOWN_GENRES = {
    "Action", "Adventure", "Animation", "Children", "Children's", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror",
    "IMAX", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western",
}
REQUIRED_COLUMNS = {"user_id", "movie_id", "rating", "timestamp", "title", "year", "genres"}
BLUE = "#3973ac"


def split_genres(value):
    """Trim pipe-separated labels, remove empty/repeated tokens, retain unknowns."""
    if pd.isna(value):
        return [UNKNOWN_GENRE]
    tokens = [token.strip() for token in str(value).split("|") if token.strip()]
    tokens = [UNKNOWN_GENRE if token.lower() in {"unknown", "(no genres listed)"}
              else token for token in tokens]
    return list(dict.fromkeys(tokens)) or [UNKNOWN_GENRE]


def prepare_data(raw):
    """Keep the CSV untouched; document every exclusion/normalization in notes."""
    data = raw.rename(columns={"userId": "user_id", "movieId": "movie_id"}).copy()
    if data.columns.duplicated().any():
        raise ValueError("Ambiguous ID columns: provide either snake_case or camelCase IDs, not both.")
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}.")
    notes = []
    duplicates = int(data.duplicated().sum())
    data = data.drop_duplicates().copy()
    notes.append(f"Removed {duplicates:,} exact duplicate rows. Distinct repeat ratings are retained.")
    valid_ids = pd.Series(True, index=data.index)
    for column in ["user_id", "movie_id"]:
        values = pd.to_numeric(data[column], errors="coerce")
        valid_ids &= values.notna() & values.gt(0) & values.lt(2**63) & values.mod(1).eq(0)
        data[column] = values
    invalid_ids = int((~valid_ids).sum())
    data = data.loc[valid_ids].copy()
    for column in ["user_id", "movie_id"]:
        data[column] = data[column].astype("int64")
    notes.append(f"Excluded {invalid_ids:,} rows with missing or invalid user/movie IDs from all analyses.")
    data["rating"] = pd.to_numeric(data["rating"], errors="coerce")
    invalid_ratings = ~data["rating"].between(1, 5)
    data.loc[invalid_ratings, "rating"] = float("nan")
    notes.append(
        f"Excluded {int(invalid_ratings.sum()):,} missing, nonnumeric, or out-of-range ratings "
        "from means and rating counts (the verified scale is 1–5). Their movies remain in Question 1."
    )
    years = pd.to_numeric(data["year"], errors="coerce")
    valid_years = years.between(1888, date.today().year) & years.mod(1).eq(0)
    data["year"] = years.where(valid_years).astype("Int64")
    notes.append(
        f"Excluded {int((~valid_years).sum()):,} rating rows with missing or invalid release years "
        f"only from Question 3. Valid years must be whole numbers from 1888 to {date.today().year}; "
        "years are never inferred from titles or rating timestamps."
    )
    missing_titles = data["title"].isna() | data["title"].astype(str).str.strip().eq("")
    data.loc[missing_titles, "title"] = data.loc[missing_titles, "movie_id"].map(
        lambda movie_id: f"Untitled movie (ID {movie_id})"
    )
    notes.append(f"Used movie-ID labels for {int(missing_titles.sum()):,} missing/blank titles.")
    parsed = data["genres"].map(split_genres)
    # Tuples let us check that each movie has one consistent metadata record.
    data["genre_list"] = parsed.map(tuple)
    normalized = data["genres"].fillna("").astype(str).ne(parsed.map("|".join))
    notes.append(
        f"Normalized genre labels on {int(normalized.sum()):,} rows: trimmed whitespace, removed "
        "empty/repeated pipe tokens, and labeled missing/unknown genres as Unknown / unlisted."
    )
    unexpected = sorted({g for genres in parsed for g in genres} - KNOWN_GENRES - {UNKNOWN_GENRE})
    if unexpected:
        notes.append("Unrecognized genre labels are retained literally for review: " + ", ".join(unexpected))
    conflicts = data.groupby("movie_id")[["title", "year", "genre_list"]].nunique(dropna=False).gt(1).any(axis=1)
    if conflicts.any():
        ids = ", ".join(map(str, conflicts[conflicts].index[:5]))
        raise ValueError(f"Conflicting title/year/genre metadata for movie IDs {ids}. Resolve this before analysis.")
    return data, notes


def summarize(data):
    movies = data.drop_duplicates("movie_id")
    movie_genres = movies[["movie_id", "genre_list"]].explode("genre_list").rename(columns={"genre_list": "genre"})
    genre_counts = movie_genres.groupby("genre").size().reset_index(name="movie_count")
    genre_counts = genre_counts.sort_values(["movie_count", "genre"], ascending=[False, True])
    ratings = data.loc[data["rating"].notna()]
    rating_genres = ratings[["rating", "genre_list"]].explode("genre_list").rename(columns={"genre_list": "genre"})
    genre_means = rating_genres.groupby("genre").agg(
        mean_rating=("rating", "mean"), rating_count=("rating", "size")
    ).reset_index().sort_values(["mean_rating", "genre"], ascending=[False, True])
    by_year = ratings.dropna(subset=["year"]).groupby("year").agg(
        mean_rating=("rating", "mean"), rating_count=("rating", "size"), movie_count=("movie_id", "nunique")
    ).reset_index().sort_values("year")
    by_year["year"] = by_year["year"].astype(int)
    movie_stats = ratings.groupby("movie_id").agg(
        title=("title", "first"), mean_rating=("rating", "mean"), rating_count=("rating", "size")
    ).reset_index()
    return genre_counts, genre_means, by_year, movie_stats


@st.cache_data(show_spinner="Loading MovieLens ratings…")
def load_data(path, modified_ns):
    # modified_ns is part of the cache key so replacing the CSV invalidates the cache.
    data, notes = prepare_data(pd.read_csv(path))
    return data, notes, summarize(data)


def top_movies(movie_stats, floor):
    return movie_stats.loc[movie_stats["rating_count"] >= floor].sort_values(
        ["mean_rating", "rating_count", "title", "movie_id"],
        ascending=[False, False, True, True],
    ).head(5).reset_index(drop=True)


def select_years(by_year, year_range):
    return by_year.loc[by_year["year"].between(*year_range)].copy()


def rating_bars(data, category, axis_title, title):
    return alt.Chart(data).mark_bar(color=BLUE).encode(
        x=alt.X("mean_rating:Q", title="Mean rating (1–5)", scale=alt.Scale(domain=[0, 5])),
        y=alt.Y(f"{category}:N", title=axis_title, sort=data[category].tolist(),
                  axis=alt.Axis(labelLimit=480)),
        tooltip=[alt.Tooltip(f"{category}:N", title=axis_title),
                 alt.Tooltip("mean_rating:Q", title="Mean rating", format=".3f"),
                 alt.Tooltip("rating_count:Q", title="Ratings", format=",")],
    ).properties(title=title, height=max(200, len(data) * 26))


def ranking_table(ranked):
    table = ranked[["title", "mean_rating", "rating_count"]].copy()
    table.insert(0, "Rank", range(1, len(table) + 1))
    table.columns = ["Rank", "Movie", "Mean rating", "Ratings"]
    st.dataframe(table, hide_index=True, width="stretch", column_config={
        "Mean rating": st.column_config.NumberColumn(format="%.3f"),
        "Ratings": st.column_config.NumberColumn(format="%d"),
    })


def main():
    st.set_page_config(page_title="MovieLens Dashboard", page_icon="🎬", layout="wide")
    st.title("MovieLens Dashboard")
    st.write("Explore the genres, ratings, release years, and best-rated movies in the supplied MovieLens data.")
    try:
        data, notes, summaries = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime_ns)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"Could not load movie_ratings.csv: {error}")
        st.info("Keep movie_ratings.csv beside app.py and check the CSV columns and movie metadata.")
        st.stop()
    if data.empty:
        st.warning("No usable movie records are available in this CSV.")
        st.stop()
    genre_counts, genre_means, by_year, movie_stats = summaries
    columns = st.columns(3)
    columns[0].metric("Rating observations used", f"{data['rating'].notna().sum():,}")
    columns[1].metric("Movies with rating records", f"{data['movie_id'].nunique():,}")
    columns[2].metric("Users with rating records", f"{data['user_id'].nunique():,}")
    with st.expander("Data handling"):
        for note in notes:
            st.write("• " + note)
        st.caption("Extra columns are not used. The source CSV is unchanged. Controls affect only their own section.")

    st.header("1. Genre Breakdown")
    st.write("What's the distribution of genres among the movies that were rated?")
    st.caption("One movie per movie ID. A multi-genre movie contributes once to every listed genre, so totals overlap.")
    counts_chart = alt.Chart(genre_counts).mark_bar(color=BLUE).encode(
        x=alt.X("movie_count:Q", title="Number of distinct movies", scale=alt.Scale(zero=True)),
        y=alt.Y("genre:N", title="Genre", sort=genre_counts["genre"].tolist()),
        tooltip=[alt.Tooltip("genre:N", title="Genre"),
                 alt.Tooltip("movie_count:Q", title="Movies", format=",")],
    ).properties(title="Rated movies by genre", height=len(genre_counts) * 26)
    st.altair_chart(counts_chart, width="stretch")

    st.header("2. Genre Satisfaction")
    st.write("Which genres have the highest average rating? Which have the lowest?")
    if genre_means.empty:
        st.info("No valid ratings are available for this analysis.")
    else:
        high, low = genre_means.iloc[0], genre_means.iloc[-1]
        st.write(f"Highest: **{high['genre']} ({high['mean_rating']:.3f})**. "
                 f"Lowest: **{low['genre']} ({low['mean_rating']:.3f})**.")
        known = genre_means.loc[genre_means["genre"] != UNKNOWN_GENRE]
        if not known.empty and low["genre"] == UNKNOWN_GENRE:
            lowest_known = known.iloc[-1]
            st.caption(f"Among listed genres, the lowest is {lowest_known['genre']} ({lowest_known['mean_rating']:.3f}).")
        st.altair_chart(rating_bars(genre_means, "genre", "Genre", "Mean rating by genre"), width="stretch")
    st.caption("Each rating contributes to every genre of its movie. Popular movies carry more weight; genres overlap "
               "and have different sample sizes. Hover for counts. Unknown / unlisted is a missing-classification category.")

    st.header("3. Ratings Over Movie Release Years")
    st.write("How has the mean rating changed across movie release years?")
    missing_years = int(data["year"].isna().sum())
    st.caption(f"Uses movie release year from year, never timestamp or rating_year. "
               f"{missing_years:,} records have missing/invalid years and are excluded only here.")
    if by_year.empty:
        st.info("No valid release-year ratings are available.")
    else:
        first, last = int(by_year["year"].min()), int(by_year["year"].max())
        if first == last:
            year_range = (first, last)
            st.caption(f"Only release year {first} is available.")
        else:
            year_range = st.slider("Movie release-year range (Question 3 only)", first, last,
                                   (first, last), step=1, key="release_year_range")
        selected = select_years(by_year, year_range)
        if selected.empty:
            st.info("No ratings fall in this release-year range. Widen the range.")
        else:
            st.caption(f"Showing {int(selected['rating_count'].sum()):,} ratings across {len(selected):,} release years.")
            year_chart = alt.Chart(selected).mark_line(point=True, color=BLUE).encode(
                x=alt.X("year:Q", title="Movie release year", scale=alt.Scale(zero=False),
                        axis=alt.Axis(format="d", tickMinStep=1)),
                y=alt.Y("mean_rating:Q", title="Mean rating (1–5)", scale=alt.Scale(domain=[0, 5])),
                tooltip=[alt.Tooltip("year:Q", title="Release year", format="d"),
                         alt.Tooltip("mean_rating:Q", title="Mean rating", format=".3f"),
                         alt.Tooltip("rating_count:Q", title="Ratings", format=","),
                         alt.Tooltip("movie_count:Q", title="Movies", format=",")],
            ).properties(title="Mean rating by movie release year", height=320)
            st.altair_chart(year_chart, width="stretch")
            st.caption("Every rating has equal weight. Sparse years can fluctuate; hover for sample sizes. "
                       "Lines connect available years; missing years are not filled or estimated.")

    st.header("4. Best Movies, With a Floor")
    st.write("What are the top 5 best-rated movies with at least 50 ratings? What changes at 150?")
    floor = st.radio("Minimum number of ratings per movie (Question 4 only)", [50, 150],
                     horizontal=True, key="minimum_ratings")
    ranked = top_movies(movie_stats, floor)
    if ranked.empty:
        st.info(f"No movies have at least {floor} valid ratings.")
    else:
        st.subheader(f"Top {len(ranked)} — at least {floor} ratings")
        st.altair_chart(rating_bars(ranked, "title", "Movie", f"Best-rated movies: minimum {floor} ratings"), width="stretch")
        ranking_table(ranked)
    st.caption("Ranked by unrounded mean rating descending, rating count descending, title ascending, "
               "then movie ID ascending. The floor is a count of ratings, not a rating score.")
    st.subheader("Compare 50 vs. 150 ratings")
    top50, top150 = top_movies(movie_stats, 50), top_movies(movie_stats, 150)
    for column, threshold, table in zip(st.columns(2), [50, 150], [top50, top150]):
        with column:
            st.markdown(f"**At least {threshold} ratings**")
            if table.empty:
                st.info("No qualifying movies.")
            else:
                ranking_table(table)
    ids50, ids150 = set(top50["movie_id"]), set(top150["movie_id"])
    if ids50 or ids150:
        st.write(f"{len(ids50 & ids150)} movies appear in both top-five lists.")
        removed = top50.loc[~top50["movie_id"].isin(ids150), "title"].tolist()
        entered = top150.loc[~top150["movie_id"].isin(ids50), "title"].tolist()
        st.write("Leave the top five at 150: " + ("; ".join(removed) or "None") + ".")
        st.write("Enter the top five at 150: " + ("; ".join(entered) or "None") + ".")
    st.caption("A higher floor filters out less-rated movies; it does not change a movie's mean rating "
               "or eliminate selection bias.")


if __name__ == "__main__":
    main()
