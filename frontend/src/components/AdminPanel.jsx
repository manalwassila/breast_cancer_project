import React, { useState, useEffect } from 'react';
import { Loader2, Plus, Pencil, Trash2, X, Check, ShieldCheck, Users, Contact } from 'lucide-react';

const API = 'http://127.0.0.1:8000';

const ROLE_LABELS = {
  admin:  { label: '⚙️ Admin',          cls: 'badge-admin'  },
  doctor: { label: '👨‍⚕️ Doctor',        cls: 'badge-doctor' },
  staff:  { label: '🏥 Medical Staff',  cls: 'badge-staff'  },
};

export default function AdminPanel({ token }) {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers]       = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState('');

  // Modal state
  const [modalType, setModalType] = useState(null); // 'user' | 'patient'
  const [modalMode, setModalMode] = useState(null); // 'create' | 'edit'
  const [currentItem, setCurrentItem] = useState(null);
  
  const [userForm, setUserForm] = useState({ email: '', password: '', role: 'staff' });
  const [patientForm, setPatientForm] = useState({ first_name: '', last_name: '', date_of_birth: '' });
  
  const [saving, setSaving]     = useState(false);
  const [formError, setFormError] = useState('');

  // Confirm delete
  const [deleteTarget, setDeleteTarget] = useState(null); // { type: 'user'|'patient', id: number }

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'users') {
        const res = await fetch(`${API}/users`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) setUsers(await res.json());
      } else {
        const res = await fetch(`${API}/patients`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) setPatients(await res.json());
      }
    } catch { setError('Cannot connect to server.'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, [token, activeTab]);

  // --- USER ACTIONS ---
  const openUserModal = (mode, u = null) => {
    setModalType('user');
    setModalMode(mode);
    setCurrentItem(u);
    setFormError('');
    setUserForm(mode === 'create' ? { email: '', password: '', role: 'staff' } : { email: u.email, password: '', role: u.role });
  };

  const saveUser = async () => {
    if (!userForm.email || (modalMode === 'create' && !userForm.password)) {
      setFormError('Email and password are required.');
      return;
    }
    setSaving(true);
    try {
      const url = modalMode === 'create' ? `${API}/users` : `${API}/users/${currentItem.id}`;
      const method = modalMode === 'create' ? 'POST' : 'PATCH';
      const body = modalMode === 'create' 
        ? { ...userForm } 
        : { email: userForm.email, role: userForm.role, ...(userForm.password ? { password: userForm.password } : {}) };

      const res = await fetch(url, {
        method,
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (res.ok) { setModalType(null); fetchData(); }
      else { setFormError('Erreur de sauvegarde'); }
    } catch { setFormError('Connexion impossible'); }
    finally { setSaving(false); }
  };

  // --- PATIENT ACTIONS ---
  const openPatientModal = (mode, p = null) => {
    setModalType('patient');
    setModalMode(mode);
    setCurrentItem(p);
    setFormError('');
    setPatientForm(mode === 'create' ? { first_name: '', last_name: '', date_of_birth: '' } : { first_name: p.first_name, last_name: p.last_name, date_of_birth: p.date_of_birth });
  };

  const savePatient = async () => {
    if (!patientForm.first_name || !patientForm.last_name) {
      setFormError('Nom et prénom requis.');
      return;
    }
    setSaving(true);
    try {
      const url = modalMode === 'create' ? `${API}/patients` : `${API}/patients/${currentItem.id}`;
      const method = modalMode === 'create' ? 'POST' : 'PATCH';
      const res = await fetch(url, {
        method,
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(patientForm)
      });
      if (res.ok) { setModalType(null); fetchData(); }
      else { setFormError('Erreur de sauvegarde'); }
    } catch { setFormError('Connexion impossible'); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    try {
      const { type, id } = deleteTarget;
      const url = type === 'user' ? `${API}/users/${id}` : `${API}/patients/${id}`;
      const res = await fetch(url, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) { setDeleteTarget(null); fetchData(); }
    } catch { setError('Erreur de suppression'); }
  };

  return (
    <div className="admin-container">
      {/* Tab Switcher */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid #eee' }}>
        <button 
          onClick={() => setActiveTab('users')}
          style={{ 
            padding: '10px 20px', border: 'none', background: 'none', cursor: 'pointer',
            borderBottom: activeTab === 'users' ? '2px solid var(--primary-color)' : 'none',
            color: activeTab === 'users' ? 'var(--primary-color)' : '#666',
            display: 'flex', alignItems: 'center', gap: '8px'
          }}
        >
          <Users size={18} /> Gérer Utilisateurs
        </button>
        <button 
          onClick={() => setActiveTab('patients')}
          style={{ 
            padding: '10px 20px', border: 'none', background: 'none', cursor: 'pointer',
            borderBottom: activeTab === 'patients' ? '2px solid var(--primary-color)' : 'none',
            color: activeTab === 'patients' ? 'var(--primary-color)' : '#666',
            display: 'flex', alignItems: 'center', gap: '8px'
          }}
        >
          <Contact size={18} /> Gérer Patients
        </button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2>{activeTab === 'users' ? 'Gestion Utilisateurs' : 'Base de Données Patients'}</h2>
        <button className="btn-primary" onClick={() => activeTab === 'users' ? openUserModal('create') : openPatientModal('create')}>
          <Plus size={18} /> {activeTab === 'users' ? 'Nouvel Utilisateur' : 'Nouveau Patient'}
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}><Loader2 className="spinner" /></div>
      ) : activeTab === 'users' ? (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr><th>ID</th><th>Email</th><th>Rôle</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>#{u.id}</td>
                  <td>{u.email}</td>
                  <td><span className={`admin-badge ${ROLE_LABELS[u.role]?.cls}`}>{ROLE_LABELS[u.role]?.label}</span></td>
                  <td>
                    <button className="icon-btn" onClick={() => openUserModal('edit', u)}><Pencil size={15} /></button>
                    <button className="icon-btn danger" onClick={() => setDeleteTarget({type: 'user', id: u.id})}><Trash2 size={15} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr><th>ID</th><th>Nom</th><th>Date de Naissance</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.id}>
                  <td>#{p.id}</td>
                  <td>{p.first_name} {p.last_name}</td>
                  <td>{p.date_of_birth}</td>
                  <td>
                    <button className="icon-btn" onClick={() => openPatientModal('edit', p)}><Pencil size={15} /></button>
                    <button className="icon-btn danger" onClick={() => setDeleteTarget({type: 'patient', id: p.id})}><Trash2 size={15} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* --- MODALS --- */}
      {modalType && (
        <div className="modal-overlay">
          <div className="modal-box">
            <div className="modal-header">
              <h3>{modalMode === 'create' ? 'Ajouter' : 'Modifier'} {modalType === 'user' ? 'Utilisateur' : 'Patient'}</h3>
              <button className="icon-btn" onClick={() => setModalType(null)}><X /></button>
            </div>
            <div className="modal-body" style={{ padding: '20px' }}>
              {modalType === 'user' ? (
                <>
                  <div className="form-group">
                    <label>Email</label>
                    <input type="email" value={userForm.email} onChange={e => setUserForm({...userForm, email: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label>Mot de passe {modalMode === 'edit' && '(Optionnel)'}</label>
                    <input type="password" value={userForm.password} onChange={e => setUserForm({...userForm, password: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label>Rôle</label>
                    <select value={userForm.role} onChange={e => setUserForm({...userForm, role: e.target.value})}>
                      <option value="staff">🏥 Staff</option>
                      <option value="doctor">👨‍⚕️ Docteur</option>
                      <option value="admin">⚙️ Admin</option>
                    </select>
                  </div>
                </>
              ) : (
                <>
                  <div className="form-group">
                    <label>Prénom</label>
                    <input type="text" value={patientForm.first_name} onChange={e => setPatientForm({...patientForm, first_name: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label>Nom</label>
                    <input type="text" value={patientForm.last_name} onChange={e => setPatientForm({...patientForm, last_name: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label>Date de Naissance</label>
                    <input type="date" value={patientForm.date_of_birth} onChange={e => setPatientForm({...patientForm, date_of_birth: e.target.value})} max={new Date().toISOString().split('T')[0]} />
                  </div>
                </>
              )}
              {formError && <p style={{ color: 'red' }}>{formError}</p>}
            </div>
            <div className="modal-footer" style={{ padding: '20px', display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button className="btn-secondary" onClick={() => setModalType(null)}>Annuler</button>
              <button className="btn-primary" onClick={modalType === 'user' ? saveUser : savePatient} disabled={saving}>
                {saving ? <Loader2 className="spinner" /> : 'Sauvegarder'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {deleteTarget && (
        <div className="modal-overlay">
          <div className="modal-box" style={{ maxWidth: 400 }}>
            <h3>Confirmation</h3>
            <p>Êtes-vous sûr de vouloir supprimer {deleteTarget.type === 'user' ? 'cet utilisateur' : 'ce patient et tout son historique'} ?</p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button className="btn-secondary" onClick={() => setDeleteTarget(null)}>Annuler</button>
              <button className="btn-primary" style={{ background: '#e74c3c' }} onClick={handleDelete}>Supprimer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
