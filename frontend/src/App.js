// src/App.js

import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import Routes from './routes';
import { AppProvider } from './context/AppContext';

function App() {
  return (
    <AppProvider>
      <Router>
        <Routes />
      </Router>
    </AppProvider>
  );
}

export default App;
