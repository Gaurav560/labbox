import { useId } from "react";
import LessonMarkdown from "./LessonMarkdown";

export interface ChoiceState {
  wrong: number[]; // options picked wrongly, in order
  solved: boolean;
  answer: number | null; // known only once solved (checked on the server)
  explain: string | null;
}

interface Props {
  question: string; // markdown
  options: string[]; // markdown
  state: ChoiceState;
  busy: boolean;
  onPick: (option: number) => void;
  onRun?: (command: string) => void;
}

// A multiple choice question checked on the server: predict steps, daily drills.
export default function ChoiceQuestion({ question, options, state, busy, onPick, onRun }: Props) {
  const qid = useId();
  const done = state.solved;
  return (
    <div className="predict">
      <div className="predict-question" id={qid}>
        <LessonMarkdown markdown={question} onRun={onRun} />
      </div>
      <div className="predict-options" role="group" aria-labelledby={qid}>
        {options.map((text, i) => {
          const wrong = state.wrong.includes(i);
          const right = done && i === state.answer;
          return (
            <button
              key={i}
              className={`predict-option ${wrong ? "is-wrong" : ""} ${right ? "is-right" : ""}`}
              onClick={() => onPick(i)}
              disabled={done || wrong || busy}
              aria-pressed={wrong || right}
            >
              <span className="predict-mark" aria-hidden="true">{right ? "✓" : wrong ? "✗" : String.fromCharCode(65 + i)}</span>
              <LessonMarkdown markdown={text} inline />
            </button>
          );
        })}
      </div>
      <div aria-live="polite">
        {!done && state.wrong.length > 0 && <p className="fail">Not quite. Have another go.</p>}
        {done && (
          <div className="predict-explain">
            <p className="pass"><strong>{state.wrong.length === 0 ? "Right first time!" : "That's it."}</strong></p>
            {state.explain && <LessonMarkdown markdown={state.explain} onRun={onRun} />}
          </div>
        )}
      </div>
    </div>
  );
}
