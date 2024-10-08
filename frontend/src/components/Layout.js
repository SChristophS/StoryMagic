// src/components/Layout.js

import React from 'react';
import Navbar from './Navbar';

const Layout = ({ children }) => {
  return (
    <>
      <Navbar />
      <main style={styles.mainContent}>
        {children}
      </main>
    </>
  );
};

const styles = {
  mainContent: {
    padding: '20px',
  },
};

export default Layout;
