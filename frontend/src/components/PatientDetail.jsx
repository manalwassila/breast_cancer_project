import React, { useState, useEffect } from 'react';
import { Loader2, ArrowLeft, ShieldAlert, Calendar } from 'lucide-react';

export default function PatientDetail({ token, patientId, onBack }) {
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPatientDetails = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/patients/${patientId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          // Sort reverse chronologically
          if (data.analyses) {
            data.analyses.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
          }
          setPatient(data);
        }
      } catch (err) {
        console.error("Failed to load patient", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPatientDetails();
  }, [patientId, token]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '4rem' }}><Loader2 className="spinner" size={32} /></div>;
  }

  if (!patient) {
    return <div>Error: Patient not found</div>;
  }

  const formatDateTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="patient-detail-container">
      <button className="btn-secondary" onClick={onBack} style={{ marginBottom: '2rem' }}>
        <ArrowLeft size={16} /> Back to Patients Let
      </button>

      <div className="stats-box" style={{ marginBottom: '2rem', display: 'flex', gap: '3rem', flexWrap: 'wrap' }}>
        <div>
          <p className="text-muted text-sm">Patient ID</p>
          <h3 style={{ margin: 0 }}>#{patient.id}</h3>
        </div>
        <div>
          <p className="text-muted text-sm">Full Name</p>
          <h3 style={{ margin: 0 }}>{patient.first_name} {patient.last_name}</h3>
        </div>
        <div>
          <p className="text-muted text-sm">Date of Birth</p>
          <h3 style={{ margin: 0 }}>{patient.date_of_birth}</h3>
        </div>
      </div>

      <h3 className="mb-4">Analysis History</h3>

      {(!patient.analyses || patient.analyses.length === 0) ? (
        <p>No analysis history for this patient.</p>
      ) : (
        <div className="history-grid">
          {patient.analyses.map(analysis => (
            <div key={analysis.id} className="history-card">
              <div className="history-image-wrap">
                <img src={analysis.image_path} alt="Scan" className="history-image" />
                {/* Show corrected result if available, else AI result */}
                <span className={`status-badge ${(analysis.doctor_result || analysis.ai_result) === 'High Risk' ? 'bg-danger' : 'bg-success'}`}>
                  {analysis.doctor_result ? `✏️ ${analysis.doctor_result}` : `AI: ${analysis.ai_result}`}
                </span>
              </div>
              <div className="history-card-body">
                <div className="history-stat">
                  <strong>AI Confidence:</strong> {analysis.probability}%
                </div>

                {/* Doctor Review Section */}
                {analysis.status === 'Pending' ? (
                  <div className="pending-notice" style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem', marginTop: '0.5rem' }}>
                    ⏳ Awaiting doctor review
                  </div>
                ) : (
                  <div className={`doctor-decision-badge ${analysis.status === 'Confirmed' ? 'decision-confirmed' : 'decision-corrected'}`}>
                    {analysis.status === 'Confirmed' ? '✅ Confirmed' : '✏️ Corrected'} by Doctor
                  </div>
                )}

                {analysis.doctor_notes && (
                  <div className="doctor-notes-display">
                    <strong>📋 Doctor Notes:</strong>
                    <p>{analysis.doctor_notes}</p>
                  </div>
                )}

                <div className="history-date mt-4">
                  <Calendar size={14} /> {formatDateTime(analysis.created_at)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
