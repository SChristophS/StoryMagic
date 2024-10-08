// src/App.js

import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import Routes from './routes';
import { AppProvider } from './context/AppContext';
import { useContext } from 'react';

function App() {
	const { currentUser, setAuthToken } = useContext(AppContext);

	const handleLogout = () => {
		setAuthToken(null);
		localStorage.removeItem('authToken');
	};
  
  return (
    <AppProvider>
      <Router>
        <div>
          {currentUser ? (
            <div>
              Eingeloggt als {currentUser}
              <button onClick={handleLogout}>Abmelden</button>
            </div>
          ) : (
            <div>
              <Link to="/login">Anmelden</Link>
              <Link to="/register">Registrieren</Link>
            </div>
          )}
          <Routes />
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;
