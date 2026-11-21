import { Suspense, lazy, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type SkillMap, type SkillNode } from "../api";
import type { Stop } from "../components/NeonWorld";
import { useAuth } from "../auth";
import { LogoMark } from "../components/Logo";
import StatsBadges from "../components/StatsBadges";
import ThemeButton from "../components/ThemeButton";
import { useToast } from "../components/Toasts";
import { useTheme } from "../theme";
import { usePhone } from "../usePhone";

/*
 * A track's skill map as a 3D roadmap (owner, 21 November): the board on the left, and on the right every topic,
 * in order. Choosing a topic (on the board or in the list) shows its chapters, each opening its lab at that
 * chapter. Phones, and browsers without WebGL, get the list on its own.
 */

// three.js is large: load it only when a skill map is opened.
const NeonWorld = lazy(() => import("../components/NeonWorld"));

const STATE_LABEL = { done: "✓ Done", available: "Start", locked: "Locked", coming_soon: "Coming soon" } as const;

export default function TrackPage() {
  const { track = "" } = useParams();
  const { user } = useAuth();
  const { theme } = useTheme();
  const toast = useToast();
  const phone = usePhone();
  const [map, setMap] = useState<SkillMap | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [reset, setReset] = useState(0);
  const [noWebGl, setNoWebGl] = useState(false);

  useEffect(() => {
    setSelected(null);
    api.skills(track).then(setMap).catch((e) => toast(e.message));
  }, [track, toast]);

  const nodes = useMemo(() => map?.nodes ?? [], [map]);
  // Topics in learning order (prerequisites first) as stops on the road; the first one you can start is "you are here".
  const stops: Stop[] = useMemo(() => {
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
    const depth: Record<string, number> = {};
    const req = (id: string) => byId[id].requires.filter((r) => byId[r]);
    const depthOf = (id: string): number => (depth[id] ??= req(id).length ? 1 + Math.max(...req(id).map(depthOf)) : 0);
    const sorted = nodes.map((n, i) => ({ n, d: depthOf(n.id), i })).sort((a, b) => a.d - b.d || a.i - b.i).map((x) => x.n);
    const firstOpen = sorted.findIndex((n) => n.state === "available");
    return sorted.map((n, i) => ({
      id: n.id,
      number: String(i + 1).padStart(2, "0"),
      title: n.title,
      state: n.state === "done" ? "done" : n.state === "coming_soon" ? "soon" : n.state === "locked" ? "locked" : i === firstOpen ? "next" : "open",
    }));
  }, [nodes]);
  const node = nodes.find((n) => n.id === selected) ?? null;
  const done = nodes.filter((n) => n.state === "done").length;
  const show3d = !phone && !noWebGl;

  return (
    <div className="track-page">
      <header className="topbar">
        <Link to="/" className="logo" aria-label="LabBox by Telusko home"><LogoMark size={24} /></Link>
        <Link to="/skills" className="link">← Skill maps</Link>
        <span className="brand">{map?.title ?? track}</span>
        {map && <span className="muted small-text">{done} of {nodes.length} skills</span>}
        <span className="spacer" />
        <ThemeButton />
        <StatsBadges username={user?.username ?? ""} />
      </header>
      <main className={`track-main ${show3d ? "has-3d" : ""}`} aria-label="Skill map">
        {map && show3d && (
          <div className="roadmap-stage">
            <Suspense fallback={<div className="roadmap3d muted small-text roadmap-loading">Building your roadmap...</div>}>
              <NeonWorld stops={stops} selected={selected} onSelect={setSelected} resetSignal={reset} theme={theme} onFail={() => setNoWebGl(true)} />
            </Suspense>
            <div className="roadmap-help small-text" aria-hidden="true">Drag to look around · scroll to zoom · click a sign to ride there</div>
            <button className="btn btn-small roadmap-reset" onClick={() => setReset((r) => r + 1)}>Behind the rider</button>
          </div>
        )}
        {map && (
          <aside className="roadmap-panel" aria-label={node ? node.title : "Topics"}>
            {node ? (
              <TopicDetails node={node} nodes={nodes} onBack={() => setSelected(null)} />
            ) : (
              <>
                <h2 className="roadmap-panel-title">{map.title}</h2>
                <p className="muted small-text">Each topic opens the lab chapters that teach it.</p>
                <ol className="topic-list">
                  {nodes.map((n) => (
                    <li key={n.id} className={`skill-node skill-${n.state}`}>
                      <button onClick={() => setSelected(n.id)} aria-label={`${n.title}: ${STATE_LABEL[n.state]}`}>
                        <span className="skill-title">{n.title}</span>
                        <span className="skill-state">{STATE_LABEL[n.state]}</span>
                      </button>
                    </li>
                  ))}
                </ol>
              </>
            )}
          </aside>
        )}
      </main>
    </div>
  );
}

function TopicDetails({ node, nodes, onBack }: { node: SkillNode; nodes: SkillNode[]; onBack: () => void }) {
  const needs = node.requires.map((r) => nodes.find((n) => n.id === r)).filter((n): n is SkillNode => !!n);
  const notYet = needs.filter((n) => n.state !== "done");
  return (
    <div className="topic-details">
      <button className="link topic-back" onClick={onBack}>← All topics</button>
      <div className={`topic-state skill-${node.state}`}>{STATE_LABEL[node.state]}</div>
      <h2 className="roadmap-panel-title">{node.title}</h2>
      {node.state === "coming_soon" ? (
        <p className="muted">This topic is coming soon.</p>
      ) : (
        <>
          {notYet.length > 0 && (
            <p className="muted small-text">Best after: {notYet.map((n) => n.title).join(", ")}. You can still open it.</p>
          )}
          <ol className="topic-chapters">
            {node.chapters.map((c) => (
              <li key={`${c.lab_id}/${c.chapter_id}`} className={c.done ? "is-done" : ""}>
                <div>
                  <div className="muted small-text">{c.lab_title}{c.number !== undefined ? ` · Ch ${c.number}` : ""}</div>
                  <div className="topic-chapter-title">{c.done ? "✓ " : ""}{c.title}</div>
                </div>
                <Link className="btn btn-small btn-primary" to={`/labs/${c.lab_id}?chapter=${encodeURIComponent(c.chapter_id)}`} aria-label={`Open ${c.title}`}>
                  Open
                </Link>
              </li>
            ))}
          </ol>
        </>
      )}
    </div>
  );
}
