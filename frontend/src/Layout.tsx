import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useSearchContext } from './context/SearchContext';

interface NavItem {
  path: string;
  label: string;
}

const Layout: React.FC = () => {
  const location = useLocation();
  const { searchResults } = useSearchContext();

  const navItems: NavItem[] = [
    { path: '/', label: 'Search' },
    ...(searchResults ? [{ path: '/results', label: `Results (${searchResults.stores.length})` }] : []),
    { path: '/about', label: 'About' },

  ];


  return (
    <div className="App layout-container">
      <header className="App-header">
        <nav className="layout-nav">
          <div className="nav-container">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </nav>
      </header>
      
      <main className="layout-main">
        <Outlet />
      </main>
      
      <footer className="layout-footer">
        <div className="footer-info">
          <span>v3.0</span>
          <span>Powered by Google Places API</span>
          <span>Built with React & FastAPI</span>
        </div>
        <div className="footer-copyright">
          © 2024 Hardware Store Finder. 
        </div>
      </footer>
    </div>
  );
};

export default Layout;