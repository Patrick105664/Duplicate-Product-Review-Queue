import React, { useEffect, useState } from "react";
import { CheckCircle2, CircleAlert, Target, Timer, ShieldCheck, Gauge } from "lucide-react";
import { getMetrics } from "../api/metrics";
import StatCard from "../components/StatCard";
import { formatCurrencyINR } from "../utils/formatters";

export default function Evaluation() {
  const [m, setM] = useState(null);
  useEffect(() => { getMetrics().then(setM).catch(() => setM(null)); }, []);
  const precision = m?.precision ?? 0, recall = m?.recall ?? 0;
  return <div className="page-content">
    <div className="page-toolbar"><div><div className="overline">MODEL QUALITY</div><h2>Evaluation & quality</h2><p>Measure duplicate suggestions against labelled examples before expanding the pilot.</p></div><span className="evaluation-target"><Target size={16} /> Target precision ≥ 90%</span></div>
    <div className="demo-banner"><CircleAlert size={16} /><span><strong>Important:</strong> the values below are illustrative demo metrics. Use the labelled <code>Starter_Data/C06/fixture.json</code> and actual reviewer labels for a valid evaluation.</span></div>
    <div className="stats-grid evaluation-stats">
      <StatCard label="Precision" value={`${precision}%`} icon={Target} tone="mint" change={`${m?.precisionCorrect ?? 0} correct / ${m?.precisionReviewed ?? 0} reviewed`} footnote="share of suggested pairs that are correct" />
      <StatCard label="Recall" value={`${recall}%`} icon={CheckCircle2} tone="lavender" change={`${m?.recallFound ?? 0} found / ${m?.recallExpected ?? 0} expected`} footnote="share of labelled duplicates found" />
      <StatCard label="Accuracy" value={m?.accuracy == null ? "—" : `${m.accuracy}%`} icon={Gauge} tone="blue" change={m?.accuracyCorrect != null && m?.accuracyTotal != null ? `${m.accuracyCorrect} correct / ${m.accuracyTotal} decisions` : "Overall decision accuracy"} footnote="share of all review decisions that are correct" />
      <StatCard label="Average review time" value={`${m?.avgReviewTimeSeconds ?? "—"}s`} icon={Timer} tone="peach" change="Track during pilot" footnote="median is preferable when available" />
      <StatCard label="False merge rate" value={`${m?.falseMergeRate ?? "—"}%`} icon={ShieldCheck} tone="blue" change="Must remain zero" footnote="distinct labelled variants incorrectly merged" />
      <StatCard label="False merge cost" value={m ? formatCurrencyINR(m.falseMergeCostPerMerge) : "—"} icon={CircleAlert} tone="peach" change={m ? `${m.falseMergeCount} false merges · ${formatCurrencyINR(m.falseMergeExposure)} estimated exposure` : "Estimated cost per false merge"} footnote="estimated damage for each incorrect product merge" />
    </div>
    <section className="panel false-merge-breakdown">
      <div className="panel-heading"><div><h3>Estimated false merge cost</h3><p>Estimated damage is separate from the false merge rate.</p></div></div>
      <div className="false-merge-cost-rows">
        <div><span>Correction labour ({m?.labourMinutes ?? 0} min at {formatCurrencyINR(m?.labourRatePerHour)} / hour)</span><strong>{formatCurrencyINR(m ? m.labourMinutes / 60 * m.labourRatePerHour : 0)}</strong></div>
        <div><span>Downstream operational loss</span><strong>{formatCurrencyINR(m?.downstreamLoss)}</strong></div>
        <div><span>Customer remediation</span><strong>{formatCurrencyINR(m?.remediationCost)}</strong></div>
        <div className="false-merge-cost-total"><span>Cost per false merge</span><strong>{m ? formatCurrencyINR(m.falseMergeCostPerMerge) : "—"}</strong></div>
      </div>
      <p className="false-merge-exposure">{m ? `${m.falseMergeCount} false merges x ${formatCurrencyINR(m.falseMergeCostPerMerge)} = ${formatCurrencyINR(m.falseMergeExposure)} estimated total exposure.` : "Estimated total exposure is unavailable."}</p>
      <p className="false-merge-notice">Review the false merge cost before enabling bulk automation.</p>
    </section>
    <div className="evaluation-grid">
      <section className="panel"><div className="panel-heading"><div><h3>Quality thresholds</h3><p>Checks to pass before any catalogue write integration.</p></div></div>
        <div className="threshold-row"><div className={`threshold-icon ${precision >= 90 ? "pass" : "warning"}`}><CheckCircle2 size={18} /></div><div><strong>Precision at least 90%</strong><p>Report the numerator and denominator, not just a percentage.</p></div><span className={`threshold-state ${precision >= 90 ? "pass-text" : "warning-text"}`}>{precision >= 90 ? "Demo target met" : "Needs improvement"}</span></div>
        <div className="threshold-row"><div className="threshold-icon pass"><ShieldCheck size={18} /></div><div><strong>Zero false merges of distinct variants</strong><p>Single items, multipacks, model variants and size variants must remain distinct.</p></div><span className="threshold-state pass-text">Required</span></div>
        <div className="threshold-row"><div className="threshold-icon warning"><Timer size={18} /></div><div><strong>Measure reviewer time</strong><p>Record time spent per decision during the pilot.</p></div><span className="threshold-state warning-text">Collect data</span></div>
      </section>
      <section className="panel methodology"><div className="panel-heading"><div><h3>How to evaluate</h3><p>Use the same labelled test set for each run.</p></div></div><ol><li><strong>Load fixture data</strong><p>Use the provided 20-product C06 fixture with positive and hard-negative pairs.</p></li><li><strong>Compare suggestions to labels</strong><p>Count true positives, false positives and false negatives.</p></li><li><strong>Calculate metrics</strong><p>Precision = TP / (TP + FP). Recall = TP / (TP + FN).</p></li><li><strong>Inspect variant errors</strong><p>Review every false positive involving pack quantity or model variants.</p></li></ol></section>
    </div>
    <p className="metric-disclaimer">Do not present demo metrics as measured production performance. Keep the pilot suggestion-only until quality and review-time results are validated.</p>
  </div>;
}
