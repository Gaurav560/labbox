import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, jarvisApi, type JarvisCheer, type JarvisMode, type JarvisNudge, type JarvisStatus, type JarvisWelcome } from "../api";

/*
 * Jarvis, the learner's realtime voice assistant (owner, 28 November). The browser talks straight to OpenAI's realtime
 * model over WebRTC: the microphone goes up, Jarvis's voice comes back, and the learner can interrupt him at any time.
 * The backend decides who may talk and for how long, builds what Jarvis knows (the session's instructions), mints the
 * short-lived pass this page connects with (never the real key), answers his tools (the lesson step, the task, the
 * learner's code, their last check, their progress) and counts the cost from the usage reported after each reply.
 * Pro learners talk; a free learner gets one short trial, then the lock that points to Pro.
 */

type Phase = "idle" | "connecting" | "live" | "ending" | "ended";
type Mood = "listening" | "thinking" | "speaking";

const CALLS_URL = "https://api.openai.com/v1/realtime/calls";
const BEAT_MS = 15_000;

const POLL_MS = 60_000; // how often to ask "stuck?" while the learner sits on a task step
const OFFER_KEY = "labbox.jarvis.offered"; // task ids Jarvis already offered help on, with when (never nag)
const OFFER_AGAIN_MS = 6 * 3600 * 1000;

function offeredRecently(taskId: string): boolean {
  try {
    const at = (JSON.parse(localStorage.getItem(OFFER_KEY) || "{}") as Record<string, number>)[taskId];
    return !!at && Date.now() - at < OFFER_AGAIN_MS;
  } catch {
    return false;
  }
}

function markOffered(taskId: string): void {
  try {
    const all = JSON.parse(localStorage.getItem(OFFER_KEY) || "{}") as Record<string, number>;
    all[taskId] = Date.now();
    localStorage.setItem(OFFER_KEY, JSON.stringify(all));
  } catch {
    /* private mode: offers may repeat, which is fine */
  }
}

const WELCOMED_KEY = "labbox.jarvis.welcomed"; // once per browser session (step 3)
const MEMORY_WAIT_MS = 8_000; // how long the end of a Pro conversation waits for Jarvis's note to himself
const MEMORY_PROMPT = "The conversation is ending. Write two or three plain sentences for your own memory of this learner: "
  + "what they worked on, where they struggled or what they understood, and anything they told you about themselves or their "
  + "goals that would help next time. Facts only, no greeting, no advice to them.";

const CHEERED_KEY = "labbox.jarvis.cheered"; // celebrations already shown (each once)
const SETTINGS_EVENT = "labbox:jarvis-settings"; // the profile menu's switch tells the orb

function seenOnce(key: string, id: string): boolean {
  try {
    const all = JSON.parse(localStorage.getItem(key) || "[]") as string[];
    if (all.includes(id)) return true;
    localStorage.setItem(key, JSON.stringify([...all, id].slice(-200)));
  } catch { /* private mode: it may show again, which is fine */ }
  return false;
}

/* What Jarvis can see, said plainly (step 4). Shown once before the first conversation, and in his settings. */
function WhatHeSees({ pro }: { pro: boolean }) {
  return (
    <>
      <ul className="jv-see">
        <li>Your name, your goal, your level and streak, and the labs you have started, with your progress.</li>
        <li>The lesson step on your screen, your code in the lab, and your last check.</li>
        <li>{pro ? "A short note he writes himself at the end of each conversation, so he remembers you next time. You can make him forget in his settings."
          : "On Pro, a short note he writes himself after each conversation, so he remembers you next time."}</li>
      </ul>
      <p className="jv-small">
        The microphone is on only while you talk with him. Your voice goes to OpenAI, whose realtime model is Jarvis's
        voice, for that conversation. LabBox does not record it; it keeps how long you talked.
      </p>
    </>
  );
}

/* The on and off switch in the profile menu, so Jarvis can come back after he is turned off (step 4). */
export function JarvisSwitch() {
  const [st, setSt] = useState<JarvisStatus | null>(null);
  useEffect(() => { jarvisApi.status().then(setSt).catch(() => {}); }, []);
  if (!st || !st.enabled) return null;
  const change = (mode: JarvisMode) => jarvisApi.settings({ mode }).then((s) => { setSt(s); window.dispatchEvent(new CustomEvent(SETTINGS_EVENT)); }).catch(() => {});
  return (
    <label className="profile-jarvis">
      <span>Jarvis</span>
      <select value={st.mode} onChange={(e) => change(e.target.value as JarvisMode)} aria-label="Jarvis">
        <option value="tap">On: offers, waits for my tap</option>
        {st.plan === "pro" && <option value="first">On: talks first</option>}
        <option value="off">Off</option>
      </select>
    </label>
  );
}

const mmss = (s: number) => `${Math.floor(Math.max(0, s) / 60)}:${String(Math.max(0, s) % 60).padStart(2, "0")}`;

export default function Jarvis({ labId, chapterId, step }: { labId?: string; chapterId?: string; step?: number }) {
  const [status, setStatus] = useState<JarvisStatus | null>(null);
  const [open, setOpen] = useState(false);
  const [phase, setPhase] = useState<Phase>("idle");
  const [mood, setMood] = useState<Mood>("listening");
  const [caption, setCaption] = useState("");
  const [note, setNote] = useState("");
  const [left, setLeft] = useState(0);
  const [offer, setOffer] = useState<JarvisNudge | null>(null);
  const [welcome, setWelcome] = useState<JarvisWelcome | null>(null);
  const [cheer, setCheer] = useState<JarvisCheer | null>(null);
  const [view, setView] = useState<"main" | "settings" | "note">("main");
  const [noteFor, setNoteFor] = useState<string | null>(null); // the conversation waiting for "What Jarvis can see"
  const [forgot, setForgot] = useState("");

  const pc = useRef<RTCPeerConnection | null>(null);
  const dc = useRef<RTCDataChannel | null>(null);
  const mic = useRef<MediaStream | null>(null);
  const audio = useRef<HTMLAudioElement | null>(null);
  const sid = useRef<number | null>(null);
  const callId = useRef<string | null>(null);
  const startedAt = useRef(0);
  const usage = useRef<unknown[]>([]);
  const timers = useRef<number[]>([]);
  const stepRef = useRef(step);
  stepRef.current = step;
  const reasonRef = useRef("");
  const kindRef = useRef<"pro" | "trial">("pro");
  const memory = useRef<((text: string) => void) | null>(null);
  const onStepSince = useRef(Date.now());

  const refresh = useCallback(() => { jarvisApi.status().then(setStatus).catch(() => setStatus(null)); }, []);
  useEffect(refresh, [refresh]);
  useEffect(() => {
    window.addEventListener(SETTINGS_EVENT, refresh);
    return () => window.removeEventListener(SETTINGS_EVENT, refresh);
  }, [refresh]);
  const statusRef = useRef(status);
  statusRef.current = status;

  // Step 3: a welcome for a new learner, or one back after a while, once per browser session (on the dashboard).
  useEffect(() => {
    if (labId || !status?.enabled) return;
    try { if (sessionStorage.getItem(WELCOMED_KEY)) return; } catch { /* no storage: show it */ }
    jarvisApi.welcome().then((w) => {
      try { sessionStorage.setItem(WELCOMED_KEY, "1"); } catch { /* fine */ }
      if (w.show) { setWelcome(w); setOpen(true); talkFirst("welcome"); }
    }).catch(() => {});
  }, [labId, status?.enabled]);

  // Step 2: notice when the learner is stuck. Rules on the backend, no model, so asking costs nothing.
  useEffect(() => { onStepSince.current = Date.now(); setOffer(null); }, [labId, chapterId, step]);
  useEffect(() => {
    if (!labId || !chapterId || step == null || !status?.enabled) return;
    let live = true;
    const ask = (idle: number) => {
      if (sid.current != null) return; // already talking
      jarvisApi.nudge(labId, chapterId, step, idle).then((n) => {
        if (!live || !n.nudge || !n.task_id || offeredRecently(n.task_id)) return;
        markOffered(n.task_id);
        setOffer(n);
        setOpen(true);
        talkFirst(n.reason);
      }).catch(() => {});
    };
    const onCheck = () => { onStepSince.current = Date.now(); ask(0); };
    window.addEventListener("labbox:check-done", onCheck);
    const t = window.setInterval(() => ask((Date.now() - onStepSince.current) / 1000), POLL_MS);
    return () => { live = false; window.removeEventListener("labbox:check-done", onCheck); window.clearInterval(t); };
  }, [labId, chapterId, step, status?.enabled]);

  // Step 4: celebrate a first task, a finished chapter or a finished lab, right after the check that did it.
  useEffect(() => {
    if (!labId || !chapterId || !status?.enabled || status.mode === "off") return;
    const onCheck = () => {
      if (sid.current != null) return;
      jarvisApi.cheer(labId, chapterId).then((c) => {
        if (!c.show || seenOnce(CHEERED_KEY, c.key)) return;
        setOffer(null);
        setCheer(c);
        setView("main");
        setOpen(true);
        if (c.kind !== "first") talkFirst("cheer");
      }).catch(() => {});
    };
    window.addEventListener("labbox:check-done", onCheck);
    return () => window.removeEventListener("labbox:check-done", onCheck);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [labId, chapterId, status?.enabled, status?.mode]);

  const seconds = () => Math.round((Date.now() - startedAt.current) / 1000);

  const beat = useCallback(async (ended = false) => {
    if (sid.current == null) return;
    const batch = usage.current.splice(0);
    try {
      const out = await jarvisApi.heartbeat(sid.current, { seconds: seconds(), usage: batch, call_id: callId.current, ended });
      setLeft(out.seconds_left);
      if (out.stop && !ended) stop(out.reason);
    } catch {
      usage.current.unshift(...batch); // try again on the next beat
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cleanup = useCallback(() => {
    timers.current.forEach((t) => window.clearInterval(t));
    timers.current = [];
    dc.current?.close();
    pc.current?.close();
    mic.current?.getTracks().forEach((t) => t.stop());
    dc.current = null;
    pc.current = null;
    mic.current = null;
  }, []);

  // At the end of a Pro conversation, Jarvis writes himself a short note (a text-only reply outside the conversation),
  // kept for the next one (step 3). If it takes too long, the conversation ends without it.
  const askMemory = (): Promise<string | null> => {
    if (kindRef.current !== "pro" || dc.current?.readyState !== "open") return Promise.resolve(null);
    return new Promise((resolve) => {
      const t = window.setTimeout(() => { memory.current = null; resolve(null); }, MEMORY_WAIT_MS);
      memory.current = (text) => { window.clearTimeout(t); memory.current = null; resolve(text); };
      send({ type: "response.cancel" });
      send({ type: "response.create", response: { conversation: "none", output_modalities: ["text"], metadata: { topic: "memory" }, instructions: MEMORY_PROMPT } });
    });
  };

  const stop = useCallback(async (reason = "") => {
    if (sid.current == null) return;
    const id = sid.current;
    sid.current = null;
    setPhase("ending");
    if (audio.current) audio.current.muted = true;
    mic.current?.getTracks().forEach((t) => (t.enabled = false));
    const summary = await askMemory();
    const batch = usage.current.splice(0);
    cleanup();
    jarvisApi.heartbeat(id, { seconds: seconds(), usage: batch, call_id: callId.current, ended: true, summary }).catch(() => {});
    if (audio.current) audio.current.muted = false;
    setPhase("ended");
    setNote(reason);
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cleanup, refresh]);

  // Leaving the page ends the conversation.
  useEffect(() => () => { if (sid.current != null) stop(); }, [stop]);

  const send = (event: object) => { if (dc.current?.readyState === "open") dc.current.send(JSON.stringify(event)); };

  const onEvent = useCallback(async (e: MessageEvent) => {
    let ev: Record<string, any>;
    try { ev = JSON.parse(e.data); } catch { return; }
    switch (ev.type) {
      case "input_audio_buffer.speech_started": setMood("listening"); setCaption(""); break;
      case "input_audio_buffer.speech_stopped": setMood("thinking"); break;
      case "output_audio_buffer.started": setMood("speaking"); break;
      case "output_audio_buffer.stopped": setMood("listening"); break;
      case "response.output_audio_transcript.delta": setCaption((c) => (c + (ev.delta ?? "")).slice(-280)); break;
      case "response.created": setCaption(""); break;
      case "response.done": {
        if (ev.response?.usage) usage.current.push(ev.response.usage);
        if (ev.response?.metadata?.topic === "memory") {
          const text = (ev.response.output ?? []).flatMap((o: { content?: { text?: string; transcript?: string }[] }) => o.content ?? [])
            .map((c: { text?: string; transcript?: string }) => c.text ?? c.transcript ?? "").join(" ").trim();
          memory.current?.(text);
          break;
        }
        // Jarvis may call several tools in one reply: answer them all, then ask for one reply (OpenAI refuses a
        // second response while one is in progress).
        const calls = (ev.response?.output ?? []).filter((o: { type?: string }) => o.type === "function_call");
        if (calls.length) {
          setMood("thinking");
          const outputs = await Promise.all(calls.map(async (c: { call_id: string; name: string }) => {
            try {
              return { id: c.call_id, output: (await jarvisApi.tool(sid.current!, c.name, stepRef.current)).output };
            } catch (err) {
              return { id: c.call_id, output: `The tool failed: ${err instanceof ApiError ? err.message : String(err)}` };
            }
          }));
          outputs.forEach((o) => send({ type: "conversation.item.create", item: { type: "function_call_output", call_id: o.id, output: o.output } }));
          send({ type: "response.create" });
        }
        break;
      }
      case "response.function_call_arguments.done": setMood("thinking"); break;
      case "error": if (ev.error?.message && sid.current != null) setNote(ev.error.message); break; // errors while ending (a cancel with nothing to cancel) are not news
    }
  }, []);

  const begin = useCallback(async (reason = "") => {
    reasonRef.current = reason;
    setOffer(null);
    setWelcome(null);
    setCheer(null);
    setView("main");
    setNoteFor(null);
    setNote("");
    setCaption("");
    setPhase("connecting");
    try {
      const media = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
      mic.current = media;
      const s = await jarvisApi.start(labId, chapterId, stepRef.current, reason);
      sid.current = s.session_id;
      kindRef.current = s.kind;
      setLeft(s.max_seconds);
      const conn = new RTCPeerConnection();
      pc.current = conn;
      conn.ontrack = (ev) => { if (audio.current) audio.current.srcObject = ev.streams[0]; };
      media.getTracks().forEach((t) => conn.addTrack(t, media));
      const channel = conn.createDataChannel("oai-events");
      dc.current = channel;
      channel.onmessage = onEvent;
      // Jarvis speaks first: a short greeting by name, from what he knows.
      channel.onopen = () => {
        send({ type: "conversation.item.create", item: { type: "message", role: "system", content: [{ type: "input_text",
          text: reasonRef.current === "welcome" || reasonRef.current === "cheer"
            ? "Follow the instructions under 'Why this conversation started'. Keep it short and warm."
            : reasonRef.current
            ? "The learner just accepted your offer of help with the task in front of them. In one short, kind sentence, say what you noticed, then ask what they have tried so far. You may use your tools to look at the task and their code."
            : "The learner has just opened the conversation. Greet them by their first name in one or two short sentences, mention where they are or what they did last, and ask how you can help. Do not call any tool yet." }] } });
        send({ type: "response.create" });
      };
      conn.onconnectionstatechange = () => { if (["failed", "closed"].includes(conn.connectionState) && sid.current != null) stop("The connection dropped."); };
      const offer = await conn.createOffer();
      await conn.setLocalDescription(offer);
      const r = await fetch(CALLS_URL, { method: "POST", body: offer.sdp, headers: { Authorization: `Bearer ${s.client_secret}`, "Content-Type": "application/sdp" } });
      if (!r.ok) throw new Error(`Jarvis could not connect (${r.status}).`);
      const loc = r.headers.get("Location");
      callId.current = loc ? loc.split("/").pop() || null : null;
      await conn.setRemoteDescription({ type: "answer", sdp: await r.text() });
      startedAt.current = Date.now();
      setPhase("live");
      setMood("thinking");
      timers.current.push(window.setInterval(() => beat(), BEAT_MS));
      timers.current.push(window.setInterval(() => setLeft((l) => {
        if (l <= 1) { stop(s.kind === "trial" ? "That was your free trial with Jarvis." : "That is all the time we have for now."); return 0; }
        return l - 1;
      }), 1000));
    } catch (err) {
      const msg = err instanceof ApiError ? err.message
        : err instanceof DOMException && err.name === "NotAllowedError" ? "Jarvis needs your microphone. Allow it in the browser and try again."
        : err instanceof Error ? err.message : String(err);
      if (sid.current != null) stop(msg); else { cleanup(); setPhase("idle"); setNote(msg); }
    }
  }, [labId, chapterId, onEvent, beat, stop, cleanup]);

  // Before the first conversation, the learner reads what Jarvis can see (once).
  const talk = (reason = "") => {
    if (status && !status.note_seen) { setNoteFor(reason); setView("note"); setOpen(true); return; }
    begin(reason);
  };

  // "Talk first" (Pro): when Jarvis has something to say he starts by himself, if the browser lets the page use the
  // microphone and play sound without asking again; otherwise the offer waits for a tap as usual.
  async function talkFirst(reason: string) {
    const st = statusRef.current;
    if (!st || st.mode !== "first" || st.kind !== "pro" || !st.note_seen || sid.current != null) return;
    const nav = navigator as Navigator & { userActivation?: { hasBeenActive: boolean } };
    if (nav.userActivation && !nav.userActivation.hasBeenActive) return;
    try {
      const p = await navigator.permissions.query({ name: "microphone" as PermissionName });
      if (p.state !== "granted") return;
    } catch { return; }
    begin(reason);
  }

  const setMode = (mode: JarvisMode) => jarvisApi.settings({ mode }).then((s) => {
    setStatus(s);
    if (mode === "off") { setOpen(false); setView("main"); }
  }).catch(() => {});

  if (!status || !status.enabled || (status.mode === "off" && phase !== "live")) return null;
  const locked = status.kind === "locked" && phase !== "live";
  const live = phase === "live";
  const label = live ? (mood === "speaking" ? "Jarvis is speaking" : mood === "thinking" ? "Jarvis is thinking" : "Jarvis is listening") : "Talk to Jarvis";

  return (
    <div className={`jv ${open ? "is-open" : ""} ${(offer || welcome) && !live ? "has-offer" : ""} ${cheer && !live ? "has-cheer" : ""}`} data-phase={phase} data-mood={live ? mood : "idle"}>
      <audio ref={audio} autoPlay />
      {open && (
        <section className="jv-panel" aria-label="Jarvis" aria-live="polite">
          <header className="jv-head">
            <strong>Jarvis</strong>
            <span className="jv-plan">{status.plan === "pro" ? "Pro" : status.kind === "trial" ? "Free trial" : "Pro feature"}</span>
            {!live && phase !== "connecting" && phase !== "ending" && (
              <button type="button" className="jv-gear" aria-label="Jarvis settings" title="Settings" aria-pressed={view === "settings"}
                onClick={() => setView((v) => (v === "settings" ? "main" : "settings"))}>⚙</button>
            )}
            <button type="button" className="jv-x" aria-label="Close Jarvis" onClick={() => { if (live) stop(); setOpen(false); setView("main"); }}>✕</button>
          </header>
          {view === "note" && !live ? (
            <div className="jv-set">
              <h4>What Jarvis can see</h4>
              <WhatHeSees pro={status.plan === "pro"} />
              {noteFor !== null ? (
                <div className="jv-row jv-offer">
                  <button type="button" className="btn btn-small btn-primary" onClick={() => {
                    const r = noteFor;
                    jarvisApi.settings({ note_seen: true }).then(setStatus).catch(() => {});
                    begin(r);
                  }}>Got it, start talking</button>
                  <button type="button" className="btn btn-small" onClick={() => { setNoteFor(null); setView("main"); }}>Not now</button>
                </div>
              ) : (
                <button type="button" className="jv-linkish" onClick={() => setView("settings")}>Back to settings</button>
              )}
            </div>
          ) : view === "settings" && !live ? (
            <div className="jv-set">
              <h4>When Jarvis speaks</h4>
              {([
                ["tap", "Offer, then wait for my tap", "He lets you know when you look stuck or did something good; you decide when to talk."],
                ["first", "Talk first", status.plan === "pro" ? "When he has something to say, he starts talking by himself (once you have allowed the microphone)." : "Pro: he starts talking by himself when he has something to say."],
                ["off", "Off", "No offers, no welcome, no orb. Turn him back on from your profile menu (top right)."],
              ] as [JarvisMode, string, string][]).map(([m, title, help]) => {
                const blocked = m === "first" && status.plan !== "pro";
                return (
                  <label key={m} className={`jv-choice ${blocked ? "is-off" : ""}`}>
                    <input type="radio" name="jv-mode" checked={status.mode === m} disabled={blocked} onChange={() => setMode(m)} />
                    <span>{title}<small>{help}</small></span>
                  </label>
                );
              })}
              {status.plan === "pro" && (
                <>
                  <h4>What he remembers</h4>
                  <p className="jv-small">
                    {status.memories
                      ? `Jarvis keeps ${status.memories} short ${status.memories === 1 ? "note" : "notes"} from your conversations and reads the last 3 before he talks with you.`
                      : forgot || "No notes yet. After each conversation he writes himself a short one."}
                  </p>
                  {status.memories > 0 && (
                    <button type="button" className="btn btn-small" onClick={() => jarvisApi.forget().then((r) => {
                      setForgot(`Forgotten: ${r.forgotten} ${r.forgotten === 1 ? "note" : "notes"}.`);
                      refresh();
                    }).catch(() => {})}>Forget them</button>
                  )}
                </>
              )}
              <button type="button" className="jv-linkish" onClick={() => { setNoteFor(null); setView("note"); }}>What Jarvis can see</button>
            </div>
          ) : cheer && !live && phase !== "connecting" ? (
            <>
              <p className="jv-caption">{cheer.line}</p>
              <div className="jv-row jv-offer">
                {cheer.link_url && <Link className="btn btn-small btn-primary" to={cheer.link_url} onClick={() => { setCheer(null); setOpen(false); }}>{cheer.link_label} →</Link>}
                {status.kind === "pro" && cheer.kind !== "first" && (
                  <button type="button" className="btn btn-small" onClick={() => talk("cheer")}>Talk to Jarvis</button>
                )}
                <button type="button" className="btn btn-small" onClick={() => { setCheer(null); setOpen(false); }}>{cheer.link_url ? "Later" : "Thanks"}</button>
              </div>
            </>
          ) : welcome && !live && phase !== "connecting" ? (
            <>
              <p className="jv-caption">{welcome.line}</p>
              <div className="jv-row jv-offer">
                {welcome.continue_url && <Link className="btn btn-small btn-primary" to={welcome.continue_url}>{welcome.continue_label} →</Link>}
                {status.kind !== "locked" && (
                  <button type="button" className={`btn btn-small ${welcome.continue_url ? "" : "btn-primary"}`} onClick={() => talk("welcome")}>
                    {status.kind === "trial" ? "Talk to Jarvis (free trial)" : "Talk to Jarvis"}
                  </button>
                )}
                {!welcome.continue_url && status.kind === "locked" && <Link className="btn btn-small btn-primary" to="/labs#labs">See the labs</Link>}
                <button type="button" className="btn btn-small" onClick={() => { setWelcome(null); setOpen(false); }}>Not now</button>
              </div>
            </>
          ) : offer && !live && phase !== "connecting" ? (
            <>
              <p className="jv-caption">{offer.line}</p>
              <div className="jv-row jv-offer">
                {status.kind !== "locked" ? (
                  <button type="button" className="btn btn-small btn-primary" onClick={() => talk(offer.reason)}>
                    {status.kind === "trial" ? "Talk it through (free trial)" : "Talk it through"}
                  </button>
                ) : (
                  <button type="button" className="btn btn-small btn-primary" onClick={() => { window.dispatchEvent(new CustomEvent("labbox:open-tutor")); setOffer(null); setOpen(false); }}>
                    ✦ Ask AI (typed)
                  </button>
                )}
                <button type="button" className="btn btn-small" onClick={() => { setOffer(null); setOpen(false); }}>Not now</button>
              </div>
              {status.kind === "locked" && status.plan !== "pro" && (
                <p className="jv-small">With Pro, Jarvis talks it through with you, out loud. <Link to="/pricing">See Pro</Link></p>
              )}
            </>
          ) : live ? (
            <>
              <p className="jv-caption">{caption || (mood === "speaking" ? "..." : label + ".")}</p>
              <div className="jv-row">
                <span className="jv-time" title="Time left in this conversation">{mmss(left)} left</span>
                <button type="button" className="btn btn-small" onClick={() => stop()}>End</button>
              </div>
            </>
          ) : phase === "connecting" ? (
            <p className="jv-caption">Waking Jarvis up...</p>
          ) : phase === "ending" ? (
            <p className="jv-caption">Jarvis is noting what to remember...</p>
          ) : locked ? (
            <>
              <p className="jv-caption">{status.reason}</p>
              {status.plan !== "pro" && status.trial_used && (
                <p className="jv-small">Pro learners talk with Jarvis every day: he knows your labs, your code and where you are stuck. Until then, <b>✦ Ask AI</b> under a task gives typed help.</p>
              )}
              {status.plan !== "pro" && <Link className="btn btn-small btn-primary" to="/pricing">See Pro</Link>}
            </>
          ) : (
            <>
              {note && <p className="jv-note" role="status">{note}</p>}
              <p className="jv-caption">
                {status.kind === "trial"
                  ? `Meet Jarvis, your personal guide. Your free trial is ${Math.round(status.seconds_left / 60)} minutes, once.`
                  : "Jarvis knows your labs, your code and where you are. Ask him anything, out loud."}
              </p>
              <button type="button" className="btn btn-small btn-primary" onClick={() => talk()}>Start talking</button>
            </>
          )}
          {phase === "ended" && note && <p className="jv-note" role="status">{note}</p>}
        </section>
      )}
      <button type="button" className="jv-orb" aria-label={label} aria-expanded={open} title={label}
        onClick={() => setOpen((o) => !o || live)}>
        <span className="jv-core" aria-hidden="true" />
        <span className="jv-ring" aria-hidden="true" />
        <span className="jv-ring jv-ring-2" aria-hidden="true" />
      </button>
    </div>
  );
}
