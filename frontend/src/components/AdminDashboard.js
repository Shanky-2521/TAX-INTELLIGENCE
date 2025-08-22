import React from 'react';
import { useAuth } from '../services/AuthContext';

const AdminDashboard = () => {
  const { logout } = useAuth();

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
          <button
            onClick={logout}
            className="btn-secondary"
          >
            Logout
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Conversations</h3>
            <p className="text-3xl font-bold text-blue-600">--</p>
            <p className="text-sm text-gray-500">Total conversations</p>
          </div>
          
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Active Sessions</h3>
            <p className="text-3xl font-bold text-green-600">--</p>
            <p className="text-sm text-gray-500">Currently active</p>
          </div>
          
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Feedback</h3>
            <p className="text-3xl font-bold text-purple-600">--</p>
            <p className="text-sm text-gray-500">Average rating</p>
          </div>
        </div>
        
        <div className="mt-8">
          <p className="text-gray-600">
            Admin dashboard functionality will be implemented in the next phase.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
