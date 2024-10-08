// src/components/Preview.js

import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext';

const Preview = () => {
  const { selectedStory, userInfo, userImages } = useContext(AppContext);

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
                  {text.content.replace('{child_name}', userInfo.childName || '...')}
                </span>
              ))}
            </p>
            {userImages[index] && (
              <img src={userImages[index]} alt={`User Upload ${index}`} width="200" />
            )}
          </div>
        ))}
      </div>
      {/* Optional: Button zum Generieren des PDFs */}
      {/* <button onClick={handleGeneratePDF}>PDF generieren</button> */}
    </div>
  );
};

export default Preview;
