# Cleaning Plan — enrolments_raw.csv

**Written as a spec, before any code.** Same discipline as Module 2: decide
what you are going to do and how you will know it worked, then do it.

A cleaning script written without this becomes a list of pandas calls nobody
can justify six weeks later. Every step below says **what**, **why**, and
**how it is checked**.

---

## Order of operations, and why order matters

| # | Step | Why it must come here |
|---|------|------------------------|
| 1 | Strip whitespace and fix encoding | Everything downstream compares strings. `" Data Science "` and `"Data Science"` must be the same thing before you deduplicate or group |
| 2 | Convert "missing" disguises to real nulls | `"N/A"` and `"   "` are text. Until they are nulls, `isna()` lies to you and so does every count you report |
| 3 | Fix types | `fee_paid` is text with commas and currency symbols. You cannot check whether a fee is negative while it is a string |
| 4 | Standardise categories | Four spellings of one course become one |
| 5 | Parse dates | Needs step 1 done; produces the column step 7 validates |
| 6 | Remove duplicates | **After** standardising, or near-duplicates survive |
| 7 | Handle impossible values | **Last**, because "impossible" needs the right type to test |

Step 6 before step 1 is the classic mistake: `drop_duplicates()` on raw data
keeps every row that differs only by stray whitespace or capitalisation.

---

## Step 1 — Whitespace and encoding

**What:** strip leading/trailing whitespace from every text column; replace
non-breaking spaces (` `) with ordinary spaces; normalise the smart
apostrophe (`’`) to `'`.

**Why:** these are invisible in a spreadsheet and fatal to grouping. `"Priya "`
and `"Priya"` are different keys.

**Check:** no text value starts or ends with a space; no value contains
` ` or `’`.

---

## Step 2 — Missing values

**What:** convert `""`, `"   "`, `"N/A"`, `"n/a"`, `"NA"`, `"-"`, `"null"` to
a real null.

**Why:** a missing value disguised as text is worse than a missing value.
`df["campus"].isna().sum()` returns 0 while twelve rows have no campus, and
every downstream count is quietly wrong.

**Decision — do not impute.** We mark them and keep them. Filling a missing
grade with the mean would invent 18 students' performance, and the
distribution work in Week 9 would then be measuring our own arithmetic.
Imputation is a modelling decision, not a cleaning decision.

**Check:** no text column contains any of the disguise strings; null counts
are reported per column, before and after.

---

## Step 3 — Types

**What:** `fee_paid` → integer, by stripping `Rs`, commas and spaces.
`student_id` → integer. `final_grade` → float.

**Why:** `"Rs 48,000"`, `"48,000"` and `"48000"` are the same fee written
three ways, and none of them can be compared or summed as text.

**Check:** `fee_paid` has an integer dtype; every value is either null or a
whole number.

---

## Step 4 — Categories

**What:** map every spelling of a course to one canonical value:

| Raw | Canonical |
|---|---|
| `Data Science`, `data science`, `DATA SCIENCE`, `" Data Science "` | `Data Science` |
| `Computer Science`, `computer science`, `Comp Sci`, `CS` | `Computer Science` |
| `Engineering`, `engineering`, `ENGINEERING`, `Eng.` | `Engineering` |

**Why:** three courses reported as twelve. Any `groupby("course")` before
this is wrong, and wrong in a way that looks plausible.

**Decision — map explicitly, do not just lowercase.** Lowercasing turns
`"CS"` into `"cs"`, not into `"computer science"`. An explicit map is longer
and is the only version that is right. It also **fails loudly** on a spelling
nobody anticipated, instead of silently creating a thirteenth category.

**Check:** exactly three distinct course values after cleaning.

---

## Step 5 — Dates

**What:** parse `enrolled_on` into a real date. Four formats are present:
ISO (`2025-03-14`), UK (`14/03/2025`), US (`03/14/2025`) and long
(`14 Mar 2025`).

**Why:** sorting text dates gives nonsense, and `2025-03-14` sorts before
`14/03/2025` for reasons that have nothing to do with time.

**The honest problem — and this is the important one:** UK and US formats are
**genuinely ambiguous**. `03/04/2025` is 3 April or 4 March and nothing in the
data can tell you which. This is not solvable by a cleverer parser.

**Decision:** parse day-first, record how many rows were ambiguous
(day ≤ 12 and month ≤ 12), and **report that number in the data quality
summary**. The number is the finding. Anyone using this column for monthly
analysis needs to know how many rows might be in the wrong month.

**Check:** the column has a datetime dtype; the ambiguous-row count is
reported, not hidden.

---

## Step 6 — Duplicates

**What:** drop exact duplicate rows. Then look for near-duplicates — rows
identical except for case in `email`.

**Why:** 10 exact duplicates inflate every count by 3%. The 6 near-duplicates
are the interesting ones: `drop_duplicates()` will not touch them, because to
a computer `"TOM.SMITH@..."` and `"tom.smith@..."` are different strings.

**Decision:** drop exact duplicates automatically. **Report** near-duplicates
rather than dropping them, because two students can legitimately share a
`student_id` in a broken export and we do not know which case this is. A
cleaning step that silently deletes real data is worse than the duplicate.

**Check:** zero exact duplicates after; near-duplicate count reported.

---

## Step 7 — Impossible values

**What:** flag, do not delete.

| Column | Rule | Found |
|---|---|---|
| `age` | must be 16–80 | 0, 1, 150, 999 |
| `final_grade` | must be 0–100 | -10, 150.5, 200 |
| `fee_paid` | must be ≥ 0 | -32000 |

**Why:** these pass every type check. `age = 999` is a perfectly valid
integer. Only domain knowledge catches it, which is why this step cannot be
automated away.

**Decision — set to null, do not drop the row.** A student with an impossible
age still has a valid grade and fee. Dropping the row throws away four good
values to remove one bad one.

**Check:** after cleaning, no age outside 16–80, no grade outside 0–100, no
negative fee — and the count of values nulled is reported per column.

---

## What the pipeline must produce

1. `data/enrolments_clean.csv`
2. A **before/after data quality summary table** — rows, nulls per column,
   distinct courses, duplicates, impossible values
3. A record of **every decision above**, in the code, next to the step

## What success looks like

| Check | Target |
|---|---|
| Distinct courses | exactly 3 |
| Exact duplicate rows | 0 |
| Values disguised as missing (`N/A`, blank) | 0 |
| `fee_paid` dtype | integer |
| `enrolled_on` dtype | datetime |
| Ages outside 16–80 | 0 |
| Grades outside 0–100 | 0 |
| Rows lost | **0** — nothing is deleted except exact duplicates |

That last row is the one to defend in the write-up. **Cleaning should remove
errors, not data.**
