# Claimdesk runbook

Claimdesk reads two-wheeler claim emails (up to Rs 50,000) and drafts "pay" or "refer" with reasons. An adjuster
decides every claim. Owner at Deccan Shield: the claims IT team (Priya). Business owner: head of claims (Meera).

## Run it

    export OPENAI_BASE_URL=...   OPENAI_API_KEY=...      (from the secrets store, never from this file)
    export PILOT_LIMIT_RS=50000  PROMPT_VERSION=v1        (optional; these are the defaults)
    python smoke.py                                        (3 known claims; exit code 0 means healthy)

## Before changing the prompt, the model or the rules

1. Change PROMPT_VERSION (the cache keys on it).
2. Run the evals on the golden set; the gate must pass (no field may fall).
3. Run the smoke test.

## Alerts and who acts

| Alert | Usually means | First step | Owner |
|---|---|---|---|
| p95 latency or errors up | the model provider is slow or down | check the provider's status page; drafts fall back to refer | claims IT |
| no-amount or refer rate up | the emails changed | read 10 recent emails; tell the head of claims | claims IT, then business |
| cost up | more traffic, or longer emails | compare tokens per call with last week | claims IT |

## Known limits

- Reads email text only; estimates in PDF attachments are not read (December finding).
- Names in emails are not redacted from log excerpts.
- The phrase list for instructions is a tripwire; the pilot limit and the adjuster are the real protection.

## Decisions (newest first)

- Thefts always go to the investigation team (shadow week).
- Years without a date are fixed in code against the email's arrival date (failure analysis).
- Pilot: two-wheelers, by email, up to Rs 50,000 (scoping, week one).
