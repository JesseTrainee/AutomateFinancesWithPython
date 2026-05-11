# Copilot Instructions

## Project Overview
This repository is a personal finance dashboard built in Python with Streamlit. The main user flow is:

1. Import Nubank transaction CSV files.
2. Normalize transaction titles and remove unwanted rows.
3. Persist data into a local SQLite database.
4. Visualize expenses by category, month, and top expenses.
5. Optionally fetch invoice PDFs from Gmail and upload them to Google Drive.

The target user is an individual tracking personal expenses, not a multi-user SaaS or API product. The root README describes the project as heavily modified from Tech With Tim's AutomateFinancesWithPython example.

## Tech Stack
- Python 3.10.9 in a local `venv`.
- Streamlit 1.32.0 for the interactive UI in `main.py`.
- pandas 2.2.0 for CSV loading, date handling, grouping, and tabular output.
- Plotly 5.18.0 for the pie chart dashboard in `display_expense_dashboard`.
- matplotlib 3.10.6 for the horizontal bar chart in `show_dashboards`.
- NumPy 1.26.4 installed in the environment.
- SQLAlchemy 2.0.41 for ORM models, schema creation, updates, and SQLite connectivity in `src/models.py`.
- SQLite via `sqlite:///finances.db` as the local database.
- Google APIs for OAuth and integrations:
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`
  - `google-api-python-client`
- Streamlit theme configuration in `.streamlit/config.toml`.

Important dependency note:
- `requirements.txt` pins `streamlit`, `pandas`, `plotly`, `numpy`, and Google libraries.
- The code also imports `sqlalchemy` and `matplotlib`, but they are not listed in `requirements.txt`. If you recreate the environment from scratch, install them explicitly.

## Architecture
This is a small monolithic Python application with loose layering.

Folder responsibilities:
- `main.py`: Streamlit UI, tab layout, filters, upload flow, dashboards, and category editing.
- `src/models.py`: SQLAlchemy models and persistence logic for categories, transactions, and keywords.
- `src/utils.py`: CSV discovery/loading helpers and date defaults.
- `src/normalize.py`: transaction-title normalization rules.
- `drive_gmail_sync.py`: OAuth login plus Gmail download and Google Drive upload workflow.
- `data/`: sample CSV exports and downloaded PDF invoices.
- `.streamlit/config.toml`: UI theme.
- `test.py`: ad hoc database inspection script, not a formal automated test suite.

Application flow:
- `main.py` calls `src.models.create_tables()` at import time to ensure tables exist.
- Uploaded CSV files are read by `src.utils.load_transactions()`.
- The DataFrame is normalized by `src.normalize.title_normalize()`.
- Transactions are saved through `src.models.save_transactions()` into `finances.db`.
- Reads for the UI come from `src.models.get_transactions_data()` and `src.models.get_categories()`.
- Category edits in the Streamlit data editor are applied through `add_category_to_transaction()`, `src.models.add_keyword_to_category()`, and `src.models.update_transactions()`.
- Gmail/Drive sync is triggered from the UI button that calls `sincronizar_faturas()` from `drive_gmail_sync.py`.

There is no API layer, background worker, Docker setup, CI pipeline, or migrations directory in this repository.

## Coding Conventions
Observed conventions in the current codebase:
- Use `snake_case` for functions and variables: `save_transactions`, `display_expense_summary`, `buscar_faturas`.
- Use `PascalCase` for SQLAlchemy model classes: `Category`, `Transaction`, `Keyword`.
- Keep user-facing UI logic in `main.py` and persistence logic in `src/models.py`.
- Keep lightweight data cleanup rules in dedicated helpers such as `src/normalize.py` rather than embedding all transforms inline.
- Use pandas DataFrames as the main exchange object between ingestion, normalization, persistence reads, and dashboards.
- Existing code mixes English and Portuguese in identifiers and labels. Preserve the local style of the file you are editing instead of forcing a global rename.
- Existing Streamlit code relies heavily on reruns and `st.session_state`; when adding new UI flows, stay compatible with that pattern.

Patterns already present:
- A module-level SQLAlchemy `engine`, `Session`, and global `session` in `src/models.py`.
- ORM reads plus `pandas.read_sql(...)` for converting select statements to DataFrames.
- Streamlit tabs for major sections: summary, dashboard, categories, and upload.
- Inline business actions inside UI callbacks, for example the upload and category application flows.

Patterns to avoid unless you are intentionally refactoring:
- Do not introduce a new framework or layered abstraction that does not match the repo size.
- Do not assume there is an `.env` loader or secrets manager; the current Google integration uses local files and a hardcoded Drive folder ID.
- Do not add raw SQL or migrations unless the task explicitly requires a database refactor.
- Do not move database logic into `main.py`; keep it in `src/models.py` or a nearby `src/` module.

Data assumptions that matter:
- CSV imports are expected to contain at least `date`, `title`, and `amount` columns.
- `src.normalize.title_normalize()` removes rows where `title` is `Pagamento recebido` or `Estorno`.
- Installment suffixes like `- Parcela 1/12` are stripped from titles before persistence.
- Default category creation falls back to `Uncategorized`.

## Key Files and Entry Points
- `main.py`: primary entry point for the Streamlit app.
- `drive_gmail_sync.py`: secondary executable entry point for Gmail/Drive sync via `if __name__ == "__main__":`.
- `src/models.py`: database schema and persistence functions.
- `src/utils.py`: CSV loading and default date-range helper.
- `src/normalize.py`: title normalization rules.
- `requirements.txt`: pinned dependencies, but currently incomplete relative to the imports used.
- `.streamlit/config.toml`: Streamlit theme values.
- `README.md`: product intent and future ideas.
- `finances.db`: local SQLite database file used by the app.
- `credentials.json` and `token.json`: Google OAuth credential files used by `drive_gmail_sync.py`.

Most important functions to know before editing:
- `main()` in `main.py`
- `handle_file_upload()` in `main.py`
- `show_dashboards()` in `main.py`
- `create_tables()` in `src/models.py`
- `save_transactions()` in `src/models.py`
- `get_transactions_data()` in `src/models.py`
- `title_normalize()` in `src/normalize.py`
- `sincronizar_faturas()` in `drive_gmail_sync.py`

## Database
- Engine: SQLite.
- Connection string: `sqlite:///finances.db` in `src/models.py`.
- ORM: SQLAlchemy ORM, not raw sqlite3.
- Schema creation: `Base.metadata.create_all(engine)` inside `create_tables()`.
- Migration strategy: none. There is no Alembic, migrations folder, or schema versioning process.

Current ORM tables:
- `categories`
  - `id`
  - `name` unique, non-null
- `transactions`
  - `id`
  - `date`
  - `title`
  - `amount`
  - `category_id` foreign key to `categories.id`
- `keywords`
  - `id`
  - `word` unique, non-null
  - `category_id` foreign key to `categories.id`

Relationship model:
- One `Category` has many `Transaction` rows.
- One `Category` has many `Keyword` rows.
- `delete_category()` currently deletes a category object directly; be careful changing category deletion because transaction rows reference categories and only keyword relationships have explicit cascade configured.

Query style:
- SQLAlchemy ORM queries for entity lookup.
- `select(...)` plus `pandas.read_sql(...)` when returning tabular results.
- `update(Transaction)` for bulk category updates in `update_transactions()`.

## Testing
There is no formal automated test framework configured in this repository.

What exists today:
- `test.py` is a manual inspection script that connects to `finances.db` and prints table names and category columns.
- There are no `pytest` tests, `unittest` suites, fixtures, or CI test jobs.

Testing guidance for contributions:
- For UI changes, validate by running the Streamlit app and exercising upload, filters, category edits, and dashboard rendering.
- For database changes, verify table creation and query behavior against `finances.db`.
- For Gmail/Drive changes, keep testing isolated because the flow depends on live Google OAuth credentials and local token state.

## Common Commands
Set up the local environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install SQLAlchemy matplotlib
```

Run the Streamlit dashboard:

```bash
streamlit run main.py
```

Run the Gmail and Drive sync script directly:

```bash
python drive_gmail_sync.py
```

Run the manual database inspection script:

```bash
python test.py
```

Useful repo-local Python invocations when not activating the venv:

```bash
/home/jesse/applications/python/AutomateFinancesWithPython/.venv/bin/python drive_gmail_sync.py
/home/jesse/applications/python/AutomateFinancesWithPython/.venv/bin/python test.py
```

There are no `Makefile`, `package.json` scripts, Docker commands, migration commands, or deploy scripts in this repository.

## Environment Setup
Local files and state expected by the project:
- `.venv/` Python virtual environment.
- `finances.db` SQLite database in the repository root.
- `credentials.json` from Google Cloud Console.
- `token.json` generated after the first OAuth login.
- `data/` directory for CSV imports and downloaded invoice PDFs.

Google integration setup:
- `drive_gmail_sync.py` uses `InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)`.
- Required scopes are Gmail read-only and Drive file access.
- The Google Drive target folder is controlled by the hardcoded `PASTA_DRIVE_ID` constant in `drive_gmail_sync.py`.

Configuration gaps to be aware of:
- There is no `.env.example`.
- There is no environment-variable based configuration layer.
- Secrets are file-based, not injected from the shell.

If you add configuration, prefer a minimal and explicit approach that fits the current project size.

## Important Rules for Copilot
- Treat this as a local personal-finance Streamlit app, not as an API server or enterprise architecture.
- Keep edits small and consistent with the current monolithic layout unless the task explicitly requests refactoring.
- Preserve the current database location and SQLAlchemy model names unless a change request specifically targets persistence.
- Assume uploaded CSVs follow the existing `date` / `title` / `amount` format used by `src.utils.load_transactions()` and `src.normalize.title_normalize()`.
- When touching categorization logic, check the keyword flow in `add_keyword_to_category()` and `update_transactions()` before adding duplicate logic elsewhere.
- When touching Google sync, keep OAuth file handling compatible with `credentials.json` and `token.json` in the repository root.
- Do not invent missing infrastructure. There is currently no Docker, CI, `.env` loading, migrations tool, REST API, or formal test runner.
- If you change dependencies, update `requirements.txt` so it matches actual imports. This is currently needed for at least `SQLAlchemy` and `matplotlib`.
- Be careful with credential and token files. Do not log secrets or hardcode additional sensitive values.
- If you add new modules, prefer placing reusable data logic under `src/` and keeping Streamlit rendering code in `main.py`.