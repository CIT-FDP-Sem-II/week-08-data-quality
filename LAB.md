# Week 8 Lab — Data Quality and Real Datasets

**Time: 2 hours · API calls used: 0**

| # | Activity | Time | Code? |
|---|----------|------|-------|
| 1 | Audit the dataset — find every fault | 25 min | run only |
| 2 | Write the cleaning plan as a spec | 25 min | no |
| 3 | Build the pipeline | 40 min | yes |
| 4 | Before/after summary and provenance | 20 min | no |
| 5 | Check the answer key | 10 min | no |

---

## 1. Audit the dataset (25 min)

```powershell
pip install -r requirements.txt
python tools/make_messy_data.py
```

Open `worksheets/data-audit.md` and find **every** quality problem **before
touching the data**.

A complete audit finds **13 faults across 5 categories**. Fewer than 8 means
you have read the summary statistics but not the data.

Three questions the worksheet forces, and they are the whole lab:

1. **Does `isna()` tell the truth here?** Run it on `campus`. Now run
   `value_counts()`. They disagree, and nothing warns you.
2. **Does `duplicated()` tell the *whole* truth?** It returns a correct
   number. It is not a complete number.
3. **Is there a fault here that cannot be fixed?** Look at `enrolled_on`.

**Do not open `data/PLANTED_FAULTS.md` yet.**

---

## 2. Write the cleaning plan as a spec (25 min, no code)

Before any pandas. Same discipline as Module 2: decide what you will do and
how you will know it worked.

For each step: **what**, **why**, and **how it is checked**.

Read [CLEANING_PLAN.md](CLEANING_PLAN.md) after you have attempted your own.
The thing to compare is not the steps — most people get those — but the
**order**, and the **decisions**:

| Decision | The plan's answer |
|---|---|
| Impute missing grades? | **No.** Inventing 18 students' performance makes Week 9 measure our arithmetic |
| Lowercase the courses? | **No.** `"CS"` lowercases to `"cs"`, not to `"computer science"` |
| Drop near-duplicates? | **No.** Report them. We do not know if they are real |
| Drop rows with impossible ages? | **No.** Null the cell. The grade and fee are still good |

**Order matters most.** Deduplicating before stripping whitespace keeps every
row that differs only by a stray space. There is a test for this.

---

## 3. Build the pipeline (40 min)

```powershell
python src/clean.py
```

One function per step of the plan, in the plan's order:

```
strip -> nulls -> types -> categories -> dates -> duplicates -> impossible
```

**Document every decision in the code, next to the step.** In six weeks the
question will be "why does this lowercase the email but not the name?" and
the answer needs to be where the code is, not in a document nobody opens.

```powershell
python -m pytest tests -v     # 15 tests
```

---

## 4. Before/after summary and provenance (20 min, no code)

The pipeline prints the data quality summary. Copy it into your write-up and
answer:

- Which number changed most, and does that surprise you?
- `rows_in - rows_out` should equal exactly the exact-duplicate count.
  **Cleaning removes errors, not data.** Can you defend that?
- 57 dates are ambiguous. What does that mean for anyone doing monthly
  analysis on this column?

Then the provenance questions at the bottom of the audit worksheet. They
change what cleaning is *allowed* to do:

- Where did this come from, and who typed it in?
- What was it collected **for**?
- **Who is missing from it entirely?** A row never created cannot be found by
  any amount of auditing.
- What would a wrong conclusion cost, and who pays?

---

## 5. Check the answer key (10 min)

Now open [data/PLANTED_FAULTS.md](data/PLANTED_FAULTS.md).

| | Count | Which |
|---|---|---|
| Found | | |
| Missed | | |

The three most commonly missed are the near-duplicates, `"N/A"` as text, and
the date ambiguity. If you missed the third, you are in the majority — and it
is the one that matters most, because it is the fault with **no fix, only a
disclosure**.

---

## Before you leave

- [ ] Audit completed **before** reading the answer key
- [ ] 8+ of 13 faults found independently
- [ ] Cleaning plan written as a spec, with a reason per step
- [ ] Pipeline runs and produces `data/enrolments_clean.csv`
- [ ] Every decision documented **in the code**
- [ ] `python -m pytest tests` passes
- [ ] Before/after summary table in your write-up
- [ ] Provenance questions answered

## Looking ahead

Week 9 takes `enrolments_clean.csv` and does the distributional analysis. If
you imputed the missing grades today, Week 9's distribution is partly your own
arithmetic — which is exactly why the plan says not to.
