// src/components/StorySelection.js
import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AppContext } from '../contexts/AppContext';
import './StorySelection.css';

function StorySelection() {
  const navigate = useNavigate();
  const { userRole, childAge, setStory } = useContext(AppContext);
  const [stories, setStories] = useState([]);

  useEffect(() => {
    // API-Anfrage mit Parametern für Rolle und Alter
    axios
      .get('http://localhost:5000/api/stories', {
        params: {
          role: userRole,
          age: childAge,
        },
      })
      .then((response) => {
        setStories(response.data);
      })
      .catch((error) => {
        console.error('Fehler beim Abrufen der Geschichten:', error);
      });
  }, [userRole, childAge]);

  const handleSelection = (story) => {
    setStory(story);
    navigate('/personalization');
  };

  return (
    <div className="story-selection-container">
      <h2>Wähle eine Geschichte aus</h2>
      <div className="stories-grid">
        {stories.length > 0 ? (
          stories.map((story) => (
            <div key={story._id} className="story-card">
              <img src={story.coverImage} alt={story.title} />
              <h3>{story.title}</h3>
              <p>{story.description}</p>
              <button onClick={() => handleSelection(story)}>Auswählen</button>
            </div>
          ))
        ) : (
          <p>Keine passenden Geschichten gefunden.</p>
        )}
      </div>
    </div>
  );
}

export default StorySelection;
