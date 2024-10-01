// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import Home from './components/Home';
import UserSelection from './components/UserSelection';
import StorySelection from './components/StorySelection';
import Personalization from './components/Personalization';
import PhotoCapture from './components/PhotoCapture';
import Preview from './components/Preview';
import Order from './components/Order';

function App() {
  return (
    <AppProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/user-selection" element={<UserSelection />} />
          <Route path="/story-selection" element={<StorySelection />} />
          <Route path="/personalization" element={<Personalization />} />
          <Route path="/photo-capture" element={<PhotoCapture />} />
          <Route path="/preview" element={<Preview />} />
          <Route path="/order" element={<Order />} />
        </Routes>
      </Router>
    </AppProvider>
  );
}

export default App;
