// src/components/UserSelection.js
import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../contexts/AppContext';
import './UserSelection.css';

function UserSelection() {
  const navigate = useNavigate();
  const { setUserRole, setChildAge } = useContext(AppContext);
  const [selectedRole, setSelectedRole] = useState('');
  const [childAgeInput, setChildAgeInput] = useState('');

  const handleRoleSelection = (role) => {
    setSelectedRole(role);
    setUserRole(role);
  };

  const handleNext = () => {
    if (!selectedRole) {
      alert('Bitte wähle deine Rolle aus.');
      return;
    }
    if (!childAgeInput || isNaN(childAgeInput) || childAgeInput <= 0) {
      alert('Bitte gib ein gültiges Alter des Kindes ein.');
      return;
    }
    setChildAge(Number(childAgeInput));
    navigate('/story-selection');
  };

  return (
    <div className="user-selection-container">
      <h2>Wer bist du?</h2>
      <div className="role-buttons">
        <button
          className={selectedRole === 'Oma' ? 'selected' : ''}
          onClick={() => handleRoleSelection('Oma')}
        >
          👵 Oma
        </button>
        <button
          className={selectedRole === 'Opa' ? 'selected' : ''}
          onClick={() => handleRoleSelection('Opa')}
        >
          👴 Opa
        </button>
        <button
          className={selectedRole === 'Mama' ? 'selected' : ''}
          onClick={() => handleRoleSelection('Mama')}
        >
          👩 Mama
        </button>
        <button
          className={selectedRole === 'Papa' ? 'selected' : ''}
          onClick={() => handleRoleSelection('Papa')}
        >
          👨 Papa
        </button>
        <button
          className={selectedRole === 'Tante' ? 'selected' : ''}
          onClick={() => handleRoleSelection('Tante')}
        >
          👩‍🦰 Tante
        </button>
        <button
          className={selectedRole === 'Onkel' ? 'selected' : ''}
          onClick={() => handleRoleSelection('Onkel')}
        >
          👨‍🦱 Onkel
        </button>
      </div>

      <div className="child-age-input">
        <label>Alter des Kindes:</label>
        <input
          type="number"
          min="1"
          value={childAgeInput}
          onChange={(e) => setChildAgeInput(e.target.value)}
        />
      </div>

      <button className="next-button" onClick={handleNext}>
        Weiter
      </button>
    </div>
  );
}

export default UserSelection;
