# MovieLens dashboard build log

This log records the real conversation and development work. Assistant implementation choices are not represented as student-approved revisions. Later requests are appended below as separate iterations.

## Iteration 1 — Initial build, October 1, 2026

### Exact initial user message

```text
heya chat. I'm supposed to practice vibe coding for my ds class (lol). I watched some prompt engineering courses for the pre reqs, and they want me to prompt you to build this project. I asked another version of you to prepare the prompt, according to the principles of those videos. without further ado... here you go :) 



I want you to help me build my MovieLens dashboard homework project in Streamlit. Act as an experienced data scientist and Python/Streamlit developer, but treat me as the engineer making the final decisions. Your job is to propose sensible choices, explain them briefly, implement them, and point out anything ambiguous rather than silently making arbitrary assumptions.

## Goal

Build a clean, functional Streamlit dashboard from `movie_ratings.csv` that answers the four required analytical questions below and can be deployed on Streamlit Community Cloud.

The final project should be simple enough for a student project: do not overengineer it, add unnecessary frameworks, or introduce complexity that does not help satisfy the assignment.

## Dataset

The CSV contains:

- `userId`
- `movieId`
- `rating`
- `timestamp`
- `title`
- `year`
- `genres`

`genres` contains pipe-separated values such as:

`Action|Adventure|Sci-Fi`

Before coding, inspect the actual uploaded CSV and verify that the columns and data types match these expectations. Do not invent columns or assume values that are not present in the file.

## Required Analysis

The dashboard must answer exactly these four questions.

### 1. Genre Breakdown

Question:

"What's the distribution of genres among the movies that were rated?"

Movies may have multiple genres.

Before calculating anything, explain how you interpret this question and how you will handle multi-genre movies.

My preferred interpretation is:

- We are interested in movies that received ratings, not the number of rating events.
- Deduplicate movies by `movieId` before counting genres so that a heavily rated movie is not counted hundreds of times.
- Split the pipe-separated `genres` field.
- Explode the genres so that a movie belonging to multiple genres contributes once to each applicable genre.

If the actual dataset gives you a reason this interpretation is inappropriate, tell me before changing it.

Choose an appropriate chart type and sort it meaningfully rather than alphabetically by default.

### 2. Genre Satisfaction

Question:

"Which genres have the highest average rating? Which have the lowest?"

For this analysis, use the rating-level data.

Split/explode the genre field so that a rating for a multi-genre movie contributes to each genre associated with that movie, then calculate the mean rating for each genre.

Clearly label the axis and sort the genres by average rating so the highest and lowest are easy to identify.

If there is an important statistical caveat to this interpretation, mention it briefly.

### 3. Ratings Over Time

Question:

"How has the mean rating changed across movie release years?"

Use the movie's `year` column.

Do NOT interpret "over time" as the year in which the user submitted the rating unless the assignment explicitly requires that. The question is asking about movie release year.

Group rating observations by movie release year and calculate mean rating.

Handle missing, malformed, or unreasonable year values cleanly rather than allowing them to break the chart.

Choose a chart suited to showing change across ordered years.

### 4. Best Movies, With a Floor

Question:

"What are the top 5 best-rated movies, once you only count movies with at least 50 ratings? What changes if you raise that floor to 150?"

For each movie:

1. Calculate its number of ratings.
2. Calculate its mean rating.
3. Filter out movies below the selected minimum number of ratings.
4. Sort the remaining movies by mean rating descending.
5. Display the top 5.

The dashboard must make it possible to compare a threshold of 50 ratings against a threshold of 150 ratings.

Use a sensible deterministic tie-breaking rule if movies have identical mean ratings, such as rating count and then title, and tell me what rule you used.

Do not confuse "at least 50 ratings" with a rating score of 50.

## Interactive Controls

Include at least 1–2 genuinely working Streamlit controls.

Use controls that make analytical sense rather than adding widgets just to satisfy the requirement.

A good option would be:

- a control for the minimum-rating threshold in Question 4, with 50 and 150 easy to compare;
- a release-year range control for Question 3.

If you propose different controls, explain why they are useful.

Make sure the controls actually affect the relevant data/chart.

## Chart Design

Choose the chart type that best communicates each answer.

Prefer simple, readable visualizations.

In particular:

- sort categorical bar charts meaningfully;
- use horizontal bars when category/movie names would otherwise be difficult to read;
- avoid a pie chart with many genres;
- do not confuse release year with rating timestamp;
- label axes and titles clearly;
- avoid misleading scales;
- keep charts readable without unnecessary decoration.

Use one consistent charting library unless there is a good reason not to.

## Streamlit Structure

The dashboard should have:

- a clear page title;
- a short introduction;
- the four required analytical sections;
- appropriate interactive controls;
- concise captions or explanations where the interpretation is important;
- readable charts.

Do NOT add the future audit/write-up assignment to the dashboard. The homework explicitly says that does not belong in this week's app.

## Implementation Requirements

Use Python and Streamlit.

Create at minimum:

- `app.py`
- `requirements.txt`

You may create other small supporting files if genuinely useful, but keep the project simple.

Use pandas for data manipulation.

Cache loading/preprocessing appropriately with Streamlit if useful.

Do not hard-code calculated answers that should come from the CSV.

The app should work when the repository is deployed from GitHub to Streamlit Community Cloud.

Use a relative path to load `movie_ratings.csv` from the repository.

Do not rely on files or absolute paths from my local computer.

## Robustness

Handle obvious data-quality problems gracefully:

- missing years;
- missing genres;
- malformed genre strings;
- duplicate rating rows if relevant;
- movies that do not meet the rating threshold;
- a user-selected year range containing no data.

Do not silently alter the underlying data unless there is a clear reason.

If you clean or exclude records, briefly explain what was done.

## Workflow

Work in this order:

1. Inspect the dataset.
2. Briefly summarize its shape, columns, and any obvious data-quality issues.
3. Before writing the full app, explain your proposed interpretation of each of the four questions.
4. State which chart you chose for each question and why.
5. Point out any assumptions you are making.
6. Implement the dashboard.
7. Run/check the code for errors.
8. Verify that each of the four assignment questions is actually answered.
9. Verify that the interactive controls work.
10. Give me the final project files.
11. Give me the exact Git commands needed to initialize the repository, commit it, connect it to a new GitHub repository, and push `main`.
12. Give me the Streamlit Community Cloud deployment steps for this project.
13. Give me a short pre-flight checklist to use before submitting the public URL.

Do not skip directly from the assignment description to a giant code dump. I want to see the analytical decisions first so I can judge them.

## Build Log

I need to preserve my real vibe-coding process for a later assignment.

Maintain a simple `BUILD_LOG.md`.

For each meaningful iteration, record:

- the exact prompt/request I gave you;
- what you produced or changed;
- any issue I noticed;
- what I asked you to change and why.

Do not fabricate revisions or pretend that we made decisions that did not actually happen. The purpose is to preserve the genuine development process, including mistakes and corrections.

For this first iteration, record this prompt as the initial prompt and summarize the major decisions you make in response to it.

## Interaction With Me

If you encounter an ambiguity that has a reasonable conventional solution, make a sensible choice, state the assumption, and continue rather than stopping unnecessarily.

If an ambiguity would materially change the meaning of one of the four required analyses, call it out clearly so I can evaluate the choice.

If I later ask for a modification, change only what is necessary unless the change requires restructuring something else.

When fixing bugs, explain the cause briefly rather than merely replacing the code.

Do not claim that something works unless you have actually checked it to the extent available in your environment.

## Final Validation

Before considering the project finished, explicitly check:

- Question 1 is answered with correct handling of multi-genre movies.
- Question 2 shows average rating by genre.
- Question 3 uses movie release year, not rating timestamp.
- Question 4 shows the top 5 after applying the rating-count floor and supports comparing 50 vs. 150.
- At least 1–2 interactive controls work.
- All charts have clear titles and labels.
- `requirements.txt` contains the needed dependencies.
- The application uses repository-relative paths.
- The app can reasonably be deployed on Streamlit Community Cloud.
- The build log contains only genuine prompts and changes.
- No next-week audit/report material has been unnecessarily embedded in the dashboard.
```

### What the assistant produced and decided

- Inspected the actual CSV before building: 100,000 rows, 13 columns, 1,682 movies, 943 users; 1–5 integer ratings; release years 1922–1998.
- Verified dtypes: IDs/rating/age/rating_year are int64; year/decade are float64 with missing values; timestamp/title/genres and the other text fields are object/string columns. Timestamp values are date/time text.
- Found actual ID names `user_id` and `movie_id`, rather than the prompt's camelCase. Used these fields and added explicit alias support for camelCase input. Unused demographic/derived columns were not added to the analyses.
- Found 30 missing release years across five movies, no exact duplicate rows or repeated user/movie pairs, and consistent movie metadata.
- Used the student's preferred distinct-movie genre counts, with each movie once per applicable genre; used rating-level genre means.
- Chose horizontal bars for Questions 1, 2, and 4 and a release-year line chart for Question 3. Used Altair throughout, with meaningful sorting, explicit axes, zero-baseline bars, and rating-count tooltips.
- Retained literal `unknown` genres under the visible label Unknown / unlisted. This category has the lowest mean; the app also identifies Fantasy as the lowest listed genre. No unknown-genre ratings were discarded.
- Excluded missing years only from Question 3, without inferring years from titles or timestamps. The conventional valid-year range is whole-number 1888 through the current year. The supplied nonmissing years all pass it.
- Implemented the year-range slider for Question 3 and a 50/150 rating-count radio selector for Question 4, with both rankings also displayed together and a computed description of which movies leave/enter.
- Ranked using unrounded mean descending, count descending, title ascending, then ID ascending.
- Added visible data-handling notes and empty/error states. Future bad IDs/ratings, exact duplicates, blank/repeated genre tokens, missing titles, unknown genre labels, and inconsistent metadata have explicit handling.
- Produced `app.py`, `requirements.txt`, the unchanged CSV copy, `README.md`, `.gitignore`, this log, and a small reproducible `validate_app.py`. The README includes local startup, Git commands, deployment steps, and a public-URL checklist.
- Cached loading/preprocessing with the CSV modification time in the cache key. Used the CSV beside `app.py`, with no machine-specific path in app code.
- Added no future audit/write-up section to the dashboard.

### Real issues encountered and corrections

These were assistant-discovered development issues, not feedback from the student:

1. The initial inspection printed the actual schema but then attempted `data.movieId`, which raised an AttributeError because the uploaded CSV uses `movie_id`. The assistant reran inspection with the verified column names. This discrepancy was explained before app implementation.
2. Streamlit and Altair were initially absent. The assistant installed the exact direct versions recorded in `requirements.txt`; pandas 2.2.3 was already available.
3. An exploratory AppTest script searched for chart elements named `arrow_vega_lite_chart`. Streamlit 1.55 exposes them as `vega_lite_chart`, so the exploratory script raised an IndexError after correctly loading the app. The assistant corrected the inspection and the reproducible validation script. This was a test-harness issue, not an app failure.
4. A Playwright browser screenshot attempt failed because Chromium was not installed. Its installation then failed because the downloaded archive was invalid/truncated. No screenshot or visual browser verification is claimed.
5. Separate-tool-call HTTP health probes received connection refused even after Streamlit printed its startup URLs. The cause was not established. A subsequent check launched the server and probed it within the same process; its result is recorded below.

### Checks completed

- Syntax compilation of `app.py` passed.
- Launched a local Streamlit server and received HTTP 200 with body `ok` from its health endpoint when server startup and probing ran in the same process. This is a startup check, not a browser visual check.
- SHA-256 checks confirmed the project CSV exactly matches the supplied file: `a94b2f45766f49911985efdc5eb2e5c266be5bf4c0dac7872c2cc7ed6f29358d`.
- All seven checks in `python validate_app.py` passed on Python 3.12.14, Streamlit 1.55.0, pandas 2.2.3, and Altair 5.5.0.
- An independent CSV row-by-row calculation matched genre counts, genre means/counts, yearly means/counts, and per-movie means/counts.
- Question 1 counts unique movies with multi-genre overlap; duplicate genre tokens cannot double-count a movie.
- Question 2 shows rating-level genre means, sorted descending, with clear sample-size caveats.
- Question 3 uses release years. Exactly 99,970 ratings contribute across the full valid-year range. Changing the slider to 1990–1998 updates the chart to 69,452 ratings across nine years.
- Question 4 applies the floor before ranking. Checked movie IDs at 50: 408, 318, 169, 483, 114; at 150: 318, 483, 64, 603, 12. Answers are computed at runtime, not hard-coded into the app.
- The AppTest runner changed both widgets and verified affected output changes, including switching the threshold back to 50.
- Chart specifications contain titles and x/y axis titles.
- Fixtures exercised malformed/missing/fractional years, invalid ratings, missing/empty/repeated genre tokens, exact duplicates, schema problems, metadata conflicts, tie breaking, empty year ranges, no qualifying movies, and all missing years.
- Requirements contain all three direct dependencies; app loading is relative to the app file. The repository structure matches Community Cloud documentation.
- Actual browser rendering and actual Community Cloud deployment remain unverified. The student should inspect the public deployment before submitting it.

### Issues noticed by the student

None reported yet.

### Student-requested changes and reasons

None after the initial prompt yet. Implementation decisions and assistant-side corrections above belong to this first iteration; they are not fabricated student revisions.

## Future iterations

Append the actual user request verbatim, the change made, any real observed issue, the reason for the requested change, and the checks performed. Do not invent prompts, approval, feedback, or verification.


## Iteration 2 — Add the project to the existing CTP fork, October 1, 2026

### Exact user request

```text
can you update my fork of the ctp data science and upload the project there? I'd like you to create a folder under week 4.
```

### What changed and why

- Verified the connected account is `stalris` and the repository is the user's public fork `stalris/ds-fall-2026`, with write access.
- Compared fork `main` and `CUNYTechPrep/ds-fall-2026` `main`: both pointed to `f7e448650f9caf4df679c2b2683c23aa7a8d4320`, so no upstream sync was needed.
- Located the existing `Week-04-Vibe-Coding-101` folder and reviewed its assignment instructions. No AGENTS.md files were present in the repository tree.
- Prepared all seven project files under `Week-04-Vibe-Coding-101/Salvador_Cardoso_MovieLens_Dashboard`, as requested, preserving other repository files.
- Verified that the CSV already in the course repository exactly matches the uploaded CSV by Git blob SHA `714060e428be70db85772a63d653450ef1a43faf`. Reused that identical blob for the project's adjacent CSV.
- Adapted this folder's README for the existing fork, future updates, and the full nested Streamlit deployment entrypoint. No app calculations or controls changed.
- Appended this real request and the work performed to the build log.

### Issues noticed by the student

No bug reported. The student requested a different repository destination: their existing CTP fork instead of a new standalone repository.

### Checks

- All seven checks passed again from the nested project folder; syntax compilation passed. Both widgets and all four calculations were rechecked before publication.
- The GitHub commit and repository history provide the publication record; no Community Cloud deployment is claimed by this iteration.
