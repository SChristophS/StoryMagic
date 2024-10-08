// src/routes.js

import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import WelcomePage from './components/WelcomePage';
import UserInfoForm from './components/UserInfoForm';
import StorySelection from './components/StorySelection';
import ImagePrompts from './components/ImagePrompts';
import Preview from './components/Preview';
import NotFound from './components/NotFound';
import UserStories from './components/UserStories';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

const AppRoutes = () => (
  <Routes>
    {/* Startseite */}
    <Route path="/" element={<Layout><WelcomePage /></Layout>} />

    {/* Authentifizierungsrouten */}
    <Route path="/login" element={<Layout><Login /></Layout>} />	
    <Route path="/register" element={<Layout><Register /></Layout>} />

    {/* Geschützte Routen */}
    <Route
      path="/preview"
      element={
        <ProtectedRoute>
          <Layout>
            <Preview />
          </Layout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/my-stories"
      element={
        <ProtectedRoute>
          <Layout>
            <UserStories />
          </Layout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/user-info"
      element={
        <ProtectedRoute>
          <Layout>
            <UserInfoForm />
          </Layout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/stories"
      element={
        <ProtectedRoute>
          <Layout>
            <StorySelection />
          </Layout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/image-prompts"
      element={
        <ProtectedRoute>
          <Layout>
            <ImagePrompts />
          </Layout>
        </ProtectedRoute>
      }
    />

    {/* Wildcard-Route für 404 Not Found */}
    <Route path="*" element={<Layout><NotFound /></Layout>} />
  </Routes>
);

export default AppRoutes;
