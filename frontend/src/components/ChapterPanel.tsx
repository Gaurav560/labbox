import LessonMarkdown from "../lesson/LessonMarkdown";

// A v1 chapter (no step markers) is one long page: render it without step chrome.
export default function ChapterPanel({ markdown, onRun }: { markdown: string | null; onRun?: (command: string) => void }) {
  if (markdown === null) return <div className="chapter muted">Loading chapter...</div>;
  return (
    <div className="chapter step-card">
      <LessonMarkdown markdown={markdown} onRun={onRun} />
    </div>
  );
}
