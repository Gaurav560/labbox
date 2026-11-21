import { useEffect, useRef } from "react";
import * as THREE from "three";
import { CSS2DObject, CSS2DRenderer } from "three/addons/renderers/CSS2DRenderer.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

/*
 * "Sky islands": the skill-map world. Every chapter (or topic) is a small floating island; glowing stepping
 * stones climb from one to the next through drifting clouds. Finished islands fly a flag, the one you are on has
 * a glowing crystal, and our own character, Bit, hops from stone to stone to the island you choose while the
 * camera follows. Labels are real HTML (crisp at any size, clickable). Dawn colours in the light theme, twilight
 * with stars in the dark one. Everything is drawn in code: no downloaded models.
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

const LOOK = {
  light: {
    skyTop: "#6fb3ff", skyMid: "#ffc6dd", skyLow: "#ffd7a3", fog: "#f3c9dc", sunCol: "#fff1d6",
    grass: ["#8ed07a", "#7cc46b", "#9bd88a"], sand: "#f2d6a2", rock: ["#c79a72", "#a9805e", "#8a6a50"],
    leaf: ["#5fb85c", "#4fa652", "#77c86a"], trunk: "#8a5a3c", stone: "#f4f1ea", stoneLit: "#ffd36b",
    crystal: "#ff6fb1", flag: "#d1605a", cloud: "#ffffff", hemiSky: "#ffffff", hemiGround: "#c8a2a8",
    sunI: 2.1, hemiI: 0.85, bloom: 0.12, exposure: 0.95, stars: false,
  },
  dark: {
    skyTop: "#070b24", skyMid: "#2b2366", skyLow: "#7a3f86", fog: "#26204d", sunCol: "#b9c4ff",
    grass: ["#3f8f6e", "#357f62", "#4aa07c"], sand: "#a88c74", rock: ["#5a4a66", "#4a3d58", "#3a304a"],
    leaf: ["#2f7d63", "#276b55", "#3a9174"], trunk: "#5b3f3a", stone: "#bfc6ff", stoneLit: "#7df9ff",
    crystal: "#7df9ff", flag: "#ff7aa8", cloud: "#8f86c9", hemiSky: "#8f9dff", hemiGround: "#2a1f3d",
    sunI: 1.3, hemiI: 0.9, bloom: 0.9, exposure: 1.1, stars: true,
  },
};

function rng(seed: number) {
  return () => {
    seed = (seed * 1664525 + 1013904223) % 4294967296;
    return seed / 4294967296;
  };
}

/** An organic island: a grass cap with a wavy edge, a sandy lip, and a rocky underside that tapers to a point. */
function makeIsland(L: typeof LOOK.light, r: () => number, radius: number): THREE.Group {
  const g = new THREE.Group();
  const wobble = Array.from({ length: 4 }, () => ({ f: 2 + Math.floor(r() * 4), a: 0.05 + r() * 0.08, p: r() * 6.28 }));
  const edge = (ang: number) => 1 + wobble.reduce((s, w) => s + Math.sin(ang * w.f + w.p) * w.a, 0);
  const shape = (geo: THREE.BufferGeometry, colorAt: (y: number, v: THREE.Vector3) => THREE.Color, rough: number) => {
    const pos = geo.getAttribute("position") as THREE.BufferAttribute;
    const cols: number[] = [];
    const v = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      const ang = Math.atan2(v.z, v.x);
      const k = edge(ang);
      const n = rough ? 1 + (Math.sin(v.y * 3.1 + ang * 5) * 0.5 + Math.sin(ang * 11 + v.y * 1.7) * 0.5) * rough : 1;
      v.x *= k * n; v.z *= k * n;
      pos.setXYZ(i, v.x, v.y, v.z);
      const c = colorAt(v.y, v);
      cols.push(c.r, c.g, c.b);
    }
    geo.setAttribute("color", new THREE.Float32BufferAttribute(cols, 3));
    geo.computeVertexNormals();
    return geo;
  };
  const mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9, metalness: 0 });
  const grassCols = L.grass.map((c) => new THREE.Color(c));
  const top = shape(new THREE.CylinderGeometry(radius, radius * 1.02, 0.7, 64, 2), (y, v) => (y > 0.2 ? grassCols[0].clone().lerp(grassCols[2], 0.5 + 0.5 * Math.sin(v.x * 0.9) * Math.cos(v.z * 0.8)) : new THREE.Color(L.sand)), 0);
  const cap = new THREE.Mesh(top, mat);
  cap.receiveShadow = true;
  cap.castShadow = true;
  g.add(cap);
  const rocks = L.rock.map((c) => new THREE.Color(c));
  const depth = 3.2 + r() * 2.2;
  const under = new THREE.ConeGeometry(radius * 1.0, depth, 48, 8);
  under.rotateX(Math.PI);
  under.translate(0, -depth / 2 - 0.34, 0);
  shape(under, (y) => rocks[0].clone().lerp(rocks[2], Math.min(1, -y / depth)), 0.08);
  const rock = new THREE.Mesh(under, mat);
  rock.castShadow = true;
  g.add(rock);
  return g;
}

function makeTree(L: typeof LOOK.light, r: () => number): THREE.Group {
  const g = new THREE.Group();
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.14, 0.9, 8), new THREE.MeshStandardMaterial({ color: L.trunk, roughness: 0.9 }));
  trunk.position.y = 0.45;
  g.add(trunk);
  const leafMat = new THREE.MeshStandardMaterial({ color: L.leaf[Math.floor(r() * 3)], roughness: 0.8, flatShading: false });
  for (let i = 0; i < 3; i++) {
    const s = 0.55 - i * 0.12 + r() * 0.1;
    const blob = new THREE.Mesh(new THREE.IcosahedronGeometry(s, 2), leafMat);
    blob.position.set((r() - 0.5) * 0.3, 1.0 + i * 0.32, (r() - 0.5) * 0.3);
    g.add(blob);
  }
  g.traverse((o) => { if ((o as THREE.Mesh).isMesh) { o.castShadow = true; } });
  return g;
}

/** Bit, our own character: a round body in a LabBox-red hoodie, big eyes, a little backpack and a scarf. */
function makeBit(): { group: THREE.Group; body: THREE.Group } {
  const g = new THREE.Group();
  const body = new THREE.Group();
  g.add(body);
  const hoodie = new THREE.MeshStandardMaterial({ color: "#e0645d", roughness: 0.6 });
  const skin = new THREE.MeshStandardMaterial({ color: "#f2c39b", roughness: 0.6 });
  const dark = new THREE.MeshStandardMaterial({ color: "#1d1a24", roughness: 0.4 });
  const white = new THREE.MeshStandardMaterial({ color: "#ffffff", emissive: "#ffffff", emissiveIntensity: 0.3 });
  const scarf = new THREE.MeshStandardMaterial({ color: "#ffd36b", roughness: 0.6 });
  const pack = new THREE.MeshStandardMaterial({ color: "#3b4a8c", roughness: 0.6 });
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.34, 0.32, 8, 20), hoodie); torso.position.y = 0.62; body.add(torso);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.42, 32, 24), skin); head.position.y = 1.28; body.add(head);
  const hairMat = new THREE.MeshStandardMaterial({ color: "#2b1d1a", roughness: 0.7 });
  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.44, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.42), hairMat); hair.position.set(0, 1.31, 0.03); hair.rotation.x = 0.25; body.add(hair);
  const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.26, 12), hairMat); tuft.position.set(0.05, 1.78, 0.02); tuft.rotation.z = -0.4; body.add(tuft);
  for (const x of [-0.13, 0.13]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.075, 16, 12), dark); eye.position.set(x, 1.27, -0.37); eye.scale.z = 0.6; body.add(eye);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.025, 8, 6), white); glint.position.set(x + 0.025, 1.3, -0.42); body.add(glint);
  }
  const blush = new THREE.MeshStandardMaterial({ color: "#ff9a9a", roughness: 0.8, transparent: true, opacity: 0.7 });
  for (const x of [-0.22, 0.22]) { const b = new THREE.Mesh(new THREE.CircleGeometry(0.05, 16), blush); b.position.set(x, 1.16, -0.38); b.rotation.y = Math.PI + x; body.add(b); }
  const sc = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.07, 10, 28), scarf); sc.rotation.x = Math.PI / 2; sc.position.y = 0.92; body.add(sc);
  const tail = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.3, 0.05), scarf); tail.position.set(0.16, 0.78, 0.28); tail.rotation.z = 0.3; body.add(tail);
  const bag = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.44, 0.2), pack); bag.position.set(0, 0.68, 0.36); body.add(bag);
  const strap = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.06, 0.02), new THREE.MeshStandardMaterial({ color: "#ffffff", emissive: "#ffffff", emissiveIntensity: 0.4 })); strap.position.set(0, 0.78, 0.47); body.add(strap);
  for (const x of [-0.14, 0.14]) { const foot = new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 12), dark); foot.scale.set(1, 0.6, 1.3); foot.position.set(x, 0.1, -0.02); body.add(foot); }
  for (const x of [-0.4, 0.4]) { const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.08, 0.22, 6, 10), hoodie); arm.position.set(x, 0.62, 0); arm.rotation.z = x > 0 ? -0.35 : 0.35; body.add(arm); }
  g.traverse((o) => { if ((o as THREE.Mesh).isMesh) o.castShadow = true; });
  g.scale.setScalar(2);
  return { group: g, body };
}

function cloudTexture(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d")!;
  const grad = g.createRadialGradient(64, 64, 4, 64, 64, 62);
  grad.addColorStop(0, "rgba(255,255,255,0.95)");
  grad.addColorStop(0.5, "rgba(255,255,255,0.55)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export default function IslandWorld({ stops, selected, onSelect, resetSignal, theme, onFail }: Props) {
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
    const L = dark ? LOOK.dark : LOOK.light;
    const r = rng(7);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = L.exposure;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    host.appendChild(renderer.domElement);
    renderer.domElement.setAttribute("aria-hidden", "true");
    const labels = new CSS2DRenderer();
    labels.domElement.className = "island-labels";
    host.appendChild(labels.domElement);

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(L.fog, 90, 260);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 2000);

    // sky dome with a soft sun glow
    const skyMat = new THREE.ShaderMaterial({
      side: THREE.BackSide, depthWrite: false, fog: false,
      uniforms: { top: { value: new THREE.Color(L.skyTop) }, mid: { value: new THREE.Color(L.skyMid) }, low: { value: new THREE.Color(L.skyLow) }, sun: { value: new THREE.Color(L.sunCol) }, sunDir: { value: new THREE.Vector3(0.3, 0.25, -1).normalize() } },
      vertexShader: "varying vec3 vp; void main(){ vp = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
      fragmentShader: "uniform vec3 top; uniform vec3 mid; uniform vec3 low; uniform vec3 sun; uniform vec3 sunDir; varying vec3 vp; void main(){ float h = vp.y; vec3 c = h < 0.1 ? mix(low, mid, smoothstep(-0.3, 0.1, h)) : mix(mid, top, smoothstep(0.1, 0.75, h)); float s = max(dot(vp, sunDir), 0.0); c += sun * (pow(s, 60.0) * 0.9 + pow(s, 6.0) * 0.25); gl_FragColor = vec4(c, 1.0); }",
    });
    scene.add(new THREE.Mesh(new THREE.SphereGeometry(1000, 48, 24), skyMat));

    // light
    scene.add(new THREE.HemisphereLight(L.hemiSky, L.hemiGround, L.hemiI));
    const sun = new THREE.DirectionalLight(L.sunCol, L.sunI);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.radius = 4;
    sun.shadow.bias = -0.0005;
    scene.add(sun, sun.target);

    // ---- islands along a climbing, winding path ----
    const n = stops.length;
    const centers: THREE.Vector3[] = [];
    for (let i = 0; i < n; i++) centers.push(new THREE.Vector3(Math.sin(i * 0.85) * 9 + Math.sin(i * 0.31) * 4, i * 1.4, -i * 12));
    const pickables: THREE.Object3D[] = [];
    const crystals: THREE.Mesh[] = [];
    const flags: THREE.Mesh[] = [];
    const labelEls: { el: HTMLDivElement; obj: CSS2DObject; id: string }[] = [];
    const islands: THREE.Group[] = [];
    stops.forEach((s, i) => {
      const radius = 3.2 + r() * 0.9;
      const island = makeIsland(L, r, radius);
      island.position.copy(centers[i]);
      island.rotation.y = r() * Math.PI * 2;
      island.userData = { stop: s.id, baseY: centers[i].y, phase: r() * 6.28 };
      island.traverse((o) => { o.userData.stop = s.id; });
      scene.add(island);
      islands.push(island);
      pickables.push(island);
      // decoration: trees and rocks, more of them on islands you have not reached yet
      const trees = s.state === "done" ? 2 : 3 + Math.floor(r() * 2);
      for (let k = 0; k < trees; k++) {
        const t = makeTree(L, r);
        const a = r() * Math.PI * 2, d = radius * (0.45 + r() * 0.35);
        t.position.set(Math.cos(a) * d, 0.35, Math.sin(a) * d);
        t.scale.setScalar(0.8 + r() * 0.5);
        island.add(t);
      }
      for (let k = 0; k < 3; k++) {
        const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(0.18 + r() * 0.2, 0), new THREE.MeshStandardMaterial({ color: L.rock[0], roughness: 0.9 }));
        const a = r() * Math.PI * 2, d = radius * (0.3 + r() * 0.55);
        rock.position.set(Math.cos(a) * d, 0.42, Math.sin(a) * d);
        rock.castShadow = true;
        island.add(rock);
      }
      if (s.state === "done") {
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.2, 8), new THREE.MeshStandardMaterial({ color: "#f5f5f5" }));
        pole.position.set(0, 1.45, 0);
        const flag = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.55, 10, 4), new THREE.MeshStandardMaterial({ color: L.flag, side: THREE.DoubleSide, roughness: 0.7 }));
        flag.position.set(0.47, 2.25, 0);
        island.add(pole, flag);
        flags.push(flag);
      }
      if (s.state === "next") {
        const crystal = new THREE.Mesh(new THREE.OctahedronGeometry(0.45, 0), new THREE.MeshStandardMaterial({ color: L.crystal, emissive: L.crystal, emissiveIntensity: 1.6, roughness: 0.2, metalness: 0.1 }));
        crystal.position.set(1.4, 2.0, 0);
        crystal.scale.y = 1.6;
        island.add(crystal);
        crystals.push(crystal);
        const glow = new THREE.PointLight(L.crystal, 6, 9);
        glow.position.copy(crystal.position);
        island.add(glow);
      }
      // the label, as real HTML
      const el = document.createElement("div");
      el.className = `island-label is-${s.state}`;
      el.innerHTML = `<span class="il-num">${s.number}</span><span class="il-title"></span>${s.state === "done" ? '<span class="il-badge">✓</span>' : s.state === "next" ? '<span class="il-badge">You are here</span>' : ""}`;
      (el.querySelector(".il-title") as HTMLElement).textContent = s.title;
      el.addEventListener("click", () => onSelectRef.current(s.id));
      const obj = new CSS2DObject(el);
      obj.position.set(centers[i].x, centers[i].y + 4.2, centers[i].z);
      scene.add(obj);
      labelEls.push({ el, obj, id: s.id });
    });

    // ---- stepping stones between islands, and the path Bit hops along ----
    const stoneMat = new THREE.MeshStandardMaterial({ color: L.stone, roughness: 0.5 });
    const stoneLit = new THREE.MeshStandardMaterial({ color: L.stoneLit, emissive: L.stoneLit, emissiveIntensity: dark ? 1.4 : 0.6, roughness: 0.4 });
    const stoneGeo = new THREE.CylinderGeometry(0.42, 0.34, 0.22, 20);
    const route: THREE.Vector3[] = []; // where Bit can stand: island tops and stones, in order
    const routeIsland: number[] = []; // index into route for each island
    for (let i = 0; i < n; i++) {
      routeIsland.push(route.length);
      route.push(centers[i].clone().add(new THREE.Vector3(0, 0.36, 0)));
      if (i + 1 < n) {
        const a = centers[i], b = centers[i + 1];
        const steps = 6;
        for (let k = 1; k <= steps; k++) {
          const t = k / (steps + 1);
          const p = a.clone().lerp(b, t);
          p.y += Math.sin(t * Math.PI) * 1.2 + 0.25;
          p.x += Math.sin(t * Math.PI * 2) * 0.8;
          const lit = stops[i].state === "done";
          const stone = new THREE.Mesh(stoneGeo, lit ? stoneLit : stoneMat);
          stone.position.copy(p);
          stone.castShadow = true;
          stone.receiveShadow = true;
          stone.userData = { baseY: p.y, phase: r() * 6.28 };
          scene.add(stone);
          islands.push(stone as unknown as THREE.Group);
          route.push(p.clone().add(new THREE.Vector3(0, 0.12, 0)));
        }
      }
    }

    // ---- clouds and stars ----
    const cTex = cloudTexture();
    const clouds: THREE.Sprite[] = [];
    for (let i = 0; i < n * 3 + 12; i++) {
      const m = new THREE.SpriteMaterial({ map: cTex, color: L.cloud, transparent: true, opacity: dark ? 0.22 : 0.5, depthWrite: false });
      const s = new THREE.Sprite(m);
      const k = r() * (n + 2) - 1;
      s.position.set((r() - 0.5) * 90, k * 1.4 - 14 - r() * 8, -k * 12 + (r() - 0.5) * 24);
      const sc = 6 + r() * 12;
      s.scale.set(sc * 1.8, sc, 1);
      s.userData.drift = 0.2 + r() * 0.4;
      scene.add(s);
      clouds.push(s);
    }
    if (L.stars) {
      const sp: number[] = [];
      for (let i = 0; i < 1800; i++) {
        const th = r() * Math.PI * 2, ph = 0.15 + r() * 1.3;
        sp.push(Math.cos(th) * Math.sin(ph) * 900, Math.cos(ph) * 900 + 100, Math.sin(th) * Math.sin(ph) * 900);
      }
      const sg = new THREE.BufferGeometry();
      sg.setAttribute("position", new THREE.Float32BufferAttribute(sp, 3));
      scene.add(new THREE.Points(sg, new THREE.PointsMaterial({ color: "#ffffff", size: 1.4, sizeAttenuation: false, fog: false })));
    }

    // ---- Bit ----
    const bit = makeBit();
    scene.add(bit.group);
    const chosen = stops.findIndex((s) => s.id === host.dataset.selected);
    const startIsland = chosen >= 0 ? chosen : Math.max(0, stops.findIndex((s) => s.state === "next"));
    let at = routeIsland[startIsland]; // a float index into route
    let goal = at;
    const routeAt = (f: number) => {
      const i = Math.max(0, Math.min(route.length - 1, Math.floor(f)));
      const j = Math.min(route.length - 1, i + 1);
      const t = f - i;
      const p = route[i].clone().lerp(route[j], t);
      p.y += Math.sin(t * Math.PI) * 0.7; // a hop between two footholds
      return p;
    };
    const placeBit = () => {
      const p = routeAt(at);
      bit.group.position.copy(p);
      const ahead = routeAt(Math.min(route.length - 1, at + (goal >= at ? 0.3 : -0.3)));
      ahead.y = p.y;
      if (ahead.distanceToSquared(p) > 1e-4) bit.group.lookAt(ahead);
      bit.group.rotateY(Math.PI); // the model's face looks down -z
    };
    placeBit();

    // ---- camera ----
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.07;
    controls.minDistance = 6;
    controls.maxDistance = 90;
    controls.maxPolarAngle = 1.5;
    controls.enablePan = false;
    const OFFSET = new THREE.Vector3(5.5, 4.2, 10);
    const lookAt = () => bit.group.position.clone().add(new THREE.Vector3(0, 1.4, -6));
    controls.target.copy(lookAt());
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const introFrom = centers[Math.min(n - 1, startIsland + 6)].clone().add(new THREE.Vector3(30, 40, 40));
    const finalPos = () => bit.group.position.clone().add(OFFSET);
    let intro = reduce ? 1 : 0;
    camera.position.copy(reduce ? finalPos() : introFrom);
    controls.update();
    sun.position.copy(bit.group.position).add(new THREE.Vector3(18, 30, 12));
    sun.target.position.copy(bit.group.position);
    Object.assign(sun.shadow.camera, { left: -30, right: 30, top: 30, bottom: -30, near: 1, far: 120 });

    api.current = {
      go: (id) => { const k = stops.findIndex((s) => s.id === id); if (k >= 0) goal = routeIsland[k]; },
      reset: () => { camera.position.copy(finalPos()); controls.target.copy(lookAt()); },
    };

    // ---- clicking an island ----
    const ray = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let down: { x: number; y: number } | null = null;
    const pick = (ev: PointerEvent): string | null => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.set(((ev.clientX - rect.left) / rect.width) * 2 - 1, -((ev.clientY - rect.top) / rect.height) * 2 + 1);
      ray.setFromCamera(mouse, camera);
      return (ray.intersectObjects(pickables, true)[0]?.object.userData.stop as string) ?? null;
    };
    const target = labels.domElement; // the label layer sits on top and receives pointer events
    const onMove = (ev: PointerEvent) => { target.style.cursor = pick(ev) ? "pointer" : down ? "grabbing" : "grab"; };
    const onDown = (ev: PointerEvent) => { down = { x: ev.clientX, y: ev.clientY }; };
    const onUp = (ev: PointerEvent) => {
      if (down && Math.hypot(ev.clientX - down.x, ev.clientY - down.y) < 6) { const id = pick(ev); if (id) onSelectRef.current(id); }
      down = null;
    };
    target.addEventListener("pointermove", onMove);
    target.addEventListener("pointerdown", onDown);
    target.addEventListener("pointerup", onUp);
    controls.dispose();
    const orbit = new OrbitControls(camera, target);
    Object.assign(orbit, { enableDamping: true, dampingFactor: 0.07, minDistance: 6, maxDistance: 90, maxPolarAngle: 1.5, enablePan: false });
    orbit.target.copy(controls.target);
    orbit.update();

    // ---- glow ----
    const composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    composer.addPass(new UnrealBloomPass(new THREE.Vector2(256, 256), L.bloom, 0.6, dark ? 0.8 : 0.97));
    composer.addPass(new OutputPass());

    const resize = () => {
      const w = host.clientWidth, h = host.clientHeight;
      if (!w || !h) return;
      renderer.setSize(w, h);
      labels.setSize(w, h);
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
      // islands and stones bob gently
      if (!reduce) for (const o of islands) o.position.y = o.userData.baseY + Math.sin(time * 0.8 + o.userData.phase) * 0.12;
      for (const c of crystals) { c.rotation.y += dt * 1.2; c.position.y = 2.0 + Math.sin(time * 2) * 0.15; }
      for (const f of flags) {
        const pos = f.geometry.getAttribute("position") as THREE.BufferAttribute;
        for (let i = 0; i < pos.count; i++) { const x = pos.getX(i); pos.setZ(i, Math.sin(x * 5 + time * 6) * 0.06 * (x + 0.45)); }
        pos.needsUpdate = true;
      }
      for (const c of clouds) { c.position.x += c.userData.drift * dt; if (c.position.x > 40) c.position.x = -40; }
      // Bit hops along the route towards the chosen island
      const before = bit.group.position.clone();
      if (Math.abs(goal - at) > 0.001) {
        const step = reduce ? goal - at : Math.sign(goal - at) * Math.min(Math.abs(goal - at), dt * 3.2);
        at += step;
        settle = 1.2;
      }
      placeBit();
      if (!reduce) bit.body.position.y = Math.abs(goal - at) > 0.001 ? 0 : Math.abs(Math.sin(time * 2.2)) * 0.06;
      const moved = bit.group.position.clone().sub(before);
      camera.position.add(moved);
      orbit.target.add(moved);
      if (intro < 1) {
        intro = Math.min(1, intro + dt / 2.6);
        const e = 1 - Math.pow(1 - intro, 3);
        camera.position.lerpVectors(introFrom, finalPos(), e);
        orbit.target.lerp(lookAt(), 0.1);
      } else if (settle > 0) {
        settle -= dt;
        camera.position.lerp(finalPos(), 0.04);
        orbit.target.lerp(lookAt(), 0.08);
      }
      sun.position.copy(bit.group.position).add(new THREE.Vector3(18, 30, 12));
      sun.target.position.copy(bit.group.position);
      // far labels fade, so the view stays calm
      for (const l of labelEls) {
        const d = camera.position.distanceTo(l.obj.position);
        const sel = l.id === host.dataset.selected;
        l.el.style.opacity = String(sel ? 1 : Math.max(0, Math.min(1, (70 - d) / 30)));
        l.el.classList.toggle("is-selected", sel);
      }
      orbit.update();
      composer.render();
      labels.render(scene, camera);
    };
    loop();

    return () => {
      cancelAnimationFrame(frame);
      ro.disconnect();
      target.removeEventListener("pointermove", onMove);
      target.removeEventListener("pointerdown", onDown);
      target.removeEventListener("pointerup", onUp);
      orbit.dispose();
      composer.dispose();
      scene.traverse((o) => {
        const m = o as THREE.Mesh;
        if (m.geometry) m.geometry.dispose();
        const mats = m.material ? (Array.isArray(m.material) ? m.material : [m.material]) : [];
        mats.forEach((x) => { (x as THREE.SpriteMaterial).map?.dispose(); x.dispose(); });
      });
      cTex.dispose();
      renderer.dispose();
      renderer.domElement.remove();
      labels.domElement.remove();
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

  return <div ref={hostRef} className="roadmap3d island-world" />;
}
