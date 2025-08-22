import React, { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery } from 'react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, AlertCircle, ThumbsUp, ThumbsDown } from 'lucide-react';
import toast from 'react-hot-toast';

import { useLanguage } from '../services/LanguageContext';
import { useSession } from '../services/SessionContext';
import { chatAPI, feedbackAPI } from '../services/api';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import EITCCalculator from './EITCCalculator';
import FeedbackModal from './FeedbackModal';

const ChatInterface = () => {
  const { language, translations } = useLanguage();
  const { sessionId } = useSession();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [showCalculator, setShowCalculator] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [selectedMessageId, setSelectedMessageId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initial welcome message
  useEffect(() => {
    const welcomeMessage = {
      id: 'welcome',
      type: 'assistant',
      content: translations.welcome_message,
      timestamp: new Date().toISOString(),
      isWelcome: true
    };
    setMessages([welcomeMessage]);
  }, [language, translations]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Chat mutation
  const chatMutation = useMutation(
    (messageData) => chatAPI.sendMessage(messageData),
    {
      onSuccess: (response) => {
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: response.response,
          timestamp: response.timestamp,
          sessionId: response.session_id
        };
        setMessages(prev => [...prev, assistantMessage]);
      },
      onError: (error) => {
        console.error('Chat error:', error);
        toast.error(translations.error_message || 'Sorry, something went wrong. Please try again.');
        
        const errorMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: translations.error_response || 'I apologize, but I encountered an error. Please try again or contact support if the problem persists.',
          timestamp: new Date().toISOString(),
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    }
  );

  // Feedback mutation
  const feedbackMutation = useMutation(
    (feedbackData) => feedbackAPI.submitFeedback(feedbackData),
    {
      onSuccess: () => {
        toast.success(translations.feedback_success || 'Thank you for your feedback!');
        setShowFeedback(false);
      },
      onError: () => {
        toast.error(translations.feedback_error || 'Failed to submit feedback. Please try again.');
      }
    }
  );

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || chatMutation.isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    // Send to API
    chatMutation.mutate({
      message: userMessage.content,
      session_id: sessionId,
      language: language,
      context: {}
    });
  };

  const handleQuickAction = (action) => {
    let message = '';
    
    switch (action) {
      case 'eitc_eligibility':
        message = translations.quick_eitc_eligibility || 'Am I eligible for the Earned Income Tax Credit?';
        break;
      case 'eitc_amount':
        message = translations.quick_eitc_amount || 'How much EITC can I receive?';
        break;
      case 'calculator':
        setShowCalculator(true);
        return;
      case 'requirements':
        message = translations.quick_requirements || 'What are the EITC requirements?';
        break;
      default:
        return;
    }

    setInputMessage(message);
    inputRef.current?.focus();
  };

  const handleFeedback = (messageId, rating) => {
    setSelectedMessageId(messageId);
    if (rating) {
      // Quick feedback
      feedbackMutation.mutate({
        session_id: sessionId,
        rating: rating,
        feedback_text: '',
        message_id: messageId
      });
    } else {
      // Open detailed feedback modal
      setShowFeedback(true);
    }
  };

  const quickActions = [
    { id: 'eitc_eligibility', label: translations.quick_eitc_eligibility || 'EITC Eligibility', icon: '🎯' },
    { id: 'eitc_amount', label: translations.quick_eitc_amount || 'Credit Amount', icon: '💰' },
    { id: 'calculator', label: translations.quick_calculator || 'EITC Calculator', icon: '🧮' },
    { id: 'requirements', label: translations.quick_requirements || 'Requirements', icon: '📋' }
  ];

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">
              {translations.chat_title || 'Tax Intelligence Assistant'}
            </h2>
            <p className="text-blue-100 text-sm">
              {translations.chat_subtitle || 'EITC guidance and support'}
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-4 bg-gray-50 border-b">
        <p className="text-sm text-gray-600 mb-3">
          {translations.quick_actions_title || 'Quick actions:'}
        </p>
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => handleQuickAction(action.id)}
              className="inline-flex items-center space-x-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors"
            >
              <span>{action.icon}</span>
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Messages Container */}
      <div className="h-96 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onFeedback={handleFeedback}
              translations={translations}
            />
          ))}
        </AnimatePresence>
        
        {/* Typing Indicator */}
        {chatMutation.isLoading && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="p-4 border-t bg-gray-50">
        <div className="flex space-x-3">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={translations.input_placeholder || 'Ask about EITC eligibility, requirements, or calculations...'}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={chatMutation.isLoading}
              maxLength={500}
            />
            <div className="absolute right-3 bottom-3 text-xs text-gray-400">
              {inputMessage.length}/500
            </div>
          </div>
          <button
            type="submit"
            disabled={!inputMessage.trim() || chatMutation.isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">
              {translations.send_button || 'Send'}
            </span>
          </button>
        </div>
        
        {/* Character count warning */}
        {inputMessage.length > 400 && (
          <p className="text-xs text-amber-600 mt-2">
            {translations.character_warning || 'Approaching character limit'}
          </p>
        )}
      </form>

      {/* EITC Calculator Modal */}
      {showCalculator && (
        <EITCCalculator
          isOpen={showCalculator}
          onClose={() => setShowCalculator(false)}
          language={language}
          translations={translations}
        />
      )}

      {/* Feedback Modal */}
      {showFeedback && (
        <FeedbackModal
          isOpen={showFeedback}
          onClose={() => setShowFeedback(false)}
          onSubmit={(feedbackData) => {
            feedbackMutation.mutate({
              ...feedbackData,
              session_id: sessionId,
              message_id: selectedMessageId
            });
          }}
          translations={translations}
        />
      )}
    </div>
  );
};

export default ChatInterface;
