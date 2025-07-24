import React, { useState, useEffect } from 'react';
import { useSearchContext, Store } from '../context/SearchContext';

const SearchPage: React.FC = () => {
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<Store[]>([]);
  const { setSearchResults, searchResults } = useSearchContext();
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [iframeError, setIframeError] = useState(false);

  useEffect(() => {
    if (iframeError && previewUrl) {
      window.open(previewUrl, '_blank', 'noopener,noreferrer');
      setPreviewUrl(null);
      setIframeError(false);
    }
  }, [iframeError, previewUrl]);

  // Load previous search results on page load
  useEffect(() => {
    if (searchResults && searchResults.stores.length > 0) {
      setLocation(searchResults.location);
      setResults(searchResults.stores);
    }
  }, [searchResults]);

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);
    
    try {
      const response = await fetch(
        `https://search-on-google-map-production.up.railway.app/search?location=${encodeURIComponent(location)}`,
        {
          method: 'GET',
          redirect: 'follow'
        }
      );
      
      const text = await response.text();
      console.log('API Response:', text);
      
      try {
        const data = JSON.parse(text);
        console.log('Parsed API data:', data);
        
        if (Array.isArray(data.stores)) {
          // Save to context and localStorage
          const searchData = {
            location,
            stores: data.stores,
            timestamp: Date.now()
          };
          setSearchResults(searchData);
          
          // Add stores one by one with a delay for visual effect
          for (let i = 0; i < data.stores.length; i++) {
            setResults(prev => [...prev, data.stores[i]]);
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        } else {
          setError('No stores found in response.');
        }
      } catch (jsonErr) {
        console.error('Failed to parse JSON. Raw response:', text);
        setError('Failed to parse server response. See console for details.');
      }
    } catch (err: any) {
      console.error('Search error:', err);
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleWebsiteClick = (url: string, e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    setPreviewUrl(url);
    setIframeError(false);
  };

  const handleClosePreview = () => {
    setPreviewUrl(null);
    setIframeError(false);
  };

  return (
    <div className="page-container--search">
      <div className="content-section--centered">
        <h1 className="page-title--gradient">
          Hardware Store Finder
        </h1>
        <p className="page-subtitle">
          Find hardware stores near you with ease
        </p>
      </div>
      
      <h2 className="section-title">Search for Hardware Stores</h2>
      <p className="section-description">
        Enter a location to search for hardware stores in that area
      </p>
      
      <form onSubmit={handleSearch} className="form-container">
        <div className="form-group--inline">
          <input
            type="text"
            value={location}
            onChange={e => setLocation(e.target.value)}
            placeholder="Enter a location (city, address, etc.)"
            className="form-input--search"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="btn btn--primary"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Search Results Table */}
      {results.length > 0 && (
        <div className="results-container">
          <h3 className="results-title">Found {results.length} Hardware Store{results.length !== 1 ? 's' : ''} near "{location}"</h3>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Address</th>
                  <th>Phone</th>
                  <th>Website</th>
                </tr>
              </thead>
              <tbody>
                {results.map((store: Store, idx: number) => (
                  <tr key={idx}>
                    <td className="cell-name">{store.name}</td>
                    <td>{store.address}</td>
                    <td>
                      {store.phone ? (
                        <a href={`tel:${store.phone}`} className="link--phone">
                          {store.phone}
                        </a>
                      ) : ''}
                    </td>
                    <td>
                      {store.website && (
                        <a
                          href={store.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="link--website"
                          onClick={e => store.website && handleWebsiteClick(store.website, e)}
                        >
                          Visit Website
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Website Preview Modal */}
      {previewUrl && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-controls">
              <button 
                onClick={handleClosePreview} 
                className="btn--modal-close"
              >
                ✕
              </button>
              <button
                onClick={() => {
                  window.open(previewUrl, '_blank', 'noopener,noreferrer');
                  handleClosePreview();
                }}
                className="btn--modal-open"
              >
                Open in new tab
              </button>
            </div>
            <iframe
              src={previewUrl}
              title="Website Preview"
              className="modal-iframe"
              onError={() => setIframeError(true)}
            />
          </div>
        </div>
      )}

      {results.length === 0 && !loading && !error && (
        <div className="instructions">
          <h3>How it works:</h3>
          <ol className="instructions__list">
            <li>Enter your location (city, address, or landmark)</li>
            <li>Click search to find nearby hardware stores</li>
            <li>Browse results with contact information</li>
            <li>Visit store websites directly from the results</li>
          </ol>
        </div>
      )}
    </div>
  );
};

export default SearchPage;