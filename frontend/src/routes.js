// src/routes.js

import React from 'react';
import { Routes, Route } from 'react-router-dom';
import WelcomePage from './components/WelcomePage';
import UserInfoForm from './components/UserInfoForm';
import StorySelection from './components/StorySelection';
import ImagePrompts from './components/ImagePrompts';
import Preview from './components/Preview';
import NotFound from './components/NotFound';

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<WelcomePage />} />
    <Route path="/user-info" element={<UserInfoForm />} />
    <Route path="/stories" element={<StorySelection />} />
    <Route path="/image-prompts" element={<ImagePrompts />} />
    <Route path="/preview" element={<Preview />} />
    {/* Wildcard-Route für 404 Not Found */}
    <Route path="*" element={<NotFound />} />
  </Routes>
);

export default AppRoutes;
