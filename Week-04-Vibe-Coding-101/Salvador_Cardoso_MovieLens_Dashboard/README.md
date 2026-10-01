# MovieLens Dashboard

A student Streamlit dashboard answering exactly four questions from the supplied `movie_ratings.csv`.

## Files

- `app.py`: dashboard, preprocessing, and aggregations.
- `requirements.txt`: the three tested direct dependencies.
- `movie_ratings.csv`: unchanged copy of the supplied dataset.
- `BUILD_LOG.md`: the original request and genuine first-iteration decisions/checks.
- `validate_app.py`: reproducible checks using Python's unittest and Streamlit AppTest.
- `.gitignore`: excludes environments, Python caches, and secrets.

## Run locally

Use Python 3.12, matching the tested environment. From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Using the environment's Python directly avoids PowerShell activation-policy problems. On macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Open the local URL printed in the terminal. Stop the app with Ctrl+C.

Optional verification on Windows:

```powershell
.\.venv\Scripts\python.exe validate_app.py
```

On macOS/Linux use `.venv/bin/python validate_app.py`.

## Dataset inspection and analytical choices

The supplied file has 100,000 rows and 13 columns: `user_id`, `movie_id`, `rating`, `timestamp`, `age`, `gender`, `occupation`, `zip_code`, `title`, `year`, `decade`, `genres`, and `rating_year`. It contains 1,682 movie IDs and 943 user IDs. Ratings are integers from 1–5. Release years are 1922–1998. There are no exact duplicate rows, repeated user/movie pairs, or conflicting movie metadata. Thirty observations across five movies have missing release years. Ten observations across two movies use the literal genre `unknown`.

Pandas reads `user_id`, `movie_id`, `rating`, `age`, and `rating_year` as int64; `year` and `decade` as float64 because they contain missing values; and `timestamp`, `gender`, `occupation`, `zip_code`, `title`, and `genres` as object/string columns. Timestamps contain date/time text, not Unix numeric timestamps. The app does not need to parse them.

The app uses the actual snake_case IDs and also accepts the prompt's camelCase aliases. Extra columns are unused; `timestamp` and `rating_year` never determine the release-year chart.

| Question | Calculation | Display |
| --- | --- | --- |
| Genre breakdown | One record per movie ID; split/explode genres, once per applicable genre | Horizontal bars, descending movie count |
| Genre satisfaction | Split/explode rating observations; mean rating by genre | Horizontal bars, descending mean; rating-count tooltips |
| Ratings across release years | Mean of valid ratings grouped by the movie's `year` | Ordered line chart with points and year-range slider |
| Top five with a floor | Per-movie valid rating count and mean; filter count before sorting | 50/150 radio selector, ranked bars/table, and both rankings side by side |

Genre totals overlap; they are not mutually exclusive shares. Genre means are rating-weighted, so popular movies have more influence. Different genres and release years have different sample sizes and user/movie composition. Counts appear in tooltips. Unknown / unlisted remains visible as a missing-classification category; the satisfaction section also identifies the lowest listed genre if unknown is lowest.

All rating charts use a 0–5 axis with the observed rating scale labeled 1–5. Bars begin at zero. Categorical ordering is descending; release years are chronological. Means are sorted at full precision, with ties resolved by rating count descending, title ascending, and movie ID ascending. Displaying three decimals does not change sorting.

## Data handling

The app never writes to the CSV. Its Data handling expander reports:

- Exact duplicate full rows removed; distinct repeat ratings retained.
- Missing/invalid positive integer user/movie IDs excluded from all analyses.
- Missing/nonnumeric ratings or ratings outside 1–5 excluded from means and rating counts. Their movie records remain in the genre breakdown.
- Missing/nonnumeric/fractional release years, years before 1888, and future years excluded only from Question 3. No title-based year imputation.
- Missing titles displayed with the movie ID.
- Genre whitespace trimmed; empty/repeated pipe tokens removed; missing/unknown genres labeled Unknown / unlisted. Unrecognized labels are retained literally and reported rather than guessed or discarded.
- Conflicting title/year/genre metadata for one movie ID stops analysis with a clear error.

In the supplied file, only the 30 missing years are excluded, and `unknown` is relabeled for readability. No ratings are removed. The original data remains unchanged. The year control affects only Question 3; the threshold control affects only Question 4.

## Project location and future updates

This dashboard lives in the existing public fork [stalris/ds-fall-2026](https://github.com/stalris/ds-fall-2026), on branch `main`, under:

`Week-04-Vibe-Coding-101/Salvador_Cardoso_MovieLens_Dashboard`

From the repository root, enter that folder before using the local run commands above:

```bash
cd Week-04-Vibe-Coding-101/Salvador_Cardoso_MovieLens_Dashboard
```

There is no need to initialize another repository inside this folder. To obtain a local checkout:

```bash
git clone https://github.com/stalris/ds-fall-2026.git
cd ds-fall-2026
```

For later edits, record your real request and observed outcome in the build log. From the repository root:

```bash
git pull --ff-only origin main
git add Week-04-Vibe-Coding-101/Salvador_Cardoso_MovieLens_Dashboard
git commit -m "Describe the actual dashboard change"
git push origin main
```

## Deploy on Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) and connect the GitHub account containing this repository.
2. Choose **Create app**, then **Yup, I have an app** if prompted.
3. Select repository `stalris/ds-fall-2026`, branch `main`, and main file `Week-04-Vibe-Coding-101/Salvador_Cardoso_MovieLens_Dashboard/app.py`.
4. In **Advanced settings**, choose **Python 3.12**, matching the checks performed here. This app needs no secrets.
5. Choose an optional URL/subdomain, then deploy. Wait for dependency installation and startup; consult the app logs if startup fails.
6. Open the resulting `https://....streamlit.app` URL, set sharing/access to public if needed, and test it in a signed-out/incognito window.

Keep `requirements.txt` and `movie_ratings.csv` beside `app.py` in the repository. Data loads relative to the app file, with no machine-specific paths. Community Cloud loads the repository and installs its dependencies. Pushing future changes to `main` updates the deployed app.

Official references checked during this build:

- [Deploy an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Repository file organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)
- [AppTest reference](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)

## Pre-flight before submitting

- [ ] Public URL opens while signed out, with no errors.
- [ ] All four analytical sections and their labeled charts render clearly.
- [ ] Genre counts use distinct movies, with multi-genre overlap explained.
- [ ] Genre satisfaction shows mean ratings and sample counts in tooltips.
- [ ] Release-year slider changes the line chart; missing years are explained.
- [ ] The 50/150 selector changes the selected ranking; both lists remain visible for comparison.
- [ ] App, dependency file, and unchanged CSV are present on `main`.
- [ ] Build log records actual prompts, outcomes, and any real subsequent corrections.
- [ ] No future audit/write-up has been added to the dashboard.

## Validation status

Seven automated checks passed on Python 3.12.14, Streamlit 1.55.0, pandas 2.2.3, and Altair 5.5.0. These cover independent CSV calculations for all four questions, multi-genre handling, data-quality fixtures, deterministic sorting, chart titles/axes, changes to both Streamlit controls, empty year ranges, and no qualifying movies. Syntax compilation also passed.

The local server started and its health endpoint returned HTTP 200. SHA-256 checks confirmed that the packaged CSV exactly matches the uploaded CSV.

The dependency file specifies the tested direct versions. Browser screenshot verification could not be completed because the Chromium download failed in this environment. The project uses the existing fork and folder described above. No Community Cloud deployment has been performed here. Verify the actual public deployment with the checklist above.
