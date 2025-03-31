import React, { useState } from 'react';
import { generateQuestions } from '../services/api';

const QuestionGenerator = ({ jdText, onQuestionsGenerated }) => {
  const [questionCount, setQuestionCount] = useState(10);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [detailedError, setDetailedError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    setError(null);
    setDetailedError(null);
    
    try {
      console.log(`Submitting request to generate ${questionCount} questions...`);
      const result = await generateQuestions(jdText, questionCount);
      console.log("Generated questions result:", result);
      
      if (result.questions && result.questions.length > 0) {
        console.log(`Successfully generated ${result.questions.length} questions (requested ${questionCount})`);
        
        // Check if we got the requested number of questions
        if (result.questions.length < questionCount) {
          console.warn(`Warning: Received fewer questions (${result.questions.length}) than requested (${questionCount})`);
        }
        
        onQuestionsGenerated(result.questions);
      } else {
        console.error("No questions were returned in the response");
        setError('No questions were generated. Please try again.');
      }
    } catch (err) {
      console.error("Question generation error:", err);
      setError('Error generating questions. Please try again.');
      
      // Extract and display more detailed error information
      if (err.response && err.response.data) {
        setDetailedError(JSON.stringify(err.response.data, null, 2));
      } else {
        setDetailedError(err.message || String(err));
      }
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Generate Interview Questions</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="question-count" className="block text-sm font-medium text-gray-700 mb-1">
            Number of Questions
          </label>
          <select
            id="question-count"
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value))}
          >
            <option value={5}>5 Questions</option>
            <option value={10}>10 Questions</option>
            <option value={20}>20 Questions</option>
            <option value={30}>30 Questions</option>
            <option value={40}>40 Questions</option>
            <option value={50}>50 Questions</option>
          </select>
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
            <p className="font-medium">{error}</p>
            {detailedError && (
              <details className="mt-2">
                <summary className="cursor-pointer text-sm">Show technical details</summary>
                <pre className="mt-2 text-xs overflow-auto p-2 bg-gray-100 rounded">
                  {detailedError}
                </pre>
              </details>
            )}
          </div>
        )}
        
        <button
          type="submit"
          className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          disabled={isGenerating}
        >
          {isGenerating ? 'Generating Questions...' : 'Generate Questions'}
        </button>
      </form>
    </div>
  );
};

export default QuestionGenerator; 