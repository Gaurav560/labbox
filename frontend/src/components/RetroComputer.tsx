import { Link } from "react-router-dom";

/*
 * The dashboard's "Continue" picture for labs where you write code (owner, 22 November): a retro computer in the
 * lab's colour whose screen shows the step the learner stopped at, its title and the first lines of its code, with
 * a blinking "> continue". Below it, a round play key (Continue) and a bar for the place in the chapter. Labs that
 * are not about writing code keep the cassette (see labDeck in brand.ts).
 */

// Squares behind the computer: [column, row, shade]; "c" is the lab's colour.
const PIXELS: [number, number, "c" | "g1" | "g2" | "g3"][] = [
  [0, 0, "g1"], [1, 0, "g2"], [5, 0, "c"], [6, 0, "g1"], [0, 1, "c"], [1, 1, "g3"], [6, 1, "g2"], [0, 3, "g2"],
  [5, 3, "g3"], [6, 3, "c"], [1, 4, "g1"], [2, 4, "c"], [4, 4, "g2"], [6, 4, "g3"], [0, 5, "g3"], [5, 5, "g1"],
];

export interface RetroScreen {
  path: string; // e.g. "JAVA / 02-METHODS"
  clock: string; // chapter:step, e.g. "02:07"
  title: string; // the step's title
  code: string[]; // up to 5 lines; empty shows the title alone
}

export default function RetroComputer({ screen, progress, playTo, playLabel, courseTo, stepText, chapterText }: {
  screen: RetroScreen;
  progress: number; // 0..1, the place in the chapter
  playTo: string;
  playLabel: string;
  courseTo: string;
  stepText: string;
  chapterText: string;
}) {
  const pct = Math.round(progress * 100);
  return (
    <div className="retro">
      <div className="retro-stage">
        {PIXELS.map(([x, y, k]) => (
          <span key={`${x}-${y}`} className={`retro-pix retro-${k}`} style={{ left: x * 62 - 8, top: y * 52 }} aria-hidden="true" />
        ))}
        <div className="retro-float">
          <div className="retro-pc">
            <div className="retro-side" aria-hidden="true" />
            <div className="retro-body" aria-hidden="true" />
            <Link className="retro-bezel" to={playTo} aria-label={`${playLabel}: ${screen.title}`}>
              <div className="retro-crt">
                <div className="retro-top"><span>{screen.path}</span><span>{screen.clock}</span></div>
                <div className="retro-head">{screen.title}</div>
                {screen.code.length > 0 && <pre className="retro-code">{screen.code.join("\n")}</pre>}
                <div className="retro-prompt">&gt; continue<span className="retro-cursor" /></div>
                <div className="retro-bar"><i style={{ width: `${pct}%` }} /></div>
              </div>
            </Link>
            <div className="retro-slot" aria-hidden="true" />
            <Link className="retro-power" to={courseTo} aria-label="Course page and skill map" title="Course page and skill map" />
          </div>
        </div>
      </div>
      <div className="retro-controls">
        <Link className="retro-play next-go" to={playTo} aria-label={playLabel}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3.5v17l14-8.5z" /></svg>
        </Link>
        <div className="retro-track" role="progressbar" aria-label="Progress in this chapter" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <div className="retro-meter"><i style={{ width: `${pct}%` }} /></div>
          <div className="retro-meta"><span>{stepText}</span><span>{chapterText}</span></div>
        </div>
      </div>
    </div>
  );
}
