import React, { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

const SessionContext = createContext();

export const SessionProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(() => {
    // Get existing session ID from localStorage or create new one
    const existingSessionId = localStorage.getItem('tax-intelligence-session-id');
    return existingSessionId || uuidv4();
  });

  const [sessionData, setSessionData] = useState({
    conversationCount: 0,
    startTime: new Date().toISOString(),
    lastActivity: new Date().toISOString()
  });

  useEffect(() => {
    // Save session ID to localStorage
    localStorage.setItem('tax-intelligence-session-id', sessionId);
  }, [sessionId]);

  const createNewSession = () => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    setSessionData({
      conversationCount: 0,
      startTime: new Date().toISOString(),
      lastActivity: new Date().toISOString()
    });
    localStorage.setItem('tax-intelligence-session-id', newSessionId);
  };

  const updateActivity = () => {
    setSessionData(prev => ({
      ...prev,
      lastActivity: new Date().toISOString()
    }));
  };

  const incrementConversationCount = () => {
    setSessionData(prev => ({
      ...prev,
      conversationCount: prev.conversationCount + 1,
      lastActivity: new Date().toISOString()
    }));
  };

  const value = {
    sessionId,
    sessionData,
    createNewSession,
    updateActivity,
    incrementConversationCount
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};
