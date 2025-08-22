import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User, ThumbsUp, ThumbsDown } from 'lucide-react';

const MessageBubble = ({ message, onFeedback, translations }) => {
  const isUser = message.type === 'user';
  const isWelcome = message.isWelcome;
  const isError = message.isError;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex max-w-xs lg:max-w-md ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-2`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-600 text-white ml-2' : 'bg-gray-200 text-gray-600 mr-2'
        }`}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Message Content */}
        <div className={`rounded-lg px-4 py-2 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : isError 
              ? 'bg-red-50 border border-red-200 text-red-800'
              : isWelcome
                ? 'bg-green-50 border border-green-200 text-green-800'
                : 'bg-gray-100 text-gray-800'
        }`}>
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          
          {/* Timestamp */}
          <p className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-500'
          }`}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </p>

          {/* Feedback buttons for assistant messages */}
          {!isUser && !isWelcome && !isError && (
            <div className="flex items-center space-x-2 mt-2">
              <span className="text-xs text-gray-500">
                {translations.feedback_helpful}
              </span>
              <button
                onClick={() => onFeedback(message.id, 5)}
                className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                title={translations.feedback_yes}
              >
                <ThumbsUp className="w-3 h-3" />
              </button>
              <button
                onClick={() => onFeedback(message.id, 1)}
                className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                title={translations.feedback_no}
              >
                <ThumbsDown className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;
