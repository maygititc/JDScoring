import React, { useState, useEffect } from 'react';
import { evaluateAnswer, generateModelAnswer, generateModelAnswerStream } from '../services/api';

// Store questions in localStorage when they're received
const storeQuestionsLocally = (questions) => {
  try {
    const questionsMap = {};
    questions.forEach(q => {
      questionsMap[q.id] = {
        text: q.text,
        reference_answer: q.reference_answer
      };
    });
    localStorage.setItem('storedQuestions', JSON.stringify(questionsMap));
    console.log('Questions stored locally:', questionsMap);
  } catch (e) {
    console.error('Error storing questions locally:', e);
  }
};

// Get a question from localStorage by ID
const getQuestionFromLocalStorage = (questionId) => {
  try {
    const storedQuestions = JSON.parse(localStorage.getItem('storedQuestions') || '{}');
    return storedQuestions[questionId];
  } catch (e) {
    console.error('Error retrieving question from localStorage:', e);
    return null;
  }
};

const QuestionItem = ({ question, onAnswerEvaluated }) => {
  const [userAnswer, setUserAnswer] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isGeneratingAnswer, setIsGeneratingAnswer] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [generatedAnswer, setGeneratedAnswer] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!userAnswer.trim()) {
      alert("Please enter an answer before submitting.");
      return;
    }
    
    setIsEvaluating(true);
    
    try {
      // Get the question from localStorage as a backup
      const storedQuestion = getQuestionFromLocalStorage(question.id);
      
      // Log the stored question for debugging
      console.log("Stored question from localStorage:", storedQuestion);
      
      // Use the reference answer from props or localStorage
      const referenceAnswer = question.reference_answer || 
                             (storedQuestion ? storedQuestion.reference_answer : "");
      
      console.log("Using reference answer:", referenceAnswer.substring(0, 50) + "...");
      
      // Try to fetch the question data from the backend first
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/debug-question/${question.id}`);
        const debugData = await response.json();
        console.log("Debug question data from backend:", debugData);
      } catch (err) {
        console.error("Error fetching debug data:", err);
      }
      
      const result = await evaluateAnswer(
        question.id, 
        userAnswer, 
        referenceAnswer
      );
      
      console.log("Evaluation result:", result);
      
      setEvaluation(result);
      onAnswerEvaluated(question.id, result.score);
    } catch (err) {
      console.error('Error evaluating answer:', err);
      
      // Set a fallback evaluation
      const fallbackEvaluation = {
        score: 50.0,
        feedback: "We encountered an error while evaluating your answer.",
        improvement_suggestions: "Please try again or check your network connection."
      };
      
      setEvaluation(fallbackEvaluation);
      onAnswerEvaluated(question.id, fallbackEvaluation.score);
    } finally {
      setIsEvaluating(false);
    }
  };

  // New function to generate an answer with streaming
  const handleGenerateAnswerStream = async () => {
    setIsGeneratingAnswer(true);
    setGeneratedAnswer(''); // Clear any previous answer
    
    let streamedAnswer = '';
    let receivedAnyContent = false;
    let wordCount = 0;
    const wordLimit = 100;
    
    try {
      console.log(`Requesting streaming answer generation (limit: ${wordLimit} words) for question:`, question.text);
      
      // Set a timeout to detect if streaming is taking too long
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error("Streaming timeout")), 10000);
      });
      
      // Create the streaming request
      const streamingPromise = generateModelAnswerStream(question.text, (chunk) => {
        if (chunk && chunk.trim()) {
          receivedAnyContent = true;
          
          // Add the chunk to the answer
          streamedAnswer += chunk;
          
          // Count words and truncate if needed
          const words = streamedAnswer.split(/\s+/);
          wordCount = words.length;
          
          // If we've exceeded the word limit, truncate
          if (wordCount > wordLimit) {
            streamedAnswer = words.slice(0, wordLimit).join(' ') + '...';
            console.log(`Answer truncated to ${wordLimit} words`);
          }
          
          // Update the displayed answer
          setGeneratedAnswer(streamedAnswer);
          
          // Also update the user answer textarea in real-time
          setUserAnswer(streamedAnswer);
        }
      });
      
      // Race the streaming request against the timeout
      await Promise.race([streamingPromise, timeoutPromise]);
      
      // If we didn't receive any content, use fallback
      if (!receivedAnyContent) {
        console.warn("No content received from streaming endpoint");
        const fallbackAnswer = await generateFallbackAnswer(question.text, wordLimit);
        setGeneratedAnswer(fallbackAnswer);
        setUserAnswer(fallbackAnswer);
      } else {
        console.log(`Successfully generated streaming answer (${wordCount} words)`);
      }
    } catch (err) {
      console.error('Error generating streaming answer:', err);
      
      // If streaming fails, fall back to the regular method
      try {
        console.log("Falling back to non-streaming answer generation");
        const response = await generateModelAnswer(question.text, wordLimit);
        
        if (response && response.answer) {
          setGeneratedAnswer(response.answer);
          setUserAnswer(response.answer);
        } else {
          const fallbackAnswer = await generateFallbackAnswer(question.text, wordLimit);
          setGeneratedAnswer(fallbackAnswer);
          setUserAnswer(fallbackAnswer);
        }
      } catch (fallbackErr) {
        console.error('Fallback answer generation also failed:', fallbackErr);
        const fallbackAnswer = await generateFallbackAnswer(question.text, wordLimit);
        setGeneratedAnswer(fallbackAnswer);
        setUserAnswer(fallbackAnswer);
      }
    } finally {
      setIsGeneratingAnswer(false);
    }
  };

  // Replace the hardcoded generateFallbackAnswer function with a dynamic one
  const generateFallbackAnswer = async (questionText, wordLimit = 100) => {
    try {
      // Try to generate a fallback answer using the non-streaming API
      console.log(`Generating fallback answer (limit: ${wordLimit} words) for:`, questionText);
      const response = await generateModelAnswer(questionText, wordLimit);
      
      if (response && response.answer) {
        return response.answer;
      }
      
      throw new Error("Empty response from fallback generator");
    } catch (err) {
      console.error("Error generating fallback answer:", err);
      
      // If all else fails, return a generic response
      return "I couldn't generate a specific answer at this time. Please write your own answer based on your experience and knowledge relevant to this question.";
    }
  };

  return (
    <div className="mb-6 p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
      <div 
        className="flex justify-between items-start cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3 className="text-lg font-medium text-gray-900 flex-1 pr-4">{question.text}</h3>
        <span className="text-blue-600">
          {isExpanded ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 011.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          )}
        </span>
      </div>
      
      {isExpanded && (
        <div className="mt-4">
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor={`answer-${question.id}`} className="block text-sm font-medium text-gray-700 mb-1">
                Your Answer
              </label>
              <textarea
                id={`answer-${question.id}`}
                rows="6"
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                placeholder="Type your answer here..."
              ></textarea>
            </div>
            
            <div className="flex space-x-2 mb-4">
              <button
                type="submit"
                disabled={isEvaluating}
                className="py-2 px-4 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 disabled:bg-green-300"
              >
                {isEvaluating ? 'Evaluating...' : 'Submit Answer'}
              </button>
              
              {/* Generate Answer button */}
              <button
                onClick={handleGenerateAnswerStream}
                disabled={isGeneratingAnswer}
                className="py-2 px-4 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-blue-300"
              >
                {isGeneratingAnswer ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </span>
                ) : "Generate Answer"}
              </button>
              
              {/* Debug button - only show in development mode */}
              {process.env.NODE_ENV === 'development' && (
                <button
                  onClick={async () => {
                    setIsGeneratingAnswer(true);
                    try {
                      // Try the non-streaming version as a fallback
                      const wordLimit = 100;
                      const response = await generateModelAnswer(question.text, wordLimit);
                      if (response && response.answer) {
                        setGeneratedAnswer(response.answer);
                        setUserAnswer(response.answer);
                        console.log(`Successfully generated non-streaming answer (${response.answer.split(/\s+/).length} words)`);
                      } else {
                        throw new Error("Empty response from non-streaming endpoint");
                      }
                    } catch (err) {
                      console.error("Debug button error:", err);
                      const fallbackAnswer = await generateFallbackAnswer(question.text, 100);
                      setGeneratedAnswer(fallbackAnswer);
                      setUserAnswer(fallbackAnswer);
                    } finally {
                      setIsGeneratingAnswer(false);
                    }
                  }}
                  className="py-2 px-4 bg-purple-600 text-white font-semibold rounded-md hover:bg-purple-700"
                  disabled={isGeneratingAnswer}
                >
                  Debug Generate (Non-Streaming)
                </button>
              )}
            </div>
            
            {/* Display the generated answer */}
            {generatedAnswer && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <h4 className="text-sm font-medium text-green-800 mb-1">Generated Answer:</h4>
                <p className="text-sm text-green-700">{generatedAnswer}</p>
              </div>
            )}
            
            {evaluation && (
              <div className="mt-4">
                <div className="flex items-center mb-2">
                  <span className="font-medium mr-2">Score:</span>
                  <span 
                    className={
                      evaluation.score >= 80 ? 'text-green-600 font-bold' : 
                      evaluation.score >= 60 ? 'text-yellow-600 font-bold' : 
                      'text-red-600 font-bold'
                    }
                  >
                    {evaluation.score.toFixed(1)}%
                  </span>
                </div>
                
                <div className="mb-2">
                  <span className="font-medium">Feedback:</span>
                  <p className="text-gray-700">{evaluation.feedback}</p>
                </div>
                
                <div>
                  <span className="font-medium">Improvement Suggestions:</span>
                  <p className="text-gray-700">{evaluation.improvement_suggestions}</p>
                </div>
              </div>
            )}
          </form>
        </div>
      )}
    </div>
  );
};

const QuestionList = ({ questions, onAnswerEvaluated, onNavigateToResults }) => {
  const [scores, setScores] = useState({});
  
  // Store questions in localStorage when they're received
  useEffect(() => {
    if (questions && questions.length > 0) {
      storeQuestionsLocally(questions);
    }
  }, [questions]);
  
  const handleAnswerEvaluated = (questionId, score) => {
    setScores(prev => {
      const newScores = {
        ...prev,
        [questionId]: score
      };
      
      // Notify parent component about the updated scores
      onAnswerEvaluated(questionId, score);
      
      // Log progress
      console.log(`Question progress: ${Object.keys(newScores).length}/${questions.length}`);
      
      return newScores;
    });
  };
  
  const calculateOverallScore = () => {
    const scoreValues = Object.values(scores);
    if (scoreValues.length === 0) return 0;
    
    return scoreValues.reduce((sum, score) => sum + score, 0) / scoreValues.length;
  };
  
  const answeredCount = Object.keys(scores).length;
  const totalCount = questions.length;
  const overallScore = calculateOverallScore();

  const areAllQuestionsAnswered = () => {
    return questions.length > 0 && Object.keys(scores).length === questions.length;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Interview Questions</h2>
      
      <div className="mb-6 p-4 bg-blue-50 rounded-md">
        <div className="flex justify-between items-center">
          <div>
            <span className="font-medium">Progress: </span>
            <span>{answeredCount} of {totalCount} questions answered</span>
          </div>
          <div>
            <span className="font-medium">Overall Score: </span>
            <span 
              className={
                overallScore >= 80 ? 'text-green-600 font-bold' : 
                overallScore >= 60 ? 'text-yellow-600 font-bold' : 
                'text-red-600 font-bold'
              }
            >
              {overallScore.toFixed(1)}%
            </span>
          </div>
        </div>
        
        <div className="mt-2 w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className={`h-2.5 rounded-full ${
              overallScore >= 80 ? 'bg-green-600' : 
              overallScore >= 60 ? 'bg-yellow-500' : 
              'bg-red-600'
            }`}
            style={{ width: `${(answeredCount / totalCount) * 100}%` }}
          ></div>
        </div>
      </div>
      
      {questions.length === 0 ? (
        <div className="p-4 bg-yellow-100 text-yellow-800 rounded-md">
          No questions were generated. Please go back and try again with different settings.
        </div>
      ) : (
        questions.map(question => (
          <QuestionItem 
            key={question.id} 
            question={question} 
            onAnswerEvaluated={handleAnswerEvaluated}
          />
        ))
      )}

      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 p-4 bg-gray-100 rounded-md">
          <div className="flex space-x-2">
            <button
              onClick={async () => {
                // Mark all UNANSWERED questions as answered with a score of 75
                const debugScores = { ...scores }; // Start with existing scores
                
                // For each question, check if it's already answered
                for (const q of questions) {
                  // Skip questions that already have scores
                  if (debugScores[q.id] !== undefined) {
                    console.log(`Debug: Preserving existing score ${debugScores[q.id]} for question ${q.id}`);
                    continue;
                  }
                  
                  try {
                    // Generate a mock answer for each unanswered question
                    const mockAnswer = await generateFallbackAnswer(q.text, 100);
                    
                    // Create a mock evaluation result
                    const mockEvaluation = {
                      score: 75,
                      feedback: "This is a mock evaluation generated by the debug button.",
                      improvement_suggestions: "Since this is a debug feature, no real improvement suggestions are available."
                    };
                    
                    // Store the score
                    debugScores[q.id] = 75;
                    
                    // Notify parent component about the score
                    onAnswerEvaluated(q.id, 75);
                    
                    // Log the mock answer and evaluation
                    console.log(`Debug: Generated mock answer for question ${q.id}:`, mockAnswer.substring(0, 50) + "...");
                    console.log(`Debug: Created mock evaluation for question ${q.id}:`, mockEvaluation);
                  } catch (err) {
                    console.error(`Error generating mock data for question ${q.id}:`, err);
                    // Still add a score even if there's an error
                    debugScores[q.id] = 75;
                    onAnswerEvaluated(q.id, 75);
                  }
                }
                
                // Update local state
                setScores(debugScores);
                
                console.log("Debug: Force moved to results with scores:", debugScores);
                
                // Navigate to results using the prop
                if (onNavigateToResults) {
                  onNavigateToResults(debugScores);
                }
              }}
              className="py-2 px-4 bg-gray-600 text-white font-semibold rounded-md"
            >
              Force Move to Results
            </button>
            
            <button
              onClick={() => {
                // Clear all scores
                setScores({});
                console.log("Debug: Cleared all scores");
              }}
              className="py-2 px-4 bg-red-600 text-white font-semibold rounded-md"
            >
              Clear All Scores
            </button>
          </div>
        </div>
      )}

      {areAllQuestionsAnswered() && (
        <div className="mt-4 text-center">
          <button
            onClick={() => {
              // Use the navigation prop instead of direct navigation
              console.log("Navigating to results with scores:", scores);
              if (onNavigateToResults) {
                onNavigateToResults(scores);
              }
            }}
            className="py-2 px-6 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700"
          >
            View Your Results
          </button>
        </div>
      )}
    </div>
  );
};

export default QuestionList; 