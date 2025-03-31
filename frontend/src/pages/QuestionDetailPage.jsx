import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const QuestionDetailPage = () => {
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState(null);
  const { questionId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    // In a real app, we would fetch the question details from the API
    // For now, we'll just simulate loading the question
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Mock question data based on the ID
      const mockQuestions = {
        'q1': {
          id: 'q1',
          text: 'What experience do you have with React?',
          reference_answer: 'A strong answer would demonstrate practical experience with React, including specific projects and measurable results.'
        },
        'q2': {
          id: 'q2',
          text: 'Describe a challenging project where you used Node.js.',
          reference_answer: 'The candidate should describe a specific project involving Node.js, the challenges faced, and how they overcame them.'
        },
        'q3': {
          id: 'q3',
          text: 'How do you stay current with developments in web development?',
          reference_answer: 'A good answer would mention specific learning resources, communities, or practices the candidate uses to stay updated with web development.'
        }
      };
      
      const foundQuestion = mockQuestions[questionId];
      
      if (foundQuestion) {
        setQuestion(foundQuestion);
      } else {
        setError('Question not found');
      }
      
      setLoading(false);
    }, 800);
  }, [questionId]);

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      alert('Please provide an answer before submitting');
      return;
    }
    
    setEvaluating(true);
    
    // In a real app, we would send the answer to the API for evaluation
    // For now, we'll just simulate an API call
    setTimeout(() => {
      // Mock evaluation response
      const mockEvaluation = {
        score: Math.floor(Math.random() * 41) + 60, // Random score between 60-100
        feedback: 'Your answer demonstrates good understanding of the topic.',
        improvement_suggestions: 'Consider adding more specific examples from your experience to strengthen your answer.'
      };
      
      setEvaluation(mockEvaluation);
      setEvaluating(false);
    }, 1500);
  };

  const handleGenerateAnswer = async () => {
    setEvaluating(true);
    
    // In a real app, we would request an AI-generated answer from the API
    // For now, we'll just simulate an API call
    setTimeout(() => {
      // Mock generated answer
      const generatedAnswer = 
        "I have over 5 years of experience working with React in professional settings. " +
        "In my most recent role, I led the development of a complex dashboard application using React, Redux, and TypeScript. " +
        "The application needed to display real-time data from multiple sources and allow users to interact with the data in various ways. " +
        "I implemented a component-based architecture that improved code reusability by 40% and reduced bundle size by 25% through code splitting. " +
        "I've also worked extensively with React hooks, context API, and have experience migrating class components to functional components. " +
        "One of my notable achievements was optimizing rendering performance in a list component that displayed thousands of items, reducing render time by 70% through virtualization and memoization techniques.";
      
      setAnswer(generatedAnswer);
      setEvaluating(false);
    }, 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center">
            <div className="spinner mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading question...</p>
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
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Interview Question</h1>
        
        <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">{question?.text}</h2>
            
            <div className="mb-6">
              <label htmlFor="answer" className="block text-sm font-medium text-gray-700 mb-2">
                Your Answer:
              </label>
              <textarea
                id="answer"
                rows="8"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Type your answer here..."
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
              ></textarea>
            </div>
            
            <div className="flex flex-wrap gap-4">
              <button
                onClick={handleSubmitAnswer}
                disabled={evaluating}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
              >
                {evaluating ? 'Evaluating...' : 'Submit Answer'}
              </button>
              
              <button
                onClick={handleGenerateAnswer}
                disabled={evaluating}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition disabled:opacity-50"
              >
                {evaluating ? 'Generating...' : 'Generate Sample Answer'}
              </button>
            </div>
          </div>
        </div>
        
        {evaluation && (
          <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Evaluation Result</h3>
              
              <div className="mb-4">
                <div className="flex items-center">
                  <span className="text-gray-700 font-medium">Score:</span>
                  <div className="ml-2 flex-1 max-w-xs">
                    <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${
                          evaluation.score >= 80 ? 'bg-green-500' : 
                          evaluation.score >= 60 ? 'bg-yellow-500' : 
                          'bg-red-500'
                        }`}
                        style={{ width: `${evaluation.score}%` }}
                      ></div>
                    </div>
                  </div>
                  <span className="ml-2 font-semibold">{evaluation.score}%</span>
                </div>
              </div>
              
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700">Feedback:</h4>
                <p className="mt-1 text-gray-600">{evaluation.feedback}</p>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-700">Improvement Suggestions:</h4>
                <p className="mt-1 text-gray-600">{evaluation.improvement_suggestions}</p>
              </div>
            </div>
          </div>
        )}
        
        <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Reference Answer</h3>
            <p className="text-gray-600">{question?.reference_answer}</p>
          </div>
        </div>
        
        <div className="mt-6">
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition"
          >
            Back to Questions
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuestionDetailPage; 