// src/components/UserInfoForm.js

import React, { useState, useContext } from 'react';
import { AppContext } from '../context/AppContext';
import { useNavigate  } from 'react-router-dom';

const UserInfoForm = () => {
  const { userInfo, setUserInfo } = useContext(AppContext);
  const [role, setRole] = useState(userInfo.role || '');
  const [childAge, setChildAge] = useState(userInfo.childAge || '');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setUserInfo({ role, childAge });
    console.debug('Benutzerinformationen gesetzt:', { role, childAge });
    navigate('/stories');
  };

  return (
    <div>
      <h1>Informationen eingeben</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Wer bist du?
          <select value={role} onChange={(e) => setRole(e.target.value)} required>
            <option value="" disabled>
              Bitte auswählen
            </option>
            <option value="Mama">Mama</option>
            <option value="Papa">Papa</option>
            <option value="Oma">Oma</option>
            <option value="Opa">Opa</option>
            <option value="Tante">Tante</option>
            <option value="Onkel">Onkel</option>
            <option value="Freund">Freund</option>
          </select>
        </label>
        <label>
          Alter des Kindes:
          <input
            type="number"
            value={childAge}
            onChange={(e) => setChildAge(e.target.value)}
            min="0"
            max="18"
            required
          />
        </label>
        <button type="submit">Weiter</button>
      </form>
    </div>
  );
};

export default UserInfoForm;
