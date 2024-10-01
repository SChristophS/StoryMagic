// src/components/Order.js
import React, { useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../contexts/AppContext';
import './Order.css';

function Order() {
  const { userName, childName, photo, story, orderData, setOrderData } = useContext(AppContext);
  const [formData, setFormData] = useState({
    fullName: '',
    address: '',
    city: '',
    zipCode: '',
    email: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleOrder = () => {
    // Validierung
    for (let key in formData) {
      if (formData[key].trim() === '') {
        alert('Bitte alle Felder ausfüllen');
        return;
      }
    }

    // Bestellung aufgeben
    const orderPayload = {
      userName,
      childName,
      photo,
      storyId: story._id,
      orderData: formData,
    };

    axios
      .post('http://localhost:5000/api/place-order', orderPayload)
      .then((response) => {
        alert('Bestellung erfolgreich aufgegeben!');
        // Bestellung zurücksetzen oder zu einer Bestätigungsseite navigieren
      })
      .catch((error) => {
        console.error('Fehler beim Aufgeben der Bestellung:', error);
      });
  };

  return (
    <div className="order-container">
      <h2>Bestellung abschließen</h2>
      <div className="form-group">
        <label>Vollständiger Name:</label>
        <input
          type="text"
          name="fullName"
          value={formData.fullName}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label>Adresse:</label>
        <input
          type="text"
          name="address"
          value={formData.address}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label>Stadt:</label>
        <input
          type="text"
          name="city"
          value={formData.city}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label>Postleitzahl:</label>
        <input
          type="text"
          name="zipCode"
          value={formData.zipCode}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label>E-Mail:</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
        />
      </div>
      <button className="place-order-button" onClick={handleOrder}>
        Bestellung aufgeben
      </button>
    </div>
  );
}

export default Order;
