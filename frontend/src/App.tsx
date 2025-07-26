import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import './styles/global.css';
import Layout from './Layout';
import SearchPage from './pages/SearchPage';
import ResultsPage from './pages/ResultsPage';
import AboutPage from './pages/AboutPage';
import { SearchProvider } from './context/SearchContext';

function App() {
  return (
    <SearchProvider>
      <Router basename="/Search-on-google-map">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<SearchPage />} />
            <Route path="results" element={<ResultsPage />} />
            <Route path="about" element={<AboutPage />} />

          </Route>
        </Routes>
      </Router>
    </SearchProvider>
  );
}

export default App;