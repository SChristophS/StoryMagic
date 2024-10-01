// src/components/Home.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

function Home() {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate('/user-selection');
  };

  return (
    <div className="home-container">
      <h1>Willkommen bei FamilienbuchZauber</h1>
      <p>Erstelle dein persönliches Kinderbuch in wenigen Schritten!</p>
      <button className="start-button" onClick={handleStart}>
        Jetzt starten
      </button>
    </div>
  );
}

export default Home;
