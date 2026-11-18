import { useEffect, useState } from "react";
import { api, type DrillState } from "../api";
import ChoiceQuestion from "../lesson/ChoiceQuestion";
import { useStats } from "../stats";
import { useToast } from "./Toasts";

const KIND_LABEL = { predict: "Predict the output", bug: "Spot the bug", command: "What does it do?" } as const;

export default function DrillCard() {
  const toast = useToast();
  const { celebrate } = useStats();
  const [drill, setDrill] = useState<DrillState | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.drillToday().then(setDrill).catch((e) => toast(e.message));
  }, [toast]);

  if (!drill?.drill) return null;

  async function pick(choice: number) {
    setBusy(true);
    try {
      const d = await api.answerDrill(choice);
      setDrill(d);
      celebrate(d.xp_awarded);
    } catch (e) {
      toast(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="drill-card" aria-labelledby="drill-title">
      <div className="drill-head">
        <h2 id="drill-title">Today's drill</h2>
        <span className="meta-chip">{KIND_LABEL[drill.drill.kind]}</span>
        <span className="meta-chip">2 min</span>
        <span className="spacer" />
        <span className="xp-chip">{drill.solved ? "Done ✓" : `+${drill.xp} XP`}</span>
      </div>
      <p className="muted small-text">One question a day keeps your streak going, even on busy days.</p>
      <ChoiceQuestion question={drill.drill.question} options={drill.drill.options} state={drill} busy={busy} onPick={pick} />
    </section>
  );
}
