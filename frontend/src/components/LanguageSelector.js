import React from 'react';
import { useLanguage } from '../services/LanguageContext';

const LanguageSelector = () => {
  const { language, changeLanguage, availableLanguages } = useLanguage();

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm text-gray-600">Language:</span>
      <select
        value={language}
        onChange={(e) => changeLanguage(e.target.value)}
        className="form-input text-sm py-1 px-2"
      >
        {availableLanguages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.nativeName}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;
