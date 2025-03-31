import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import QuestionList from '../components/QuestionList';

const handleAnswerEvaluated = (questionId, score) => {
  // Update the scores in state
  setQuestionScores(prev => ({
    ...prev,
    [questionId]: score
  }));
  
  // Check if all questions have been answered
  const allAnswered = questions.every(q => 
    questionScores[q.id] !== undefined || q.id === questionId
  );
  
  if (allAnswered) {
    console.log("All questions have been answered, ready to show results");
    // Enable the "View Results" button or automatically navigate to results
  }
};

const InterviewPage = () => {
  const navigate = useNavigate();
  
  const handleNavigateToResults = (scores) => {
    // Navigate to results page
    navigate('/results');
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <QuestionList 
        questions={questions} 
        onAnswerEvaluated={handleAnswerEvaluated}
        onNavigateToResults={handleNavigateToResults}
      />
    </div>
  );
};

export default InterviewPage; 