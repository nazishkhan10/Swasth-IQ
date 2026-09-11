import React, { createContext, useState, useEffect, useCallback } from 'react';
import authApi from '../services/authApi';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  // Logout handler
  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  }, []);

  // Demo auto-login helper
  const performDemoLogin = useCallback(async () => {
    try {
      const demoData = await authApi.demoLogin();
      const { access_token, user: userData } = demoData;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      return userData;
    } catch (err) {
      console.error('Demo auto-login failed:', err);
    }
  }, []);

  // Check persistent auth status on app initialization
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          const userData = await authApi.getMe();
          setUser(userData);
          setToken(storedToken);
        } catch (error) {
          console.warn("Auth token invalid/expired. Auto-logging into demo session...", error);
          await performDemoLogin();
        }
      } else {
        await performDemoLogin();
      }
      setLoading(false);
    };

    initAuth();
  }, [performDemoLogin]);

  // Handle unauthorized event dispatched by Axios interceptor
  useEffect(() => {
    const handleUnauthorized = () => {
      performDemoLogin();
    };

    window.addEventListener('auth-unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth-unauthorized', handleUnauthorized);
  }, [performDemoLogin]);

  // Login handler
  const login = async (credentials) => {
    const response = await authApi.login(credentials);
    const { access_token, user: userData } = response;
    
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  // Register handler
  const register = async (userDataInput) => {
    const response = await authApi.register(userDataInput);
    return response;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!token && !!user,
        login,
        register,
        logout,
        performDemoLogin
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
