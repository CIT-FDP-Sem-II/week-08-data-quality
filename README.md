# Week 8 — Data Quality and Real Datasets

**CIT AI-Native Engineering Program · Year 1 · Semester 2 · Module M3**

Garbage in, garbage out is not a cliché — it is the reason an AI system that
passed every test in Week 3 can still be wrong about everything. This week is
about the data underneath.

**Lab time: 2 hours. API calls: 0.** See [LAB.md](LAB.md).

## Contents

| Path | What it is |
|---|---|
| `tools/make_messy_data.py` | Generates the dataset, with every fault planted on a fixed seed |
| `data/enrolments_raw.csv` | 316 rows, 13 faults, 5 categories |
| `data/PLANTED_FAULTS.md` | **Answer key — do not read until the audit is done** |
| `worksheets/data-audit.md` | Find every fault before touching the data |
| `CLEANING_PLAN.md` | The cleaning plan, written as a spec, with the decisions |
| `src/clean.py` | The pipeline — one function per step of the plan |
| `tests/` | 15 tests. No API key needed. |

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # mac/linux: source .venv/bin/activate
pip install -r requirements.txt

python tools/make_messy_data.py       # build the dataset
python src/clean.py                   # clean it
python -m pytest tests -v             # 15 tests
```

> Everything in this repo runs offline and is **verified**. There are no API
> calls this week.

## What the pipeline produces

```
DATA QUALITY SUMMARY
========================================================
rows in                                  316
rows out                                 306
exact duplicates removed                  10
near-duplicates (reported only)            6
distinct courses before                   12
distinct courses after                     3
ambiguous dates (UK/US unresolvable)      57

impossible values nulled
  age                                       5
  final_grade                               3
  fee_paid                                  1
```

`rows_in - rows_out` equals exactly the duplicate count. **Cleaning removes
errors, not data.** Impossible values were nulled, not deleted — a student
with an age of 999 still has a valid grade and fee, and dropping the row
throws away four good values to remove one bad one.

## The order is the lesson

```
strip -> nulls -> types -> categories -> dates -> duplicates -> impossible
```

Deduplicating before stripping whitespace keeps every row that differs only by
a stray space. There is a test for exactly this
(`test_stripping_must_happen_before_deduplicating`).

Nulling impossible values before fixing types fails, because `"Rs 48,000"` has
no opinion about being negative.

## Four decisions worth defending

| Decision | Why |
|---|---|
| **Do not impute** missing grades | Filling 18 with the mean invents those students' performance. Week 9's distribution would then measure our arithmetic |
| **Map courses explicitly**, do not lowercase | `"CS"` lowercases to `"cs"`, not to `"computer science"`. The map is longer and is the only version that is right — and it leaves an unexpected spelling null rather than silently creating a new category |
| **Report near-duplicates**, do not drop them | We do not know if they are a broken export or two real records. Silently deleting real data is worse than the duplicate |
| **Null impossible values**, do not drop rows | One bad cell should not cost four good ones |

## The fault with no fix

57 rows have a date like `03/04/2025`. That is 3 April or 4 March and
**nothing in the data can tell you which**. No parser resolves it. No regex
helps.

The pipeline parses day-first, counts the ambiguous rows, and **reports the
number**. The number is the finding. Anyone doing monthly analysis on this
column needs to know that 57 of 306 rows might be in the wrong month.

Most data quality problems have a fix. Some only have a disclosure, and
knowing the difference is the week's real content.

## Two things that lie to you

**`isna()` lies** before step 2. `campus` has twelve rows reading `"N/A"` —
text, not a null. `df.isna().sum()` reports 0 and every count you build on it
is wrong.

**`duplicated()` tells the truth but not the whole truth.** It finds the 10
exact duplicates. Six more rows differ only in the case of an email address;
to a computer those are different strings.

---

## Set B (non-IT background)

**`tools/make_messy_data.py`** — builds the dataset. Creates 300 plausible
student records, then deliberately damages some of them: blanks out grades,
writes `"N/A"` into campuses, puts impossible ages in, copies some rows to
make duplicates, and writes the same course name four different ways. The
fixed `SEED` means everyone gets an identical file.

**`src/clean.py`** — one function per cleaning step.

- `strip_and_fix_encoding(df)` — removes spaces from the ends of text, and
  replaces two invisible characters (a non-breaking space and a curly
  apostrophe) with ordinary ones. First, because every later step compares
  text.
- `convert_missing_disguises(df)` — replaces `"N/A"`, `""` and `"   "` with
  real nulls, so the computer knows they are missing.
- `fix_types(df)` — turns `"Rs 48,000"` into the number `48000` by removing
  the symbols and commas.
- `standardise_courses(df)` — looks each course up in a table and replaces it
  with the one agreed spelling.
- `parse_dates(df)` — turns the four date formats into real dates, and counts
  how many are genuinely impossible to read correctly.
- `remove_duplicates(df)` — deletes rows that are exactly identical, and
  *counts* rows that are nearly identical without deleting them.
- `null_impossible_values(df)` — blanks out values that cannot be true (an age
  of 999), keeping the rest of the row.
- `clean(df)` — calls all of the above in order and collects the numbers.
- `summary_table(report)` — formats those numbers into the before/after table.

### What Set B may simplify

- Describe each step in **plain-language comments** — what it does and why.
  That is the Set B requirement in place of formal documentation.
- You may find **8 of the 13 faults** rather than all of them, provided your
  eight span at least four of the five categories.
- The provenance section may be answered in a short paragraph.

### What Set B may **not** simplify

- The cleaning plan must be **written before the code**.
- Every step needs a stated **reason**, not just an action.
- The before/after summary table is required in both sets.
