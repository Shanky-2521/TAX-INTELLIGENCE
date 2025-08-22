import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import './App.css';

// Components
import ChatInterface from './components/ChatInterface';
import AdminDashboard from './components/AdminDashboard';
import LanguageSelector from './components/LanguageSelector';
import Header from './components/Header';
import Footer from './components/Footer';
import LoadingSpinner from './components/LoadingSpinner';

// Services
import { LanguageProvider, useLanguage } from './services/LanguageContext';
import { AuthProvider, useAuth } from './services/AuthContext';
import { SessionProvider } from './services/SessionContext';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

function AppContent() {
  const { language, translations } = useLanguage();
  const { isAuthenticated, isLoading } = useAuth();
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    // Simulate app initialization
    const timer = setTimeout(() => {
      setIsInitializing(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isInitializing || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/" 
            element={
              <div className="max-w-4xl mx-auto">
                <div className="text-center mb-8">
                  <h1 className="text-4xl font-bold text-gray-900 mb-4">
                    {translations.welcome_title}
                  </h1>
                  <p className="text-xl text-gray-600 mb-6">
                    {translations.welcome_subtitle}
                  </p>
                  <div className="flex justify-center mb-8">
                    <LanguageSelector />
                  </div>
                </div>
                <ChatInterface />
              </div>
            } 
          />
          
          {/* Admin Routes */}
          <Route 
            path="/admin/*" 
            element={
              isAuthenticated ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/admin/login" replace />
              )
            } 
          />
          
          {/* Redirect unknown routes to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      
      <Footer />
      
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#4ade80',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <LanguageProvider>
          <AuthProvider>
            <SessionProvider>
              <AppContent />
            </SessionProvider>
          </AuthProvider>
        </LanguageProvider>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
