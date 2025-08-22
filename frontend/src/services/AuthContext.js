import React, { createContext, useContext, useState, useEffect } from 'react';
import { adminAPI } from './api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('tax-intelligence-token');
    if (token) {
      setIsAuthenticated(true);
      // In a real app, you'd validate the token with the server
    }
    setIsLoading(false);
  }, []);

  const login = async (credentials) => {
    try {
      const response = await adminAPI.login(credentials);
      const { access_token } = response;
      
      localStorage.setItem('tax-intelligence-token', access_token);
      setIsAuthenticated(true);
      setUser({ email: credentials.email });
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('tax-intelligence-token');
    setIsAuthenticated(false);
    setUser(null);
  };

  const value = {
    isAuthenticated,
    user,
    isLoading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
