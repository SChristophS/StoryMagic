// src/components/Personalization.js
import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../contexts/AppContext';
import './Personalization.css';

function Personalization() {
  const navigate = useNavigate();
  const { userRole, setUserName, setChildName } = useContext(AppContext);
  const [userNameInput, setUserNameInput] = useState('');
  const [childNameInput, setChildNameInput] = useState('');

  const handleNext = () => {
    if (userNameInput.trim() === '' || childNameInput.trim() === '') {
      alert('Bitte alle Felder ausfüllen');
      return;
    }
    setUserName(userNameInput);
    setChildName(childNameInput);
    navigate('/photo-capture');
  };

  return (
    <div className="personalization-container">
      <h2>Personalisierung</h2>
      <div className="form-group">
        <label>Dein Name ({userRole}):</label>
        <input
          type="text"
          value={userNameInput}
          onChange={(e) => setUserNameInput(e.target.value)}
        />
      </div>
      <div className="form-group">
        <label>Name des Kindes:</label>
        <input
          type="text"
          value={childNameInput}
          onChange={(e) => setChildNameInput(e.target.value)}
        />
      </div>
      <button className="next-button" onClick={handleNext}>
        Weiter
      </button>
    </div>
  );
}

export default Personalization;
