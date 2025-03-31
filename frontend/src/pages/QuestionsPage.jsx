import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const QuestionsPage = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { jdId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    // In a real app, we would fetch questions for this JD ID from the API
    // For now, we'll just simulate loading some questions
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Mock questions data
      const mockQuestions = [
        {
          id: 'q1',
          text: 'What experience do you have with React?',
          reference_answer: 'A strong answer would demonstrate practical experience with React, including specific projects and measurable results.'
        },
        {
          id: 'q2',
          text: 'Describe a challenging project where you used Node.js.',
          reference_answer: 'The candidate should describe a specific project involving Node.js, the challenges faced, and how they overcame them.'
        },
        {
          id: 'q3',
          text: 'How do you stay current with developments in web development?',
          reference_answer: 'A good answer would mention specific learning resources, communities, or practices the candidate uses to stay updated with web development.'
        }
      ];
      
      setQuestions(mockQuestions);
      setLoading(false);
    }, 1000);
  }, [jdId]);

  const handleQuestionClick = (questionId) => {
    navigate(`/question/${questionId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center">
            <div className="spinner mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading questions...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p>Error: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Interview Questions</h1>
        
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Questions for Job Description #{jdId}
            </h2>
            
            <div className="space-y-4">
              {questions.map((question) => (
                <div 
                  key={question.id}
                  className="p-4 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer transition"
                  onClick={() => handleQuestionClick(question.id)}
                >
                  <h3 className="text-lg font-medium text-gray-800">{question.text}</h3>
                  <p className="text-sm text-gray-500 mt-1">Click to view details and answer</p>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="mt-6">
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition"
          >
            Back to JD Analyzer
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuestionsPage; 