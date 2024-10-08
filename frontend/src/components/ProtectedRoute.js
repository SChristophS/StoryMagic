// src/components/ProtectedRoute.js

import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';

const ProtectedRoute = ({ children }) => {
  const { authToken } = useContext(AppContext);

  if (!authToken) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
