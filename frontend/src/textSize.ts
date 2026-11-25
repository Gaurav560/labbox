import { useSyncExternalStore } from "react";

// Text size per area of the lab page, in percent. Saved on this device only.
export interface TextSizes { lesson: number; tasks: number; editor: number; terminal: number }
export type TextArea = keyof TextSizes;

export const DEFAULT_SIZES: TextSizes = { lesson: 100, tasks: 100, editor: 100, terminal: 100 };
export const PRESETS = { S: 95, M: 100, L: 115, XL: 130 } as const;
export const MIN_SIZE = 80;
export const MAX_SIZE = 150;

const KEY = "labbox.textSize";
const clamp = (n: unknown) => (typeof n === "number" && isFinite(n) ? Math.min(MAX_SIZE, Math.max(MIN_SIZE, Math.round(n))) : 100);

function load(): TextSizes {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) ?? "{}");
    return { lesson: clamp(raw.lesson), tasks: clamp(raw.tasks), editor: clamp(raw.editor), terminal: clamp(raw.terminal) };
  } catch {
    return DEFAULT_SIZES;
  }
}

let current = load();
const listeners = new Set<() => void>();

export function setTextSizes(next: Partial<TextSizes>) {
  current = { ...current, ...Object.fromEntries(Object.entries(next).map(([k, v]) => [k, clamp(v)])) };
  try {
    localStorage.setItem(KEY, JSON.stringify(current));
  } catch {
    // private mode: the sizes still apply until the page is closed
  }
  listeners.forEach((l) => l());
}

export function useTextSizes(): TextSizes {
  return useSyncExternalStore(
    (l) => { listeners.add(l); return () => listeners.delete(l); },
    () => current,
  );
}
