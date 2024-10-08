// src/components/WelcomePage.js

import React from 'react';
import { useNavigate  } from 'react-router-dom';

const WelcomePage = () => {
  const navigate = useNavigate();

  const handleCreateBook = () => {
	navigate('/user-info');
  };

  return (
    <div>
      <h1>Willkommen bei StoryMagic</h1>
      <button onClick={handleCreateBook}>Buch erstellen</button>
    </div>
  );
};

export default WelcomePage;
