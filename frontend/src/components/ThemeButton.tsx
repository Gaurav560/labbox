import { useTheme } from "../theme";

/** The light and dark switch, the same on every page with a top bar. */
export default function ThemeButton() {
  const { theme, toggle } = useTheme();
  return (
    <button type="button" className="btn btn-small btn-ghost" onClick={toggle} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`} title="Theme">
      {theme === "dark" ? "☀" : "☾"}
    </button>
  );
}
