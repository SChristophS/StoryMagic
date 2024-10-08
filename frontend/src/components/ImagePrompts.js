// src/components/ImagePrompts.js

import React, { useState, useContext } from 'react';
import axios from 'axios';
import { AppContext } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';

const ImagePrompts = () => {
  const { imagePrompts, userImages, setUserImages } = useContext(AppContext);
  const [currentIndex, setCurrentIndex] = useState(0);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    console.debug('Ausgewählte Datei:', file);
    const formData = new FormData();
    formData.append('file', file);

    axios
      .post('http://192.168.178.25:49158/api/upload-image', formData)
      .then((response) => {
        const imagePath = response.data.file_path;
        setUserImages([...userImages, imagePath]);
        console.debug('Bild hochgeladen:', imagePath);
        if (currentIndex < imagePrompts.length - 1) {
          setCurrentIndex(currentIndex + 1);
        } else {
          navigate('/preview');
        }
      })
      .catch((error) => {
        console.error('Fehler beim Hochladen des Bildes:', error);
      });
  };

  if (!imagePrompts || imagePrompts.length === 0) {
    console.debug('imagePrompts ist leer oder nicht definiert:', imagePrompts);
    return <p>Keine Bildanweisungen vorhanden.</p>;
  }

  return (
    <div>
      <h1>Bild {currentIndex + 1} von {imagePrompts.length}</h1>
      <p>{imagePrompts[currentIndex]}</p>
      <input type="file" onChange={handleFileChange} accept="image/*" capture="camera" />
      <div>
        {userImages.map((image, index) => (
          <img key={index} src={image} alt={`User Upload ${index}`} width="100" />
        ))}
      </div>
    </div>
  );
};

export default ImagePrompts;
