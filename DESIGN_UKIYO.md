# LabBox "Ukiyo" design

Japanese woodblock prints (ukiyo-e) meet Swiss editorial layout. A second design for LabBox, built on the
branch `design/ukiyo` to compare with the current one (owner, 24 November). Only the frontend differs; both
copies use the same backend, labs, accounts and progress.

## How to see it

| Copy | Folder | Address |
|---|---|---|
| Current design | `labs_poc` (branch `master`) | http://localhost:5173 |
| Ukiyo | `labs_poc_ukiyo` (branch `design/ukiyo`, a git worktree) | http://localhost:5174 |

Start the Ukiyo copy with `cd ../labs_poc_ukiyo/frontend && npx vite --port 5174 --strictPort` (the backend on
8000 serves both). Logins are kept per address, so log in once on each. All prints: http://localhost:5174/ukiyo/art.
Browser tests against it: `LABBOX_URL=http://localhost:5174 npx playwright test` (the worktree's `backend/.venv`
and `backend/.env` are links to the main ones, so `scripts/labbox` works there too).

## Principles

1. A technical learning product first: decoration never sits behind code, terminals or task panels.
2. One red thing per screen: vermilion marks the main action (Continue, Start, Check) and "you are here".
3. Fine rules instead of shadows and pills; small radii (2 to 6 px).
4. Different content, different shape: a feature for the next step, compact tiles for categories, rows for the
   lab directory.
5. Signature details used sparingly: the hanko seal, seigaiha waves, one vertical label, a brush underline.

## Tokens (`frontend/src/ukiyo.css`, section 1)

| Token | Washi (light, default) | Sumi (dark) | Use |
|---|---|---|---|
| `--bg` | `#f3eee3` | `#14120f` | paper, with a faint fixed fibre grain |
| `--panel` / `--card` | `#faf7f0` / `#fffdf8` | `#1b1915` / `#211e19` | bars, cards |
| `--text` | `#1c1a17` | `#ede6d8` | ink |
| `--muted` | `#6a6358` | `#a49b8c` | secondary text |
| `--rule` | ink at 14% | ink at 15% | fine borders |
| `--vermilion` | `#c63f28` | `#e2583f` | main action, seals, current step |
| `--indigo` | `#1f3a64` | `#8aa6d6` | AI, links in prints |
| category inks | gold, sage, river, slate, earth, cloud | lighter in sumi | one per track |

Spacing: 4, 8, 12, 16, 20, 24, 32, 48, 72 px. Radius: `--radius: 6px`, buttons 4 px, cards 0 to 4 px.

## Type

- Headlines: **Fraunces** (editorial serif), weights 400 (italic for a name), 600, 700, bundled with the app.
- Interface: **Inter**. Code, kickers and counts: **JetBrains Mono**, small caps style with wide tracking.
- Scale: 12, 14, 16, 18, 22, 28, 40, 56 px (headlines use `clamp` to scale down on phones).

## Components

| Piece | Where | Notes |
|---|---|---|
| `LogoMark` | everywhere | a vermilion hanko with the shell prompt, stamp texture |
| `TrackArt` | dashboard, home, course page | the category's picture (`TRACK_IMAGES`); drawn SVG prints only as a fallback |
| `LabPrint` | course page, dashboard feature | the lab's own woodblock print with a credit line |
| `Seal` | feature, finished labs | small vermilion stamp with one or two words |
| `BrushLevel` | lab rows | one to three brush marks for beginner, intermediate, advanced |
| `InkProgress` | feature, rows | a fine ink line with a vermilion diamond |
| Feature | dashboard | the next step: print, serif title, ink progress, red button, chapter ladder |
| `UkiyoDirectory` | dashboard | category tiles (print, name, count) that narrow the lab rows (logo, serif title, level, size, progress) |
| Folding screen | home | six tall category panels; the one under the pointer opens and lists its labs |
| `UkiyoMachine` | home | "start a lab": a Docker-style container that loads a lab's real stack and starts (below) |

## Artwork

- Category pictures (`TRACK_IMAGES` in `components/UkiyoArt.tsx`, files in `public/ukiyo/tracks/`), all calm
  public-domain Hiroshige prints (owner, 25 November: "cool images that soothe the eyes"): AI, a cat on a windowsill
  gazing out at Fuji and the rice fields (Asakusa Ricefields and Torinomachi Festival, 1857); Languages, cherry
  blossoms on the Tama River embankment; Frameworks, the bamboo yards at Kyobashi under a full moon; System design,
  the drum bridge under wisteria at Kameido Tenjin; Databases, a boat on the Sumida with Azuma Bridge and Fuji (all
  One Hundred Famous Views of Edo, 1856 to 1858); DevOps, the Monkey Bridge in Kai Province by moonlight (about
  1842). The drawn SVG prints stay as the fallback for categories without a picture (Cloud).
- Hokusai's The Great Wave (about 1831, public domain, `public/ukiyo/great-wave.webp`) on the dashboard's All labs tile.
- Home page: Hiroshige's Kinryuzan Temple at Asakusa in snow (hero, `public/ukiyo/heroes/kinryuzan.webp`) and
  Evening Snow on Mount Hira (closing panel, `public/ukiyo/hira-evening-snow.webp`). Red Fuji is kept but unused.
- Every lab has its own real woodblock print (owner, 24 November: "classy unique images for each one of the lab"),
  shown on its course page with a credit line and on the dashboard's Continue feature. The category tiles keep
  the shared category print; "All labs" shows the Great Wave. Files: `public/ukiyo/labs/<lab>.webp` (1280 px,
  about 200 KB each), from Wikimedia Commons, public domain (most are CC0 scans by the Metropolitan Museum of Art).
  The list lives in `LAB_PRINTS` (`components/UkiyoArt.tsx`); a new lab without a print falls back to its
  category print. Each print echoes the lab's project (wind for Windwatch, a bridge for Setu, water for the
  water board, a merchant's shop for payments).

| Lab | Artist | Print | Year |
|---|---|---|---|
| `rust-basics` | Katsushika Hokusai | Ejiri in Suruga Province | about 1831 |
| `langchain4j` | Katsushika Hokusai | The Suspension Bridge between Hida and Etchū | about 1834 |
| `langchain` | Katsushika Hokusai | Fujimigahara in Owari Province | about 1831 |
| `langgraph` | Katsushika Hokusai | The Waterwheel at Onden | about 1831 |
| `rag-vector-databases` | Katsushika Hokusai | Ushibori in Hitachi Province | about 1831 |
| `spring-ai` | Katsushika Hokusai | Sazai Hall at the Temple of the Five Hundred Arhats | about 1831 |
| `java-collections` | Katsushika Hokusai | Mitsui Shop at Surugachō in Edo | about 1831 |
| `go-basics` | Katsushika Hokusai | Hodogaya on the Tōkaidō | about 1831 |
| `python-collections` | Utagawa Hiroshige | Driving Rain at Shōno | about 1833 |
| `javascript-basics` | Katsushika Hokusai | Honganji at Asakusa in Edo | about 1831 |
| `python-basics` | Utagawa Hiroshige | Nihonbashi: Morning View | about 1833 |
| `spring-boot-first-api` | Katsushika Hokusai | Fuji from Gotenyama at Shinagawa | about 1831 |
| `redis-in-practice` | Katsushika Hokusai | Shower Below the Summit | about 1831 |
| `postgres-indexing-incident` | Utagawa Hiroshige | Night Snow at Kanbara | about 1833 |
| `linux-on-call` | Utagawa Hiroshige | Autumn Moon on the Tama River | about 1838 |
| `rate-limiter` | Katsushika Hokusai | Fuji Seen from Kanaya on the Tōkaidō | about 1831 |
| `javascript-inside-out` | Katsushika Hokusai | Kajikazawa in Kai Province | about 1831 |
| `java-basics` | Katsushika Hokusai | The Tama River in Musashi Province | about 1831 |
| `express-api` | Utagawa Hiroshige | The Mie River at Yokkaichi | about 1833 |
| `fastapi-first-api` | Utagawa Hiroshige | The Lake at Hakone | about 1833 |
| `sql-from-zero` | Katsushika Hokusai | Lake Suwa in Shinano Province | about 1831 |
| `postgres-transactions-and-locks` | Katsushika Hokusai | Under the Mannen Bridge at Fukagawa | about 1831 |
| `git-without-fear` | Katsushika Hokusai | Kintai Bridge in Suō Province | about 1834 |

- Login and sign-up: Hiroshige's Plum Garden at Kameido (1857, public domain, `public/ukiyo/plum-garden.webp`).
- No AI-generated art (that needs the owner's approval for the OpenAI key).

## What changed per page

- Dashboard: rewritten (`pages/LabsPage.tsx`).
- Course page: the lab's own print with its logo stamped on it and a credit line; flat hero; ink metro map headed "Skill map".
- Home (redesigned 25 November, `pages/HomePage.tsx`, `ukiyo.css` sections 10 and 15), top to bottom:
  - Hero: "The AI wave is here. / Learn to build AI apps, / or get left behind." (vermilion italic, then muted); the
    lead (a code editor, a terminal and a model gateway in about a minute); "No fluff. No tutorial hell. Only
    action."; Start free; on the right a lab session in a terminal over the Kinryuzan print (picked from eight).
  - Start a lab (`components/UkiyoMachine.tsx`, picked from nine options and refined with the owner): nine lab tabs,
    AI first (LangChain, Spring AI, RAG, Spring Boot, Python, Postgres, Linux, FastAPI, Redis); "One click, and a
    container spins up for you with everything the lab needs."; the run command `$ docker run <lab>` types itself,
    with a green Run key and "Try it: tap Run". Beside it a Docker-style shipping container (corrugated walls,
    frame, castings, stencils, the whale). The first run starts by itself when the section comes into view; then
    each piece of the lab's real stack appears, flies into the open doors and rides in as a cardboard crate seen
    through the glass wall; the doors lock, `docker start` runs, the lamp and lights turn green ("RUNNING"), a
    clock counts to 58 s, a green tick and Start (to the course, through login) appear. 1.6 s per piece
    (`PIECE_MS`); reduced motion shows the running container at once. A tab change waits for Run or a tap.
  - Labs: "Pick a lab. Start in a minute." and the folding screen of six category panels, then "See all labs"
    (the full directory stays on `/labs`).
  - A closing paper panel ("Your machine is ready when you are.") with Evening Snow on Mount Hira.
  - FAQs without numbers, a thin plus and minus.
  - Removed on the owner's request: the logo strip, the numbers, Inside a lab, the AI stage ladder, the AI section
    (parked; see git history at 3b89404), the old "first win" line.
- Menu: "AI labs" opens `/labs?category=ai` (through login, `next=`).
- Premium Reads, login: restyled through tokens and sections 9 and 11 of `ukiyo.css`.
- Lab page: the frame only (Check button, step marks, labels, headings); the lesson watermark is off.
