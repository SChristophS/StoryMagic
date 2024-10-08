// src/components/WelcomePage.js

import React, { useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AppContext } from '../context/AppContext';

const WelcomePage = () => {
  const navigate = useNavigate();
  const { currentUser } = useContext(AppContext);
	console.log(currentUser)

  const handleCreateBook = () => {
    if (currentUser) {
      navigate('/user-info');
    } else {
      navigate('/login');
    }
  };

  return (
    <div>
      <h1>Willkommen bei StoryMagic</h1>
      {currentUser ? (
        <div>
          <p>Hallo, {currentUser}!</p>
          <button onClick={handleCreateBook}>Buch erstellen</button>
          <Link to="/my-stories">Vorhandenes Buch laden</Link>
        </div>
      ) : (
        <div>
          <p>Bitte melde dich an oder registriere dich, um fortzufahren.</p>
          <Link to="/login">Anmelden</Link>
          <Link to="/register">Registrieren</Link>
        </div>
      )}
    </div>
  );
};

export default WelcomePage;
