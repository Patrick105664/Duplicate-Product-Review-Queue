import React from "react";
import { CheckCircle2, CircleAlert, Fingerprint, Sparkles } from "lucide-react";

export default function EvidencePanel({ pair }) {
  const signals = pair?.signals || [];
  return <section className="panel evidence-panel">
    <div className="panel-heading"><div><h3>Match evidence</h3><p>Signals behind this suggestion</p></div><div className="soft-icon"><Sparkles size={17} /></div></div>
    <div className="confidence-block">
      <div><span className="muted-label">Similarity score</span><strong>{Math.round((pair?.score || 0) * 100)}%</strong></div>
      <div className="progress-track"><span style={{ width: `${Math.round((pair?.score || 0) * 100)}%` }} /></div>
      <small>Model confidence is a signal, not an automatic decision.</small>
    </div>
    <div className="evidence-list">
      {signals.map((signal, i) => {
        const caution = /conflict|mismatch|differs|quantity/i.test(signal);
        const Icon = caution ? CircleAlert : CheckCircle2;
        return <div className={`evidence-row ${caution ? "caution" : ""}`} key={`${signal}-${i}`}><Icon size={17} /><span>{signal}</span></div>;
      })}
      {!signals.length && <div className="evidence-row"><Fingerprint size={17} /><span>No evidence signals supplied by the API.</span></div>}
    </div>
    <div className="evidence-note"><CircleAlert size={16} /><p>Check pack size, model number and product variants before accepting. Similar products are not always duplicates.</p></div>
  </section>;
}
