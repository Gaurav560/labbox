// AI code completion: grey ghost text at the cursor, accepted with Tab. It waits until typing pauses,
// drops stale requests, and stays quiet on errors (an editor must never nag). The server picks the
// model, applies the learner's completion limits, and never suggests a line of the task's solution.
import { api } from "./api";
import { MODEL_PREFIX, monaco } from "./monaco";

const PAUSE_MS = 400;
const state = { labId: "", enabled: false };
let registered = false;

/** Called by the editor: which lab the completions are for, and whether the learner has AI on. */
export function setAiCompletion(labId: string, enabled: boolean): void {
  state.labId = labId;
  state.enabled = enabled;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export function registerAiCompletion(): void {
  if (registered) return;
  registered = true;
  monaco.languages.registerInlineCompletionsProvider({ pattern: "**" }, {
    async provideInlineCompletions(model, position, _context, token) {
      if (!state.enabled || !state.labId || !model.uri.toString().startsWith(MODEL_PREFIX)) return { items: [] };
      await sleep(PAUSE_MS);
      if (token.isCancellationRequested) return { items: [] };
      const last = model.getLineCount();
      const prefix = model.getValueInRange(new monaco.Range(1, 1, position.lineNumber, position.column));
      const suffix = model.getValueInRange(new monaco.Range(position.lineNumber, position.column, last, model.getLineMaxColumn(last)));
      if (!prefix.trim()) return { items: [] };
      try {
        const path = model.uri.toString().slice(MODEL_PREFIX.length);
        const { text } = await api.complete(state.labId, decodeURIComponent(path), prefix, suffix);
        if (token.isCancellationRequested || !text) return { items: [] };
        return { items: [{ insertText: text, range: new monaco.Range(position.lineNumber, position.column, position.lineNumber, position.column) }] };
      } catch {
        return { items: [] }; // over the limit or no model: just no suggestion
      }
    },
    freeInlineCompletions() {},
  });
}
