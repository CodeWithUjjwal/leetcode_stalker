# LeetCode Stalker

A Python package to track and monitor LeetCode progress for a group of students. It fetches live stats from the LeetCode GraphQL API and stores them in a PostgreSQL database, giving you a clean historical record you can query at any time.

## Features

- Fetch and store daily LeetCode stats (total, easy, medium, hard solved) per student
- Track the last accepted-submission timestamp per student
- Safe to re-run: one snapshot per student per day, refreshed in place (upsert)
- Batch-friendly: students that can't be resolved are skipped so the rest of the run completes
- View stored progress as formatted, indexed tables (any `tabulate` style)
- Built-in queries for full history, latest snapshot, recent progress, overall growth, and date coverage
- SQL and GraphQL live in plain `.sql` / `.graphql` files, and table names come from environment variables, so the schema is easy to adapt

## Requirements

- Python 3.11+
- PostgreSQL
- See `requirements.txt` for Python dependencies

## Project Structure

```
leetcode_stalker/
├── __init__.py
├── _data_scraper.py
├── _data_viewer.py
├── config.py
├── .env.example
├── requirements.txt
├── LICENSE
├── db/
│   ├── migrations/
│   │   └── init.sql
│   └── sql/
│       ├── query_loader.py
│       └── queries/
└── graphql/
    ├── query_loader.py
    └── queries/
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/CodeWithUjjwal/leetcode_stalker.git
cd leetcode_stalker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable        | Description                                   |
|-----------------|-----------------------------------------------|
| `DB_NAME`       | PostgreSQL database name                      |
| `DB_USER`       | Database user                                 |
| `DB_PASSWORD`   | Database password                             |
| `DB_HOST`       | Database host (e.g. `localhost`)              |
| `DB_PORT`       | Database port (default: `5432`)               |
| `STUDENT_TABLE` | Table mapping student names to LeetCode IDs   |
| `STORAGE_TABLE` | Table storing daily fetched stats per student |

### 4. Set up the database

Make sure your PostgreSQL instance is running, then run the migration:

```bash
psql -U your_db_user -d your_db_name -f db/migrations/init.sql
```

This creates the following tables if they don't already exist:

**`students`** (`STUDENT_TABLE`)
```sql
CREATE TABLE IF NOT EXISTS students (
    student_name  TEXT PRIMARY KEY,
    leetid        TEXT NOT NULL
);
```

**`storage`** (`STORAGE_TABLE`)
```sql
CREATE TABLE IF NOT EXISTS storage (
    stat_date            DATE      NOT NULL,
    student_name         TEXT      NOT NULL,
    solved_all           INTEGER   NOT NULL,
    solved_easy          INTEGER   NOT NULL,
    solved_medium        INTEGER   NOT NULL,
    solved_hard          INTEGER   NOT NULL,
    last_submission_time TIMESTAMP NOT NULL,

    PRIMARY KEY (stat_date, student_name)
);
```

The composite primary key `(stat_date, student_name)` guarantees one row per student per day. Storing again on the same day updates that day's row instead of creating duplicates, so you can run the collector as often as you like.

> The table names above are the defaults from `.env.example`. If you change `STUDENT_TABLE` / `STORAGE_TABLE`, use the same names in your own copy of the migration.

## Usage

Run your scripts from the folder that contains the `leetcode_stalker/` directory, then import it:

```python
import leetcode_stalker as ls
```

### Storing data

```python
# Store by student name (looks up the LeetCode ID from the students table)
ls.store_by_name(["Alice", "Bob"])

# Store directly by mapping name -> LeetCode username
ls.store_by_leetcode_id({"Alice": "alice_lc", "Bob": "bob_lc"})

# Skip the confirmation table that is printed after a successful store
ls.store_by_name(["Alice", "Bob"], display_msg = False)
```

| Parameter     | Default | Description                                                     |
|---------------|---------|-----------------------------------------------------------------|
| `display_msg` | `True`  | Print today's stored stats as a table after a successful store  |

Notes on behaviour:

- **Name matching:** `store_by_name` title-cases each name (`"alice"` → `"Alice"`), so input is forgiving about capitalisation.
- **Resilient batches:** a student who isn't in the students table, isn't found on LeetCode, or has no accepted submissions yet is skipped, and everyone else is still processed and saved. Lookup problems on the LeetCode side print a short message naming the user.
- **Network handling:** requests use a 10-second timeout, and network, JSON and response-shape errors are caught per user.
- **Atomic writes:** all collected rows are committed atomically (the "A" in ACID), so a run is saved completely or not at all.

### Viewing data

```python
# Print a table directly to stdout
ls.print_data(ls.StudentStats.GET_ALL_STATS)

# Get a formatted string instead of printing
table = ls.format_data(ls.get_data(ls.StudentStats.GET_ALL_STATS))

# Get the raw QueryResult (behaves like a list of tuples, with a .headers attribute)
data = ls.get_data(ls.StudentStats.GET_OVERALL_PROGRESS)

# Look up a student's LeetCode profile link
ls.print_data(ls.StudentData.GET_LEETCODE_ID, params = ["Alice"])

# Query stats for a specific date
ls.print_data(ls.StudentStats.GET_STATS_BY_DATE, params = "2026-06-21")
```

Display options (available on `print_data` and `format_data`):

| Parameter     | Default        | Description                                                        |
|---------------|----------------|--------------------------------------------------------------------|
| `table_style` | `"fancy_grid"` | Any [`tabulate`](https://pypi.org/project/tabulate/) table format  |
| `show_index`  | `True`         | Show a `#` row-number column                                       |

```python
ls.print_data(ls.StudentStats.GET_LATEST_SAVED, table_style = "github", show_index = False)
```

Queries that take parameters accept a single value or a list of values. With a list, the query runs once per value and the rows are combined into one table, which makes batch lookups easy:

```python
ls.print_data(ls.StudentData.GET_LEETCODE_ID, params = ["Alice", "Bob"])
```

### Available queries

| Enum                                   | Params | Description                                                                       |
|----------------------------------------|--------|-----------------------------------------------------------------------------------|
| `ls.StudentStats.GET_ALL_STATS`        | —      | Every stored record, ordered by date then student                                 |
| `ls.StudentStats.GET_LATEST_SAVED`     | —      | The most recent day's snapshot for all students                                   |
| `ls.StudentStats.GET_STATS_BY_DATE`    | `date` | All records for a given date (`YYYY-MM-DD`)                                       |
| `ls.StudentStats.GET_RECENT_PROGRESS`  | —      | Change between each student's two most recent snapshots (works with any schedule) |
| `ls.StudentStats.GET_OVERALL_PROGRESS` | —      | Growth from each student's first to latest snapshot, including days elapsed       |
| `ls.StudentData.GET_LEETCODE_ID`       | `name` | A student's LeetCode profile link                                                 |
| `ls.InfoData.GET_STORED_STUDENTS`      | —      | Every tracked student with their number of stored entries                         |
| `ls.InfoData.GET_DATE_RANGE`           | —      | Continuous date ranges covered by stored data, which also shows any gaps          |

## Meta

```python
import leetcode_stalker as ls

print(ls.__author__)   # Ujjwal Gupta
print(ls.__url__)      # https://github.com/CodeWithUjjwal/leetcode_stalker
print(ls.__version__)  # 1.0.0
print(ls.__license__)  # MIT
```

## License

MIT — see [LICENSE](LICENSE) for details.