// src/components/UserStories.js

import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../context/AppContext';

const UserStories = () => {
  const [userStories, setUserStories] = useState([]);
  const { currentUser } = useContext(AppContext);

  useEffect(() => {
    if (currentUser) {
      axios
        .get('/api/user-stories')
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
    return <p>Bitte melden Sie sich an, um Ihre Geschichten zu sehen.</p>;
  }

  return (
    <div>
      <h1>Meine Geschichten</h1>
      <ul>
        {userStories.map((story) => (
          <li key={story.id}>
            <h2>{story.personal_data.childName}'s Geschichte</h2>
            <p>Erstellt am: {new Date(story.created_at).toLocaleString()}</p>
            {/* Optional: Button zum Laden der Geschichte */}
            {/* <button onClick={() => handleLoadStory(story)}>Laden</button> */}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserStories;
