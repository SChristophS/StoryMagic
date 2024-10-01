// src/components/Preview.js
import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../contexts/AppContext';
import './Preview.css';

function Preview() {
  const navigate = useNavigate();
  const { userName, childName, photo, story } = useContext(AppContext);

  const handleOrder = () => {
    navigate('/order');
  };

  return (
    <div className="preview-container">
      <h2>Vorschau deines Buches</h2>
      <div className="book-preview">
        <h3>{story.title}</h3>
        <p>
          Geschichte für <strong>{childName}</strong> von <strong>{userName}</strong>
        </p>
        <img src={photo} alt="User" />
        <p>{story.description}</p>
      </div>
      <button className="order-button" onClick={handleOrder}>
        Bestellung fortsetzen
      </button>
    </div>
  );
}

export default Preview;
