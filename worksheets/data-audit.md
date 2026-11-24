# Worksheet — Data Audit

**Find every quality problem before you touch the data.** (25 minutes)

Do not open `data/PLANTED_FAULTS.md` until you have finished.

```python
import pandas as pd
df = pd.read_csv("data/enrolments_raw.csv")

df.shape
df.dtypes
df.head(20)
df.describe()
df.isna().sum()
for col in df.columns:
    print(col, df[col].nunique())
df.course.value_counts()
df.duplicated().sum()
```

## The five categories

| Category | Question |
|---|---|
| **Completeness** | What is missing — including things that *look* present? |
| **Consistency** | Is the same thing written more than one way? |
| **Accuracy** | Are any values impossible? |
| **Uniqueness** | Are any rows repeated? |
| **Timeliness** | Is anything out of date or out of range? |

## Your findings

| # | Column | Category | Fault | How many | How you found it |
|---|--------|----------|-------|---------:|------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |
| 9 | | | | | |
| 10 | | | | | |

A complete audit finds **13 faults across 5 categories**. Fewer than 8 means
you have looked at the summary statistics but not at the data.

## Three questions to force before you stop

**1. Does `isna()` tell the truth here?**

> Run `df.isna().sum()`. Now run `df.campus.value_counts()`. Do they agree?

**2. Does `duplicated()` tell the whole truth?**

> It will report a number and the number will be correct. Is it complete?
> Try `df.assign(email=df.email.str.lower()).duplicated().sum()`.

**3. Is there a fault here that cannot be fixed?**

> Look at `enrolled_on`. Count the values of the form `dd/mm/yyyy` where both
> numbers are 12 or under. What do you actually know about those rows?

That third question is the one worth the most. Most data quality problems have
a fix. Some only have a disclosure.

## Provenance

Before cleaning anything, answer these — they change what cleaning is
*allowed* to do:

- Where did this data come from, and who typed it in?
- What was it collected **for**? (Data collected for billing has different
  blind spots from data collected for teaching.)
- Who is missing from it entirely? A row that was never created cannot be
  found by any amount of auditing.
- What would a wrong conclusion from this data cost, and who pays?
