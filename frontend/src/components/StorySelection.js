// src/components/StorySelection.js

import React, { useEffect, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';

const StorySelection = () => {
  const { userInfo, stories, setStories, setSelectedStory, setImagePrompts } = useContext(AppContext);
  const navigate = useNavigate();

  useEffect(() => {
    console.debug('Lade passende Geschichten von der API');
    axios
      .get('http://192.168.178.25:49158/api/stories', { // Verwende relativen Pfad, wenn Proxy konfiguriert ist
        params: {
          role: userInfo.role,
          childAge: userInfo.childAge,
        },
      })
      .then((response) => {
        setStories(response.data);
        console.debug('Passende Geschichten geladen:', response.data);
      })
      .catch((error) => {
        console.error('Fehler beim Laden der Geschichten:', error);
      });
  }, [userInfo, setStories]);

  const handleSelectStory = (story) => {
    setSelectedStory(story);
    // Sammle die Bildanweisungen aus allen Szenen und deren imageElements
    const prompts = story.scenes.flatMap(scene => 
      scene.imageElements.map(imageElement => imageElement.imagePrompt)
    ).filter(Boolean);
    setImagePrompts(prompts);
    console.debug('Bildanweisungen gesammelt:', prompts);
    navigate('/image-prompts');
  };

  return (
    <div>
      <h1>Wähle eine Geschichte</h1>
      <ul>
        {stories.map((story) => (
          <li key={story.id}>
            <h2>{story.title}</h2>
            <p>{story.description}</p>
            <button onClick={() => handleSelectStory(story)}>Diese Geschichte wählen</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StorySelection;
