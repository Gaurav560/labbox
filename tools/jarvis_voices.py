"""Jarvis voice audition (owner, 28 November): every built-in OpenAI realtime voice says the same two lines and answers
the same discouraged learner, with Jarvis's instructions as they are in app/jarvis.py. The clips and a page to listen
to them go to .authoring-scratch/jarvis-voices/ (not in git). Paid: about a cent per voice; it stops at MAX_USD.

    cd backend && .venv/bin/python ../tools/jarvis_voices.py [voice ...]

The API key is read from backend/.env through the app's settings and never printed.
"""
import asyncio
import base64
import html
import json
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import websockets  # noqa: E402

from app import jarvis  # noqa: E402
from app.config import get_settings  # noqa: E402

VOICES = ["cedar", "ash", "ballad", "echo", "verse", "marin", "alloy", "sage", "coral", "shimmer"]
MAX_USD = 0.60
OUT = ROOT / ".authoring-scratch" / "jarvis-voices"

CONTEXT = """What you know about this learner right now:
Name: Meera. Goal: get a backend job. Level: beginner. Right now they are in the lab "Python from zero", chapter 3,
"Loops", on the task "Add up the week's spending". Their last check said: "Expected 1240, got 1090: the last day is
not counted"."""

LINES = [
    ("greeting", "Good evening, Meera. Chapter three, the loop task. Your last check stopped one day short."),
    ("dry", "Three tests pass. The fourth is complaining about an empty list, which, to be fair, is a reasonable thing "
            "to complain about."),
]
LEARNER = "I've been stuck on this for an hour. I think I'm just bad at coding."


async def audition(voice: str, spent: list[float]) -> list[dict]:
    s = get_settings()
    url = f"wss://api.openai.com/v1/realtime?model={s.JARVIS_MODEL}"
    out = []
    async with websockets.connect(url, additional_headers={"Authorization": f"Bearer {s.OPENAI_API_KEY}"}, max_size=None) as ws:
        await ws.send(json.dumps({"type": "session.update", "session": {
            "type": "realtime", "instructions": jarvis.PERSONA + "\n\n" + CONTEXT, "output_modalities": ["audio"],
            "audio": {"output": {"voice": voice, "format": {"type": "audio/pcm", "rate": 24000}}}}}))

        async def reply(name: str, response: dict) -> None:
            if sum(spent) > MAX_USD:
                return
            await ws.send(json.dumps({"type": "response.create", "response": response}))
            pcm, text = bytearray(), ""
            while True:
                ev = json.loads(await ws.recv())
                t = ev.get("type")
                if t == "response.output_audio.delta":
                    pcm += base64.b64decode(ev["delta"])
                elif t == "response.output_audio_transcript.delta":
                    text += ev.get("delta", "")
                elif t == "error":
                    raise RuntimeError(f"{voice} {name}: {ev.get('error', {}).get('message')}")
                elif t == "response.done":
                    usage = ev["response"].get("usage") or {}
                    spent.append(jarvis.cost(jarvis.usage_from_event(usage)))
                    break
            path = OUT / f"{voice}-{name}.wav"
            with wave.open(str(path), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(24000)
                w.writeframes(bytes(pcm))
            out.append({"voice": voice, "name": name, "file": path.name, "text": text.strip(), "seconds": round(len(pcm) / 48000, 1)})

        for name, line in LINES:  # the same words from every voice: only the voice differs
            await reply(name, {"conversation": "none", "instructions": jarvis.PERSONA + "\n\nFor this reply only: say exactly "
                               "these words, in your usual voice and manner, adding nothing before or after:\n" + line})
        await ws.send(json.dumps({"type": "conversation.item.create", "item": {"type": "message", "role": "user",
                                  "content": [{"type": "input_text", "text": LEARNER}]}}))
        await reply("discouraged", {})  # his own words: the tone, not only the voice
    return out


def page(clips: list[dict], total: float) -> str:
    rows = []
    for v in dict.fromkeys(c["voice"] for c in clips):
        cells = "".join(
            f'<div class="clip"><b>{html.escape(c["name"])}</b> <small>{c["seconds"]} s</small>'
            f'<audio controls preload="none" src="{c["file"]}"></audio><p>{html.escape(c["text"])}</p></div>'
            for c in clips if c["voice"] == v)
        rows.append(f'<section><h2>{v}</h2><div class="clips">{cells}</div></section>')
    return f"""<!doctype html><meta charset="utf-8"><title>Jarvis voices</title>
<style>body{{font:15px system-ui;margin:24px;max-width:1200px;background:#111;color:#eee}}h2{{margin:18px 0 6px}}
.clips{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}.clip{{background:#1c1c1c;padding:10px;border-radius:8px}}
audio{{width:100%;margin:6px 0}}p{{margin:0;font-size:13px;color:#bbb}}small{{color:#888}}</style>
<h1>Jarvis voice audition</h1><p>The learner said: "{html.escape(LEARNER)}" (third clip: his own answer).
Cost of this run: ${total:.3f}.</p>{"".join(rows)}"""


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    voices = sys.argv[1:] or VOICES
    spent: list[float] = []
    sem = asyncio.Semaphore(4)

    async def one(v: str) -> list[dict]:
        async with sem:
            try:
                return await audition(v, spent)
            except Exception as e:  # one voice failing should not lose the others
                print(f"{v}: failed: {e}")
                return []

    clips = [c for group in await asyncio.gather(*(one(v) for v in voices)) for c in group]
    total = sum(spent)
    (OUT / "index.html").write_text(page(clips, total))
    (OUT / "clips.json").write_text(json.dumps(clips, indent=1, ensure_ascii=False))
    for c in clips:
        print(f"{c['voice']:8} {c['name']:12} {c['seconds']:5} s  {c['text'][:110]}")
    print(f"{len(clips)} clips, ${total:.3f}; open {OUT / 'index.html'}")


if __name__ == "__main__":
    asyncio.run(main())
