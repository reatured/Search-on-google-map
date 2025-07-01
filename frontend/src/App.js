import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [location, setLocation] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [iframeError, setIframeError] = useState(false);

  // Always use modal for preview
  const isMobile = true;

  useEffect(() => {
    if (iframeError && previewUrl) {
      window.open(previewUrl, '_blank', 'noopener,noreferrer');
      setPreviewUrl(null);
      setIframeError(false);
    }
  }, [iframeError, previewUrl]);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);
    try {
      const response = await fetch(`http://127.0.0.1:8000/search?location=${encodeURIComponent(location)}`);
      const text = await response.text();
      try {
        const data = JSON.parse(text);
        console.log('Full API JSON data:', data);
        // If backend returns all details, just add one by one with a delay for effect
        if (Array.isArray(data.stores)) {
          for (let i = 0; i < data.stores.length; i++) {
            setResults(prev => [...prev, data.stores[i]]);
            // Simulate network delay for demo (remove or adjust as needed)
            await new Promise(res => setTimeout(res, 80));
          }
        } else {
          setError('No stores found in response.');
        }
      } catch (jsonErr) {
        console.error('Failed to parse JSON. Raw response:', text);
        setError('Failed to parse server response. See console for details.');
      }
    } catch (err) {
      console.error('Fetch or parse error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleWebsiteClick = (url, e) => {
    e.preventDefault();
    setPreviewUrl(url);
    setIframeError(false);
  };

  const handleClosePreview = () => {
    setPreviewUrl(null);
    setIframeError(false);
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
        <div style={{ width: '100%', maxWidth: 1000, margin: '0 auto', position: 'relative' }}>
          <div style={{ width: '100%', maxHeight: '60vh', overflowY: 'auto', background: 'transparent' }}>
            {results.length > 0 && (
              <table style={{ width: '100%', background: '#222', borderRadius: 8, color: '#fff', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr>
                    <th style={{ padding: '6px', borderBottom: '1px solid #444' }}>Name</th>
                    <th style={{ padding: '6px', borderBottom: '1px solid #444' }}>Address</th>
                    <th style={{ padding: '6px', borderBottom: '1px solid #444' }}>Phone</th>
                    <th style={{ padding: '6px', borderBottom: '1px solid #444' }}>Website</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((store, idx) => (
                    <tr key={idx} style={{ background: idx % 2 === 0 ? '#222' : '#292929' }}>
                      <td style={{ padding: '6px' }}>{store.name}</td>
                      <td style={{ padding: '6px' }}>{store.address}</td>
                      <td style={{ padding: '6px' }}>{store.phone ? `📞 ${store.phone}` : ''}</td>
                      <td style={{ padding: '6px' }}>
                        {store.website && (
                          <a
                            href={store.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: '#61dafb', cursor: 'pointer', fontSize: 13 }}
                            onClick={e => handleWebsiteClick(store.website, e)}
                          >
                            Website
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {results.length === 0 && !loading && !error && <div>Enter a location and search for hardware stores.</div>}
          </div>
          {/* Always show modal preview */}
          {previewUrl && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              background: 'rgba(0,0,0,0.8)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <div style={{ width: '95vw', height: '80vh', background: '#fff', borderRadius: 8, position: 'relative', display: 'flex', flexDirection: 'column' }}>
                <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 2, display: 'flex', gap: 8 }}>
                  <button onClick={handleClosePreview} style={{ fontSize: 24, background: 'none', border: 'none', cursor: 'pointer' }}>✕</button>
                  <button
                    onClick={() => {
                      window.open(previewUrl, '_blank', 'noopener,noreferrer');
                      handleClosePreview();
                    }}
                    style={{ fontSize: 16, padding: '4px 12px', background: '#222', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}
                  >
                    Open in new tab
                  </button>
                </div>
                <iframe
                  src={previewUrl}
                  title="Website Preview"
                  style={{ width: '100%', height: '100%', border: 'none', borderRadius: 8, marginTop: 40 }}
                />
              </div>
            </div>
          )}
        </div>
      </header>

      <footer>
      v0.4
      </footer>
    </div>
  );
}

export default App;
