import React, { useState } from 'react';
import JDInput from './components/JDInput';
import QuestionGenerator from './components/QuestionGenerator';
import QuestionList from './components/QuestionList';
import ResultsDashboard from './components/ResultsDashboard';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import JDAnalyzerPage from './pages/JDAnalyzerPage';
import QuestionsPage from './pages/QuestionsPage';
import QuestionDetailPage from './pages/QuestionDetailPage';
import LogsPage from './pages/LogsPage';
import Navbar from './components/Navbar';

function App() {
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
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <Routes>
          <Route path="/" element={<JDAnalyzerPage />} />
          <Route path="/questions/:jdId" element={<QuestionsPage />} />
          <Route path="/question/:questionId" element={<QuestionDetailPage />} />
          <Route path="/logs" element={<LogsPage />} />
          <Route path="/logs/:logType" element={<LogsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 