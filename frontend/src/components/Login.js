// src/components/Login.js

import React, { useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../context/AppContext';
import { useHistory } from 'react-router-dom';

const Login = () => {
  const { setAuthToken } = useContext(AppContext);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const history = useHistory();

  const handleLogin = (e) => {
    e.preventDefault();
    axios
      .post('/api/login', { username, password })
      .then((response) => {
        setAuthToken(response.data.access_token);
        localStorage.setItem('authToken', response.data.access_token);
        history.push('/');
      })
      .catch((error) => {
        console.error('Fehler bei der Anmeldung:', error);
      });
  };

  return (
    <div>
      <h1>Anmelden</h1>
      <form onSubmit={handleLogin}>
        <label>
          Benutzername:
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </label>
        <label>
          Passwort:
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        <button type="submit">Anmelden</button>
      </form>
    </div>
  );
};

export default Login;
