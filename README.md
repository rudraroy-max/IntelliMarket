# IntelliMarket

IntelliMarket compares marketplace listings, records price history, and presents
analytics through a Django JSON API and a Streamlit dashboard. Google Books
catalog data and cryptocurrency snapshots have separate tables in the same
SQLite market data database.

## Local setup

From the repository root, create a virtual environment with Python 3.12 or
3.13 using `python -m venv .venv`. Activate it with
`.venv\Scripts\Activate.ps1` on Windows or `source .venv/bin/activate` on
macOS or Linux. Then install the dependencies and start Django.

```sh
python -m pip install -r requirements.txt
python -m database.connection
python backend/manage.py migrate
python backend/manage.py runserver
```

In another terminal with the environment active, run
`python -m streamlit run dashboard/app.py`. The dashboard uses the local API
at `http://127.0.0.1:8000/api`.

Django uses `backend/db.sqlite3` for its own tables and `prices.db` for
market data. On an existing `prices.db`, apply the additive migrations before
using the new features. Each command creates a SQLite backup alongside the database.

```sh
python -m database.migrate_google_books
python -m database.migrate_crypto
```

Set `DJANGO_SECRET_KEY` to a stable secret for persistent sessions. The
development default generates a temporary key when none is provided. For a
deployment, set `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, and a comma-separated
`DJANGO_ALLOWED_HOSTS`.

## Ingestion and endpoints

- `python -m data_sources.run_ingestion` ingests Fake Store and Mock Marketplace.
  Add `--google-books-query "Python programming" --google-books-pages 2` to
  ingest books in the same run. Set `GOOGLE_BOOKS_API_KEY` if your Google Books
  access requires a key. Marketplace matching downloads the
  `all-MiniLM-L6-v2` model on first use when it is absent from the local cache.
- `GET /api/books/search/?q=python` searches Google Books. It accepts
  `start_index` and `page_size`.
- `GET /api/books/?q=python` searches the stored catalog.
- `GET /api/books/<volume_id>/price-history/` returns observed Google Books
  eBookstore prices in their reported currencies.
- Set `FREECRYPTO_API_KEY` before running
  `python -m data_sources.run_crypto_ingestion`. Set `CRYPTO_WATCHLIST` to
  comma-separated symbols or pass `--symbols BTC,ETH`. An external scheduler
  can invoke the same command. A failed run exits nonzero and retains
  successfully committed observations.

## Verification

```sh
python -m unittest discover -s data_sources/tests
python backend/manage.py test api
python backend/manage.py check
python -m compileall -q analytics backend dashboard data_sources database ml
```

`python test_hybrid_matcher.py` runs the original matching demonstration and
requires the model described above.
