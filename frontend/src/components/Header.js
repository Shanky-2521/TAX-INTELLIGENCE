import React from 'react';
import { useLanguage } from '../services/LanguageContext';

const Header = () => {
  const { translations } = useLanguage();

  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">TI</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">
              {translations.welcome_title}
            </h1>
          </div>
          <nav className="hidden md:flex space-x-6">
            <a href="/" className="text-gray-600 hover:text-blue-600 transition-colors">
              {translations.home}
            </a>
            <a href="/help" className="text-gray-600 hover:text-blue-600 transition-colors">
              {translations.help}
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
