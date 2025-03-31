import React, { useState } from 'react';
import { analyzeJD } from '../services/api';

const JDInput = ({ onJDValidated }) => {
  const [jdText, setJdText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (jdText.length < 200) {
      setError('Job description must be at least 200 characters');
      return;
    }
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const result = await analyzeJD(jdText);
      setAnalysisResult(result);
      
      if (result.is_valid_jd && result.confidence >= 80) {
        onJDValidated(jdText, result.overview);
      }
    } catch (err) {
      setError('Error analyzing job description. Please try again.');
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Job Description Analysis</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="jd-text" className="block text-sm font-medium text-gray-700 mb-1">
            Paste Job Description
          </label>
          <textarea
            id="jd-text"
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            rows="10"
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste job description here (minimum 200 characters)"
            required
          />
          <div className="mt-1 text-sm text-gray-500">
            Character count: {jdText.length} (minimum 200)
          </div>
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
        
        <button
          type="submit"
          className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          disabled={isAnalyzing || jdText.length < 200}
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Job Description'}
        </button>
      </form>
      
      {analysisResult && (
        <div className="mt-6 p-4 border rounded-md">
          <h3 className="text-lg font-semibold mb-2">Analysis Result</h3>
          <div className="mb-2">
            <span className="font-medium">Valid Job Description: </span>
            <span className={analysisResult.is_valid_jd ? 'text-green-600' : 'text-red-600'}>
              {analysisResult.is_valid_jd ? 'Yes' : 'No'}
            </span>
          </div>
          <div className="mb-2">
            <span className="font-medium">Confidence: </span>
            <span className={analysisResult.confidence >= 80 ? 'text-green-600' : 'text-yellow-600'}>
              {analysisResult.confidence.toFixed(1)}%
            </span>
          </div>
          {analysisResult.overview && (
            <div className="mb-2">
              <span className="font-medium">Overview: </span>
              <p className="mt-1 text-gray-700">{analysisResult.overview}</p>
            </div>
          )}
          
          {analysisResult.is_valid_jd && analysisResult.confidence >= 80 ? (
            <div className="mt-4 p-3 bg-green-100 text-green-700 rounded-md">
              Job description validated successfully! You can now generate questions.
            </div>
          ) : (
            <div className="mt-4 p-3 bg-yellow-100 text-yellow-700 rounded-md">
              This text doesn't appear to be a valid job description or has low confidence. 
              Please try with a different text.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default JDInput; 