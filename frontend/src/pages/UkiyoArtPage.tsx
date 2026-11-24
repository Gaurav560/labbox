/* The Ukiyo artwork on one page, for design review (owner, 24 November). Not linked from the app. */
import { BrushLevel, InkProgress, Seal, TRACK_MOTIF, TrackArt } from "../components/UkiyoArt";
import Logo from "../components/Logo";
import { TRACK_LABEL } from "./LabsPage";

export default function UkiyoArtPage() {
  return (
    <main className="u-gallery">
      <Logo to="/" />
      <h1 style={{ fontSize: 44, marginTop: 28 }}>The LabBox prints</h1>
      <p className="muted">One woodblock print per category, plus the seal, the level marks and the ink progress line.</p>
      <div className="u-gallery-grid">
        {["ai", "languages", "frameworks", "databases", "devops", "system-design", "cloud"].map((t) => (
          <figure key={t}>
            <div><TrackArt track={t} /></div>
            <figcaption><strong>{TRACK_LABEL[t]}</strong><span className="muted">{TRACK_MOTIF[t]}</span></figcaption>
          </figure>
        ))}
      </div>
      <div style={{ display: "flex", gap: 28, alignItems: "center", marginTop: 40 }}>
        <Seal lines={["LAB", "BOX"]} size={64} />
        <Seal lines={["✓"]} />
        <Seal lines={["NEW"]} />
        <BrushLevel level="beginner" /><BrushLevel level="intermediate" /><BrushLevel level="advanced" />
        <div style={{ width: 260 }}><InkProgress value={0.42} label="Progress" /></div>
      </div>
    </main>
  );
}
