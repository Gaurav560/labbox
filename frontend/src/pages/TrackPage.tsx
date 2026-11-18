import { Background, Position, ReactFlow, type Edge, type Node } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, type SkillMap, type SkillNode } from "../api";
import { useAuth } from "../auth";
import StatsBadges from "../components/StatsBadges";
import { useToast } from "../components/Toasts";
import { useTheme } from "../theme";

const STATE_LABEL = { done: "Done", available: "Start", locked: "Locked", coming_soon: "Coming soon" } as const;
const COL_W = 240;
const ROW_H = 110;

// Simple layered layout: a node's column is the length of its longest prerequisite chain.
function layout(nodes: SkillNode[]): Record<string, { x: number; y: number }> {
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const depth: Record<string, number> = {};
  const depthOf = (id: string): number =>
    (depth[id] ??= byId[id].requires.length ? 1 + Math.max(...byId[id].requires.map(depthOf)) : 0);
  const rows: Record<number, number> = {};
  const pos: Record<string, { x: number; y: number }> = {};
  for (const n of nodes) {
    const d = depthOf(n.id);
    const r = (rows[d] = (rows[d] ?? -1) + 1);
    pos[n.id] = { x: d * COL_W, y: r * ROW_H };
  }
  return pos;
}

export default function TrackPage() {
  const { track = "" } = useParams();
  const { user } = useAuth();
  const { theme } = useTheme();
  const navigate = useNavigate();
  const toast = useToast();
  const [map, setMap] = useState<SkillMap | null>(null);

  useEffect(() => {
    api.skills(track).then(setMap).catch((e) => toast(e.message));
  }, [track, toast]);

  const { nodes, edges } = useMemo(() => {
    if (!map) return { nodes: [] as Node[], edges: [] as Edge[] };
    const pos = layout(map.nodes);
    const nodes: Node[] = map.nodes.map((n) => ({
      id: n.id,
      position: pos[n.id],
      className: `skill-node skill-${n.state}`,
      data: {
        label: (
          <div aria-label={`${n.title}: ${STATE_LABEL[n.state]}`}>
            <div className="skill-title">{n.title}</div>
            <div className="skill-state">{n.state === "done" ? "✓ Done" : STATE_LABEL[n.state]}</div>
          </div>
        ),
      },
      sourcePosition: Position.Right, // the map reads left to right
      targetPosition: Position.Left,
      draggable: false,
      connectable: false,
    }));
    const edges: Edge[] = map.nodes.flatMap((n) =>
      n.requires.map((r) => ({ id: `${r}-${n.id}`, source: r, target: n.id, className: `skill-edge ${n.state === "done" ? "edge-done" : ""}` })),
    );
    return { nodes, edges };
  }, [map]);

  function open(id: string) {
    const n = map?.nodes.find((x) => x.id === id);
    const ch = n?.chapters.find((c) => !c.done) ?? n?.chapters[0];
    if (n && ch && n.state !== "locked") navigate(`/labs/${ch.lab_id}`);
  }

  const done = map?.nodes.filter((n) => n.state === "done").length ?? 0;
  return (
    <div className="track-page">
      <header className="topbar">
        <Link to="/labs" className="link">← Labs</Link>
        <span className="brand">{map?.title ?? track}</span>
        {map && <span className="muted small-text">{done} of {map.nodes.length} skills</span>}
        <span className="spacer" />
        <StatsBadges username={user?.username ?? ""} />
      </header>
      <main className="track-main" aria-label="Skill map">
        {map && (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            fitViewOptions={{ padding: 0.25 }}
            nodesDraggable={false}
            nodesConnectable={false}
            onNodeClick={(_, node) => open(node.id)}
            proOptions={{ hideAttribution: false }}
            colorMode={theme}
          >
            <Background gap={24} />
          </ReactFlow>
        )}
        {map && (
          <ul className="sr-only" aria-label="Skills">
            {map.nodes.map((n) => (
              <li key={n.id}>{n.title}: {STATE_LABEL[n.state]}</li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
