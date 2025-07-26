import React, { useState } from 'react';

interface FormData {
  name: string;
  email: string;
  subject: string;
  message: string;
}

const ContactPage: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // For now, just show an alert - in a real app, you'd send this to a backend
    alert('Thank you for your message! We\'ll get back to you soon.');
    setFormData({ name: '', email: '', subject: '', message: '' });
  };


  return (
    <div className="page-container--narrow">
      <h2 className="page-title">Contact Us</h2>
      
      <div className="content-section">
        <p className="text-content">
          Have questions, suggestions, or need help with Hardware Store Finder? 
          We'd love to hear from you! Send us a message and we'll get back to you as soon as possible.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="form-container">
        <div className="form-group">
          <label className="form-label">
            Name *
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            className="form-input"
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            Email *
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            className="form-input"
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            Subject *
          </label>
          <input
            type="text"
            name="subject"
            value={formData.subject}
            onChange={handleInputChange}
            className="form-input"
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            Message *
          </label>
          <textarea
            name="message"
            value={formData.message}
            onChange={handleInputChange}
            rows={6}
            className="form-textarea"
            required
          />
        </div>

        <div className="form-submit">
          <button
            type="submit"
            className="btn btn--primary btn--large"
          >
            Send Message
          </button>
        </div>
      </form>

      <div className="info-box">
        <h3 className="info-box__title">Other Ways to Reach Us</h3>
        <div className="info-box__content">
          <p><strong>Email:</strong> support@hardwarestorefinder.com</p>
          <p><strong>Bug Reports:</strong> Found an issue? Please report it so we can fix it quickly!</p>
          <p><strong>Feature Requests:</strong> Have ideas for new features? We'd love to hear them!</p>
          <p><strong>Feedback:</strong> Your feedback helps us improve our service</p>
        </div>
      </div>

      <div className="info-box--response-time">
        <p className="info-box__text font-small m-0">
          We typically respond within 24 hours during business days.
        </p>
      </div>
    </div>
  );
};

export default ContactPage;