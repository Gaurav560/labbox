"""Add playing diagrams (SketchSteps timelines) to frontend/src/lesson/Diagrams.tsx.

    python3 tools/authoring/add_diagrams.py diagrams.py

diagrams.py defines D, a list of (ComponentName, key, title, intro, label, steps), where steps is a list of
(label, says) pairs, one per moment of the process:

    D = [("AiRag", "ai-rag", "One question, answered from the cards",
          "Press Play to follow a question.", "RAG",
          [("Question", "A visitor asks ..."), ("Search", "The store finds the 3 closest cards ...")])]

A lesson then uses :::diagram{name="ai-rag"}. A key that already exists stops the script, so nothing is
replaced. Keep labels short and "says" to one or two plain sentences; up to about 7 steps. After adding,
check the page in the browser in both themes. See COURSE_PRODUCTION.md, "Diagrams".
"""
import sys
from pathlib import Path

DIAGRAMS = Path(__file__).resolve().parents[2] / "frontend/src/lesson/Diagrams.tsx"
ANCHOR = "\nconst DIAGRAMS: Record<string, () => JSX.Element> = {\n"


def quote(text: str) -> str:
    return f'"{text}"' if '"' not in text else f"'{text}'"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ns: dict = {}
    exec(Path(sys.argv[1]).read_text(), ns)
    s = DIAGRAMS.read_text()
    if ANCHOR not in s:
        sys.exit("the DIAGRAMS table was not found in Diagrams.tsx")
    code = ""
    for name, key, title, intro, label, steps in ns["D"]:
        if f'"{key}":' in s:
            sys.exit(f"diagram {key!r} already exists")
        body = "\n".join(f"        {{ label: {quote(lbl)}, says: {quote(says)} }}," for lbl, says in steps)
        code += f'''
function {name}() {{
  return (
    <SketchSteps
      title="{title}"
      intro="{intro}"
      label="{label}"
      steps={{[
{body}
      ]}}
    />
  );
}}
'''
    s = s.replace(ANCHOR, code + ANCHOR + "".join(f'  "{key}": {name},\n' for name, key, *_ in ns["D"]))
    DIAGRAMS.write_text(s)
    print(len(ns["D"]), "diagrams added")


if __name__ == "__main__":
    main()
