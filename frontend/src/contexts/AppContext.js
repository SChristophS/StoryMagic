// src/contexts/AppContext.js
import React, { createContext, useState } from 'react';

export const AppContext = createContext();

export function AppProvider({ children }) {
  const [userRole, setUserRole] = useState('');
  const [userName, setUserName] = useState('');
  const [childName, setChildName] = useState('');
  const [childAge, setChildAge] = useState(null); // Hinzugefügt
  const [story, setStory] = useState(null);
  const [photo, setPhoto] = useState('');
  const [orderData, setOrderData] = useState({});

  return (
    <AppContext.Provider
      value={{
        userRole,
        setUserRole,
        userName,
        setUserName,
        childName,
        setChildName,
        childAge,       // Hinzugefügt
        setChildAge,    // Hinzugefügt
        story,
        setStory,
        photo,
        setPhoto,
        orderData,
        setOrderData,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}
