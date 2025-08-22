import React, { useState } from 'react';
import { X } from 'lucide-react';

const EITCCalculator = ({ isOpen, onClose, translations }) => {
  const [formData, setFormData] = useState({
    filing_status: 'single',
    adjusted_gross_income: '',
    earned_income: '',
    investment_income: '',
    qualifying_children: 0
  });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    // Calculator logic will be implemented
    console.log('Calculate EITC:', formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold">{translations.calculator_title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="form-label">{translations.filing_status}</label>
            <select 
              className="form-input"
              value={formData.filing_status}
              onChange={(e) => setFormData({...formData, filing_status: e.target.value})}
            >
              <option value="single">{translations.filing_status_single}</option>
              <option value="married_joint">{translations.filing_status_married_joint}</option>
              <option value="married_separate">{translations.filing_status_married_separate}</option>
              <option value="head_of_household">{translations.filing_status_head_household}</option>
            </select>
          </div>
          
          <div>
            <label className="form-label">{translations.adjusted_gross_income}</label>
            <input
              type="number"
              className="form-input"
              value={formData.adjusted_gross_income}
              onChange={(e) => setFormData({...formData, adjusted_gross_income: e.target.value})}
              placeholder="0"
            />
          </div>
          
          <div>
            <label className="form-label">{translations.earned_income}</label>
            <input
              type="number"
              className="form-input"
              value={formData.earned_income}
              onChange={(e) => setFormData({...formData, earned_income: e.target.value})}
              placeholder="0"
            />
          </div>
          
          <div>
            <label className="form-label">{translations.qualifying_children}</label>
            <select 
              className="form-input"
              value={formData.qualifying_children}
              onChange={(e) => setFormData({...formData, qualifying_children: parseInt(e.target.value)})}
            >
              <option value={0}>0</option>
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3+</option>
            </select>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              {translations.calculate_button}
            </button>
            <button type="button" onClick={onClose} className="btn-secondary">
              {translations.cancel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EITCCalculator;
