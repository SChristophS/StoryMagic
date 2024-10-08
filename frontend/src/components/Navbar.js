// src/components/Navbar.js

import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';

const Navbar = () => {
  const { currentUser, setAuthToken } = useContext(AppContext);
  const navigate = useNavigate();

  console.log('Navbar gerendert. Aktueller Benutzer:', currentUser);

  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem('authToken');
    navigate('/login');
  };
  
  const handleCreateBook = () => {
    if (currentUser) {
      navigate('/user-info');
    } else {
      navigate('/login');
    }
  };

  return (
    <nav style={styles.navbar}>
      <Link to="/" style={styles.link}>Home</Link>
      {currentUser ? (
        <div style={styles.navItems}>
          <span style={styles.userInfo}>Eingeloggt als {currentUser}</span>
          <button onClick={handleCreateBook} style={styles.button}>Buch erstellen</button>
          <Link to="/my-stories" style={styles.link}>Meine Geschichten</Link>
          <button onClick={handleLogout} style={styles.button}>Abmelden</button>
        </div>
      ) : (
        <div style={styles.navItems}>
          <Link to="/login" style={styles.link}>Anmelden</Link>
          <Link to="/register" style={styles.link}>Registrieren</Link>
        </div>
      )}
    </nav>
  );
};

const styles = {
  navbar: {
    backgroundColor: '#333',
    padding: '10px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  navItems: {
    display: 'flex',
    gap: '15px',
    alignItems: 'center',
  },
  link: {
    color: '#fff',
    textDecoration: 'none',
    fontSize: '1em',
  },
  userInfo: {
    color: '#fff',
  },
  button: {
    backgroundColor: '#555',
    color: '#fff',
    border: 'none',
    padding: '5px 10px',
    cursor: 'pointer',
  },
};

export default Navbar;
