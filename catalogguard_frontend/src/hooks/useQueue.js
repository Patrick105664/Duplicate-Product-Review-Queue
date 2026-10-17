import { useCallback, useEffect, useState } from "react";
import { getReviewPairs, submitDecision } from "../api/reviews";

export function useQueue() {
  const [pairs, setPairs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const refresh = useCallback(async () => {
    setLoading(true); setError("");
    try { setPairs(await getReviewPairs() || []); }
    catch (err) { setError(err.message || "Unable to load review queue"); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { refresh(); }, [refresh]);
  const decide = useCallback(async (id, decision, note = "") => {
    await submitDecision(id, decision, note);
    await refresh();
  }, [refresh]);
  return { pairs, loading, error, refresh, decide };
}
