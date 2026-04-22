import React, { useState, useEffect } from 'react';

const Support = ({ user, token }) => {
  const [tickets, setTickets] = useState([]);
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [replyText, setReplyText] = useState('');
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTickets = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:8000/support', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (resp.ok) {
        const data = await resp.ok ? await resp.json() : [];
        setTickets(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const resp = await fetch('http://127.0.0.1:8000/support', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ subject, message })
      });
      if (resp.ok) {
        setSubject('');
        setMessage('');
        fetchTickets();
      } else {
        setError('Échec de l\'envoi du message.');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur.');
    } finally {
      setLoading(false);
    }
  };

  const handleReply = async (ticketId) => {
    try {
      const resp = await fetch(`http://127.0.0.1:8000/support/${ticketId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ admin_reply: replyText, status: 'closed' })
      });
      if (resp.ok) {
        setReplyText('');
        setSelectedTicket(null);
        fetchTickets();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="support-container" style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h2 style={{ color: '#2c3e50', marginBottom: '20px' }}>Support Technique</h2>
      
      {!isAdmin && (
        <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', marginBottom: '30px' }}>
          <h3>Envoyer un nouveau message</h3>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input 
              type="text" 
              placeholder="Sujet" 
              value={subject} 
              onChange={(e) => setSubject(e.target.value)}
              required 
              style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
            />
            <textarea 
              placeholder="Votre message..." 
              value={message} 
              onChange={(e) => setMessage(e.target.value)}
              required 
              rows="4"
              style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
            />
            <button 
              type="submit" 
              disabled={loading}
              style={{ 
                padding: '12px', 
                background: '#3498db', 
                color: 'white', 
                border: 'none', 
                borderRadius: '6px', 
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              {loading ? 'Envoi...' : 'Envoyer à l\'Administrateur'}
            </button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
          </form>
        </div>
      )}

      <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
        <h3>{isAdmin ? 'Messages des utilisateurs' : 'Vos demandes'}</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {tickets.length === 0 ? <p>Aucun message pour le moment.</p> : tickets.map(ticket => (
            <div key={ticket.id} style={{ border: '1px solid #eee', padding: '15px', borderRadius: '8px', position: 'relative' }}>
              <span style={{ 
                position: 'absolute', right: '15px', top: '15px', 
                padding: '4px 8px', borderRadius: '4px', fontSize: '12px',
                background: ticket.status === 'open' ? '#e74c3c' : '#2ecc71',
                color: 'white'
              }}>
                {ticket.status === 'open' ? 'Ouvert' : 'Répondu'}
              </span>
              <p><strong>Sujet:</strong> {ticket.subject}</p>
              {isAdmin && <p><small>De: {ticket.user_email}</small></p>}
              <p style={{ margin: '10px 0', color: '#555' }}>{ticket.message}</p>
              
              {ticket.admin_reply && (
                <div style={{ background: '#f8f9fa', padding: '10px', borderRadius: '6px', marginTop: '10px', borderLeft: '4px solid #3498db' }}>
                  <p><strong>Réponse Admin:</strong> {ticket.admin_reply}</p>
                </div>
              )}

              {isAdmin && ticket.status === 'open' && (
                <div style={{ marginTop: '15px' }}>
                  <textarea 
                    placeholder="Votre réponse..." 
                    value={selectedTicket === ticket.id ? replyText : ''}
                    onChange={(e) => {
                      setSelectedTicket(ticket.id);
                      setReplyText(e.target.value);
                    }}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd', marginBottom: '10px' }}
                  />
                  <button 
                    onClick={() => handleReply(ticket.id)}
                    style={{ padding: '8px 15px', background: '#2ecc71', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    Répondre et fermer
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Support;
