import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { MapContainer, TileLayer, Marker, Circle, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix Leaflet marker icon
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

function BulkMap({ center, setCenter, radius, setRadius }) {
  // Custom hook to handle map click
  useMapEvents({
    click(e) {
      setCenter([e.latlng.lat, e.latlng.lng]);
    }
  });
  return null;
}

function App() {
  const [location, setLocation] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [iframeError, setIframeError] = useState(false);
  const [activeTab, setActiveTab] = useState('search'); // 'search', 'history', 'saved', 'bulk'
  const [searchHistory, setSearchHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [savedSearches, setSavedSearches] = useState([]);
  const [savedLoading, setSavedLoading] = useState(false);
  // Bulk search state
  const [bulkCenter, setBulkCenter] = useState([35.681236, 139.767125]); // Default: Tokyo
  const [bulkRadius, setBulkRadius] = useState(2000); // meters
  const [bulkPoints, setBulkPoints] = useState([]);
  const [bulkProgress, setBulkProgress] = useState(0);
  const [bulkResults, setBulkResults] = useState([]);
  const [bulkRunning, setBulkRunning] = useState(false);
  const bulkAbortRef = useRef(null);
  const [showUniqueOnly, setShowUniqueOnly] = useState(true);
  const [bulkCity, setBulkCity] = useState('');

  // Always use modal for preview
  const isMobile = true;

  const API_BASE_URL = 'https://search-on-google-map-production.up.railway.app';

  useEffect(() => {
    if (iframeError && previewUrl) {
      window.open(previewUrl, '_blank', 'noopener,noreferrer');
      setPreviewUrl(null);
      setIframeError(false);
    }
  }, [iframeError, previewUrl]);

  const fetchSearchHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/recent-searches`);
      if (response.ok) {
        const data = await response.json();
        setSearchHistory(data);
      } else {
        console.error('Failed to fetch search history');
      }
    } catch (err) {
      console.error('Error fetching search history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const fetchSavedSearches = async () => {
    setSavedLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/cached-searches`);
      if (response.ok) {
        const data = await response.json();
        setSavedSearches(data);
      } else {
        console.error('Failed to fetch saved searches');
      }
    } catch (err) {
      console.error('Error fetching saved searches:', err);
    } finally {
      setSavedLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);
    try {
      const response = await fetch(
        `${API_BASE_URL}/search?location=${encodeURIComponent(location)}`,
        {
          method: 'GET',
          redirect: 'follow'
        }
      );
       const text = await response.text();
      console.log(text)
      console.log(response)
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

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return '#4CAF50';
      case 'error': return '#f44336';
      case 'no_results': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'history') {
      fetchSearchHistory();
    }
    if (tab === 'saved') {
      fetchSavedSearches();
    }
  };

  // Bulk search streaming
  const handleBulkSearch = () => {
    setBulkRunning(true);
    setBulkProgress(0);
    setBulkResults([]);
    setBulkCity('');
    const eventSource = new EventSource(`${API_BASE_URL}/bulk_search?center=${bulkCenter[0]},${bulkCenter[1]}&radius=${bulkRadius}&spacing=2000`);
    const uniqueStores = {};
    let totalPoints = 0;
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.city && !bulkCity) setBulkCity(data.city);
      if (Array.isArray(data.stores)) {
        data.stores.forEach(store => {
          if (!uniqueStores[store.place_id]) {
            uniqueStores[store.place_id] = store;
          }
        });
      }
      setBulkResults(prev => [...prev, data]);
      totalPoints++;
      setBulkProgress(Math.round((totalPoints / 20) * 100)); // Approximate progress
    };
    eventSource.onerror = () => {
      setBulkRunning(false);
      eventSource.close();
    };
    bulkAbortRef.current = () => {
      setBulkRunning(false);
      eventSource.close();
    };
  };

  // For search tab unique filtering by name (case-insensitive)
  const uniqueSearchResults = Object.values(
    results.reduce((acc, store) => {
      const key = store.name ? store.name.toLowerCase() : '';
      if (key && !acc[key]) acc[key] = store;
      return acc;
    }, {})
  );

  // For bulk search unique filtering by name (case-insensitive)
  const allBulkStores = bulkResults.flatMap(r => r.stores || []);
  const uniqueBulkStores = Object.values(
    allBulkStores.reduce((acc, store) => {
      const key = store.name ? store.name.toLowerCase() : '';
      if (key && !acc[key]) acc[key] = store;
      return acc;
    }, {})
  );

  return (
    <div className="App">
      <header className="App-header">
        <h1>Hardware Store Finder</h1>
        
        {/* Tab Navigation */}
        <div style={{ 
          display: 'flex', 
          marginBottom: 20, 
          borderBottom: '1px solid #444',
          width: '100%',
          maxWidth: 1000
        }}>
          <button
            onClick={() => handleTabChange('search')}
            style={{
              padding: '10px 20px',
              background: activeTab === 'search' ? '#61dafb' : 'transparent',
              color: activeTab === 'search' ? '#000' : '#fff',
              border: 'none',
              cursor: 'pointer',
              fontSize: 16,
              fontWeight: activeTab === 'search' ? 'bold' : 'normal'
            }}
          >
            🔍 Search
          </button>
          <button
            onClick={() => handleTabChange('history')}
            style={{
              padding: '10px 20px',
              background: activeTab === 'history' ? '#61dafb' : 'transparent',
              color: activeTab === 'history' ? '#000' : '#fff',
              border: 'none',
              cursor: 'pointer',
              fontSize: 16,
              fontWeight: activeTab === 'history' ? 'bold' : 'normal'
            }}
          >
            📊 Search History
          </button>
          <button
            onClick={() => handleTabChange('saved')}
            style={{
              padding: '10px 20px',
              background: activeTab === 'saved' ? '#61dafb' : 'transparent',
              color: activeTab === 'saved' ? '#000' : '#fff',
              border: 'none',
              cursor: 'pointer',
              fontSize: 16,
              fontWeight: activeTab === 'saved' ? 'bold' : 'normal'
            }}
          >
            💾 Saved Searches
          </button>
          <button
            onClick={() => handleTabChange('bulk')}
            style={{
              padding: '10px 20px',
              background: activeTab === 'bulk' ? '#61dafb' : 'transparent',
              color: activeTab === 'bulk' ? '#000' : '#fff',
              border: 'none',
              cursor: 'pointer',
              fontSize: 16,
              fontWeight: activeTab === 'bulk' ? 'bold' : 'normal'
            }}
          >
            🗺️ Bulk Search
          </button>
        </div>

        {/* Search Tab */}
        {activeTab === 'search' && (
          <>
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
            <div style={{ marginBottom: 10, fontSize: 13, color: '#6d5c3d', display: 'flex', alignItems: 'center' }}>
              <label style={{ fontSize: 13, color: '#6d5c3d', display: 'flex', alignItems: 'center', gap: 6 }}>
                <input type="checkbox" checked={showUniqueOnly} onChange={e => setShowUniqueOnly(e.target.checked)} style={{ width: 14, height: 14 }} /> Hide repeated stores
              </label>
            </div>
            {error && <div style={{ color: 'red', marginBottom: 10 }}>{error}</div>}
            <div style={{ width: '100%', maxWidth: 1000, margin: '0 auto', position: 'relative' }}>
              <div style={{ width: '100%', maxHeight: '60vh', overflowY: 'auto', background: 'transparent' }}>
                {(showUniqueOnly ? uniqueSearchResults : results).length > 0 && (
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
                      {(showUniqueOnly ? uniqueSearchResults : results).map((store, idx) => (
                        <tr key={store.place_id || idx} style={{ background: idx % 2 === 0 ? '#222' : '#292929' }}>
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
                {(showUniqueOnly ? uniqueSearchResults : results).length === 0 && !loading && !error && <div>Enter a location and search for hardware stores.</div>}
              </div>
            </div>
          </>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div style={{ width: '100%', maxWidth: 1000, margin: '0 auto' }}>
            <div style={{ marginBottom: 20 }}>
              <button 
                onClick={fetchSearchHistory}
                style={{ 
                  padding: '8px 16px', 
                  background: '#61dafb', 
                  color: '#000', 
                  border: 'none', 
                  borderRadius: 4, 
                  cursor: 'pointer',
                  fontSize: 14
                }}
                disabled={historyLoading}
              >
                {historyLoading ? 'Loading...' : '🔄 Refresh History'}
              </button>
            </div>
            
            {historyLoading ? (
              <div style={{ color: '#fff', textAlign: 'center' }}>Loading search history...</div>
            ) : searchHistory.length > 0 ? (
              <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
                <table style={{ width: '100%', background: '#222', borderRadius: 8, color: '#fff', borderCollapse: 'collapse', fontSize: 13 }}>
                  <thead>
                    <tr>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Location</th>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Status</th>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Stores Found</th>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Response Time</th>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {searchHistory.map((search, idx) => (
                      <tr key={search.id} style={{ background: idx % 2 === 0 ? '#222' : '#292929' }}>
                        <td style={{ padding: '8px' }}>{search.location}</td>
                        <td style={{ padding: '8px' }}>
                          <span style={{ 
                            color: getStatusColor(search.search_status),
                            fontWeight: 'bold'
                          }}>
                            {search.search_status}
                          </span>
                        </td>
                        <td style={{ padding: '8px' }}>{search.store_count || 0}</td>
                        <td style={{ padding: '8px' }}>
                          {search.response_time_ms ? `${search.response_time_ms}ms` : 'N/A'}
                        </td>
                        <td style={{ padding: '8px', fontSize: 12 }}>
                          {formatTimestamp(search.search_timestamp)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ color: '#fff', textAlign: 'center' }}>
                No search history available. Start searching to see your history!
              </div>
            )}
          </div>
        )}

        {/* Saved Searches Tab */}
        {activeTab === 'saved' && (
          <div style={{ width: '100%', maxWidth: 1000, margin: '0 auto' }}>
            <div style={{ marginBottom: 20 }}>
              <button onClick={fetchSavedSearches} style={{ padding: '8px 16px', background: '#61dafb', color: '#000', border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 14 }} disabled={savedLoading}>
                {savedLoading ? 'Loading...' : '🔄 Refresh Saved Searches'}
              </button>
            </div>
            {savedLoading ? (
              <div style={{ color: '#fff', textAlign: 'center' }}>Loading saved searches...</div>
            ) : savedSearches.length > 0 ? (
              <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
                <table style={{ width: '100%', background: '#222', borderRadius: 8, color: '#fff', borderCollapse: 'collapse', fontSize: 13 }}>
                  <thead>
                    <tr>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Location</th>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Stores</th>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Cached At</th>
                      <th style={{ padding: '8px', borderBottom: '1px solid #444' }}>Expires At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {savedSearches.map((item, idx) => (
                      <tr key={item.location + idx} style={{ background: idx % 2 === 0 ? '#222' : '#292929' }}>
                        <td style={{ padding: '8px' }}>{item.location}</td>
                        <td style={{ padding: '8px' }}>{item.store_count}</td>
                        <td style={{ padding: '8px', fontSize: 12 }}>{formatTimestamp(item.cached_at)}</td>
                        <td style={{ padding: '8px', fontSize: 12 }}>{formatTimestamp(item.expires_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ color: '#fff', textAlign: 'center' }}>
                No saved searches available.
              </div>
            )}
          </div>
        )}

        {/* Bulk Search Tab */}
        {activeTab === 'bulk' && (
          <div style={{ width: '100%', maxWidth: 1000, margin: '0 auto' }}>
            <h2>Bulk Grid Search</h2>
            <div style={{ height: 400, width: '100%', marginBottom: 20, borderRadius: 8, overflow: 'hidden', boxShadow: '0 2px 8px rgba(200,170,120,0.08)' }}>
              <MapContainer center={bulkCenter} zoom={12} style={{ height: '100%', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <Marker position={bulkCenter} draggable={true} eventHandlers={{ dragend: (e) => setBulkCenter([e.target.getLatLng().lat, e.target.getLatLng().lng]) }} />
                <Circle center={bulkCenter} radius={bulkRadius} pathOptions={{ color: '#ffb366', fillColor: '#ffb366', fillOpacity: 0.2 }} />
                <BulkMap center={bulkCenter} setCenter={setBulkCenter} radius={bulkRadius} setRadius={setBulkRadius} />
                {(showUniqueOnly ? uniqueBulkStores : allBulkStores).map((store, idx) => (
                  <Marker key={store.place_id || idx} position={[store.latitude, store.longitude]}>
                  </Marker>
                ))}
              </MapContainer>
            </div>
            <div style={{ marginBottom: 20 }}>
              <label>Radius (meters): </label>
              <input type="range" min={500} max={10000} step={100} value={bulkRadius} onChange={e => setBulkRadius(Number(e.target.value))} style={{ width: 200 }} />
              <span style={{ marginLeft: 10 }}>{bulkRadius} m</span>
            </div>
            <div style={{ marginBottom: 20 }}>
              <b>Center:</b> {bulkCenter[0].toFixed(5)}, {bulkCenter[1].toFixed(5)}
            </div>
            <div style={{ marginBottom: 20 }}>
              <button onClick={handleBulkSearch} disabled={bulkRunning} style={{ padding: '10px 20px', background: '#ffb366', color: '#3d2c1e', border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 16, fontWeight: 'bold', marginRight: 10 }}>Start Bulk Search</button>
              {bulkRunning && <button onClick={bulkAbortRef.current} style={{ padding: '10px 20px', background: '#f44336', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 16, fontWeight: 'bold' }}>Abort</button>}
            </div>
            <div style={{ marginBottom: 20 }}>
              <label>
                <input type="checkbox" checked={showUniqueOnly} onChange={e => setShowUniqueOnly(e.target.checked)} /> Hide repeated stores
              </label>
            </div>
            {bulkRunning && <div style={{ marginBottom: 20, color: '#3d2c1e' }}>Progress: {bulkProgress}%</div>}
            {bulkResults.length > 0 && (
              <div style={{ maxHeight: '40vh', overflowY: 'auto' }}>
                <table style={{ width: '100%', background: '#fff8ee', borderRadius: 8, color: '#3d2c1e', borderCollapse: 'collapse', fontSize: 13 }}>
                  <thead>
                    <tr>
                      <th>Lat</th>
                      <th>Lng</th>
                      <th>Stores Found</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bulkResults.map((res, idx) => (
                      <tr key={idx}>
                        <td>{res.lat.toFixed(5)}</td>
                        <td>{res.lng.toFixed(5)}</td>
                        <td>{res.stores.length}</td>
                        <td>{res.error ? <span style={{ color: '#f44336' }}>Error</span> : 'OK'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {bulkCity && <div style={{ marginTop: 10, color: '#3d2c1e' }}><b>City:</b> {bulkCity}</div>}
          </div>
        )}

        {/* Modal Preview */}
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
      </header>

      <footer>
      v1.3 - Bulk Search Streaming, Map Pins, City Names, and Filtering!
      </footer>
    </div>
  );
}

export default App;
