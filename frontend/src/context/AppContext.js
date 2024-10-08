// src/context/AppContext.js

import React, { createContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));
  const [currentUser, setCurrentUser] = useState(null);
  
  const [userInfo, setUserInfo] = useState({
    role: '',
    childAge: '',
    childName: '',
  });

  const [stories, setStories] = useState([]);
  const [selectedStory, setSelectedStory] = useState(null);
  const [imagePrompts, setImagePrompts] = useState([]);
  const [userImages, setUserImages] = useState({});
  const [personalData, setPersonalData] = useState({
    child_name: '',
    role: '',
    child_age: '',
  });
  
  useEffect(() => {
    if (authToken) {
      try {
        const decoded = jwtDecode(authToken); // Korrekt verwendet
        console.log('AuthToken dekodiert:', decoded);
        setCurrentUser(decoded.sub || decoded.identity); // Verwende das richtige Feld
        console.log('Aktueller Benutzer gesetzt:', currentUser);
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
      } catch (error) {
        console.error('Fehler beim Dekodieren des Tokens:', error);
        setCurrentUser(null);
        delete axios.defaults.headers.common['Authorization'];
      }
    } else {
      setCurrentUser(null);
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [authToken]);

  return (
    <AppContext.Provider
      value={{
        authToken,
        setAuthToken,
        currentUser,
        setCurrentUser,
        userInfo,
        setUserInfo,
        stories,
        setStories,
        selectedStory,
        setSelectedStory,
        imagePrompts,
        setImagePrompts,
        userImages,
        setUserImages,
        personalData,
        setPersonalData,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};
