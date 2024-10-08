// src/context/AppContext.js

import React, { createContext, useState } from 'react';
import jwt_decode from 'jwt-decode';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
	const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));
	const [currentUser, setCurrentUser] = useState(null);
  
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
  
	useEffect(() => {
		if (authToken) {
		  const decoded = jwt_decode(authToken);
		  setCurrentUser(decoded.identity);
		  axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
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
