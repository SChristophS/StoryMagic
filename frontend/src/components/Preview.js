// src/components/Preview.js

import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Preview = () => {
  const { selectedStory, personalData, userImages } = useContext(AppContext);
  const navigate = useNavigate();

  const handleSaveStory = () => {
	  const payload = {
		story_id: selectedStory.id,
		personal_data: personalData,
		user_images: userImages
	  };
	  
	    console.log('Payload:', payload);
		console.log('personalData:', personalData);


    axios
      .post('http://192.168.178.25:49158/api/personalize', payload)
      .then((response) => {
        console.debug('Geschichte gespeichert:', response.data);
        navigate('/my-stories');
      })
      .catch((error) => {
        console.error('Fehler beim Speichern der Geschichte:', error);
      });
  };
  
  if (!selectedStory) {
    return <p>Keine Geschichte ausgewählt.</p>;
  }

  return (
    <div>
      <h1>Vorschau deines Buches</h1>
      <h2>{selectedStory.title}</h2>
      <p>{selectedStory.description}</p>
      <div>
		{selectedStory.scenes.map((scene, index) => (
		  <div key={index}>
			<h3>Seite {index + 1}</h3>
			<p>
			  {scene.textElements.map((text, idx) => (
				<span key={idx}>
				  {text.content
					.replace('{child_name}', personalData.child_name || '...')
					.replace('{role}', personalData.role || '...')}
				</span>
			  ))}
			</p>
			{userImages[index] && (
			  <img
				src={userImages[index]}
				alt={`Bild für Szene ${index + 1}`}
				width="200"
			  />
			)}
		  </div>
		))}

        <button onClick={handleSaveStory}>Geschichte speichern</button>
      </div>
    </div>
  );
};

export default Preview;
