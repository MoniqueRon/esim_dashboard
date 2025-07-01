import { useEffect, useState } from 'react';
import axios from 'axios';

export default function DashboardPage() {
  const [esims, setEsims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchEsims = async () => {
      setLoading(true);
      setError('');
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('http://localhost:8000/esims', {
          headers: { Authorization: `Bearer ${token}` },
        });
        console.log('API response:', res.data); // Debug logging
        
        // Handle different response formats
        let esimData = res.data;
        if (esimData && Array.isArray(esimData.data)) {
          esimData = esimData.data;
        } else if (esimData && !Array.isArray(esimData)) {
          esimData = [esimData]; // Wrap single object in array
        }
        
        setEsims(Array.isArray(esimData) ? esimData : []);
      } catch (err) {
        setError(`Failed to load ESIMs: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    fetchEsims();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  return (
    <div style={{ padding: '2rem', maxWidth: 900, margin: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>ESIM Dashboard</h2>
        <button onClick={handleLogout}>Logout</button>
      </div>
      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div style={{ color: 'red' }}>{error}</div>
      ) : esims.length === 0 ? (
        <div>No ESIMs found</div>
      ) : (
        <table border="1" cellPadding="8" style={{ width: '100%', marginTop: '2rem', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {esims.length > 0 && Object.keys(esims[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {esims.map((esim, idx) => (
              <tr key={idx}>
                {Object.values(esim).map((val, i) => (
                  <td key={i}>{String(val)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
