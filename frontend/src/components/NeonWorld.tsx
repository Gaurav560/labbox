import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

/*
 * "Neon Coast": the skill-map world (owner, 21 November: "a 3D roadmap, when a new learner sees it says wow").
 * An original open-road world drawn entirely in code: a coastal highway at sunset (a striped sun on the horizon,
 * the sea, palm trees, a glowing city), neon lane lines, and every chapter or topic a roadside stop with a lit
 * sign. Our own rider on a scooter (LabBox colours) waits at your current stop; choosing another stop drives
 * there while the camera follows. Light theme: the same coast by day. Bloom makes the neon glow.
 */

export type StopState = "done" | "next" | "open" | "locked" | "soon";
export interface Stop { id: string; number: string; title: string; state: StopState }

interface Props {
  stops: Stop[];
  selected: string | null;
  onSelect: (id: string) => void;
  resetSignal: number;
  theme: string;
  onFail: () => void;
}

const SPACING = 18;
const ROAD_W = 3.2;

const PALETTE = {
  dark: {
    skyTop: "#1b0b3a", skyMid: "#6b1d6e", skyLow: "#ff6a5a", fog: "#3b1450", sunTop: "#ffe66b", sunLow: "#ff3d8a",
    sea: "#140a33", seaGlow: "#ff5c8a", ground: "#140d24", road: "#17121f", edgeA: "#ff2fa0", edgeB: "#21e6ff", dash: "#ffe8a3",
    palm: "#160b25", city: "#1d1238", win: ["#ffd36b", "#ff5cc8", "#5ce1ff", "#b48cff"], text: "#ffffff", board: "#0d0718",
    done: "#21ffb0", next: "#ff2fa0", open: "#8fa0ff", locked: "#5b5370", soon: "#4b4560", bloom: 0.95, sunStripes: true,
  },
  light: {
    skyTop: "#5fb6ff", skyMid: "#a9dcff", skyLow: "#ffe7c4", fog: "#cfe8ff", sunTop: "#fff6c9", sunLow: "#ffc36b",
    sea: "#1f8fd1", seaGlow: "#bfe8ff", ground: "#f1dcb0", road: "#4a4a55", edgeA: "#ff3d9a", edgeB: "#00b8d9", dash: "#ffffff",
    palm: "#2e6b3a", city: "#c9cfe8", win: ["#7f8bb5", "#9aa6cc", "#6e7aa3", "#a3b0d6"], text: "#ffffff", board: "#20263a",
    done: "#12b886", next: "#e64980", open: "#5c7cfa", locked: "#868e96", soon: "#adb5bd", bloom: 0.25, sunStripes: false,
  },
};

function mulberry(seed: number) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** The sign at a stop: a big chapter number, the title, and the state, on a dark panel. */
function signTexture(stop: Stop, color: string, text: string, board: string): THREE.CanvasTexture {
  const W = 768, H = 432;
  const c = document.createElement("canvas");
  c.width = W; c.height = H;
  const g = c.getContext("2d")!;
  g.fillStyle = board;
  g.fillRect(0, 0, W, H);
  g.strokeStyle = color;
  g.lineWidth = 14;
  g.strokeRect(10, 10, W - 20, H - 20);
  g.fillStyle = color;
  g.font = "800 120px Inter, system-ui, sans-serif";
  g.fillText(stop.number, 40, 140);
  g.fillStyle = text;
  g.font = "700 52px Inter, system-ui, sans-serif";
  const words = stop.title.split(" ");
  const lines: string[] = [];
  let line = "";
  for (const w of words) {
    const t = line ? `${line} ${w}` : w;
    if (g.measureText(t).width > W - 80 && line) { lines.push(line); line = w; } else line = t;
  }
  lines.push(line);
  lines.slice(0, 3).forEach((l, i) => g.fillText(i === 2 && lines.length > 3 ? `${l}...` : l, 40, 220 + i * 62));
  g.fillStyle = color;
  g.font = "800 40px Inter, system-ui, sans-serif";
  const label = { done: "✓ DONE", next: "▶ YOU ARE HERE", open: "OPEN", locked: "LOCKED", soon: "COMING SOON" }[stop.state];
  g.fillText(label, 40, H - 40);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

function windowsTexture(colors: string[], rnd: () => number, dark: boolean): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = 64; c.height = 128;
  const g = c.getContext("2d")!;
  g.fillStyle = dark ? "#0b0716" : "#b9c0dc";
  g.fillRect(0, 0, 64, 128);
  for (let y = 4; y < 124; y += 8) {
    for (let x = 4; x < 60; x += 8) {
      if (rnd() < (dark ? 0.45 : 0.6)) {
        g.fillStyle = colors[Math.floor(rnd() * colors.length)];
        g.fillRect(x, y, 4, 5);
      }
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

function makePalm(color: THREE.Color, rnd: () => number): THREE.Group {
  const g = new THREE.Group();
  const h = 7 + rnd() * 4;
  const lean = (rnd() - 0.5) * 2.5;
  const trunkCurve = new THREE.QuadraticBezierCurve3(new THREE.Vector3(0, 0, 0), new THREE.Vector3(lean * 0.3, h * 0.6, 0), new THREE.Vector3(lean, h, 0));
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.9 });
  g.add(new THREE.Mesh(new THREE.TubeGeometry(trunkCurve, 12, 0.22, 6, false), mat));
  const top = new THREE.Vector3(lean, h, 0);
  for (let i = 0; i < 8; i++) {
    const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.55, 5.2, 4, 1), mat);
    leaf.scale.set(1, 1, 0.18);
    leaf.position.copy(top);
    leaf.rotation.y = (i / 8) * Math.PI * 2 + rnd() * 0.3;
    leaf.rotation.z = Math.PI / 2 + 0.55 + rnd() * 0.25;
    leaf.translateY(-2.3);
    g.add(leaf);
  }
  return g;
}

/** Our own rider: a scooter in LabBox colours, a helmet with a visor, and a red backpack. Faces -z. */
function makeRider(dark: boolean): { group: THREE.Group; wheels: THREE.Mesh[]; light: THREE.SpotLight } {
  const g = new THREE.Group();
  const body = new THREE.MeshStandardMaterial({ color: dark ? "#21e6ff" : "#0ca5c9", roughness: 0.35, metalness: 0.3 });
  const trim = new THREE.MeshStandardMaterial({ color: "#ff2fa0", emissive: "#ff2fa0", emissiveIntensity: dark ? 1.2 : 0.4 });
  const black = new THREE.MeshStandardMaterial({ color: "#16131c", roughness: 0.8 });
  const skin = new THREE.MeshStandardMaterial({ color: "#c98a5a", roughness: 0.7 });
  const shirt = new THREE.MeshStandardMaterial({ color: "#f5f3ff", roughness: 0.7 });
  const pack = new THREE.MeshStandardMaterial({ color: "#d1605a", roughness: 0.6 });

  const deck = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.2, 1.7), body); deck.position.set(0, 0.48, 0.05); g.add(deck);
  const rear = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.5, 0.75), body); rear.position.set(0, 0.75, 0.6); g.add(rear);
  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.14, 0.8), black); seat.position.set(0, 1.06, 0.5); g.add(seat);
  const front = new THREE.Mesh(new THREE.BoxGeometry(0.55, 1.0, 0.25), body); front.position.set(0, 0.95, -0.72); front.rotation.x = -0.25; g.add(front);
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.6), black); stem.position.set(0, 1.55, -0.82); g.add(stem);
  const bar = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.06, 0.06), black); bar.position.set(0, 1.83, -0.8); g.add(bar);
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.72, 0.06, 0.77), trim); stripe.position.set(0, 0.62, 0.6); g.add(stripe);
  const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.13, 12, 8), new THREE.MeshStandardMaterial({ color: "#fff3c4", emissive: "#fff3c4", emissiveIntensity: 2 }));
  lamp.position.set(0, 1.35, -0.88); g.add(lamp);
  const wheels: THREE.Mesh[] = [];
  for (const z of [-0.75, 0.75]) {
    const w = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 0.22, 18), black);
    w.rotation.z = Math.PI / 2; w.position.set(0, 0.36, z); g.add(w); wheels.push(w);
    const hub = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.04, 6, 16), trim); hub.rotation.y = Math.PI / 2; hub.position.set(0.12, 0.36, z); g.add(hub);
  }
  // the rider
  const legL = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.6, 0.22), black); legL.position.set(-0.16, 1.0, 0.0); legL.rotation.x = -0.9; g.add(legL);
  const legR = legL.clone(); legR.position.x = 0.16; g.add(legR);
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.26, 0.55, 6, 12), shirt); torso.position.set(0, 1.68, 0.38); torso.rotation.x = -0.25; g.add(torso);
  const armL = new THREE.Mesh(new THREE.CapsuleGeometry(0.08, 0.6, 4, 8), shirt); armL.position.set(-0.3, 1.75, -0.2); armL.rotation.x = -1.2; g.add(armL);
  const armR = armL.clone(); armR.position.x = 0.3; g.add(armR);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 12), skin); head.position.set(0, 2.2, 0.25); g.add(head);
  const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.27, 18, 12, 0, Math.PI * 2, 0, Math.PI * 0.62), trim); helmet.position.set(0, 2.24, 0.27); g.add(helmet);
  const visor = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.12, 0.05), new THREE.MeshStandardMaterial({ color: "#0b0b12", metalness: 0.8, roughness: 0.1 }));
  visor.position.set(0, 2.2, 0.02); g.add(visor);
  const bag = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.55, 0.28), pack); bag.position.set(0, 1.75, 0.72); bag.rotation.x = -0.25; g.add(bag);
  const logo = new THREE.Mesh(new THREE.PlaneGeometry(0.2, 0.2), new THREE.MeshStandardMaterial({ color: "#ffffff", emissive: "#ffffff", emissiveIntensity: 0.8 }));
  logo.position.set(0, 1.78, 0.87); logo.rotation.x = -0.25; g.add(logo);

  g.traverse((o) => { if ((o as THREE.Mesh).isMesh) { o.castShadow = true; } });
  const light = new THREE.SpotLight("#fff1c1", dark ? 40 : 0, 30, 0.5, 0.6, 1.2);
  light.position.set(0, 1.4, -0.9);
  light.target.position.set(0, 0, -10);
  g.add(light, light.target);
  g.scale.setScalar(1.6);
  return { group: g, wheels, light };
}

export default function NeonWorld({ stops, selected, onSelect, resetSignal, theme, onFail }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const api = useRef<{ go: (id: string | null) => void; reset: () => void } | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  useEffect(() => {
    const host = hostRef.current;
    if (!host || stops.length === 0) return;
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true });
    } catch {
      onFail();
      return;
    }
    const dark = theme === "dark";
    const P = dark ? PALETTE.dark : PALETTE.light;
    const rnd = mulberry(42);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = dark ? 1.05 : 1.0;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    host.appendChild(renderer.domElement);
    renderer.domElement.setAttribute("aria-hidden", "true");

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(P.fog, 90, 420);
    const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 2000);

    // ---- sky: a gradient dome ----
    const sky = new THREE.Mesh(
      new THREE.SphereGeometry(1200, 32, 16),
      new THREE.ShaderMaterial({
        side: THREE.BackSide, depthWrite: false, fog: false,
        uniforms: { top: { value: new THREE.Color(P.skyTop) }, mid: { value: new THREE.Color(P.skyMid) }, low: { value: new THREE.Color(P.skyLow) } },
        vertexShader: "varying vec3 vp; void main(){ vp = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
        fragmentShader: "uniform vec3 top; uniform vec3 mid; uniform vec3 low; varying vec3 vp; void main(){ float h = clamp(vp.y, -0.2, 1.0); vec3 c = h < 0.12 ? mix(low, mid, smoothstep(-0.05, 0.12, h)) : mix(mid, top, smoothstep(0.12, 0.6, h)); gl_FragColor = vec4(c, 1.0); }",
      }),
    );
    scene.add(sky);

    // ---- the road: a winding curve away from the camera ----
    const count = stops.length;
    const pts: THREE.Vector3[] = [];
    for (let i = -2; i <= count + 3; i++) pts.push(new THREE.Vector3(Math.sin(i * 0.55) * 16, 0, -i * SPACING));
    const curve = new THREE.CatmullRomCurve3(pts, false, "catmullrom", 0.5);
    const total = curve.getLength();
    const uStop = (i: number) => {
      // where along the road (0 to 1, by length) stop i's control point lies
      const target = pts[i + 2];
      let best = 0, bestD = Infinity;
      for (let k = 0; k <= 400; k++) {
        const u = k / 400;
        const d = curve.getPointAt(u).distanceToSquared(target);
        if (d < bestD) { bestD = d; best = u; }
      }
      return best;
    };
    const stopU = stops.map((_, i) => uStop(i));
    const sideAt = (u: number) => {
      const t = curve.getTangentAt(u);
      return new THREE.Vector3().crossVectors(t, new THREE.Vector3(0, 1, 0)).normalize();
    };

    const disposables: { dispose: () => void }[] = [];
    const add = <T extends THREE.Object3D>(o: T) => { scene.add(o); return o; };

    // ground and sea
    const ground = add(new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshStandardMaterial({ color: P.ground, roughness: 1 })));
    ground.rotation.x = -Math.PI / 2; ground.position.y = -0.05; ground.receiveShadow = true;
    const seaMat = new THREE.ShaderMaterial({
      fog: false,
      uniforms: { time: { value: 0 }, sea: { value: new THREE.Color(P.sea) }, glow: { value: new THREE.Color(P.seaGlow) } },
      vertexShader: "varying vec2 vUv; varying vec3 wp; void main(){ vUv = uv; vec4 w = modelMatrix * vec4(position,1.0); wp = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }",
      fragmentShader: "uniform float time; uniform vec3 sea; uniform vec3 glow; varying vec2 vUv; varying vec3 wp; void main(){ float streak = smoothstep(0.75, 1.0, sin(wp.z * 0.08 + time * 1.5 + sin(wp.x * 0.05) * 2.0)) * smoothstep(400.0, 0.0, abs(wp.x - 300.0)); vec3 c = mix(sea, glow, streak * 0.55); gl_FragColor = vec4(c, 1.0); }",
    });
    const sea = add(new THREE.Mesh(new THREE.PlaneGeometry(900, 3000), seaMat));
    sea.rotation.x = -Math.PI / 2; sea.position.set(560, 0.02, -800);
    disposables.push(seaMat);

    // the sun on the horizon, straight down the road
    const sunMat = new THREE.ShaderMaterial({
      transparent: true, fog: false, depthWrite: false,
      uniforms: { top: { value: new THREE.Color(P.sunTop) }, low: { value: new THREE.Color(P.sunLow) }, stripes: { value: P.sunStripes ? 1 : 0 } },
      vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
      fragmentShader: "uniform vec3 top; uniform vec3 low; uniform float stripes; varying vec2 vUv; void main(){ vec2 p = vUv - 0.5; if (length(p) > 0.5) discard; float y = vUv.y; if (stripes > 0.5 && y < 0.48) { float band = fract(y * 16.0); if (band < 0.25 + (0.48 - y) * 0.9) discard; } gl_FragColor = vec4(mix(low, top, smoothstep(0.1, 0.9, y)) * 1.05, 1.0); }",
    });
    const sun = add(new THREE.Mesh(new THREE.CircleGeometry(150, 64), sunMat));
    sun.position.set(30, 55, -(count + 3) * SPACING - 700);
    disposables.push(sunMat);

    // the road surface: a ribbon along the curve
    {
      const N = Math.max(200, count * 40);
      const pos: number[] = [];
      const idx: number[] = [];
      for (let i = 0; i <= N; i++) {
        const u = i / N;
        const p = curve.getPointAt(u);
        const s = sideAt(u);
        const l = p.clone().addScaledVector(s, ROAD_W), r = p.clone().addScaledVector(s, -ROAD_W);
        pos.push(l.x, 0.02, l.z, r.x, 0.02, r.z);
        if (i < N) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
      geo.setIndex(idx);
      geo.computeVertexNormals();
      const mat = new THREE.MeshStandardMaterial({ color: P.road, roughness: 0.5, metalness: 0.2, side: THREE.DoubleSide });
      const road = add(new THREE.Mesh(geo, mat));
      road.receiveShadow = true;
      disposables.push(geo, mat);
      // neon edges
      for (const [off, col] of [[ROAD_W + 0.15, P.edgeA], [-ROAD_W - 0.15, P.edgeB]] as const) {
        const ep: THREE.Vector3[] = [];
        for (let i = 0; i <= N; i += 2) { const u = i / N; ep.push(curve.getPointAt(u).addScaledVector(sideAt(u), off).setY(0.12)); }
        const eg = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ep), N, 0.09, 6, false);
        const em = new THREE.MeshBasicMaterial({ color: new THREE.Color(col).multiplyScalar(dark ? 2.2 : 1.1) });
        add(new THREE.Mesh(eg, em));
        disposables.push(eg, em);
      }
      // centre dashes
      const dashGeo = new THREE.BoxGeometry(0.16, 0.03, 1.6);
      const dashMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(P.dash).multiplyScalar(dark ? 1.4 : 1) });
      const dashes = Math.floor(total / 4);
      const inst = new THREE.InstancedMesh(dashGeo, dashMat, dashes);
      const m = new THREE.Matrix4();
      for (let i = 0; i < dashes; i++) {
        const u = (i + 0.5) / dashes;
        const p = curve.getPointAt(u).setY(0.05);
        const t = curve.getTangentAt(u);
        m.makeRotationY(Math.atan2(t.x, t.z)).setPosition(p);
        inst.setMatrixAt(i, m);
      }
      add(inst);
      disposables.push(dashGeo, dashMat);
    }

    // palms along both sides
    const palmColor = new THREE.Color(P.palm);
    for (let i = 0; i < count * 3 + 12; i++) {
      const u = Math.min(1, Math.max(0, rnd()));
      const side = rnd() < 0.5 ? 1 : -1;
      const p = curve.getPointAt(u).addScaledVector(sideAt(u), side * (ROAD_W + 9 + rnd() * 16));
      const palm = makePalm(palmColor, rnd);
      palm.position.copy(p);
      palm.rotation.y = rnd() * Math.PI * 2;
      palm.scale.setScalar(0.9 + rnd() * 0.6);
      palm.traverse((o) => { if ((o as THREE.Mesh).isMesh) o.castShadow = true; });
      add(palm);
    }

    // the city: towers with lit windows, on the land side
    const winTex = windowsTexture(P.win, rnd, dark);
    disposables.push(winTex);
    const cityMat = new THREE.MeshStandardMaterial({ color: P.city, map: winTex, emissive: new THREE.Color("#ffffff"), emissiveMap: winTex, emissiveIntensity: dark ? 1.3 : 0.15, roughness: 0.8 });
    disposables.push(cityMat);
    for (let i = 0; i < 90; i++) {
      const w = 8 + rnd() * 16, h = 20 + rnd() * (dark ? 110 : 80), d = 8 + rnd() * 16;
      const geo = new THREE.BoxGeometry(w, h, d);
      const uv = geo.getAttribute("uv") as THREE.BufferAttribute;
      for (let k = 0; k < uv.count; k++) uv.setXY(k, uv.getX(k) * w / 16, uv.getY(k) * h / 32);
      const tower = add(new THREE.Mesh(geo, cityMat));
      tower.position.set(-110 - rnd() * 260, h / 2, 60 - rnd() * ((count + 6) * SPACING + 300));
      disposables.push(geo);
      if (dark && rnd() < 0.3) {
        const neon = new THREE.Mesh(new THREE.BoxGeometry(w + 0.6, 0.6, d + 0.6), new THREE.MeshBasicMaterial({ color: new THREE.Color(rnd() < 0.5 ? P.edgeA : P.edgeB).multiplyScalar(2) }));
        neon.position.set(tower.position.x, h + 0.3, tower.position.z);
        add(neon);
      }
    }

    // stars
    if (dark) {
      const sp: number[] = [];
      for (let i = 0; i < 1500; i++) {
        const th = rnd() * Math.PI * 2, ph = rnd() * 0.45 + 0.08;
        sp.push(Math.cos(th) * Math.cos(ph) * 1000, Math.sin(ph) * 1000, Math.sin(th) * Math.cos(ph) * 1000);
      }
      const sg = new THREE.BufferGeometry();
      sg.setAttribute("position", new THREE.Float32BufferAttribute(sp, 3));
      const sm = new THREE.PointsMaterial({ color: "#ffffff", size: 1.6, sizeAttenuation: false, fog: false });
      add(new THREE.Points(sg, sm));
      disposables.push(sg, sm);
    }

    // lights
    scene.add(new THREE.HemisphereLight(dark ? "#ff9ad5" : "#ffffff", dark ? "#1a0f2e" : "#c9b48a", dark ? 0.9 : 1.6));
    const sunLight = new THREE.DirectionalLight(dark ? "#ff9a7a" : "#fff6e0", dark ? 1.4 : 2.4);
    sunLight.position.set(40, 60, -80);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.set(2048, 2048);
    Object.assign(sunLight.shadow.camera, { left: -60, right: 60, top: 60, bottom: -60, far: 300 });
    scene.add(sunLight, sunLight.target);

    // ---- the stops: a sign, a glow on the road, and a light beam at the stop you are at ----
    interface StopObj { id: string; i: number; sign: THREE.Group; ring: THREE.Mesh; beam: THREE.Mesh | null; state: StopState }
    const stopObjs: StopObj[] = [];
    const pickables: THREE.Object3D[] = [];
    stops.forEach((s, i) => {
      const u = stopU[i];
      const p = curve.getPointAt(u);
      const side = sideAt(u);
      const dir = i % 2 === 0 ? 1 : -1;
      const color = P[s.state];
      const tex = signTexture(s, color, P.text, P.board);
      disposables.push(tex);
      const sign = new THREE.Group();
      const boardMat = new THREE.MeshStandardMaterial({ map: tex, emissive: new THREE.Color("#ffffff"), emissiveMap: tex, emissiveIntensity: dark ? (s.state === "locked" || s.state === "soon" ? 0.25 : 0.5) : 0.25 });
      const board = new THREE.Mesh(new THREE.PlaneGeometry(6.4, 3.6), boardMat);
      board.position.y = 4.6;
      const back = new THREE.Mesh(new THREE.BoxGeometry(6.7, 3.9, 0.25), new THREE.MeshStandardMaterial({ color: "#0b0712" }));
      back.position.set(0, 4.6, -0.14);
      const frame = new THREE.Mesh(new THREE.BoxGeometry(6.9, 4.1, 0.1), new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(dark ? 1.8 : 1.0) }));
      frame.position.set(0, 4.6, -0.3);
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 2.8), new THREE.MeshStandardMaterial({ color: "#2b2338", metalness: 0.6, roughness: 0.4 }));
      post.position.y = 1.4;
      sign.add(post, back, frame, board);
      sign.position.copy(p).addScaledVector(side, dir * (ROAD_W + 3.2));
      // face the oncoming rider (the camera comes from +z along the road)
      const t = curve.getTangentAt(u);
      sign.lookAt(sign.position.clone().sub(t).addScaledVector(side, -dir * 0.6));
      sign.traverse((o) => { o.userData.stop = s.id; if ((o as THREE.Mesh).isMesh) o.castShadow = true; });
      add(sign);
      pickables.push(board, back, frame);
      const ringMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(dark ? 1.6 : 1), transparent: true, opacity: 0.85, side: THREE.DoubleSide });
      const ring = new THREE.Mesh(new THREE.RingGeometry(2.0, 2.4, 40), ringMat);
      ring.rotation.x = -Math.PI / 2;
      ring.position.copy(p).setY(0.08);
      ring.userData.stop = s.id;
      add(ring);
      pickables.push(ring);
      let beam: THREE.Mesh | null = null;
      if (s.state === "next") {
        beam = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.7, 70, 20, 1, true), new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(1.2), transparent: true, opacity: 0.16, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
        beam.position.copy(p).addScaledVector(side, dir * (ROAD_W + 3.2)).setY(39);
        add(beam);
      }
      stopObjs.push({ id: s.id, i, sign, ring, beam, state: s.state });
    });

    // ---- the rider ----
    const rider = makeRider(dark);
    add(rider.group);
    // start where the learner chose last (kept across a theme switch), else at "you are here"
    const chosen = stops.findIndex((s) => s.id === host.dataset.selected);
    const startIndex = chosen >= 0 ? chosen : Math.max(0, stops.findIndex((s) => s.state === "next"));
    let u = stopU[startIndex] ?? 0;
    let uTarget = u;
    const speed = 30 / total; // fraction of the road per second
    const place = () => {
      const p = curve.getPointAt(u);
      const t = curve.getTangentAt(u);
      // ride on the right-hand lane, facing down the road (-z)
      rider.group.position.copy(p).addScaledVector(sideAt(u), -1.4);
      rider.group.lookAt(rider.group.position.clone().add(t));
      rider.group.rotateY(Math.PI);
    };
    place();

    // ---- camera: a chase camera behind the rider, with an intro swoop ----
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.maxPolarAngle = 1.45;
    controls.minDistance = 4;
    controls.maxDistance = 120;
    controls.enablePan = false;
    const behind = () => {
      const t = curve.getTangentAt(u);
      return rider.group.position.clone().addScaledVector(t, -9).add(new THREE.Vector3(0, 3.6, 0)).addScaledVector(sideAt(u), -2.2);
    };
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const lookAhead = () => rider.group.position.clone().addScaledVector(curve.getTangentAt(u), 10).add(new THREE.Vector3(0, 2.2, 0));
    controls.target.copy(lookAhead());
    const chase = behind();
    const intro = { t: reduce ? 1 : 0, from: rider.group.position.clone().add(new THREE.Vector3(60, 90, 90)) };
    camera.position.copy(reduce ? chase : intro.from);
    controls.update();

    api.current = {
      go: (id) => {
        const k = stops.findIndex((s) => s.id === id);
        if (k >= 0) uTarget = stopU[k];
      },
      reset: () => {
        camera.position.copy(behind());
        controls.target.copy(lookAhead());
      },
    };

    // ---- clicking a sign or a ring selects that stop ----
    const ray = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let down: { x: number; y: number } | null = null;
    const pick = (ev: PointerEvent): string | null => {
      const r = renderer.domElement.getBoundingClientRect();
      mouse.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(mouse, camera);
      return (ray.intersectObjects(pickables, false)[0]?.object.userData.stop as string) ?? null;
    };
    const onMove = (ev: PointerEvent) => { renderer.domElement.style.cursor = pick(ev) ? "pointer" : down ? "grabbing" : "grab"; };
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

    // ---- bloom ----
    const composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    const bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), P.bloom, 0.55, dark ? 0.62 : 0.9);
    composer.addPass(bloom);
    composer.addPass(new OutputPass());

    const resize = () => {
      const w = host.clientWidth, h = host.clientHeight;
      if (!w || !h) return;
      renderer.setSize(w, h);
      composer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };
    const ro = new ResizeObserver(resize);
    ro.observe(host);
    resize();

    const clock = new THREE.Clock();
    let frame = 0;
    let settle = 0;
    const loop = () => {
      frame = requestAnimationFrame(loop);
      const dt = Math.min(0.05, clock.getDelta());
      const time = clock.elapsedTime;
      seaMat.uniforms.time.value = time;
      // drive
      const before = rider.group.position.clone();
      if (Math.abs(uTarget - u) > 1e-4) {
        const step = reduce ? uTarget - u : Math.sign(uTarget - u) * Math.min(Math.abs(uTarget - u), speed * dt);
        u += step;
        place();
        for (const w of rider.wheels) w.rotation.x -= (Math.abs(step) * total) / 0.36 * Math.sign(step || 1);
      }
      const moved = rider.group.position.clone().sub(before);
      camera.position.add(moved);
      controls.target.add(moved);
      // while riding (and a moment after), swing the camera back in behind the rider as the road turns
      if (moved.lengthSq() > 1e-6) settle = 1.2;
      if (settle > 0 && intro.t >= 1) {
        settle -= dt;
        camera.position.lerp(behind(), 0.05);
        controls.target.lerp(lookAhead(), 0.08);
      }
      // intro swoop from high above down to the chase camera
      if (intro.t < 1) {
        intro.t = Math.min(1, intro.t + dt / 2.4);
        const e = 1 - Math.pow(1 - intro.t, 3);
        camera.position.lerpVectors(intro.from, behind(), e);
      }
      for (const s of stopObjs) {
        const sel = s.id === host.dataset.selected;
        s.ring.scale.setScalar(sel ? 1.25 + Math.sin(time * 4) * 0.08 : 1);
        if (s.beam) (s.beam.material as THREE.MeshBasicMaterial).opacity = 0.12 + Math.sin(time * 2) * 0.05;
      }
      controls.update();
      composer.render();
    };
    loop();

    return () => {
      cancelAnimationFrame(frame);
      ro.disconnect();
      renderer.domElement.removeEventListener("pointermove", onMove);
      renderer.domElement.removeEventListener("pointerdown", onDown);
      renderer.domElement.removeEventListener("pointerup", onUp);
      controls.dispose();
      composer.dispose();
      scene.traverse((o) => {
        const m = o as THREE.Mesh;
        if (m.geometry) m.geometry.dispose();
        const mats = m.material ? (Array.isArray(m.material) ? m.material : [m.material]) : [];
        mats.forEach((x) => x.dispose());
      });
      disposables.forEach((d) => d.dispose());
      renderer.dispose();
      renderer.domElement.remove();
      api.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stops, theme]);

  useEffect(() => {
    if (hostRef.current) hostRef.current.dataset.selected = selected ?? "";
    api.current?.go(selected);
  }, [selected]);

  useEffect(() => {
    if (resetSignal) api.current?.reset();
  }, [resetSignal]);

  return <div ref={hostRef} className="roadmap3d neon-world" />;
}
