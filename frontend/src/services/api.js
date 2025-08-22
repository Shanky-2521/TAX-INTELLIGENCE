import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('tax-intelligence-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem('tax-intelligence-token');
      if (window.location.pathname.startsWith('/admin')) {
        window.location.href = '/admin/login';
      }
    }
    return Promise.reject(error);
  }
);

// Chat API
export const chatAPI = {
  sendMessage: async (messageData) => {
    const response = await api.post('/api/v1/chat', messageData);
    return response.data;
  },

  getSessionHistory: async (sessionId) => {
    const response = await api.get(`/api/v1/session/${sessionId}/history`);
    return response.data;
  },

  getSupportedLanguages: async () => {
    const response = await api.get('/api/v1/languages');
    return response.data;
  }
};

// EITC Calculator API
export const eitcAPI = {
  calculateEITC: async (calculationData) => {
    const response = await api.post('/api/v1/calculate-eitc', calculationData);
    return response.data;
  },

  getIncomeLimits: async (filingStatus, qualifyingChildren) => {
    const response = await api.get('/api/v1/eitc/income-limits', {
      params: { filing_status: filingStatus, qualifying_children: qualifyingChildren }
    });
    return response.data;
  }
};

// Feedback API
export const feedbackAPI = {
  submitFeedback: async (feedbackData) => {
    const response = await api.post('/api/v1/feedback', feedbackData);
    return response.data;
  }
};

// Admin API
export const adminAPI = {
  login: async (credentials) => {
    const response = await api.post('/admin/login', credentials);
    return response.data;
  },

  getDashboardStats: async (days = 7) => {
    const response = await api.get('/admin/dashboard/stats', {
      params: { days }
    });
    return response.data;
  },

  getConversations: async (page = 1, perPage = 20, filters = {}) => {
    const response = await api.get('/admin/conversations', {
      params: { page, per_page: perPage, ...filters }
    });
    return response.data;
  },

  getConversationDetail: async (conversationId) => {
    const response = await api.get(`/admin/conversations/${conversationId}`);
    return response.data;
  },

  getFeedback: async (page = 1, perPage = 20, filters = {}) => {
    const response = await api.get('/admin/feedback', {
      params: { page, per_page: perPage, ...filters }
    });
    return response.data;
  },

  getSystemHealth: async () => {
    const response = await api.get('/admin/system/health');
    return response.data;
  }
};

// Health API
export const healthAPI = {
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  checkDetailedHealth: async () => {
    const response = await api.get('/health/detailed');
    return response.data;
  }
};

// Error handling utilities
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return data.message || 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'Access denied. You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 429:
        return 'Too many requests. Please wait a moment and try again.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return data.message || 'An unexpected error occurred.';
    }
  } else if (error.request) {
    // Network error
    return 'Network error. Please check your connection and try again.';
  } else {
    // Other error
    return error.message || 'An unexpected error occurred.';
  }
};

// Utility function to check if API is available
export const checkAPIAvailability = async () => {
  try {
    await healthAPI.checkHealth();
    return true;
  } catch (error) {
    console.error('API not available:', error);
    return false;
  }
};

// Rate limiting helper
export const withRateLimit = (apiCall, delay = 1000) => {
  let lastCall = 0;
  
  return async (...args) => {
    const now = Date.now();
    const timeSinceLastCall = now - lastCall;
    
    if (timeSinceLastCall < delay) {
      await new Promise(resolve => setTimeout(resolve, delay - timeSinceLastCall));
    }
    
    lastCall = Date.now();
    return apiCall(...args);
  };
};

// Retry helper for failed requests
export const withRetry = (apiCall, maxRetries = 3, delay = 1000) => {
  return async (...args) => {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await apiCall(...args);
      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx)
        if (error.response?.status >= 400 && error.response?.status < 500) {
          throw error;
        }
        
        // Wait before retrying (exponential backoff)
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt - 1)));
        }
      }
    }
    
    throw lastError;
  };
};

export default api;
