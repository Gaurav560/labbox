// Small per-browser preferences (panel sizes, theme, focus mode) kept in localStorage.
import { useEffect, useState } from "react";

const PREFIX = "labbox.";

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(PREFIX + key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback;
  }
}

export function usePersistentState<T>(key: string, fallback: T): [T, (v: T | ((old: T) => T)) => void] {
  const [value, setValue] = useState<T>(() => read(key, fallback));
  useEffect(() => {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value));
    } catch {
      /* storage full or blocked: the preference just is not remembered */
    }
  }, [key, value]);
  return [value, setValue];
}
