// Small file-type badges for tabs and the file tree, in the spirit of VS Code's icon themes.
const ICONS: Record<string, { label: string; color: string }> = {
  py: { label: "py", color: "#4b8bbe" },
  java: { label: "J", color: "#e76f00" },
  js: { label: "JS", color: "#e8d44d" },
  mjs: { label: "JS", color: "#e8d44d" },
  ts: { label: "TS", color: "#3178c6" },
  tsx: { label: "TS", color: "#3178c6" },
  go: { label: "go", color: "#00add8" },
  sql: { label: "db", color: "#e38c00" },
  md: { label: "M", color: "#519aba" },
  sh: { label: "$", color: "#89e051" },
  json: { label: "{}", color: "#cbcb41" },
  yaml: { label: "Y", color: "#cb171e" },
  yml: { label: "Y", color: "#cb171e" },
  html: { label: "<>", color: "#e34c26" },
  css: { label: "#", color: "#a86fd6" },
  env: { label: "⚙", color: "#8b949e" },
  txt: { label: "≡", color: "#8b949e" },
  log: { label: "≡", color: "#8b949e" },
  xml: { label: "<>", color: "#e37933" },
};

export function fileIcon(name: string): { label: string; color: string } {
  const lower = name.toLowerCase();
  if (lower === "dockerfile") return { label: "🐳", color: "#2496ed" };
  if (lower.startsWith(".git")) return { label: "◆", color: "#f05133" };
  return ICONS[lower.split(".").pop() ?? ""] ?? { label: "•", color: "#8b949e" };
}

export default function FileIcon({ name }: { name: string }) {
  const { label, color } = fileIcon(name);
  return <span className="file-icon" style={{ color }} aria-hidden="true">{label}</span>;
}

const LANGUAGE_NAMES: Record<string, string> = {
  python: "Python", java: "Java", javascript: "JavaScript", typescript: "TypeScript", go: "Go", sql: "SQL",
  markdown: "Markdown", shell: "Shell Script", json: "JSON", yaml: "YAML", plaintext: "Plain Text",
};

export const languageName = (id: string) => LANGUAGE_NAMES[id] ?? id;
