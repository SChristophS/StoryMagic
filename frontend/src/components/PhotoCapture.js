// src/components/PhotoCapture.js
import React, { useRef, useCallback, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { AppContext } from '../contexts/AppContext';
import './PhotoCapture.css';

function PhotoCapture() {
  const navigate = useNavigate();
  const { setPhoto } = useContext(AppContext);
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
  }, [webcamRef]);

  const handleRetake = () => {
    setCapturedImage(null);
  };

  const handleNext = () => {
    setPhoto(capturedImage);
    navigate('/preview');
  };

  return (
    <div className="photo-capture-container">
      <h2>Foto aufnehmen</h2>
      {!capturedImage ? (
        <>
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            width={400}
            height={300}
          />
          <button className="capture-button" onClick={capture}>
            Foto aufnehmen
          </button>
        </>
      ) : (
        <>
          <img src={capturedImage} alt="Captured" className="captured-image" />
          <div className="photo-buttons">
            <button onClick={handleRetake}>Neu aufnehmen</button>
            <button onClick={handleNext}>Weiter</button>
          </div>
        </>
      )}
    </div>
  );
}

export default PhotoCapture;
