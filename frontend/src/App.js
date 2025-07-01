import React, { useState } from 'react';
import './App.css';

function App() {
  const [location, setLocation] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);
    try {
      const response = await fetch(`http://localhost:8000/search?location=${encodeURIComponent(location)}`);
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'API error');
      }
      const data = await response.json();
      setResults(data.stores);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Hardware Store Finder</h1>
        <form onSubmit={handleSearch} style={{ marginBottom: 20 }}>
          <input
            type="text"
            value={location}
            onChange={e => setLocation(e.target.value)}
            placeholder="Enter a location (city, address, etc.)"
            style={{ padding: 8, width: 300 }}
            required
          />
          <button type="submit" style={{ marginLeft: 10, padding: 8 }} disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
        {error && <div style={{ color: 'red', marginBottom: 10 }}>{error}</div>}
        <div style={{ width: '100%', maxWidth: 600, margin: '0 auto' }}>
          {results.length > 0 && (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {results.map((store, idx) => (
                <li key={idx} style={{ background: '#222', margin: '10px 0', padding: 16, borderRadius: 8 }}>
                  <h3 style={{ margin: 0 }}>{store.name}</h3>
                  <div>{store.address}</div>
                  {store.phone && <div>📞 {store.phone}</div>}
                  {store.website && <div><a href={store.website} target="_blank" rel="noopener noreferrer">Website</a></div>}
                </li>
              ))}
            </ul>
          )}
          {results.length === 0 && !loading && !error && <div>Enter a location and search for hardware stores.</div>}
        </div>
      </header>
    </div>
  );
}

export default App;
