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
| `TrackArt` | dashboard, course page | seven SVG woodblock prints, one per category |
| `Seal` | feature, finished labs | small vermilion stamp with one or two words |
| `BrushLevel` | lab rows | one to three brush marks for beginner, intermediate, advanced |
| `InkProgress` | feature, rows | a fine ink line with a vermilion diamond |
| Feature | dashboard | the next step: print, serif title, ink progress, red button, chapter ladder |
| Category tiles | dashboard | print, name, count; they narrow the directory |
| Lab rows | dashboard | logo, serif title, one line, level, size, progress |

## Artwork

- Category prints are original SVG, flat colour blocks with a paper grain (`components/UkiyoArt.tsx`): Frameworks
  bamboo, Databases river, DevOps mountains, System design a red arched bridge, Cloud clouds.
- AI and Languages use two pictures the owner chose on 25 November (`public/ukiyo/tracks/`, `TRACK_IMAGES`): AI is
  a vermilion pagoda among snowy cedars (a shin-hanga print dated Showa 26, 1951; the owner's `kathmandu.jpeg`),
  Languages a brushed red sun over an ink wave. **Before launch, confirm the licence of both**: the sun looks like a stock graphic, and a 1951 print is
  probably still in copyright. If either cannot be licensed, the drawn SVG versions are in git history
  (commit 49cba89).
- Two public-domain prints by Hokusai (about 1831), stored in `public/ukiyo/`: The Great Wave (faint behind the
  home hero) and Red Fuji (the login page).
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

- No AI-generated art (that needs the owner's approval for the OpenAI key).

## What changed per page

- Dashboard: rewritten (`pages/LabsPage.tsx`).
- Course page: the lab's own print with its logo stamped on it and a credit line; flat hero; ink metro map headed "Skill map".
- Home (redesigned 25 November, `pages/HomePage.tsx`, `ukiyo.css` section 10): a framed Red Fuji beside the headline
  (vermilion brush underline, no highlighter), the four numbers between fine rules (no logo strip), the lab
  screenshot with the tour beside six ruled features, the AI track as a ladder of four stages under the pagoda
  picture, the dashboard's own directory (`components/UkiyoDirectory.tsx`, shared with `/labs`), a closing paper
  panel with Hiroshige's Nihonbashi, and the FAQs with a thin plus and minus.
- Premium Reads, login: restyled through tokens and sections 9 and 11 of `ukiyo.css`.
- Lab page: the frame only (Check button, step marks, labels, headings); the lesson watermark is off.
