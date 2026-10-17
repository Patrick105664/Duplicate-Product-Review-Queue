import React, { useState } from "react";
import { Check, Flag, X } from "lucide-react";

export default function ReviewActions({ onDecision, disabled = false }) {
  const [note, setNote] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(decision) {
    if (decision === "accepted" && !confirm) { setConfirm(decision); return; }
    setBusy(true);
    try { await onDecision?.(decision, note); setConfirm(""); setNote(""); }
    finally { setBusy(false); }
  }
  return <div className="review-actions">
    <label className="note-label">Reviewer note <span>Optional</span><textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Add context for the audit trail..." rows="2" /></label>
    {confirm === "accepted" && <div className="confirm-strip"><strong>Confirm acceptance?</strong><p>This records your review decision only. It will not merge, delete, or modify catalogue products.</p><div className="confirm-buttons"><button className="button button-primary" disabled={busy} onClick={() => submit("accepted")}>Confirm decision</button><button className="button button-secondary" onClick={() => setConfirm("")}>Cancel</button></div></div>}
    <div className="action-row">
      <button className="button button-danger-outline" disabled={disabled || busy} onClick={() => submit("rejected")}><X size={16} /> Reject match</button>
      <button className="button button-warning-outline" disabled={disabled || busy} onClick={() => submit("flagged")}><Flag size={16} /> Flag for review</button>
      <button className="button button-primary" disabled={disabled || busy || confirm === "accepted"} onClick={() => submit("accepted")}><Check size={16} /> Accept match</button>
    </div>
  </div>;
}
