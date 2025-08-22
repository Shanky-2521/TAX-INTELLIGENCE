import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

// Translation data
const translations = {
  en: {
    // Welcome and main interface
    welcome_title: 'Tax Intelligence Assistant',
    welcome_subtitle: 'Get help with Earned Income Tax Credit (EITC) eligibility and calculations',
    welcome_message: 'Hello! I\'m your Tax Intelligence Assistant. I can help you understand the Earned Income Tax Credit (EITC), check your eligibility, and answer questions about tax requirements. How can I assist you today?',
    
    // Chat interface
    chat_title: 'Tax Intelligence Assistant',
    chat_subtitle: 'EITC guidance and support',
    input_placeholder: 'Ask about EITC eligibility, requirements, or calculations...',
    send_button: 'Send',
    character_warning: 'Approaching character limit',
    
    // Quick actions
    quick_actions_title: 'Quick actions:',
    quick_eitc_eligibility: 'EITC Eligibility',
    quick_eitc_amount: 'Credit Amount',
    quick_calculator: 'EITC Calculator',
    quick_requirements: 'Requirements',
    
    // Messages
    error_message: 'Sorry, something went wrong. Please try again.',
    error_response: 'I apologize, but I encountered an error. Please try again or contact support if the problem persists.',
    
    // Feedback
    feedback_success: 'Thank you for your feedback!',
    feedback_error: 'Failed to submit feedback. Please try again.',
    feedback_helpful: 'Was this helpful?',
    feedback_yes: 'Yes',
    feedback_no: 'No',
    feedback_modal_title: 'Provide Feedback',
    feedback_modal_rating: 'How would you rate this response?',
    feedback_modal_comment: 'Additional comments (optional):',
    feedback_modal_submit: 'Submit Feedback',
    feedback_modal_cancel: 'Cancel',
    
    // EITC Calculator
    calculator_title: 'EITC Calculator',
    calculator_subtitle: 'Calculate your estimated Earned Income Tax Credit',
    filing_status: 'Filing Status',
    filing_status_single: 'Single',
    filing_status_married_joint: 'Married Filing Jointly',
    filing_status_married_separate: 'Married Filing Separately',
    filing_status_head_household: 'Head of Household',
    adjusted_gross_income: 'Adjusted Gross Income',
    earned_income: 'Earned Income',
    investment_income: 'Investment Income',
    qualifying_children: 'Number of Qualifying Children',
    calculate_button: 'Calculate EITC',
    calculator_result_title: 'Your EITC Estimate',
    calculator_eligible: 'You are eligible for EITC!',
    calculator_not_eligible: 'You do not appear to be eligible for EITC',
    calculator_amount: 'Estimated Credit Amount',
    calculator_disclaimer: 'This is an estimate based on the information provided. Consult a tax professional for specific advice.',
    
    // Admin
    admin_login: 'Admin Login',
    admin_dashboard: 'Admin Dashboard',
    admin_conversations: 'Conversations',
    admin_feedback: 'Feedback',
    admin_analytics: 'Analytics',
    admin_logout: 'Logout',
    
    // Navigation
    home: 'Home',
    about: 'About',
    help: 'Help',
    contact: 'Contact',
    
    // Footer
    footer_disclaimer: 'This application provides general tax information and is not a substitute for professional tax advice.',
    footer_irs_link: 'Visit IRS.gov for official tax information',
    
    // Common
    loading: 'Loading...',
    close: 'Close',
    save: 'Save',
    cancel: 'Cancel',
    submit: 'Submit',
    edit: 'Edit',
    delete: 'Delete',
    confirm: 'Confirm',
    yes: 'Yes',
    no: 'No'
  },
  
  es: {
    // Welcome and main interface
    welcome_title: 'Asistente de Inteligencia Fiscal',
    welcome_subtitle: 'Obtenga ayuda con la elegibilidad y cálculos del Crédito Tributario por Ingreso del Trabajo (EITC)',
    welcome_message: '¡Hola! Soy su Asistente de Inteligencia Fiscal. Puedo ayudarle a entender el Crédito Tributario por Ingreso del Trabajo (EITC), verificar su elegibilidad y responder preguntas sobre requisitos fiscales. ¿Cómo puedo asistirle hoy?',
    
    // Chat interface
    chat_title: 'Asistente de Inteligencia Fiscal',
    chat_subtitle: 'Orientación y apoyo para EITC',
    input_placeholder: 'Pregunte sobre elegibilidad, requisitos o cálculos del EITC...',
    send_button: 'Enviar',
    character_warning: 'Acercándose al límite de caracteres',
    
    // Quick actions
    quick_actions_title: 'Acciones rápidas:',
    quick_eitc_eligibility: 'Elegibilidad EITC',
    quick_eitc_amount: 'Monto del Crédito',
    quick_calculator: 'Calculadora EITC',
    quick_requirements: 'Requisitos',
    
    // Messages
    error_message: 'Lo siento, algo salió mal. Por favor, inténtelo de nuevo.',
    error_response: 'Me disculpo, pero encontré un error. Por favor, inténtelo de nuevo o contacte al soporte si el problema persiste.',
    
    // Feedback
    feedback_success: '¡Gracias por sus comentarios!',
    feedback_error: 'Error al enviar comentarios. Por favor, inténtelo de nuevo.',
    feedback_helpful: '¿Fue esto útil?',
    feedback_yes: 'Sí',
    feedback_no: 'No',
    feedback_modal_title: 'Proporcionar Comentarios',
    feedback_modal_rating: '¿Cómo calificaría esta respuesta?',
    feedback_modal_comment: 'Comentarios adicionales (opcional):',
    feedback_modal_submit: 'Enviar Comentarios',
    feedback_modal_cancel: 'Cancelar',
    
    // EITC Calculator
    calculator_title: 'Calculadora EITC',
    calculator_subtitle: 'Calcule su Crédito Tributario por Ingreso del Trabajo estimado',
    filing_status: 'Estado Civil',
    filing_status_single: 'Soltero',
    filing_status_married_joint: 'Casado Presentando Conjuntamente',
    filing_status_married_separate: 'Casado Presentando por Separado',
    filing_status_head_household: 'Cabeza de Familia',
    adjusted_gross_income: 'Ingreso Bruto Ajustado',
    earned_income: 'Ingreso del Trabajo',
    investment_income: 'Ingreso de Inversiones',
    qualifying_children: 'Número de Hijos Calificados',
    calculate_button: 'Calcular EITC',
    calculator_result_title: 'Su Estimación EITC',
    calculator_eligible: '¡Usted es elegible para EITC!',
    calculator_not_eligible: 'No parece ser elegible para EITC',
    calculator_amount: 'Monto Estimado del Crédito',
    calculator_disclaimer: 'Esta es una estimación basada en la información proporcionada. Consulte a un profesional fiscal para consejos específicos.',
    
    // Admin
    admin_login: 'Inicio de Sesión de Administrador',
    admin_dashboard: 'Panel de Administración',
    admin_conversations: 'Conversaciones',
    admin_feedback: 'Comentarios',
    admin_analytics: 'Analíticas',
    admin_logout: 'Cerrar Sesión',
    
    // Navigation
    home: 'Inicio',
    about: 'Acerca de',
    help: 'Ayuda',
    contact: 'Contacto',
    
    // Footer
    footer_disclaimer: 'Esta aplicación proporciona información fiscal general y no es un sustituto del consejo fiscal profesional.',
    footer_irs_link: 'Visite IRS.gov para información fiscal oficial',
    
    // Common
    loading: 'Cargando...',
    close: 'Cerrar',
    save: 'Guardar',
    cancel: 'Cancelar',
    submit: 'Enviar',
    edit: 'Editar',
    delete: 'Eliminar',
    confirm: 'Confirmar',
    yes: 'Sí',
    no: 'No'
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    // Get language from localStorage or default to English
    const savedLanguage = localStorage.getItem('tax-intelligence-language');
    return savedLanguage || 'en';
  });

  useEffect(() => {
    // Save language preference to localStorage
    localStorage.setItem('tax-intelligence-language', language);
    
    // Update document language attribute
    document.documentElement.lang = language;
  }, [language]);

  const changeLanguage = (newLanguage) => {
    if (translations[newLanguage]) {
      setLanguage(newLanguage);
    }
  };

  const value = {
    language,
    changeLanguage,
    translations: translations[language],
    availableLanguages: [
      { code: 'en', name: 'English', nativeName: 'English' },
      { code: 'es', name: 'Spanish', nativeName: 'Español' }
    ]
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
