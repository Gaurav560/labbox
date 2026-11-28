:::step{type=story title="How long did that take, and where does it run?"}
Two production questions arrive in the same week. A station screen feels slow: which requests are slow, and by how
much? And Lostdesk is about to run in three places, a laptop, a test server and the real one, each with a different
app name, photo limit and allowed website. Editing the code for each would be asking for mistakes.

Railways care about both: every platform has a clock everyone can trust, and every train carries its own timetable
without the station being rebuilt.

:::photo{src="/lesson-images/fastapi/station-clock.webp" alt="A round station clock with a white face and black numbers hanging under a platform roof, showing about twenty-five past four, with railway tracks and a sky behind it" credit="Panamitsu" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Clock_at_Wellington_railway_station.jpg"}
One of the clocks above the platforms of Wellington railway station, New Zealand.
:::

:::mission
Add a middleware that times every request in an `X-Process-Time` header, and move the app's settings into a
`Settings` class that reads environment variables.
:::
:::

:::step{type=concept title="Middleware: code around every request"}
A **middleware** is a function that every request passes through on the way in, and every response on the way out,
whatever the route:

```python
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)      # everything else: routing, dependencies, your route
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - start) * 1000:.2f} ms"
    return response
```

`call_next(request)` passes the request on and gives back the response; code before it runs first, code after it
runs last. `time.perf_counter()` is a clock made for measuring short durations. Press Play:

:::diagram{name="fastapi-middleware"}
Every request passes through each middleware on the way in and back out, so one function can time or label them all.
:::

The solution's answer to `GET /info`, headers included, had:

```text
x-process-time: 1.07 ms
```

Headers that a company adds for itself traditionally start with `X-`. Because the middleware wraps everything, even
a 404 for a path that does not exist gets the header.
:::

:::step{type=task task=timing_header title="Your turn: time every request" file="19-settings/main.py" line="25-26"}
Add the middleware: every response gets `X-Process-Time` with the milliseconds it took, like `0.42 ms`. Start this
chapter's server from `/workspace/19-settings` and look:

```bash run
curl -s -i localhost:8000/items | grep -i x-process
```

Then press **Check**: it looks at `/items`, `/info` and a path that does not exist.
:::

:::step{type=concept title="CORS: which websites may call Lostdesk" file="19-settings/main.py" line="17-22"}
The station screens are a web page served from another address, `https://screens.metro.example`. Browsers protect
people with a rule from Netscape's early days (1995), the **same-origin policy**: JavaScript on one site may not read
answers from another site, unless that other site says it may. The way it says so is **CORS** (Cross-Origin Resource
Sharing): response headers listing the sites allowed.

`main.py` already has CORS, as a middleware that FastAPI provides:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

Before some requests, a browser first asks permission with an `OPTIONS` request, a **preflight**. We sent two by
hand, from the allowed site and from another:

```text
Origin: https://screens.metro.example  ->  HTTP/1.1 200 OK
                                            access-control-allow-origin: https://screens.metro.example
Origin: https://evil.example           ->  HTTP/1.1 400 Bad Request
                                            Disallowed CORS origin
```

CORS is enforced by **browsers**. `curl`, a phone app or another server ignore it completely; it protects people
browsing the web, not your API from programs. Keep the list short and exact; `allow_origins=["*"]` lets every website
in.
:::

:::step{type=concept title="Settings from the environment"}
Lostdesk's `APP_NAME`, `MAX_PHOTO_MB` and `ALLOWED_ORIGIN` are written into the code. A guide published in 2011 by
engineers at Heroku, a cloud company, "The Twelve-Factor App", gave the rule most teams now follow: keep settings
that differ between places in **environment variables**, named values the operating system gives a program when it
starts (`LOSTDESK_MAX_PHOTO_MB=5 fastapi run main.py`).

`pydantic-settings` reads them into a Pydantic model, with types and defaults:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOSTDESK_")

    app_name: str = "Lostdesk"
    max_photo_mb: int = 2


settings = Settings()
```

- Each field is read from the environment variable of the same name plus the prefix (`LOSTDESK_MAX_PHOTO_MB`), or
  keeps its default. Capitals do not matter.
- The values are **checked**, like any Pydantic model. We started the solution with `LOSTDESK_MAX_PHOTO_MB=lots`, and
  it refused to start:

```text
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
max_photo_mb
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='lots', input_type=str]
```

A typo in a setting stops the server at once, at start-up, instead of failing at 3 a.m. on the first photo.
:::

:::step{type=example title="Worked example: a .env file"}
This is not in your project. Typing every variable before every start is tedious on a laptop, so `pydantic-settings`
can also read a file of them:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOSTDESK_", env_file=".env")
    app_name: str = "Lostdesk"
```

with a `.env` file next to the code:

```text
LOSTDESK_APP_NAME=Lostdesk (laptop)
```

1. Real environment variables still win over the file, so production can override anything.
2. `.env` files often hold secrets: keep them out of git (list them in `.gitignore`).
3. This is how LabBox's own backend keeps its settings, in `backend/.env`.
:::

:::step{type=task task=settings_env title="Your turn: a Settings class" file="19-settings/main.py" line="8-13"}
Replace the three constants with a `Settings` class (`env_prefix="LOSTDESK_"`, the same three fields and defaults),
create `settings = Settings()`, and use `settings.app_name`, `settings.max_photo_mb` and `settings.allowed_origin`
wherever the constants were.

```bash run
cd /workspace/19-settings && LOSTDESK_MAX_PHOTO_MB=5 fastapi dev main.py --host 0.0.0.0 --port 8000 --root-path /preview/fastapi-first-api/8000
```

The solution, started that way, answered `GET /info` with `{"app_name":"Lostdesk","max_photo_mb":5}`. Then press
**Check**: it sets `LOSTDESK_APP_NAME` and `LOSTDESK_MAX_PHOTO_MB`, and then tries again without them.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In a middleware, when does the code after `await call_next(request)` run?
:::
- [ ] Before the route
- [x] After the route has produced its response
- [ ] Only for errors
:::explain
`call_next` runs the rest of the app and gives back its response; the middleware can then change it.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Lostdesk allows only `https://screens.metro.example`. A Python script on a server calls Lostdesk directly. Is it
blocked by CORS?
:::
- [ ] Yes
- [x] No: CORS is enforced by browsers only
:::explain
CORS stops other websites' JavaScript, inside a browser, from reading answers. Real access control is chapter 17's
tokens.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`LOSTDESK_MAX_PHOTO_MB=lots`. When do you find out?
:::
- [x] When the server starts: it refuses with a ValidationError
- [ ] When someone uploads a photo
:::explain
`Settings()` runs at import time and checks every value, so a bad setting can never reach a request.
:::
:::

:::step{type=deep-dive title="Go deeper: more middleware, and settings in tests"}
**Ready-made middleware.** FastAPI and Starlette ship several: `GZipMiddleware` compresses large answers,
`TrustedHostMiddleware` refuses requests for host names you do not serve, `HTTPSRedirectMiddleware` sends plain HTTP
to HTTPS. They are added with `app.add_middleware(...)`, and the last one added is the outermost.

**Settings as a dependency.** FastAPI's "Settings and Environment Variables" page shows a `get_settings()` dependency
(cached with `functools.lru_cache`), so tests can override the settings with `app.dependency_overrides`, exactly as
chapter 15 overrode the database.

**Secrets.** Chapter 16's `SECRET_KEY` belongs here: `secret_key: str` with **no default**, so the server cannot start
without it.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write an HTTP middleware with `@app.middleware("http")` and `call_next`, and add headers to every response.
- Explain the same-origin policy and CORS, configure `CORSMiddleware`, and read a preflight.
- Read settings from environment variables with a `BaseSettings` class and a prefix, checked at start-up.
- Keep what differs between laptop, test and production out of the code.

:::photo{src="/lesson-images/fastapi/fa-19-sketch.webp" alt="Sketchnote: Middleware, CORS and settings. Middleware wraps every request on the way in and out. Settings come from environment variables, checked at start-up. Flow: request in, middleware before, call_next runs the app, middleware after, response out. Remember: CORS tells browsers which websites may read the answers; CORS does not stop curl or other servers; BaseSettings reads LOSTDESK_ variables with types; A bad setting stops the server at start-up." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 20: live updates, so station screens see new finds the moment they are logged.
:::
