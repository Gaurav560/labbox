import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import type { SkillNode } from "../api";

/*
 * The skill map as a 3D board (owner, 21 November: "a real 3D fun roadmap"): each topic is a raised tile on a
 * tilted board, linked to what it requires by glowing arched paths. Done tiles are green, the ones you can start
 * float and pulse gently, locked ones are dark, coming-soon ones are see-through. Drag to rotate, scroll to zoom,
 * click a tile to select it (the page shows its chapters, each opening its lab). Colours come from the page's CSS
 * variables, so it follows the light and dark themes. If WebGL is not available, onFail lets the page fall back
 * to the plain list.
 */

interface Props {
  nodes: SkillNode[];
  selected: string | null;
  onSelect: (id: string) => void;
  resetSignal: number;
  theme: string;
  onFail: () => void;
}

const TILE_W = 3.8;
const TILE_D = 2.2;
const TILE_H = 0.45;

/**
 * Topics in learning order (prerequisites first) along one road that winds away from the camera, like a game's
 * world map: the first topic is closest, the last one far ahead.
 */
const STEP = 6;
function order(nodes: SkillNode[]): SkillNode[] {
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const depth: Record<string, number> = {};
  const req = (id: string) => byId[id].requires.filter((r) => byId[r]);
  const depthOf = (id: string): number => (depth[id] ??= req(id).length ? 1 + Math.max(...req(id).map(depthOf)) : 0);
  return nodes.map((n, i) => ({ n, d: depthOf(n.id), i })).sort((x, y) => x.d - y.d || x.i - y.i).map((x) => x.n);
}
function layout(sorted: SkillNode[]): Record<string, THREE.Vector3> {
  const pos: Record<string, THREE.Vector3> = {};
  sorted.forEach((n, i) => { pos[n.id] = new THREE.Vector3(Math.sin(i * 0.75) * 6.5, 0, -i * STEP); });
  return pos;
}

/** A label card drawn on a canvas, shown as a sprite that always faces the camera. */
function labelSprite(title: string, state: string, colors: { text: string; muted: string; card: string; accent: string }): THREE.Sprite {
  const W = 640, H = 240;
  const canvas = document.createElement("canvas");
  canvas.width = W;
  canvas.height = H;
  const g = canvas.getContext("2d")!;
  g.fillStyle = colors.card;
  g.globalAlpha = 0.96;
  g.beginPath();
  g.roundRect(8, 8, W - 16, H - 16, 28);
  g.fill();
  g.globalAlpha = 1;
  g.fillStyle = colors.text;
  g.font = "600 46px Inter, system-ui, sans-serif";
  // wrap the title to two lines at most
  const words = title.split(" ");
  const lines: string[] = [];
  let line = "";
  for (const w of words) {
    const tryLine = line ? `${line} ${w}` : w;
    if (g.measureText(tryLine).width > W - 70 && line) {
      lines.push(line);
      line = w;
    } else line = tryLine;
  }
  lines.push(line);
  const shown = lines.slice(0, 2);
  if (lines.length > 2) shown[1] = shown[1].replace(/\s*\S*$/, "") + "...";
  shown.forEach((l, i) => g.fillText(l, 36, 78 + i * 56));
  g.font = "600 36px Inter, system-ui, sans-serif";
  g.fillStyle = state === "Start" ? colors.accent : colors.muted;
  g.fillText(state, 36, H - 40);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false }));
  sprite.scale.set(TILE_W * 0.9, (TILE_W * 0.9 * H) / W, 1);
  return sprite;
}

function roundedTile(): THREE.ExtrudeGeometry {
  const r = 0.35, w = TILE_W, d = TILE_D;
  const s = new THREE.Shape();
  s.moveTo(-w / 2 + r, -d / 2);
  s.lineTo(w / 2 - r, -d / 2);
  s.quadraticCurveTo(w / 2, -d / 2, w / 2, -d / 2 + r);
  s.lineTo(w / 2, d / 2 - r);
  s.quadraticCurveTo(w / 2, d / 2, w / 2 - r, d / 2);
  s.lineTo(-w / 2 + r, d / 2);
  s.quadraticCurveTo(-w / 2, d / 2, -w / 2, d / 2 - r);
  s.lineTo(-w / 2, -d / 2 + r);
  s.quadraticCurveTo(-w / 2, -d / 2, -w / 2 + r, -d / 2);
  const geo = new THREE.ExtrudeGeometry(s, { depth: TILE_H, bevelEnabled: true, bevelSize: 0.08, bevelThickness: 0.08, bevelSegments: 3 });
  geo.rotateX(-Math.PI / 2); // lie flat, extruded upwards
  return geo;
}

const STATE_TEXT = { done: "✓ Done", available: "Start", locked: "Locked", coming_soon: "Coming soon" } as const;

export default function Roadmap3D({ nodes, selected, onSelect, resetSignal, theme, onFail }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const api = useRef<{ reset: () => void; focus: (id: string | null) => void } | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      onFail();
      return;
    }
    const dark = theme === "dark";
    const C = {
      // From the theme itself (reading the page's CSS here can still see the previous theme mid-switch).
      bg: new THREE.Color(dark ? "#111512" : "#f6f8fa"),
      text: dark ? "#f0f3f1" : "#1f2328",
      muted: dark ? "#9ba39d" : "#59636e",
      card: dark ? "#0e1210" : "#ffffff",
      success: new THREE.Color(dark ? "#3fb950" : "#1a7f37"),
      accent: new THREE.Color("#7c6ff0"),
      locked: new THREE.Color(dark ? "#46504a" : "#b8c1ca"),
      soon: new THREE.Color(dark ? "#5a6560" : "#c9d1d9"),
      path: new THREE.Color(dark ? "#5b6660" : "#a9b3bd"),
      board: new THREE.Color(dark ? "#1a201c" : "#eef1f4"),
    };

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    host.appendChild(renderer.domElement);
    renderer.domElement.setAttribute("aria-hidden", "true");

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(C.bg, 45, 110);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 400);

    scene.add(new THREE.HemisphereLight(0xffffff, dark ? 0x222826 : 0xb8c0c8, dark ? 1.1 : 1.6));
    const sun = new THREE.DirectionalLight(0xffffff, dark ? 1.6 : 2.0);
    sun.position.set(-20, 40, 25);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    scene.add(sun);

    const sorted = order(nodes);
    const pos = layout(sorted);
    const pts = Object.values(pos);
    const box = new THREE.Box3().setFromPoints(pts.length ? pts : [new THREE.Vector3()]);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const span = Math.max(size.x + TILE_W * 2, size.z + TILE_D * 4, 16);
    sun.shadow.camera.left = -span; sun.shadow.camera.right = span; sun.shadow.camera.top = span; sun.shadow.camera.bottom = -span;
    sun.target.position.copy(center);
    scene.add(sun.target);

    // the board
    const board = new THREE.Mesh(new THREE.PlaneGeometry(span * 3, span * 3), new THREE.MeshStandardMaterial({ color: C.board, roughness: 1 }));
    board.rotation.x = -Math.PI / 2;
    board.position.set(center.x, -0.02, center.z);
    board.receiveShadow = true;
    scene.add(board);

    // The road: a flat, wide ribbon through every topic in order; the part behind the last done topic is green.
    const disposables: { dispose: () => void }[] = [];
    for (let i = 0; i + 1 < sorted.length; i++) {
      const a = pos[sorted[i].id], b = pos[sorted[i + 1].id];
      const mid = a.clone().lerp(b, 0.5);
      mid.x += (b.z - a.z) * 0.12;
      const curve = new THREE.QuadraticBezierCurve3(a.clone().setY(0.03), mid.setY(0.03), b.clone().setY(0.03));
      const geo = new THREE.TubeGeometry(curve, 40, 0.55, 8, false);
      geo.scale(1, 0.12, 1);
      const lit = sorted[i].state === "done";
      const mat = new THREE.MeshStandardMaterial({ color: lit ? C.success : C.path, emissive: lit ? C.success : new THREE.Color(0), emissiveIntensity: lit ? 0.35 : 0, roughness: 0.8 });
      const road = new THREE.Mesh(geo, mat);
      road.receiveShadow = true;
      scene.add(road);
      disposables.push(geo, mat);
    }
    // (Other prerequisite links are listed in the side panel as "Best after"; arcs here cluttered the view.)

    // tiles and labels
    const tileGeo = roundedTile();
    disposables.push(tileGeo);
    interface Tile { id: string; mesh: THREE.Mesh; label: THREE.Sprite; base: number; state: SkillNode["state"]; lift: number }
    const tiles: Tile[] = [];
    for (const n of nodes) {
      const color = n.state === "done" ? C.success : n.state === "available" ? C.accent : n.state === "locked" ? C.locked : C.soon;
      const mat = new THREE.MeshStandardMaterial({
        color, roughness: 0.45, metalness: 0.05,
        emissive: n.state === "available" ? C.accent : n.state === "done" ? C.success : new THREE.Color(0),
        emissiveIntensity: n.state === "available" ? 0.35 : n.state === "done" ? 0.15 : 0,
        transparent: n.state === "coming_soon", opacity: n.state === "coming_soon" ? 0.35 : 1,
      });
      const mesh = new THREE.Mesh(tileGeo, mat);
      mesh.position.copy(pos[n.id]);
      mesh.castShadow = n.state !== "coming_soon";
      mesh.receiveShadow = true;
      mesh.userData.id = n.id;
      scene.add(mesh);
      const label = labelSprite(n.title, STATE_TEXT[n.state], { text: C.text, muted: C.muted, card: C.card, accent: "#8c84e8" });
      label.position.copy(pos[n.id]).add(new THREE.Vector3(0, 1.6, -0.2));
      label.userData.id = n.id;
      scene.add(label);
      disposables.push(mat, label.material, (label.material as THREE.SpriteMaterial).map!);
      tiles.push({ id: n.id, mesh, label, base: 0, state: n.state, lift: 0 });
    }

    // A low camera behind a topic, looking ahead down the road: "you are here", with what comes next in view.
    const OFFSET = new THREE.Vector3(5, 9, 13);
    const AHEAD = new THREE.Vector3(0, 0, -6);
    const here = sorted.find((n) => n.state === "available") ?? sorted.find((n) => n.state !== "done") ?? sorted[0];
    const start = here ? pos[here.id] : center;
    camera.position.copy(start).add(OFFSET);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.copy(start).add(AHEAD);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.maxPolarAngle = 1.32;
    controls.minDistance = 6;
    controls.screenSpacePanning = false; // right-drag pans along the ground
    controls.maxDistance = span * 3;
    controls.update();
    controls.saveState();
    let focusTarget: THREE.Vector3 | null = null;
    api.current = {
      reset: () => { focusTarget = null; controls.reset(); },
      focus: (id) => { focusTarget = id && pos[id] ? pos[id].clone().add(AHEAD) : null; },
    };

    // pointer: hover lifts a tile, a click (not a drag) selects it
    const ray = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let hovered: string | null = null;
    let down: { x: number; y: number } | null = null;
    const pick = (ev: PointerEvent): string | null => {
      const r = renderer.domElement.getBoundingClientRect();
      mouse.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(mouse, camera);
      const hit = ray.intersectObjects(tiles.flatMap((t) => [t.mesh, t.label]), false)[0];
      return (hit?.object.userData.id as string) ?? null;
    };
    const onMove = (ev: PointerEvent) => {
      hovered = pick(ev);
      renderer.domElement.style.cursor = hovered ? "pointer" : down ? "grabbing" : "grab";
    };
    const onDown = (ev: PointerEvent) => { down = { x: ev.clientX, y: ev.clientY }; };
    const onUp = (ev: PointerEvent) => {
      if (down && Math.hypot(ev.clientX - down.x, ev.clientY - down.y) < 6) {
        const id = pick(ev);
        if (id) onSelectRef.current(id);
      }
      down = null;
    };
    renderer.domElement.addEventListener("pointermove", onMove);
    renderer.domElement.addEventListener("pointerdown", onDown);
    renderer.domElement.addEventListener("pointerup", onUp);

    const resize = () => {
      const w = host.clientWidth, h = host.clientHeight;
      if (!w || !h) return;
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };
    const ro = new ResizeObserver(resize);
    ro.observe(host);
    resize();
    controls.update();
    controls.saveState();

    renderer.setClearColor(C.bg, 0);
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const clock = new THREE.Clock();
    let frame = 0;
    const loop = () => {
      frame = requestAnimationFrame(loop);
      const t = clock.getElapsedTime();
      for (const tile of tiles) {
        const sel = tile.id === host.dataset.selected;
        const want = (tile.id === hovered ? 0.35 : 0) + (sel ? 0.5 : 0);
        tile.lift += (want - tile.lift) * 0.15;
        const bob = tile.state === "available" && !reduce ? Math.sin(t * 2 + tile.mesh.position.x) * 0.12 + 0.15 : 0;
        tile.mesh.position.y = tile.base + bob + tile.lift;
        tile.label.position.y = 1.6 + bob + tile.lift;
        const m = tile.mesh.material as THREE.MeshStandardMaterial;
        if (tile.state === "available") m.emissiveIntensity = (reduce ? 0.35 : 0.3 + Math.sin(t * 2.4) * 0.15) + (sel ? 0.3 : 0);
        else if (tile.state === "done") m.emissiveIntensity = 0.15 + (sel ? 0.3 : 0);
        else m.emissiveIntensity = sel ? 0.25 : 0;
        if (sel && tile.state !== "available" && tile.state !== "done") { m.emissive.copy(C.accent); m.emissiveIntensity = 0.45; }
        else if (tile.state === "locked" || tile.state === "coming_soon") m.emissive.set(0x000000);
      }
      if (focusTarget) {
        // fly: move the camera with the target, keeping the same viewing angle
        const step = focusTarget.clone().sub(controls.target).multiplyScalar(0.08);
        controls.target.add(step);
        camera.position.add(step);
        if (controls.target.distanceTo(focusTarget) < 0.05) focusTarget = null;
      }
      controls.update();
      renderer.render(scene, camera);
    };
    loop();

    return () => {
      cancelAnimationFrame(frame);
      ro.disconnect();
      renderer.domElement.removeEventListener("pointermove", onMove);
      renderer.domElement.removeEventListener("pointerdown", onDown);
      renderer.domElement.removeEventListener("pointerup", onUp);
      controls.dispose();
      disposables.forEach((d) => d.dispose());
      board.geometry.dispose();
      (board.material as THREE.Material).dispose();
      renderer.dispose();
      renderer.domElement.remove();
      api.current = null;
    };
    // Rebuilt when the map or the theme changes; selection and reset go through api.current.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes, theme]);

  useEffect(() => {
    if (hostRef.current) hostRef.current.dataset.selected = selected ?? "";
    api.current?.focus(selected);
  }, [selected]);

  useEffect(() => {
    if (resetSignal) api.current?.reset();
  }, [resetSignal]);

  return <div ref={hostRef} className="roadmap3d" />;
}
