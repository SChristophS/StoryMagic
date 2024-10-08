// src/components/UserStories.js

import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';

const UserStories = () => {
  const [userStories, setUserStories] = useState([]);
  const { currentUser, setSelectedStory, setPersonalData, setUserImages } = useContext(AppContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (currentUser) {
      axios
        .get('http://192.168.178.25:49158/api/user-stories')
        .then((response) => {
          setUserStories(response.data);
          console.debug('Benutzergeschichten geladen:', response.data);
        })
        .catch((error) => {
          console.error('Fehler beim Laden der Benutzergeschichten:', error);
        });
    }
  }, [currentUser]);

  if (!currentUser) {
    return <p>Bitte melde dich an, um deine Geschichten zu sehen.</p>;
  }

  const handleDeleteStory = (storyId) => {
    if (window.confirm('Bist du sicher, dass du diese Geschichte löschen möchtest?')) {
      axios
        .delete(`http://192.168.178.25:49158/api/personalized-stories/${storyId}`)
        .then((response) => {
          console.debug('Geschichte gelöscht:', response.data);
          // Aktualisiere die Geschichtenliste
          setUserStories(userStories.filter((story) => story.id !== storyId));
        })
        .catch((error) => {
          console.error('Fehler beim Löschen der Geschichte:', error);
          alert('Fehler beim Löschen der Geschichte. Bitte versuche es erneut.');
        });
    }
  };
  
  const handleLoadStory = (storyId) => {
    axios
      .get(`http://192.168.178.25:49158/api/personalized-stories/${storyId}`)
      .then((response) => {

		console.log("response");
		console.log(response);
		
        const story = response.data;
		
		console.log("story");
		console.log(story);
        console.debug('Geladene Geschichte:', story.created_at);
		

        // Setze die Daten im Kontext
        setSelectedStory(story);
        setPersonalData(story.personal_data);
        setUserImages(story.user_images);

        // Navigiere zur Vorschau
        navigate('/preview');
      })
      .catch((error) => {
        console.error('Fehler beim Laden der Geschichte:', error);
      });
  };

  return (
    <div>
      <h1>Meine Geschichten</h1>
      <ul>
        {userStories.map((story) => (
          <li key={story.id}>
            <h2>{story.title}</h2>
            <p>Erstellt am: {new Date(story.created_at).toLocaleString()}</p>
            <button onClick={() => handleLoadStory(story.id)}>Ansehen</button>
			<button onClick={() => handleDeleteStory(story.id)}>Löschen</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserStories;
