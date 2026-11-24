# Planted Faults — Answer Key

**Do not read this until you have finished the audit in
`worksheets/data-audit.md`.** The audit is the skill. Reading the key first
replaces it with a reading-comprehension exercise.

---

Every fault in `enrolments_raw.csv` was planted deliberately by
`tools/make_messy_data.py`, with a fixed seed so the whole cohort has the same
data.

| Category | Fault | Count | How to find it |
|---|---|---|---|
| **Completeness** | `final_grade` blank | 18 | `df.final_grade == ""` — **not** `isna()`, they are empty strings |
| | `campus` = `"N/A"` | 12 | `value_counts()` — it appears as a category |
| | `email` = whitespace only | 9 | `df.email.str.strip() == ""` |
| **Consistency** | `course` written 12 ways for 3 courses | 12 distinct | `df.course.unique()` |
| | `enrolled_on` in 4 date formats | all 316 rows | look at 20 raw values |
| | `fee_paid` as `"48000"`, `"Rs 48,000"`, `"48,000"` | all rows | `dtype` is object, not int |
| **Accuracy** | `age` of 0, 1, 150 or 999 | 5 planted | `df.age.describe()` — min and max |
| | `final_grade` of -10, 150.5 or 200 | 3 planted | `describe()` — outside 0–100 |
| | `fee_paid` of -32000 | 1 | `min()` after type conversion |
| **Uniqueness** | exact duplicate rows | 10 | `df.duplicated().sum()` |
| | near-duplicates (email case differs) | 6 | **`duplicated()` misses these** |
| **Encoding** | smart apostrophe `\u2019` in `last_name` | 7 | `df.last_name.str.contains("\u2019")` |
| | trailing non-breaking space in `first_name` | 5 | `df.first_name.str.contains("\u00a0")` |

Counts shift by one or two because the 16 duplicated rows were copied **after**
the faults were planted, so a duplicated row carries its fault twice. That is
realistic: real duplicates duplicate the errors too.

---

## The three most students miss

**1. The near-duplicates.** `drop_duplicates()` reports 10 and removes 10, and
everyone moves on. Six more rows differ only by the case of an email address.
To a computer those are different strings. This is the fault that teaches the
most, because the tool told you a true thing that was not the whole answer.

**2. `"N/A"` as text.** `df.isna().sum()` returns 0 for `campus`. Twelve rows
have no campus. Every count you report before fixing this is wrong, and
nothing warns you.

**3. The date ambiguity.** Most students parse the dates, see no error, and
move on. 70 rows are genuinely ambiguous between UK and US order and **no
parser can resolve them**. The right answer is not a cleverer regex — it is to
count them and report the number.

That third one is the week's real lesson. Some data quality problems have a
fix. Some only have a disclosure.

---

## What a complete audit looks like

- 13 distinct faults across 5 categories
- the near-duplicates found, not just the exact ones
- the date ambiguity identified as **unresolvable**, with a count
- a note that `isna()` is lying before step 2
