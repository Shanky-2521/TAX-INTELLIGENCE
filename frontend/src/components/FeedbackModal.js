import React, { useState } from 'react';
import { X, Star } from 'lucide-react';

const FeedbackModal = ({ isOpen, onClose, onSubmit, translations }) => {
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      rating,
      feedback_text: feedback
    });
    setRating(0);
    setFeedback('');
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold">{translations.feedback_modal_title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="form-label">{translations.feedback_modal_rating}</label>
            <div className="flex space-x-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className={`p-1 ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
                >
                  <Star className="w-6 h-6 fill-current" />
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <label className="form-label">{translations.feedback_modal_comment}</label>
            <textarea
              className="form-input"
              rows={4}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Your feedback helps us improve..."
            />
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button 
              type="submit" 
              className="btn-primary flex-1"
              disabled={rating === 0}
            >
              {translations.feedback_modal_submit}
            </button>
            <button type="button" onClick={onClose} className="btn-secondary">
              {translations.feedback_modal_cancel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackModal;
