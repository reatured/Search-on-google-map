import React from 'react';
import { Store } from '../context/SearchContext';

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

interface CompanyAnalysisModalProps {
  show: boolean;
  store: Store | null;
  onClose: () => void;
  onGenerateEmail: (store: Store) => void;
}

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

  // API call for company analysis
  const fetchCompanyAnalysis = React.useCallback(async () => {
    if (!store) return;
    
    setLoadingAnalysis(true);
    setAnalysisError(null);
    
    try {
      const response = await fetch(
        `https://search-on-google-map-production.up.railway.app/api/analyze-company`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: store.name,
            address: store.address,
            phone: store.phone,
            website: store.website
          })
        }
      );

      if (!response.ok) {
        throw new Error('Backend endpoint not available');
      }

      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.log('Using fallback analysis data');
      // Fallback to default analysis when backend is not ready
      setAnalysisData({
        basicInfo: {
          name: store.name,
          address: store.address,
          phone: store.phone,
          website: store.website
        },
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
      });
    } finally {
      setLoadingAnalysis(false);
    }
  }, [store]);

  // API call for email generation
  const fetchEmailGeneration = React.useCallback(async () => {
    if (!store) return;
    
    setLoadingEmail(true);
    setEmailError(null);
    
    try {
      const response = await fetch(
        `https://search-on-google-map-production.up.railway.app/api/generate-email`,
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
            analysis: analysisData
          })
        }
      );

      if (!response.ok) {
        throw new Error('Backend endpoint not available');
      }

      const data = await response.json();
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
  }, [store, analysisData]);

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

  // Load company analysis when modal opens
  React.useEffect(() => {
    if (show && store && !analysisData) {
      fetchCompanyAnalysis();
    }
  }, [show, store, analysisData, fetchCompanyAnalysis]);

  if (!show || !store) {
    return null;
  }

  return (
    <div className="modal-overlay">
      <div className={`modal-content modal-content--analysis ${showEmailSection ? 'modal-content--wide' : ''}`}>
        <div className="modal-controls">
          <button 
            onClick={onClose} 
            className="btn--modal-close"
          >
            ✕
          </button>
        </div>
        
        <div className={`analysis-container ${showEmailSection ? 'analysis-container--split' : ''}`}>
          <div className="analysis-content">
            <h2>Company Analysis - {store.name}</h2>
            
            {loadingAnalysis ? (
              <div className="loading-section">
                <p>Analyzing company information...</p>
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

                {analysisData.analysisPoints && (
                  <div className="analysis-section">
                    <h3>Analysis Points</h3>
                    <ul>
                      {analysisData.analysisPoints.map((point: string, idx: number) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {analysisData.nextSteps && (
                  <div className="analysis-section">
                    <h3>Next Steps</h3>
                    <ol>
                      {analysisData.nextSteps.map((step: string, idx: number) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}

                {analysisData.perplexityAnalysis && (
                  <div className="analysis-section">
                    <h3>AI Analysis</h3>
                    <div className="ai-analysis-content">
                      {analysisData.perplexityAnalysis}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="error-section">
                <p>Unable to load company analysis.</p>
              </div>
            )}

            <div className="analysis-footer">
              <p><em>This analysis can help inform your outreach strategy.</em></p>
              {!showEmailSection ? (
                <button
                  onClick={handleGenerateEmail}
                  className="btn btn--primary"
                  style={{marginTop: '15px'}}
                  disabled={loadingAnalysis}
                >
                  Generate Cold Email
                </button>
              ) : (
                <button
                  onClick={handleSendEmail}
                  className="btn btn--primary"
                  style={{marginTop: '15px'}}
                >
                  Send Email
                </button>
              )}
            </div>
          </div>

          {showEmailSection && (
            <div className="email-section">
              <h3>Generated Cold Email</h3>
              
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
                    />
                  </div>
                  
                  <div className="email-actions">
                    <button
                      onClick={() => {
                        const fullEmail = `Subject: ${emailSubject}\n\n${emailContent}`;
                        navigator.clipboard.writeText(fullEmail);
                      }}
                      className="btn btn--secondary"
                    >
                      Copy to Clipboard
                    </button>
                    <button
                      onClick={handleSendEmail}
                      className="btn btn--primary"
                    >
                      Open in Email Client
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