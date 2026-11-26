import { LabPrint, TRACK_HEX, printCredit } from "../components/UkiyoArt";
import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type LabDetail, type NextStep, type Slots } from "../api";
import { useAuth } from "../auth";
import { inkOn, labBrand, labTone, mix } from "../brand";
import LockIcon from "../components/LockIcon";
import MetroMap, { labLines } from "../components/MetroMap";
import { LogoMark } from "../components/Logo";
import { chapterNumber } from "../components/StatusBar";
import ProfileMenu from "../components/ProfileMenu";
import ThemeButton from "../components/ThemeButton";
import { useToast } from "../components/Toasts";
import { TRACK_LABEL } from "./LabsPage";

/*
 * A lab's own page (owner, 22 November: a lab card opens a page for that lab first, then the lab itself). The
 * cover in the lab's colour, what the course is, how far you are, one button into the lab (the lesson, editor and
 * terminal page), and the chapters as a metro map (a line per course part, as on the skill maps); each chapter
 * and subtopic opens the lab there.
 */
export default function CoursePage() {
  const { labId = "" } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const [lab, setLab] = useState<LabDetail | null>(null);
  const [next, setNext] = useState<NextStep | null>(null);
  const [slots, setSlots] = useState<Slots | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    if (!reload) setLab(null);
    api.lab(labId).then(setLab).catch((e) => toast(e.message));
    api.next(labId).then(setNext).catch(() => setNext(null));
    api.slots().then(setSlots).catch(() => setSlots(null));
  }, [labId, toast, reload]);

  const lines = useMemo(() => {
    if (!lab) return [];
    const at = next?.kind === "continue" && next.lab_id === lab.id ? lab.chapters.findIndex((c) => c.id === next.chapter_id) : -1;
    return labLines(lab, at >= 0 ? at : undefined);
  }, [lab, next]);

  if (!lab) return <div className="course-page"><Topbar title={labId} username={user?.username ?? ""} /></div>;

  const done = (c: LabDetail["chapters"][number]) => c.tasks.length > 0 && c.tasks.every((t) => t.passed);
  const doneCount = lab.chapters.filter(done).length;
  const here = next?.kind === "continue" && next.lab_id === lab.id;  // next is asked for this lab
  const nowIdx = here ? lab.chapters.findIndex((c) => c.id === next.chapter_id) : Math.max(0, lab.chapters.findIndex((c) => !done(c)));
  const now = lab.chapters[nowIdx] ?? lab.chapters[0];
  const started = here || lab.progress.passed_tasks > 0;
  const go = `/labs/${lab.id}?chapter=${encodeURIComponent(now.id)}`;
  const pct = lab.chapters.length ? Math.round((100 * doneCount) / lab.chapters.length) : 0;
  const tone = TRACK_HEX[lab.track] ?? labTone(lab.id, lab.cover_credit);  // Ukiyo: the category ink
  const vars = { "--tone": tone, "--tone-ink": inkOn(tone), "--tone-hi": mix(tone, "#ffffff", 0.18), "--tone-lo": mix(tone, "#000000", 0.22) } as CSSProperties;
  const level = lab.level ? `${lab.level[0].toUpperCase()}${lab.level.slice(1)}` : null;

  return (
    <div className="course-page" style={vars}>
      <Topbar title={lab.title} username={user?.username ?? ""} />
      <main className="course-main" aria-label={lab.title}>
        <section className="course-hero">
          <figure className="u-course-figure">
            <div className="course-cover u-course-print">
              {/* Ukiyo: the lab's own woodblock print, with its logo stamped on it like a seal */}
              <LabPrint lab={lab.id} track={lab.track} />
              {labBrand(lab.cover_credit) && (
                <span className="u-course-logo"><img src={labBrand(lab.cover_credit)!.logo} alt="" /></span>
              )}
            </div>
            {printCredit(lab.id) && <figcaption className="u-print-credit">{printCredit(lab.id)}</figcaption>}
          </figure>
          <div className="course-hero-text">
            <div className="course-kicker">{[TRACK_LABEL[lab.track] ?? lab.track, level].filter(Boolean).join(" · ")}</div>
            <h1>{lab.title}</h1>
            <p className="course-sub">{lab.subtitle}</p>
            <div className="course-progress" role="progressbar" aria-label="Chapters done" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
              <div className="course-bar"><div style={{ width: `${pct}%` }} /></div>
              <span>{doneCount} of {lab.chapters.length} chapters · {lab.progress.passed_tasks} of {lab.progress.total_tasks} tasks</span>
            </div>
            {lab.access === "locked" ? (
              <UnlockBox lab={lab} slots={slots} onChange={() => setReload((n) => n + 1)} />
            ) : (
              <>
                <div className="course-actions">
                  <Link className="course-go" to={go}>
                    <span aria-hidden="true" className="course-play">▶</span>{started ? "Continue" : "Start"}: Chapter {chapterNumber(lab.chapters, nowIdx)} →
                  </Link>
                </div>
                <p className="course-where">
                  {now.title}{here ? ` · scene ${next.step} of ${next.steps}` : ""}
                </p>
                {slots?.limit != null && <SlotNote lab={lab} slots={slots} onChange={() => setReload((n) => n + 1)} />}
              </>
            )}
          </div>
        </section>

        <section className="course-about" aria-label="About this lab">
          <p>{lab.description}</p>
          <ul className="course-facts">
            <li><strong>{lab.chapters.length}</strong><span>chapters</span></li>
            <li><strong>{lab.progress.total_tasks}</strong><span>hands-on tasks</span></li>
            {lines.length > 1 && <li><strong>{lines.length}</strong><span>parts</span></li>}
            <li><strong>Your own machine</strong><span>editor, terminal, instant checks</span></li>
          </ul>
        </section>

        {lab.before_you_start && (
          <section className="course-before" aria-labelledby="course-before-title">
            <h2 id="course-before-title">Before you start</h2>
            <p className="course-before-summary">{lab.before_you_start.summary}</p>
            {lab.before_you_start.needs.length > 0 && (
              <ul className="course-needs">
                {lab.before_you_start.needs.map((n, i) => (
                  <li key={i}>
                    <span className="course-need-check" aria-hidden="true">✓</span>
                    <div>
                      <strong>{n.know}</strong>
                      {n.why && <p>{n.why}</p>}
                      {n.lab && n.lab_title && (
                        <Link className="course-need-link" to={`/courses/${n.lab}`}>
                          Learn it in {n.lab_title}{n.where ? `, ${n.where}` : ""} →
                        </Link>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        <section className="course-syllabus" aria-label="Chapters">
          <h2>Skill map</h2>
          <p className="muted">{lab.access === "locked"
            ? "What this course covers, chapter by chapter. Unlock the lab to open its lessons."
            : "Every chapter on its line; each subtopic opens its lesson."}</p>
          <MetroMap lines={lines} />
        </section>
      </main>
    </div>
  );
}

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/** When the next swap day starts, in the learner's own time ("Monday 30 November"). */
const swapDay = (iso: string) => new Date(iso).toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });

/*
 * A locked lab (owner, 26 November: at most a few labs at a time, so learners focus): this page is all that opens.
 * One button unlocks it while a slot is free; with every slot in use, the page says how to free one.
 */
function UnlockBox({ lab, slots, onChange }: { lab: LabDetail; slots: Slots | null; onChange: () => void }) {
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  const full = slots?.free === 0;
  const unlock = () => {
    setBusy(true);
    api.unlock(lab.id).then(onChange).catch((e) => toast(e.message)).finally(() => setBusy(false));
  };
  return (
    <div className="course-lock" aria-live="polite">
      <div className="course-lock-head">
        <LockIcon />
        <strong>This lab is locked</strong>
      </div>
      {slots?.limit != null && (
        <p>
          You can work in {plural(slots.limit, "lab")} at a time, so each one gets your full attention.
          {full ? ` All ${slots.limit} are in use.` : ` ${slots.free} of ${slots.limit} ${slots.free === 1 ? "slot is" : "slots are"} free.`}
        </p>
      )}
      <div className="course-actions">
        <button type="button" className="course-go" onClick={unlock} disabled={busy || full || !slots}>
          <span className="course-play"><LockIcon size={15} /></span>Unlock this lab
        </button>
        {full && <Link className="btn btn-ghost" to="/labs">Your labs</Link>}
      </div>
      {full && slots && (
        <p className="course-where">
          A slot frees itself when you finish a lab (80% of its tasks). On Mondays you can also swap a lab out
          {slots.swap_open ? ": today is swap day, open one of your labs to swap it." : `; the next swap day is ${swapDay(slots.next_swap)}.`}
        </p>
      )}
    </div>
  );
}

/** An open lab while a limit is on: what its slot means, and the Monday swap. */
function SlotNote({ lab, slots, onChange }: { lab: LabDetail; slots: Slots; onChange: () => void }) {
  const toast = useToast();
  const [asking, setAsking] = useState(false);
  if (lab.access === "finished") {
    return <p className="course-slot-note">Finished: this lab no longer uses one of your slots, and it stays open.</p>;
  }
  if (lab.access !== "unlocked") return null;
  const swap = () => api.swap(lab.id).then(onChange).catch((e) => toast(e.message));
  return (
    <div className="course-slot-note">
      <span>
        This lab uses one of your {plural(slots.limit ?? 0, "slot")}. Finish 80% of its tasks to free it
        {slots.swap_open ? ", or swap it out today (Monday)." : `, or swap it out on ${swapDay(slots.next_swap)}.`}
      </span>
      {slots.swap_open && !asking && (
        <button type="button" className="btn btn-small btn-ghost" onClick={() => setAsking(true)}>Swap it out</button>
      )}
      {asking && (
        <span className="course-swap-ask" role="group" aria-label="Swap this lab out">
          Lock it again? Your progress stays.
          <button type="button" className="btn btn-small" onClick={swap}>Yes, swap it out</button>
          <button type="button" className="btn btn-small btn-ghost" onClick={() => setAsking(false)}>Cancel</button>
        </span>
      )}
    </div>
  );
}

function Topbar({ title, username }: { title: string; username: string }) {
  return (
    <header className="topbar">
      <Link to="/" className="logo" aria-label="LabBox by Telusko home"><LogoMark size={24} /></Link>
      <Link to="/labs" className="link">← Dashboard</Link>
      <span className="brand">{title}</span>
      <span className="spacer" />
      <ThemeButton />
      <ProfileMenu username={username} />
    </header>
  );
}
