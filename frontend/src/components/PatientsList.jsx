import React, { useState, useEffect } from 'react';
import { Search, Loader2, ChevronRight, User } from 'lucide-react';

export default function PatientsList({ token, onSelectPatient }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchPatients = async (query = '') => {
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/patients?search=${query}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPatients(data);
      }
    } catch (err) {
      console.error("Failed to fetch patients", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [token]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchPatients(search);
  };

  return (
    <div className="patients-list-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Database Patients</h2>
        
        <form onSubmit={handleSearch} className="search-bar">
          <input 
            type="text" 
            placeholder="Search by First or Last Name..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="btn-primary" style={{ padding: '0.5rem 1rem' }}>
            <Search size={18} />
          </button>
        </form>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem' }}>
          <Loader2 className="spinner" size={32} />
        </div>
      ) : patients.length === 0 ? (
        <div className="empty-state">
          <User size={48} color="var(--border-color)" />
          <p>No patients found matching your search.</p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Patient ID</th>
                <th>First Name</th>
                <th>Last Name</th>
                <th>Date of Birth</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.id} onClick={() => onSelectPatient(p.id)} style={{ cursor: 'pointer' }}>
                  <td>#{p.id}</td>
                  <td>{p.first_name}</td>
                  <td>{p.last_name}</td>
                  <td>{p.date_of_birth}</td>
                  <td style={{ color: 'var(--primary-color)' }}>
                    View Records <ChevronRight size={16} style={{ verticalAlign: 'middle' }}/>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
