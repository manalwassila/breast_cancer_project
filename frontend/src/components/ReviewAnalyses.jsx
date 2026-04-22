import React, { useState, useEffect } from 'react';
import { Loader2, CheckCircle, XCircle, RefreshCw } from 'lucide-react';

export default function ReviewAnalyses({ token }) {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState(null);
  const [decisions, setDecisions] = useState({}); // { analysisId: { decision, notes } }

  const fetchPending = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/analyses/pending', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAnalyses(data);
      }
    } catch (err) {
      console.error('Failed to fetch analyses', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPending(); }, [token]);

  const saveReview = async (analysisId) => {
    const d = decisions[analysisId] || {};
    if (!d.decision) return;
    if (d.decision === 'Corrected' && !d.correctedResult) return; // require selection
    setSavingId(analysisId);
    try {
      await fetch(`http://127.0.0.1:8000/analyses/${analysisId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          doctor_decision: d.decision,
          doctor_notes: d.notes || '',
          status: d.decision,
          doctor_result: d.decision === 'Corrected' ? d.correctedResult : null
        })
      });
      // Remove from list after review
      setAnalyses(prev => prev.filter(a => a.id !== analysisId));
    } catch (e) {
      console.error(e);
    } finally {
      setSavingId(null);
    }
  };

  const setDecision = (id, field, value) => {
    setDecisions(prev => ({
      ...prev,
      [id]: { ...prev[id], [field]: value }
    }));
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><Loader2 className="spinner" size={32} /></div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Pending Reviews</h2>
          <p className="text-sm text-muted">AI analyses waiting for your medical decision</p>
        </div>
        <button className="btn-secondary" onClick={fetchPending}><RefreshCw size={16} /> Refresh</button>
      </div>

      {analyses.length === 0 ? (
        <div className="empty-state" style={{ textAlign: 'center', padding: '4rem' }}>
          <CheckCircle size={48} color="var(--success-color)" />
          <p className="mt-4">All analyses have been reviewed. Nothing pending.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {analyses.map(a => {
            const d = decisions[a.id] || {};
            return (
              <div key={a.id} className="review-item-card">
                <div className="review-item-left">
                  <img src={a.image_path} alt="scan" className="review-thumb" />
                </div>
                <div className="review-item-body">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h4>{a.patient_name}</h4>
                      <p className="text-xs text-muted">{new Date(a.created_at).toLocaleString()}</p>
                    </div>
                    <span className={`status-badge ${a.ai_result === 'High Risk' ? 'bg-danger' : 'bg-success'}`}>
                      AI: {a.ai_result}
                    </span>
                  </div>
                  <p className="text-sm mt-4"><strong>Confidence:</strong> {a.probability}%</p>

                  <div className="decision-buttons mt-4">
                    <button
                      className={`decision-btn ${d.decision === 'Confirmed' ? 'decision-active-confirm' : ''}`}
                      onClick={() => setDecision(a.id, 'decision', 'Confirmed')}
                    >
                      <CheckCircle size={16} /> Confirm AI Result
                    </button>
                    <button
                      className={`decision-btn ${d.decision === 'Corrected' ? 'decision-active-correct' : ''}`}
                      onClick={() => setDecision(a.id, 'decision', 'Corrected')}
                    >
                      <XCircle size={16} /> Correct AI Result
                    </button>
                  </div>

                  {/* Show corrected result selector when doctor clicks Correct */}
                  {d.decision === 'Corrected' && (
                    <div className="corrected-result-box mt-4">
                      <p className="text-sm" style={{ marginBottom: '0.5rem' }}>
                        <strong>Corrected Diagnosis:</strong> Change from
                        <span className={`inline-badge ${a.ai_result === 'High Risk' ? 'bg-danger' : 'bg-success'}`}>
                          {a.ai_result}
                        </span> to:
                      </p>
                      <div className="decision-buttons">
                        <button
                          className={`decision-btn ${d.correctedResult === 'High Risk' ? 'decision-active-correct' : ''}`}
                          onClick={() => setDecision(a.id, 'correctedResult', 'High Risk')}
                        >
                          🔴 High Risk
                        </button>
                        <button
                          className={`decision-btn ${d.correctedResult === 'Low Risk' ? 'decision-active-confirm' : ''}`}
                          onClick={() => setDecision(a.id, 'correctedResult', 'Low Risk')}
                        >
                          🟢 Low Risk
                        </button>
                      </div>
                    </div>
                  )}

                  <textarea
                    className="doctor-notes-input mt-4"
                    rows={2}
                    placeholder="Clinical notes (optional)..."
                    value={d.notes || ''}
                    onChange={e => setDecision(a.id, 'notes', e.target.value)}
                  />

                  <button
                    className="btn-primary mt-4"
                    disabled={!d.decision || savingId === a.id || (d.decision === 'Corrected' && !d.correctedResult)}
                    onClick={() => saveReview(a.id)}
                    style={{ width: '100%' }}
                  >
                    {savingId === a.id ? <RefreshCw className="spinner" size={16} /> : 'Save Decision'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
