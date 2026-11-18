import Markdown from "react-markdown";

export default function ChapterPanel({ markdown }: { markdown: string | null }) {
  if (markdown === null) return <div className="chapter muted">Loading chapter...</div>;
  return (
    <div className="chapter">
      <Markdown>{markdown}</Markdown>
    </div>
  );
}
