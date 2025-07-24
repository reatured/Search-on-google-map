import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface Store {
  name: string;
  address: string;
  phone?: string;
  website?: string;
  email?: string;
}

export interface SearchResults {
  location: string;
  stores: Store[];
  timestamp: number;
}

interface SearchContextType {
  searchResults: SearchResults | null;
  setSearchResults: (results: SearchResults | null) => void;
  clearSearchResults: () => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const useSearchContext = () => {
  const context = useContext(SearchContext);
  if (context === undefined) {
    throw new Error('useSearchContext must be used within a SearchProvider');
  }
  return context;
};

interface SearchProviderProps {
  children: ReactNode;
}

export const SearchProvider: React.FC<SearchProviderProps> = ({ children }) => {
  const [searchResults, setSearchResultsState] = useState<SearchResults | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('hardwareStoreSearchResults');
      if (saved) {
        const parsed = JSON.parse(saved) as SearchResults;
        // Only load if less than 1 hour old
        if (Date.now() - parsed.timestamp < 60 * 60 * 1000) {
          setSearchResultsState(parsed);
        } else {
          localStorage.removeItem('hardwareStoreSearchResults');
        }
      }
    } catch (error) {
      console.error('Error loading search results from localStorage:', error);
      localStorage.removeItem('hardwareStoreSearchResults');
    }
  }, []);

  const setSearchResults = (results: SearchResults | null) => {
    setSearchResultsState(results);
    if (results) {
      try {
        localStorage.setItem('hardwareStoreSearchResults', JSON.stringify(results));
      } catch (error) {
        console.error('Error saving search results to localStorage:', error);
      }
    } else {
      localStorage.removeItem('hardwareStoreSearchResults');
    }
  };

  const clearSearchResults = () => {
    setSearchResultsState(null);
    localStorage.removeItem('hardwareStoreSearchResults');
  };

  return (
    <SearchContext.Provider value={{ searchResults, setSearchResults, clearSearchResults }}>
      {children}
    </SearchContext.Provider>
  );
};