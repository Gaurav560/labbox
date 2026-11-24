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

- Category prints are original SVG, flat colour blocks with a paper grain (`components/UkiyoArt.tsx`):
  AI waves, Languages sun and Fuji, Frameworks bamboo, Databases river, DevOps mountains, System design pagoda,
  Cloud clouds.
- Two public-domain prints by Hokusai (about 1831), stored in `public/ukiyo/`: The Great Wave (faint behind the
  home hero) and Red Fuji (the login page).
- No AI-generated art (that needs the owner's approval for the OpenAI key).

## What changed per page

- Dashboard: rewritten (`pages/LabsPage.tsx`).
- Course page: the print with the lab's logo stamped on it; flat hero; ink metro map.
- Premium Reads, home, login: restyled through tokens and section 9 to 11 of `ukiyo.css`.
- Lab page: the frame only (Check button, step marks, labels, headings); the lesson watermark is off.
