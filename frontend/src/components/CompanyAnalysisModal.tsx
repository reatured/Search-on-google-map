import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Store, useSearchContext } from '../context/SearchContext';

// Email template - will be replaced with backend API call in the future
const EMAIL_TEMPLATE = {
  subject: `High-Quality Hardware Products – Let's Connect for a Supply Partnership`,
  body: `Hi [Store Owner/Manager Name],

My name is [Your Name], and I'm reaching out on behalf of James Hardware, a family-owned hardware manufacturing and export company established in 1995. We specialize in high-quality home decoration hardware—including door handles, hooks, brackets, and bathroom accessories—and have been supplying wholesalers and distributors across Europe and the Middle East for nearly 30 years.

We're currently expanding our B2B network and would love to explore a potential partnership with {STORE_NAME}. Our products are known for their durability, refined finishes, and competitive pricing—perfect for retailers seeking reliable, stylish, and margin-friendly hardware options.

Store Information:
- Name: {STORE_NAME}
- Address: {STORE_ADDRESS}
{STORE_PHONE}
{STORE_WEBSITE}

Here's what we offer:

• A wide range of zinc alloy, brass, and stainless steel hardware
• Customization services with your branding or packaging  
• Low MOQs and dependable bulk fulfillment
• Strong track record with EU compliance and quality control

I'd be happy to send over a product catalog or samples for your review. Would you be open to a quick chat or email follow-up?

Looking forward to hearing from you!

Best regards,
[Your Full Name]
James Hardware
🌐 jameshardwarecn.com
✉️ [your email] | 📞 [your phone]`
};

// Fallback company analysis template - used when AI analysis is not available
const FALLBACK_ANALYSIS_TEMPLATE = {
  analysisPoints: [
    'Location-based market analysis',
    'Potential partnership opportunities', 
    'Business size estimation',
    'Contact strategy recommendations'
  ],
  nextSteps: [
    'Research company background',
    'Analyze local market presence',
    'Identify decision makers',
    'Prepare partnership proposal'
  ]
};

interface CompanyAnalysisModalProps {
  show: boolean;
  store: Store | null;
  onClose: () => void;
  onGenerateEmail: (store: Store) => void;
}

// localStorage functions for saving/loading analysis data
const getStorageKey = (store: Store) => `analysis_${store.name}_${store.address}`;

const saveAnalysisToStorage = (store: Store, analysisData: any, hasAI: boolean = false) => {
  try {
    const key = getStorageKey(store);
    const dataToSave = {
      ...analysisData,
      hasAIAnalysis: hasAI,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem(key, JSON.stringify(dataToSave));
  } catch (error) {
    console.error('Error saving analysis to localStorage:', error);
  }
};

const loadAnalysisFromStorage = (store: Store) => {
  try {
    const key = getStorageKey(store);
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Error loading analysis from localStorage:', error);
    return null;
  }
};

const CompanyAnalysisModal: React.FC<CompanyAnalysisModalProps> = ({
  show,
  store,
  onClose,
  onGenerateEmail
}) => {
  const [showEmailSection, setShowEmailSection] = React.useState(false);
  const [emailSubject, setEmailSubject] = React.useState('');
  const [emailContent, setEmailContent] = React.useState('');
  const [analysisData, setAnalysisData] = React.useState<any>(null);
  const [loadingAnalysis, setLoadingAnalysis] = React.useState(false);
  const [loadingEmail, setLoadingEmail] = React.useState(false);
  const [analysisError, setAnalysisError] = React.useState<string | null>(null);
  const [emailError, setEmailError] = React.useState<string | null>(null);
  const [hasAIAnalysis, setHasAIAnalysis] = React.useState(false);
  const [language, setLanguage] = React.useState<'english' | 'chinese'>('english');
  const [emailLanguage, setEmailLanguage] = React.useState<'english' | 'chinese'>('english');
  const [chineseAnalysis, setChineseAnalysis] = React.useState<string | null>(null);
  const [loadingChinese, setLoadingChinese] = React.useState(false);
  const modalRef = React.useRef<HTMLDivElement>(null);
  const { getAPIEndpoint } = useSearchContext();


  // API call for company analysis with streaming
  const fetchCompanyAnalysis = React.useCallback(async () => {
    if (!store) return;
    
    setLoadingAnalysis(true);
    setAnalysisError(null);
    
    try {
      const response = await fetch(
        `${getAPIEndpoint()}/api/analyze-company/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: store.name,
            address: store.address,
            phone: store.phone,
            website: store.website,
            language: language
          })
        }
      );

      if (!response.ok) {
        throw new Error('Backend endpoint not available');
      }

      // Initialize analysis data with basic info
      const initialData = {
        basicInfo: {
          name: store.name,
          address: store.address,
          phone: store.phone,
          website: store.website
        },
        perplexityAnalysis: '',
        analysisPoints: [],
        nextSteps: [],
        productCategories: []
      };
      setAnalysisData(initialData);
      setHasAIAnalysis(true);

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let streamedContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));
                
                if (data.error) {
                  console.error('Streaming error:', data.error);
                  setAnalysisError(data.error);
                  break;
                }
                
                if (data.type === 'content') {
                  streamedContent += data.content;
                  // Update the analysis data with streaming content
                  setAnalysisData(prev => ({
                    ...prev,
                    perplexityAnalysis: streamedContent
                  }));
                } else if (data.type === 'complete') {
                  // Final complete data
                  setAnalysisData(data.data);
                  saveAnalysisToStorage(store, data.data, true);
                } else if (data.status) {
                  // Status updates (optional: could show these to user)
                  console.log('Analysis status:', data.message);
                }
              } catch (e) {
                // Ignore malformed JSON lines
                console.warn('Failed to parse streaming data:', line);
              }
            }
          }
        }
      }
    } catch (error) {
      console.log('Using fallback analysis data');
      // Fallback to default analysis when backend is not ready
      const fallbackData = {
        basicInfo: {
          name: store.name,
          address: store.address,
          phone: store.phone,
          website: store.website
        },
        perplexityAnalysis: null
      };
      setAnalysisData(fallbackData);
      setHasAIAnalysis(false);
      saveAnalysisToStorage(store, fallbackData, false);
    } finally {
      setLoadingAnalysis(false);
    }
  }, [store, language]);

  // API call for Chinese company analysis with streaming
  const fetchChineseAnalysis = React.useCallback(async () => {
    if (!store) return;
    
    setLoadingChinese(true);
    setChineseAnalysis('');
    
    try {
      const response = await fetch(
        `${getAPIEndpoint()}/api/analyze-company/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: store.name,
            address: store.address,
            phone: store.phone,
            website: store.website,
            language: 'chinese'
          })
        }
      );

      if (!response.ok) {
        throw new Error('Backend endpoint not available');
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let streamedContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));
                
                if (data.error) {
                  console.error('Chinese streaming error:', data.error);
                  setChineseAnalysis('Chinese analysis not available. Please try again later.');
                  break;
                }
                
                if (data.type === 'content') {
                  streamedContent += data.content;
                  setChineseAnalysis(streamedContent);
                } else if (data.type === 'complete') {
                  // Final complete data
                  setChineseAnalysis(data.data.perplexityAnalysis);
                  // Save Chinese analysis to localStorage
                  if (store) {
                    const storageKey = `${getStorageKey(store)}_chinese`;
                    localStorage.setItem(storageKey, JSON.stringify({
                      analysis: data.data.perplexityAnalysis,
                      timestamp: new Date().toISOString()
                    }));
                  }
                } else if (data.status) {
                  console.log('Chinese analysis status:', data.message);
                }
              } catch (e) {
                console.warn('Failed to parse Chinese streaming data:', line);
              }
            }
          }
        }
      }
    } catch (error) {
      console.log('Chinese analysis failed:', error);
      setChineseAnalysis('Chinese analysis not available. Please try again later.');
    } finally {
      setLoadingChinese(false);
    }
  }, [store]);

  // API call for email generation
  const fetchEmailGeneration = React.useCallback(async () => {
    if (!store) return;
    
    setLoadingEmail(true);
    setEmailError(null);
    
    try {
      const response = await fetch(
        `${getAPIEndpoint()}/api/generate-email`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            store: {
              name: store.name,
              address: store.address,
              phone: store.phone,
              website: store.website
            },
            analysis: analysisData,
            language: emailLanguage
          })
        }
      );

      if (!response.ok) {
        throw new Error('Backend endpoint not available');
      }

      const data = await response.json();
      console.log('Email Generation Response:', data);
      setEmailSubject(data.subject);
      setEmailContent(data.body);
    } catch (error) {
      console.log('Using fallback email template');
      // Fallback to template when backend is not ready
      const subject = EMAIL_TEMPLATE.subject;
      const body = EMAIL_TEMPLATE.body
        .replace(/{STORE_NAME}/g, store.name)
        .replace(/{STORE_ADDRESS}/g, store.address)
        .replace(/{STORE_PHONE}/g, store.phone ? `- Phone: ${store.phone}` : '')
        .replace(/{STORE_WEBSITE}/g, store.website ? `- Website: ${store.website}` : '');
      
      setEmailSubject(subject);
      setEmailContent(body);
    } finally {
      setLoadingEmail(false);
    }
  }, [store, analysisData, emailLanguage]);

  const handleGenerateEmail = async () => {
    setShowEmailSection(true);
    await fetchEmailGeneration();
  };

  const handleSendEmail = () => {
    if (store) {
      onGenerateEmail(store);
    }
    onClose();
  };

  // Handle click outside to close modal
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
      }
    };
    
    if (show) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [show, onClose]);

  // Handle language switching
  const handleLanguageSwitch = (newLang: 'english' | 'chinese') => {
    setLanguage(newLang);
    if (newLang === 'chinese' && !chineseAnalysis && hasAIAnalysis) {
      // Check localStorage for Chinese analysis first
      if (store) {
        const storageKey = `${getStorageKey(store)}_chinese`;
        const cached = localStorage.getItem(storageKey);
        if (cached) {
          const parsedCache = JSON.parse(cached);
          setChineseAnalysis(parsedCache.analysis);
        } else {
          fetchChineseAnalysis();
        }
      }
    }
  };

  // Load company analysis when modal opens
  React.useEffect(() => {
    if (show && store) {
      // First check localStorage for cached analysis
      const cachedAnalysis = loadAnalysisFromStorage(store);
      if (cachedAnalysis) {
        setAnalysisData(cachedAnalysis);
        setHasAIAnalysis(cachedAnalysis.hasAIAnalysis || false);
        
        // Load Chinese analysis if available
        const chineseStorageKey = `${getStorageKey(store)}_chinese`;
        const cachedChinese = localStorage.getItem(chineseStorageKey);
        if (cachedChinese) {
          const parsedChinese = JSON.parse(cachedChinese);
          setChineseAnalysis(parsedChinese.analysis);
        }
      } else {
        // If no cached data, fetch from API
        fetchCompanyAnalysis();
      }
    }
  }, [show, store, fetchCompanyAnalysis]);

  if (!show || !store) {
    return null;
  }

  return (
    <div className="modal-overlay">
      <div ref={modalRef} className={`modal-content modal-content--analysis ${showEmailSection ? 'modal-content--wide' : ''}`}>
        <div className="modal-controls">
          <button 
            onClick={onClose} 
            className="btn--modal-close"
          >
            ✕
          </button>
        </div>
        
        <div className={`analysis-container ${showEmailSection ? 'analysis-container--split' : ''}`}>
          <div className={`analysis-content ${showEmailSection ? 'analysis-content--scrollable' : ''}`}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
            <div style={{textAlign: 'left'}}>
              <p style={{fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 'normal'}}>Company Analysis</p>
              <h2 style={{fontSize: '24px', fontWeight: 'bold', color: 'var(--text-primary)', margin: '0'}}>{store.name}</h2>
            </div>
              <div style={{display: 'flex', gap: '8px', alignItems: 'center'}}>
                {/* Language Toggle */}
                {hasAIAnalysis && (
                  <div style={{display: 'flex', gap: '8px'}}>
                    <button
                      onClick={() => handleLanguageSwitch('english')}
                      className={`btn btn--small ${language === 'english' ? 'btn--primary' : 'btn--secondary'}`}
                      style={{fontSize: '12px', padding: '6px 12px', minWidth: '70px', height: '32px'}}
                    >
                      English
                    </button>
                    <button
                      onClick={() => handleLanguageSwitch('chinese')}
                      className={`btn btn--small ${language === 'chinese' ? 'btn--primary' : 'btn--secondary'}`}
                      style={{fontSize: '12px', padding: '6px 12px', minWidth: '70px', height: '32px'}}
                      disabled={loadingChinese}
                    >
                      {loadingChinese ? '📡' : '中文'}
                    </button>
                  </div>
                )}
              </div>
            </div>
            
            {loadingAnalysis ? (
              <div className="loading-section">
                <p>Analyzing company information...</p>
                {analysisData?.perplexityAnalysis && (
                  <div style={{marginTop: '16px', padding: '12px', backgroundColor: 'var(--bg-accent)', borderRadius: '8px'}}>
                    <p style={{fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px'}}>
                      ✨ Streaming analysis results...
                    </p>
                    <div style={{lineHeight: '1.6', fontSize: '14px'}}>
                      {analysisData.perplexityAnalysis}
                      <span className="streaming-cursor">|</span>
                    </div>
                  </div>
                )}
              </div>
            ) : analysisData ? (
              <>
                <div className="analysis-section">
                  <h3>Basic Information</h3>
                  <ul>
                    <li><strong>Name:</strong> {analysisData.basicInfo?.name || store.name}</li>
                    <li><strong>Address:</strong> {analysisData.basicInfo?.address || store.address}</li>
                    {(analysisData.basicInfo?.phone || store.phone) && (
                      <li><strong>Phone:</strong> {analysisData.basicInfo?.phone || store.phone}</li>
                    )}
                    {(analysisData.basicInfo?.website || store.website) && (
                      <li>
                        <strong>Website:</strong>{' '}
                        <a 
                          href={analysisData.basicInfo?.website || store.website} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          {analysisData.basicInfo?.website || store.website}
                        </a>
                      </li>
                    )}
                  </ul>
                </div>

                {hasAIAnalysis && (analysisData.perplexityAnalysis || chineseAnalysis) ? (
                  <div className="analysis-section">
                    <h3>
                      {language === 'chinese' ? 'AI 市场分析' : 'AI Market Analysis'}
                      {loadingChinese && language === 'chinese' && (
                        <span style={{marginLeft: '8px', fontSize: '14px', color: 'var(--text-secondary)'}}>
                          ✨ Streaming...
                        </span>
                      )}
                    </h3>
                    <div className="ai-analysis-content" style={{lineHeight: '1.6'}}>
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          p: ({ children }) => <p style={{ marginBottom: '12px', lineHeight: '1.6' }}>{children}</p>,
                          ul: ({ children }) => <ul style={{ marginBottom: '12px', paddingLeft: '20px' }}>{children}</ul>,
                          ol: ({ children }) => <ol style={{ marginBottom: '12px', paddingLeft: '20px' }}>{children}</ol>,
                          li: ({ children }) => <li style={{ marginBottom: '4px' }}>{children}</li>,
                          h1: ({ children }) => <h1 style={{ marginBottom: '12px', marginTop: '20px', fontSize: '1.5em', fontWeight: 'bold' }}>{children}</h1>,
                          h2: ({ children }) => <h2 style={{ marginBottom: '10px', marginTop: '18px', fontSize: '1.3em', fontWeight: 'bold' }}>{children}</h2>,
                          h3: ({ children }) => <h3 style={{ marginBottom: '8px', marginTop: '16px', fontSize: '1.2em', fontWeight: 'bold' }}>{children}</h3>,
                          h4: ({ children }) => <h4 style={{ marginBottom: '6px', marginTop: '14px', fontSize: '1.1em', fontWeight: 'bold' }}>{children}</h4>,
                          table: ({ children }) => (
                            <table style={{ 
                              width: '100%', 
                              borderCollapse: 'collapse', 
                              marginBottom: '16px',
                              border: '1px solid var(--border-color)'
                            }}>
                              {children}
                            </table>
                          ),
                          thead: ({ children }) => (
                            <thead style={{ backgroundColor: 'var(--bg-accent)' }}>
                              {children}
                            </thead>
                          ),
                          th: ({ children }) => (
                            <th style={{ 
                              padding: '8px 12px', 
                              border: '1px solid var(--border-color)',
                              fontWeight: 'bold',
                              textAlign: 'left'
                            }}>
                              {children}
                            </th>
                          ),
                          td: ({ children }) => (
                            <td style={{ 
                              padding: '8px 12px', 
                              border: '1px solid var(--border-color)'
                            }}>
                              {children}
                            </td>
                          ),
                          a: ({ children, href }) => (
                            <a 
                              href={href} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              style={{ 
                                color: 'var(--accent-color)', 
                                textDecoration: 'none',
                                fontWeight: 'bold'
                              }}
                            >
                              {children}
                            </a>
                          ),
                          blockquote: ({ children }) => (
                            <blockquote style={{ 
                              borderLeft: '4px solid var(--accent-color)',
                              paddingLeft: '16px',
                              marginLeft: '0',
                              marginBottom: '12px',
                              fontStyle: 'italic',
                              backgroundColor: 'var(--bg-accent)',
                              padding: '12px 16px',
                              borderRadius: '4px'
                            }}>
                              {children}
                            </blockquote>
                          )
                        }}
                      >
                        {language === 'chinese' && chineseAnalysis 
                          ? chineseAnalysis + (loadingChinese ? ' ▋' : '')
                          : analysisData.perplexityAnalysis + (loadingAnalysis && analysisData.perplexityAnalysis ? ' ▋' : '')
                        }
                      </ReactMarkdown>
                    </div>
                  </div>
                ) : (
                  !hasAIAnalysis && (
                    <>
                      <div className="analysis-section">
                        <h3>Analysis Points</h3>
                        <ul>
                          {FALLBACK_ANALYSIS_TEMPLATE.analysisPoints.map((point: string, idx: number) => (
                            <li key={idx}>{point}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="analysis-section">
                        <h3>Next Steps</h3>
                        <ol>
                          {FALLBACK_ANALYSIS_TEMPLATE.nextSteps.map((step: string, idx: number) => (
                            <li key={idx}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    </>
                  )
                )}
              </>
            ) : (
              <div className="error-section">
                <p>Unable to load company analysis.</p>
              </div>
            )}

            <div className="analysis-footer">
              <p><em>This analysis can help inform your outreach strategy.</em></p>
              <div style={{display: 'flex', gap: '10px', justifyContent: 'center', marginTop: '15px'}}>
                <button
                  onClick={() => {
                    setAnalysisData(null);
                    setHasAIAnalysis(false);
                    setChineseAnalysis(null);
                    setLanguage('english');
                    fetchCompanyAnalysis();
                  }}
                  className="btn btn--secondary"
                  disabled={loadingAnalysis}
                >
                  {loadingAnalysis ? 'Refreshing...' : 'Refresh Analysis'}
                </button>
                {!showEmailSection && (
                  <button
                    onClick={handleGenerateEmail}
                    className="btn btn--primary"
                    disabled={loadingAnalysis}
                  >
                    Generate Cold Email
                  </button>
                )}
              </div>
            </div>
          </div>

          {showEmailSection && (
            <div className={`email-section email-section--scrollable ${loadingEmail ? 'email-section--loading' : ''}`}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
                <h3>Generated Cold Email</h3>
                <div style={{display: 'flex', gap: '8px', alignItems: 'center'}}>
                  {/* Email Language Toggle */}
                  <span style={{fontSize: '12px', color: 'var(--text-secondary)', marginRight: '8px'}}>
                    Language:
                  </span>
                  <button
                    onClick={() => setEmailLanguage('english')}
                    className={`btn btn--small ${emailLanguage === 'english' ? 'btn--primary' : 'btn--secondary'}`}
                    style={{fontSize: '12px', padding: '6px 12px', minWidth: '70px', height: '32px'}}
                    disabled={loadingEmail}
                  >
                    English
                  </button>
                  <button
                    onClick={() => setEmailLanguage('chinese')}
                    className={`btn btn--small ${emailLanguage === 'chinese' ? 'btn--primary' : 'btn--secondary'}`}
                    style={{fontSize: '12px', padding: '6px 12px', minWidth: '70px', height: '32px'}}
                    disabled={loadingEmail}
                  >
                    中文
                  </button>
                </div>
              </div>
              
              {loadingEmail ? (
                <div className="loading-section">
                  <p>Generating personalized email...</p>
                </div>
              ) : (
                <div className="email-form">
                  <div className="subject-section">
                    <label htmlFor="email-subject" className="email-label">Subject:</label>
                    <input
                      id="email-subject"
                      type="text"
                      value={emailSubject}
                      onChange={(e) => setEmailSubject(e.target.value)}
                      className="email-subject-input"
                      placeholder="Email subject..."
                      disabled={loadingEmail}
                    />
                  </div>
                  
                  <div className="email-body-section">
                    <label htmlFor="email-body" className="email-label">Email Body:</label>
                    <textarea
                      id="email-body"
                      value={emailContent}
                      onChange={(e) => setEmailContent(e.target.value)}
                      className="email-textarea"
                      placeholder="Generated email content will appear here..."
                      disabled={loadingEmail}
                    />
                  </div>
                  
                  <div className="email-actions">
                    <button
                      onClick={fetchEmailGeneration}
                      className="btn btn--secondary"
                      disabled={loadingEmail}
                    >
                      {loadingEmail ? 'Regenerating...' : 'Regenerate Email'}
                    </button>
                    <button
                      onClick={() => {
                        const fullEmail = `Subject: ${emailSubject}\n\n${emailContent}`;
                        navigator.clipboard.writeText(fullEmail);
                      }}
                      className="btn btn--primary"
                    >
                      Copy to Clipboard
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanyAnalysisModal;