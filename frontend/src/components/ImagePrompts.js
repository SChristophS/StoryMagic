// src/components/ImagePrompts.js

import React, { useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';

const ImagePrompts = () => {
  const { selectedStory, userImages, setUserImages } = useContext(AppContext);
  const navigate = useNavigate();

  if (!selectedStory) {
    console.debug('selectedStory ist nicht definiert:', selectedStory);
    return <p>Keine Geschichte ausgewählt.</p>;
  }

  const handleImageUpload = (sceneIndex, event) => {
    const file = event.target.files[0];
    console.debug('Ausgewählte Datei:', file);
    const formData = new FormData();
    formData.append('file', file);

    axios
      .post('/api/upload-image', formData)
      .then((response) => {
        const imagePath = response.data.file_path;

        // Update userImages mit dem Szenenindex
        setUserImages((prevImages) => ({
          ...prevImages,
          [sceneIndex]: imagePath,
        }));

        console.debug('Bild hochgeladen:', imagePath);
      })
      .catch((error) => {
        console.error('Fehler beim Hochladen des Bildes:', error);
      });
  };

  const handleNext = () => {
    navigate('/preview');
  };

  return (
    <div>
      <h1>Bilder hochladen</h1>
      {selectedStory.scenes.map((scene, index) => (
        <div key={index}>
          <p>{scene.imageElements[0].imagePrompt}</p>
          <input
            type="file"
            accept="image/*"
            onChange={(event) => handleImageUpload(index, event)}
          />
          {userImages[index] && (
            <img
              src={userImages[index]}
              alt={`Bild für Szene ${index + 1}`}
              width="200"
            />
          )}
        </div>
      ))}
      <button onClick={handleNext}>Weiter zur Vorschau</button>
    </div>
  );
};

export default ImagePrompts;
