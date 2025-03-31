import React, { useState } from 'react';
import JDInput from '../components/JDInput';
import QuestionGenerator from '../components/QuestionGenerator';
import QuestionList from '../components/QuestionList';
import ResultsDashboard from '../components/ResultsDashboard';

const JDAnalyzerPage = () => {
  const [step, setStep] = useState(1);
  const [jdText, setJdText] = useState('');
  const [jdOverview, setJdOverview] = useState('');
  const [questions, setQuestions] = useState([]);
  const [scores, setScores] = useState({});
  
  const handleJDValidated = (text, overview) => {
    setJdText(text);
    setJdOverview(overview);
    setStep(2);
  };
  
  const handleQuestionsGenerated = (generatedQuestions) => {
    if (generatedQuestions && generatedQuestions.length > 0) {
      setQuestions(generatedQuestions);
      // Reset scores when new questions are generated
      setScores({});
      setStep(3);
    } else {
      alert("No questions were generated. Please try again.");
    }
  };
  
  const handleAnswerEvaluated = (questionId, score) => {
    setScores(prev => {
      const newScores = {
        ...prev,
        [questionId]: score
      };
      
      // Check if all questions have been answered
      console.log(`Answered ${Object.keys(newScores).length} of ${questions.length} questions`);
      
      // If all questions are answered, move to results after a short delay
      if (Object.keys(newScores).length >= questions.length) {
        console.log("All questions answered, moving to results...");
        setTimeout(() => setStep(4), 1000); // Add a small delay for better UX
      }
      
      return newScores;
    });
  };
  
  const handleReset = () => {
    setStep(1);
    setJdText('');
    setJdOverview('');
    setQuestions([]);
    setScores({});
  };
  
  const getStepName = () => {
    switch (step) {
      case 1: return "Job Description Input";
      case 2: return "Generate Questions";
      case 3: return "Answer Questions";
      case 4: return "Results";
      default: return "";
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-800">JD Analyzer & Interview Question Generator</h1>
          <p className="text-gray-600 mt-2">Analyze job descriptions and generate relevant interview questions</p>
        </header>
        
        <div className="mb-8">
          <div className="flex items-center">
            {[1, 2, 3, 4].map((s) => (
              <React.Fragment key={s}>
                <div 
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    s === step ? 'bg-blue-600 text-white' : 
                    s < step ? 'bg-green-500 text-white' : 
                    'bg-gray-300 text-gray-700'
                  }`}
                >
                  {s < step ? '✓' : s}
                </div>
                {s < 4 && (
                  <div 
                    className={`h-1 flex-1 ${
                      s < step ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  ></div>
                )}
              </React.Fragment>
            ))}
          </div>
          <div className="mt-2 text-center font-medium text-gray-700">
            {getStepName()}
          </div>
        </div>
        
        {step === 1 && (
          <JDInput onJDValidated={handleJDValidated} />
        )}
        
        {step === 2 && (
          <>
            <div className="mb-6 p-4 bg-white rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-2">Job Description Overview</h3>
              <p className="text-gray-700">{jdOverview}</p>
            </div>
            <QuestionGenerator 
              jdText={jdText} 
              onQuestionsGenerated={handleQuestionsGenerated} 
            />
          </>
        )}
        
        {step === 3 && (
          <QuestionList 
            questions={questions} 
            onAnswerEvaluated={handleAnswerEvaluated}
          />
        )}
        
        {step === 4 && (
          <ResultsDashboard 
            scores={scores} 
            questions={questions}
            onReset={handleReset}
          />
        )}
      </div>
    </div>
  );
};

export default JDAnalyzerPage; 