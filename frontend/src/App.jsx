import React, { useState, useEffect } from 'react';
import { Activity, ShieldAlert, UploadCloud, X, RefreshCw, Users, FileText, LogOut, ShieldCheck, LifeBuoy } from 'lucide-react';
import './index.css';
import PatientsList from './components/PatientsList';
import PatientDetail from './components/PatientDetail';
import ReviewAnalyses from './components/ReviewAnalyses';
import AdminPanel from './components/AdminPanel';
import LandingPage from './components/LandingPage';
import Support from './components/Support';

function App() {
  const [token, setToken] = useState(localStorage.getItem('mammoscan_token'));
  
  // Login State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  // App State
  const [view, setView] = useState('dashboard');
  const [publicView, setPublicView] = useState('landing'); 
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [userEmail, setUserEmail] = useState('');
  const [currentUser, setCurrentUser] = useState(null);

  // Fetch user info on token change
  useEffect(() => {
    if (token) {
      fetch('http://127.0.0.1:8000/users/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(r => r.json())
        .then(data => {
          setUserRole(data.role);
          setUserEmail(data.email);
          setCurrentUser(data);
        })
        .catch(() => handleLogout());
    }
  }, [token]);

  // Analysis State
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [dob, setDob] = useState('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  // Reset form when navigating to analysis
  useEffect(() => {
    if (view === 'analysis') {
      setFirstName('');
      setLastName('');
      setDob('');
      setFile(null);
      setPreview(null);
      setResult(null);
      setAnalysisError(null);
    }
  }, [view]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch('http://127.0.0.1:8000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        localStorage.setItem('mammoscan_token', data.access_token);
      } else {
        setAuthError('Invalid credentials');
      }
    } catch (err) {
      setAuthError('Failed to connect to server');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUserRole(null);
    setUserEmail('');
    setCurrentUser(null);
    localStorage.removeItem('mammoscan_token');
    setView('dashboard');
  };

  const handleFileChange = (selectedFile) => {
    setAnalysisError(null);
    setResult(null);
    if (selectedFile && selectedFile.type.startsWith('image/')) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(selectedFile);
    } else {
      setAnalysisError('Veuillez télécharger une image valide.');
    }
  };

  const removeFile = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
  };

  const analyzeImage = async () => {
    if (!file || !firstName || !lastName || !dob) {
      setAnalysisError("Veuillez remplir toutes les informations et télécharger un scan.");
      return;
    }
    
    setAnalysisLoading(true);
    setAnalysisError(null);
    setResult(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('first_name', firstName);
    formData.append('last_name', lastName);
    formData.append('date_of_birth', dob);

    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de l’analyse.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setAnalysisError(err.message);
    } finally {
      setAnalysisLoading(false);
    }
  };

  if (!token) {
    if (publicView === 'landing') {
      return <LandingPage onLogin={() => setPublicView('login')} />;
    }
    return (
      <div className="login-container">
        <div className="login-card">
          <Activity size={48} color="var(--primary-color)" style={{ margin: '0 auto 1rem auto' }}/>
          <h2>MammoScan AI Portal</h2>
          <p className="text-muted mb-6">Accès réservé au personnel médical autorisé</p>
          <form onSubmit={handleLogin} className="login-form">
            <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
            <input type="password" placeholder="Mot de passe" value={password} onChange={e => setPassword(e.target.value)} required />
            {authError && <p className="text-danger text-sm mb-2">{authError}</p>}
            <button type="submit" className="btn-primary" disabled={authLoading}>
              {authLoading ? <RefreshCw className="spinner" size={18} /> : 'Se connecter'}
            </button>
          </form>
          <button className="btn-secondary" style={{ width: '100%', marginTop: '1rem' }} onClick={() => setPublicView('landing')}>
            ← Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  const getRoleBadge = (role) => {
    if (role === 'admin') return { label: '⚙️ Admin', cls: 'role-admin' };
    if (role === 'doctor') return { label: '👨‍⚕️ Doctor', cls: 'role-doctor' };
    return { label: '🏥 Medical Staff', cls: 'role-staff' };
  };

  const badge = getRoleBadge(userRole);

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/logo.png" alt="Logo" style={{ width: '32px', height: '32px', borderRadius: '50%' }} />
          <div>
            <h2>MammoScan</h2>
            <span className={`role-badge ${badge.cls}`}>{badge.label}</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          <button className={`sidebar-btn ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>
            <Activity size={18} /> Dashboard
          </button>
          {userRole === 'admin' && (
            <button className={`sidebar-btn ${view === 'admin' ? 'active' : ''}`} onClick={() => setView('admin')}>
              <ShieldCheck size={18} /> Administration
            </button>
          )}
          {userRole === 'staff' && (
            <button className={`sidebar-btn ${view === 'analysis' ? 'active' : ''}`} onClick={() => setView('analysis')}>
              <UploadCloud size={18} /> Nouvelle Analyse
            </button>
          )}
          {userRole === 'doctor' && (
            <button className={`sidebar-btn ${view === 'review' ? 'active' : ''}`} onClick={() => setView('review')}>
              <FileText size={18} /> Révision Analyses
            </button>
          )}
          <button className={`sidebar-btn ${view === 'patients' || view === 'patient_detail' ? 'active' : ''}`} onClick={() => setView('patients')}>
            <Users size={18} /> Patients
          </button>
          <button className={`sidebar-btn ${view === 'support' ? 'active' : ''}`} onClick={() => setView('support')}>
            <LifeBuoy size={18} /> Support Technique
          </button>
        </nav>
        <div className="sidebar-footer">
          <p className="text-xs text-muted" style={{padding: '0 1rem 0.5rem'}}>{userEmail}</p>
          <button className="sidebar-btn text-danger" onClick={handleLogout}>
            <LogOut size={18} /> Déconnexion
          </button>
        </div>
      </aside>

      <main className="main-content">
        {view === 'dashboard' && (
          <div className="dashboard-view">
             <h2>Bienvenue, {userRole === 'doctor' ? 'Docteur' : userRole === 'admin' ? 'Administrateur' : 'Membre du Staff'}</h2>
             <p className="text-muted mb-8">MammoScan AI — Plateforme d'analyse du cancer du sein (DenseNet121).</p>
             <div className="stats-row" style={{justifyContent: 'flex-start'}}>
                {userRole === 'staff' && (
                  <div className="stat-card" onClick={() => setView('analysis')}>
                    <UploadCloud size={32} color="var(--primary-color)" />
                    <h3 className="mt-4">Nouvelle Analyse</h3>
                    <p className="text-sm">Télécharger un scan</p>
                  </div>
                )}
                {userRole === 'doctor' && (
                  <div className="stat-card" onClick={() => setView('review')}>
                    <FileText size={32} color="var(--primary-color)" />
                    <h3 className="mt-4">Révision</h3>
                    <p className="text-sm">Confirmer les résultats AI</p>
                  </div>
                )}
                {userRole === 'admin' && (
                  <div className="stat-card" onClick={() => setView('admin')}>
                    <ShieldCheck size={32} color="var(--primary-color)" />
                    <h3 className="mt-4">Administration</h3>
                    <p className="text-sm">Gérer les comptes et patients</p>
                  </div>
                )}
                <div className="stat-card" onClick={() => setView('patients')}>
                  <Users size={32} color="var(--success-color)" />
                  <h3 className="mt-4">Base Patients</h3>
                  <p className="text-sm">Historique médical</p>
                </div>
                <div className="stat-card" onClick={() => setView('support')}>
                  <LifeBuoy size={32} color="var(--primary-color)" />
                  <h3 className="mt-4">Support</h3>
                  <p className="text-sm">Assistance technique</p>
                </div>
             </div>
          </div>
        )}

        {view === 'analysis' && userRole === 'staff' && (
          <div className="analysis-view">
            <h2 className="mb-6">Lancer une Analyse AI</h2>
            <div className="analysis-layout">
              <div className="patient-form-card">
                <h3>1. Infos Patient</h3>
                <div className="form-group"><label>Prénom</label><input type="text" value={firstName} onChange={e=>setFirstName(e.target.value)} required /></div>
                <div className="form-group"><label>Nom</label><input type="text" value={lastName} onChange={e=>setLastName(e.target.value)} required /></div>
                <div className="form-group"><label>Date de Naissance</label><input type="date" value={dob} onChange={e=>setDob(e.target.value)} max={new Date().toISOString().split('T')[0]} required /></div>
              </div>

              <div className="upload-card">
                <h3>2. Téléchargement Scan</h3>
                {!preview ? (
                  <div className="drop-zone mt-4" onClick={() => document.getElementById('fileUpload').click()}>
                    <input type="file" id="fileUpload" style={{ display: 'none' }} accept="image/*" onChange={(e) => handleFileChange(e.target.files[0])} />
                    <UploadCloud size={48} color="#94a3b8" />
                    <h4>Sélectionner une image</h4>
                  </div>
                ) : (
                  <div className="preview-container mt-4">
                    <img src={preview} alt="Scan preview" className="preview-image" />
                    <button className="remove-btn" onClick={removeFile}><X size={18} /></button>
                  </div>
                )}
                <button className="btn-primary mt-6" style={{width:'100%'}} onClick={analyzeImage} disabled={analysisLoading || !file}>
                  {analysisLoading ? <><RefreshCw className="spinner" size={18} /> Analyse...</> : 'Analyser'}
                </button>
                {analysisError && <p className="text-danger mt-2">{analysisError}</p>}
              </div>
            </div>

            {result && (
              <div className={`result-card mt-6 ${result.prediction === 'High Risk' ? 'high-risk' : 'low-risk'}`}>
                <h3>Prédiction AI: {result.prediction === 'High Risk' ? 'Risque Élevé' : 'Risque Faible'}</h3>
                <div className="prob-score">{result.probability}% de Confiance</div>
                <p className="mt-2 text-muted">Patient: {result.patient_info}</p>
                <hr style={{ margin: '1rem 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />
                <div className="pending-notice">⏳ Analyse sauvegardée. En attente de révision médicale.</div>
                <p className="text-xs text-danger mt-4"><ShieldAlert size={14} style={{verticalAlign:'bottom', marginRight:'4px'}}/> Résultat AI à confirmer par un médecin.</p>
              </div>
            )}
          </div>
        )}

        {view === 'review' && userRole === 'doctor' && <ReviewAnalyses token={token} />}
        {view === 'admin' && userRole === 'admin' && <AdminPanel token={token} />}
        {view === 'support' && <Support user={currentUser} token={token} />}
        {view === 'patients' && <PatientsList token={token} onSelectPatient={(id) => { setSelectedPatientId(id); setView('patient_detail'); }} />}
        {view === 'patient_detail' && selectedPatientId && <PatientDetail token={token} patientId={selectedPatientId} onBack={() => { setSelectedPatientId(null); setView('patients'); }} />}
      </main>
    </div>
  );
}

export default App;
