import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="page-container">
      <h2 className="page-title">About Hardware Store Finder</h2>
      
      <div className="content-section">
        <h3 className="section-title">What We Do</h3>
        <p className="text-content">
          Hardware Store Finder helps you locate hardware stores in any area using the Google Places API. 
          Simply enter a location, and we'll provide you with a comprehensive list of nearby hardware stores 
          complete with contact information and websites.
        </p>
      </div>

      <div className="content-section">
        <h3 className="section-title">Features</h3>
        <ul className="text-list">
          <li>Search hardware stores by location</li>
          <li>Accurate location-based results</li>
          <li>Phone numbers and contact information</li>
          <li>Direct website links with preview</li>
          <li>Mobile-friendly interface</li>
          <li>Fast and reliable search results</li>
        </ul>
      </div>

      <div className="content-section">
        <h3 className="section-title">How It Works</h3>
        <div className="text-content">
          <p><strong>1. Enter Location:</strong> Type in any city, address, or landmark</p>
          <p><strong>2. Search:</strong> Our system uses Google Places API to find hardware stores</p>
          <p><strong>3. Browse Results:</strong> View detailed information for each store</p>
          <p><strong>4. Connect:</strong> Call directly or visit their website</p>
        </div>
      </div>

      <div className="content-section">
        <h3 className="section-title">Technology</h3>
        <p className="text-content">
          Built with modern web technologies including React for the frontend and FastAPI for the backend, 
          integrated with Google Places API for accurate and up-to-date business information.
        </p>
      </div>

      <div className="info-box--centered">
        <h3 className="info-box__title">Ready to Find Hardware Stores?</h3>
        <p className="info-box__text">
          Start your search now and discover hardware stores in your area.
        </p>
        <a href="/" className="link--cta">
          Start Searching →
        </a>
      </div>
    </div>
  );
};

export default AboutPage;