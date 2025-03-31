import React from 'react';

const ResultsDashboard = ({ scores, questions, onReset }) => {
  const calculateOverallScore = () => {
    const scoreValues = Object.values(scores);
    if (scoreValues.length === 0) return 0;
    
    return scoreValues.reduce((sum, score) => sum + score, 0) / scoreValues.length;
  };
  
  const overallScore = calculateOverallScore();
  const answeredCount = Object.keys(scores).length;
  const totalCount = questions.length;
  
  // Group questions by score ranges
  const excellentQuestions = [];
  const goodQuestions = [];
  const needsImprovementQuestions = [];
  
  questions.forEach(question => {
    const score = scores[question.id];
    if (score === undefined) return;
    
    if (score >= 80) {
      excellentQuestions.push({ ...question, score });
    } else if (score >= 60) {
      goodQuestions.push({ ...question, score });
    } else {
      needsImprovementQuestions.push({ ...question, score });
    }
  });

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Results Summary</h2>
      
      <div className="mb-6 p-4 bg-blue-50 rounded-md">
        <div className="text-center mb-4">
          <span className="text-3xl font-bold 
            ${overallScore >= 80 ? 'text-green-600' : 
            overallScore >= 60 ? 'text-yellow-600' : 
            'text-red-600'}">
            {overallScore.toFixed(1)}%
          </span>
          <p className="text-gray-600">Overall Score</p>
        </div>
        
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <span className="text-xl font-bold text-green-600">{excellentQuestions.length}</span>
            <p className="text-gray-600">Excellent</p>
          </div>
          <div>
            <span className="text-xl font-bold text-yellow-600">{goodQuestions.length}</span>
            <p className="text-gray-600">Good</p>
          </div>
          <div>
            <span className="text-xl font-bold text-red-600">{needsImprovementQuestions.length}</span>
            <p className="text-gray-600">Needs Improvement</p>
          </div>
        </div>
        
        <div className="mt-4">
          <span className="font-medium">Completion: </span>
          <span>{answeredCount} of {totalCount} questions answered</span>
        </div>
      </div>
      
      {needsImprovementQuestions.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2 text-red-600">Areas for Improvement</h3>
          <ul className="list-disc pl-5">
            {needsImprovementQuestions.map(q => (
              <li key={q.id} className="mb-1">{q.text}</li>
            ))}
          </ul>
        </div>
      )}
      
      {excellentQuestions.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2 text-green-600">Strong Areas</h3>
          <ul className="list-disc pl-5">
            {excellentQuestions.map(q => (
              <li key={q.id} className="mb-1">{q.text}</li>
            ))}
          </ul>
        </div>
      )}
      
      <button
        onClick={onReset}
        className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Start New Assessment
      </button>
    </div>
  );
};

export default ResultsDashboard; 