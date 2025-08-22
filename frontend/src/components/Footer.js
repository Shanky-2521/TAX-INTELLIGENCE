import React from 'react';
import { useLanguage } from '../services/LanguageContext';

const Footer = () => {
  const { translations } = useLanguage();

  return (
    <footer className="bg-gray-800 text-white py-8 mt-12">
      <div className="container mx-auto px-4">
        <div className="text-center">
          <p className="text-gray-300 mb-4">
            {translations.footer_disclaimer}
          </p>
          <a 
            href="https://www.irs.gov" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 transition-colors"
          >
            {translations.footer_irs_link}
          </a>
          <p className="text-gray-400 text-sm mt-4">
            © 2025 Tax Intelligence. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
