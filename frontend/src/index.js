// src/index.js

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './routes'; // Importiere AppRoutes statt Routes
import { AppProvider } from './context/AppContext'; // Benannter Import
import ErrorBoundary from './components/ErrorBoundary'; // Optional: Error Boundary
import './styles.css';

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <AppProvider>
        <ErrorBoundary>
          <AppRoutes />
        </ErrorBoundary>
      </AppProvider>
    </BrowserRouter>
  </React.StrictMode>
);
