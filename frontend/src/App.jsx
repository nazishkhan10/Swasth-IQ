import React from 'react';
import AppRoutes from './routes/AppRoutes';
import ToastContainer from './components/common/Toast';

function App() {
  return (
    <>
      <AppRoutes />
      <ToastContainer />
    </>
  );
}

export default App;
