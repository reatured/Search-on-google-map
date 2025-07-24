import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useSearchContext, Store } from '../context/SearchContext';

const ResultsPage: React.FC = () => {
  const navigate = useNavigate();
  const { searchResults } = useSearchContext();
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [iframeError, setIframeError] = useState<boolean>(false);

  const results = useMemo(() => searchResults?.stores || [], [searchResults?.stores]);
  const searchLocation = useMemo(() => searchResults?.location || '', [searchResults?.location]);

  useEffect(() => {
    if (!searchResults || !results.length) {
      navigate('/');
    }
  }, [searchResults, results, navigate]);

  useEffect(() => {
    if (iframeError && previewUrl) {
      window.open(previewUrl, '_blank', 'noopener,noreferrer');
      setPreviewUrl(null);
      setIframeError(false);
    }
  }, [iframeError, previewUrl]);

  const handleWebsiteClick = (url: string, e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    setPreviewUrl(url);
    setIframeError(false);
  };

  const handleClosePreview = () => {
    setPreviewUrl(null);
    setIframeError(false);
  };

  if (!results.length) {
    return (
      <div className="no-results">
        <h2 className="no-results__title">No Results Found</h2>
        <p className="no-results__text">No search results to display.</p>
        <Link to="/" className="link--back">
          ← Back to Search
        </Link>
      </div>
    );
  }

  return (
    <div className="page-container--results">
      <div className="results-header">
        <h2 className="results-title">Hardware Stores near "{searchLocation}"</h2>
        <p className="results-count">Found {results.length} store{results.length !== 1 ? 's' : ''}</p>
        <Link to="/" className="link--back">
          ← Search Again
        </Link>
      </div>

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
    </div>
  );
};

export default ResultsPage;