// src/context/AppContext.js

import React, { createContext, useState } from 'react';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [userInfo, setUserInfo] = useState({
    role: '',
    childAge: 0,
    // Weitere Zustände nach Bedarf
  });

  const [stories, setStories] = useState([]);
  const [selectedStory, setSelectedStory] = useState(null);
  const [imagePrompts, setImagePrompts] = useState([]);
  const [userImages, setUserImages] = useState([]);
  const [personalData, setPersonalData] = useState({});

  return (
    <AppContext.Provider
      value={{
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
