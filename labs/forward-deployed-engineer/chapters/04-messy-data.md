:::step{type=story title="The export you were promised, and the one you got"}
In week one, Deccan Shield's IT team gave you a tidy CSV for the baseline. In week two you ask for the real thing: the
file the branches actually send every Monday, the one Claimdesk will read in production.

It arrives as `data/claims_export_raw.csv`. The first rows:

```text
claim_id,received,amount,vehicle,channel
DS-26-10038,2026-07-02,34500.00,two-wheeler,email
DS-26-10011,02/07/2026,"₹ 3,37,500",commercial,email
DS-26-10097,04 Jul 2026,"Rs 21,500",two-wheeler,email
DS-26-10201,2026-07-05,36500,two-wheeler,email
DS-26-10201,2026-07-05,36500,two-wheeler,email
```

Three different ways to write a date in five lines. Rupees with "Rs", with "₹", with paise, with commas in two
different places. And claim DS-26-10201 twice. Nobody did anything wrong: different branches use different software,
and the export job sometimes runs twice.

This is normal. Every FDE engagement has a moment when the real data arrives and it is messier than the demo data.
Your job is to read it **correctly**, and to say clearly what you could not read. In this chapter you clean the real
export.

:::mission
Read rupees written four different ways, and turn the raw export into one clean row per claim, with every rejected
row and its reason listed.
:::
:::

:::step{type=concept title="Why messy data is dangerous, not just annoying"}
Messy data rarely crashes a program. That is the danger. It usually produces **wrong numbers that look right**.

Two examples from this very file:

1. **Dates.** `02/07/2026` is 2 July in India, where the day comes first. In the United States the same text means
   February 7. Python's date parser does whatever format you give it. Read with the American format, the claim moves five
   months and the baseline of chapter 1 is silently wrong.
2. **Duplicates.** DS-26-10201 appears twice. Count both and the claims volume, the adjuster hours, everything grows a
   little. Nobody notices until the totals disagree with the insurer's finance report.

So cleaning has two jobs:

- **read every value the way its writer meant it**, and
- **reject what cannot be read, with a reason**, instead of guessing.

A rejected row is not a failure. It is information you send back to the people who own the data: "two rows had no
amount, here are the claim ids." That conversation is part of the FDE's work.

Check yourself: why not treat a blank amount as Rs 0? Because nobody claimed Rs 0. A zero would quietly pull the
averages down and hide that the branch forgot to type the amount.
:::

:::step{type=history title="Garbage in, garbage out"}
:::before{title="Before: trusting what the machine printed"}
When the first business computers arrived, people tended to trust their output simply because a machine had produced
it. Programmers knew better: the machine only computes what it is given.
:::

The phrase **"garbage in, garbage out"** (GIGO) appeared in print in 1957, in a newspaper article about US Army
mathematicians working with early computers, and is often credited to George Fuechsel, an IBM programmer and
instructor of that era. It means: if the input is wrong, the output will be wrong, however good the program.

In those years every record reached the computer through a person at a keypunch, turning a paper form into holes in a
card. These women at the US Social Security Administration punched millions of earnings records. One wrong hole, and the
machine would faithfully compute with it: garbage in, garbage out.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-cardpunch.webp" alt="A black and white photo of a large office with rows of women seated at card punch machines, papers stacked beside them." credit="U.S. Social Security Administration (photographer not credited)" license="Public domain" source="https://commons.wikimedia.org/wiki/File:SocialSecurity.cardpunching.ssa.jpg"}
Card punch operators at the US Social Security Administration, from the late 1930s on.
:::

Dates got their own fix. In 1988 the International Organization for Standardization published **ISO 8601**, which writes
dates largest unit first: `2026-07-02`. It cannot be confused between countries, and it sorts correctly as plain text,
which is why databases and APIs use it (and why this course stores every date that way after reading it).

:::solved
Clean and check data at the edge of the system, once, so everything after it can trust it.
:::

:::timeline
- **1957** "Garbage in, garbage out" appears in print.
- **1988** ISO 8601 standardises dates as year, month, day.
- **Today** Data cleaning is often said to take more of a data project's time than modelling.
:::

:::funfact
ISO 8601 also covers times and durations. `P3D` means "a period of 3 days".
:::
:::

:::step{type=example title="Worked example: reading a number that is not yet a number"}
This is only to read; it is not in your project. Python's `int()` is strict:

```text
>>> int("Rs 21,500")
ValueError: invalid literal for int() with base 10: 'Rs 21,500'
>>> int("34500.00")
ValueError: invalid literal for int() with base 10: '34500.00'
```

Both errors are real (we ran them in the lab image). The fix is to remove what is not part of the number, then read it
in a form that accepts a decimal point:

```python
def weight_kg(text):
    t = text.replace("kg", "").replace(",", "").strip()
    if not t:
        return None
    try:
        return int(float(t))
    except ValueError:
        return None

print(weight_kg("1,250 kg"))  # 1250
print(weight_kg("12.00"))     # 12
print(weight_kg(""))          # None
print(weight_kg("heavy"))     # None
```

- `replace` removes the unit and **every** comma, wherever it is (Indian amounts put commas after the lakh too:
  `3,37,500`).
- `strip()` removes spaces at both ends.
- An empty result means nothing was written: return `None`, not 0.
- `float(t)` accepts `"12.00"`; `int(...)` then drops the zeros after the point.
- `try ... except ValueError` turns unreadable text ("heavy") into `None` instead of a crash.
:::

:::step{type=predict title="Guess first"}
:::question
`datetime.strptime("02/07/2026", "%m/%d/%Y")` reads the text month first. Which date does it give?
:::
- [ ] 2 July 2026
- [x] 7 February 2026
- [ ] It raises an error
:::explain
We ran it: `2026-02-07 (month first)`. No error, just the wrong date. With `"%d/%m/%Y"` it is `2026-07-02`. A date like
`31/07/2026` would fail month first (`ValueError: time data '31/07/2026' does not match format '%m/%d/%Y'`), but
`02/07/2026` does not, so you cannot rely on errors to catch the mix-up.
:::
:::

:::step{type=try title="Nothing is clean yet"}
```text
$ python clean.py
rows in the export: 245
clean claims: 0
rejected: 0 {}
   'Rs 21,500' -> None
  '₹ 3,37,500' -> None
    '34500.00' -> None
       '36500' -> None
            '' -> None
```

245 rows, and no amount can be read yet. `parse_date` is already written for you (lines 15 to 22 of `clean.py`): it
tries the three formats the export uses, always day first, and returns `None` if none fits. Your work is the amounts and
the cleaning.
:::

:::step{type=task task=parse_amount title="Your turn: read rupees written four ways"}
In `parse_amount`:

1. Remove `"Rs"`, `"₹"` and every comma, then strip the spaces.
2. If nothing is left, return `None`.
3. Otherwise read the rest with `float()` and return it as an `int`.
4. If it is not a number at all, return `None` (catch the `ValueError`).

The check includes an amount in crores (`Rs 1,23,45,678`), a blank, and `N/A`. Press **Check**.
:::

:::step{type=concept title="One row per claim, and a reason for every rejection" file="04-messy-data/clean.py" line="32-38"}
Now the whole export. `clean_export` goes through the rows in order and sorts each into **clean** or **rejected**:

| Situation | What happens | Why |
|---|---|---|
| a claim id already seen | rejected, `"duplicate"` | the export job ran twice; keep the first copy |
| the date cannot be read | rejected, `"bad date"` | a wrong date would move the claim in time |
| the amount is blank or unreadable | rejected, `"no amount"` | a claim without an amount cannot be assessed |
| everything readable | clean | `received` becomes a real `date`, `amount_rs` an `int` |

To spot duplicates, keep a **set** of the ids you have seen. A set answers "have I seen this?" instantly, however many
ids it holds:

```python
seen = set()
if cid in seen:
    ...  # a duplicate
seen.add(cid)
```

Remember the id **before** parsing the rest. Then a second copy of a broken row is reported as a duplicate, not as a
second broken row, which matches what really happened.

Check the date before the amount, so the reason is always the first problem in the row. A reason list your customer
can act on is worth more than a clever fix you made silently.
:::

:::step{type=task task=clean_export title="Your turn: clean the real export"}
In `clean_export`:

1. Keep a set of seen claim ids. A row whose id is already in it is rejected as `"duplicate"`.
2. Otherwise add the id to the set, then parse the date (`parse_date`) and the amount (`parse_amount`).
3. A `None` date is rejected as `"bad date"`; a `None` amount as `"no amount"` (check the date first).
4. Everything else becomes a clean dict with `claim_id`, `received` (the date), `amount_rs` (the int), `vehicle` and
   `channel`.
5. Return `(clean, rejected)`, where rejected is a list of `(claim_id, reason)`.

Press **Check**.
:::

:::step{type=try title="238 claims you can trust"}
```text
$ python clean.py
rows in the export: 245
clean claims: 238
rejected: 7 {'duplicate': 5, 'no amount': 2}
   'Rs 21,500' -> 21500
  '₹ 3,37,500' -> 337500
    '34500.00' -> 34500
       '36500' -> 36500
            '' -> None
```

245 rows became **238 claims**. Five rows were copies from the double-run export job, two had no amount. Every date was
readable, which is worth knowing too: the branches use three formats, but consistently.

The 238 is not the 240 of chapter 1: two claims are missing amounts in this export. Your Monday email to the IT team
writes itself: "Two claims arrived without an amount (ids attached). Five rows were sent twice; the export job may be
running two times."
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A claim row arrives with the amount `"N/A"`. What should the cleaner do?
:::
- [ ] Treat it as Rs 0
- [x] Reject the row as "no amount" and report it
- [ ] Guess the amount from similar claims
:::explain
Never invent data at the edge. Reject with a reason; the people who own the data can fix it, and your numbers stay honest.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why keep the first copy of a duplicate claim and reject the later ones?
:::
- [x] The copies are the same claim exported twice; counting it twice inflates every total
- [ ] The first copy is always more correct
- [ ] Python sets can only hold the first value
:::explain
Here the copies are identical, so either would do; what matters is counting the claim once. If copies ever differ, that
is a question for the IT team, not a choice for your code.
:::
:::

:::step{type=deep-dive title="Go deeper: cleaning data in production"}
**Validate at the edge.** Real pipelines clean once, where data enters, and everything after trusts the cleaned form.
Chapter 7 turns these rules into a formal data contract.

**Keep the raw file.** Store the original export unchanged next to the cleaned one, so any number can be traced back to
the exact row it came from. Auditors and angry customers both ask.

**Monitor the rejection rate.** Seven rejections a week is normal; seventy means something changed upstream (a new
branch system, a broken export). Alert on the rate, not just on crashes (chapter 20).

**Libraries.** For large files, teams use pandas or Polars, and schema tools such as pandera or Great Expectations. The
ideas are the same as here; only the scale changes.
:::

:::step{type=recap}
You can now:

- explain why messy data produces wrong numbers that look right;
- read amounts written in several formats, including Indian digit grouping, and refuse what is not a number;
- read day-first dates correctly, and know why the month-first mistake raises no error;
- clean an export into one row per claim, with a reason for every rejected row.

Next, chapter 5: the customer's database. The export is a copy; the policies live in a real database, and Claimdesk
needs to ask it questions safely.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-04-notes.webp" alt="Handwritten notes about cleaning messy data: Messy data gives wrong numbers that look right. Indian dates put the day first. Remove Rs, the rupee sign and commas, then read it. A blank amount is None, never zero. Keep the first copy of a duplicate. Every rejected row gets a reason." ai="true"}
One page of notes for this chapter.
:::
:::
