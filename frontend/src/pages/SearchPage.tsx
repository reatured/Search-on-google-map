import React, { useState, useEffect } from 'react';
import { useSearchContext, Store } from '../context/SearchContext';
import CompanyAnalysisModal from '../components/CompanyAnalysisModal';

const SearchPage: React.FC = () => {
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<Store[]>([]);
  const { setSearchResults, searchResults, useLocalAPI, setUseLocalAPI, getAPIEndpoint } = useSearchContext();
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [iframeError, setIframeError] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState<{found: number, total?: number}>({found: 0});
  const [analysisModal, setAnalysisModal] = useState<{show: boolean, store: Store | null}>({show: false, store: null});


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
    setLoadingProgress({found: 0});
    
    try {
      const response = await fetch(
        `${getAPIEndpoint()}/search/stream?location=${encodeURIComponent(location)}`,
        {
          method: 'GET',
          redirect: 'follow'
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let searchLocation = location;
      let allStores: Store[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
              }

              if (data.location && data.total_found !== undefined) {
                // Initial response with location info
                searchLocation = data.location;
                setLoadingProgress({found: 0, total: data.total_found});
                console.log(`Starting stream search for "${searchLocation}", expecting ${data.total_found} stores`);
              }

              if (data.store) {
                // New store received
                const store: Store = data.store;
                allStores.push(store);
                setResults(prev => [...prev, store]);
                setLoadingProgress(prev => ({...prev, found: allStores.length}));
                console.log(`Received store ${data.index}/${data.total}: ${store.name}`);
              }

              if (data.completed) {
                // Search completed
                console.log(`Search completed with ${allStores.length} stores`);
                const searchData = {
                  location: searchLocation,
                  stores: allStores,
                  timestamp: Date.now()
                };
                setSearchResults(searchData);
                setLoading(false);
              }
            } catch (parseErr) {
              console.error('Error parsing streaming data:', parseErr, 'Line:', line);
            }
          }
        }
      }
    } catch (err: any) {
      console.error('Streaming search error:', err);
      setError(err.message || 'An error occurred during streaming search');
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

  const handleAnalyzeCompany = (store: Store) => {
    setAnalysisModal({show: true, store});
  };

  const handleCloseAnalysis = () => {
    setAnalysisModal({show: false, store: null});
  };

  const handleGenerateColdEmail = (store: Store) => {
    const subject = `Partnership Opportunity with ${store.name}`;
    const body = `Dear ${store.name} Team,

I hope this email finds you well. I'm reaching out to explore potential partnership opportunities with your hardware store.

Store Details:
- Name: ${store.name}
- Address: ${store.address}
${store.phone ? `- Phone: ${store.phone}` : ''}
${store.website ? `- Website: ${store.website}` : ''}

I believe there could be mutual benefits in working together. Would you be interested in discussing this further?

Best regards,
[Your Name]
[Your Contact Information]`;

    const mailtoLink = `mailto:${store.email || ''}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.open(mailtoLink, '_blank');
  };

  return (
    <div className="page-container--search">
      {/* API Endpoint Toggle - Top Right */}
      <div style={{position: 'absolute', top: '20px', right: '20px', zIndex: 10}}>
        <div style={{display: 'flex', gap: '6px', alignItems: 'center'}}>
          <span style={{fontSize: '11px', color: 'var(--text-secondary)', marginRight: '6px'}}>
            API:
          </span>
          <button
            onClick={() => setUseLocalAPI(false)}
            className={`btn btn--small ${!useLocalAPI ? 'btn--primary' : 'btn--secondary'}`}
            style={{fontSize: '10px', padding: '3px 6px'}}
            title="Use Production API (Railway)"
          >
            🌐 Prod
          </button>
          <button
            onClick={() => setUseLocalAPI(true)}
            className={`btn btn--small ${useLocalAPI ? 'btn--primary' : 'btn--secondary'}`}
            style={{fontSize: '10px', padding: '3px 6px'}}
            title="Use Local API (localhost:8002)"
          >
            💻 Local
          </button>
        </div>
      </div>
      
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
            {loading ? (
              loadingProgress.total 
                ? `Found ${loadingProgress.found}/${loadingProgress.total} stores...` 
                : 'Searching...'
            ) : 'Search'}
          </button>
        </div>
      </form>


      {loading && loadingProgress.total && (
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{width: `${(loadingProgress.found / loadingProgress.total) * 100}%`}}
            ></div>
          </div>
          <div className="progress-text">
            Loading stores: {loadingProgress.found} of {loadingProgress.total}
          </div>
        </div>
      )}

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
                  <th>Analyze</th>
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
                    <td>
                      <button
                        onClick={() => handleAnalyzeCompany(store)}
                        className="link--website"
                        title="Analyze company information"
                      >
                        AI Analyze
                      </button>
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

      {/* Company Analysis Modal */}
      <CompanyAnalysisModal
        show={analysisModal.show}
        store={analysisModal.store}
        onClose={handleCloseAnalysis}
        onGenerateEmail={handleGenerateColdEmail}
      />

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