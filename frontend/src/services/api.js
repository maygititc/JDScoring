import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const analyzeJD = async (jdText) => {
  try {
    const response = await api.post('/analyze-jd', { jd_text: jdText });
    return response.data;
  } catch (error) {
    console.error('Error analyzing JD:', error);
    throw error;
  }
};

export const generateQuestions = async (jdText, questionCount) => {
  try {
    console.log(`Sending request to generate ${questionCount} questions:`, { 
      jdTextLength: jdText.length,
      jdTextPreview: jdText.substring(0, 50) + "..." 
    });
    
    const response = await api.post('/generate-questions', { 
      jd_text: jdText, 
      question_count: questionCount 
    });
    
    console.log(`Received ${response.data.questions?.length || 0} questions from API (requested ${questionCount})`);
    return response.data;
  } catch (error) {
    console.error('Error generating questions:', error);
    throw error;
  }
};

export const evaluateAnswer = async (questionId, userAnswer, referenceAnswer) => {
  try {
    // Get the question from localStorage as a backup
    const storedQuestion = getQuestionFromLocalStorage(questionId);
    
    console.log("Sending request to evaluate answer:", { 
      questionId, 
      userAnswerLength: userAnswer.length,
      referenceAnswerLength: referenceAnswer ? referenceAnswer.length : 0,
      storedQuestionFound: !!storedQuestion
    });
    
    // Include the question text and reference answer directly in the request
    // This is a workaround for the backend issue
    const payload = {
      question_id: questionId,
      user_answer: userAnswer,
      reference_answer: referenceAnswer || "",
    };
    
    // If we have the question stored locally, include it in the request
    if (storedQuestion) {
      payload.question_text = storedQuestion.text;
      // Only use the stored reference answer if none was provided
      if (!referenceAnswer) {
        payload.reference_answer = storedQuestion.reference_answer;
      }
    }
    
    console.log("Full evaluation request payload:", {
      ...payload,
      user_answer: payload.user_answer.substring(0, 50) + "...",
      reference_answer: payload.reference_answer.substring(0, 50) + "..."
    });
    
    const response = await api.post('/evaluate-answer', payload);
    
    console.log("Response from evaluate answer:", response.data);
    return response.data;
  } catch (error) {
    console.error('Error evaluating answer:', error);
    
    // Return a fallback response instead of throwing
    return {
      score: 50.0,
      feedback: "We encountered an error while evaluating your answer.",
      improvement_suggestions: "Please try again or check your network connection."
    };
  }
};

export const generateModelAnswer = async (questionText, wordLimit = 100) => {
  try {
    console.log(`Generating model answer for question (limit: ${wordLimit} words):`, questionText);
    
    const response = await api.post('/generate-answer', { 
      question_text: questionText,
      word_limit: wordLimit
    });
    
    console.log("Generated answer:", response.data);
    return response.data;
  } catch (error) {
    console.error('Error generating answer:', error);
    
    // Return a fallback response instead of throwing
    return {
      answer: "I couldn't generate an answer at this time. Please try again later or write your own answer."
    };
  }
};

// Generate an answer for a question with streaming support
export const generateModelAnswerStream = async (questionText, onChunk, wordLimit = 100) => {
  try {
    console.log(`Starting streaming request (limit: ${wordLimit} words) for:`, questionText);
    
    const response = await fetch(`${import.meta.env.VITE_API_URL}/generate-answer-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        question_text: questionText,
        word_limit: wordLimit
      }),
    });

    if (!response.ok) {
      console.error(`API error: ${response.status}`);
      throw new Error(`API error: ${response.status}`);
    }

    if (!response.body) {
      console.error("ReadableStream not supported in this browser.");
      throw new Error("ReadableStream not supported in this browser.");
    }

    // Get the reader from the response body stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    console.log("Stream connected, waiting for chunks...");
    
    // Read the stream
    let receivedData = false;
    let totalWords = 0;
    const maxWords = wordLimit;
    let shouldStop = false;
    
    while (true && !shouldStop) {
      const { done, value } = await reader.read();
      
      if (done) {
        console.log("Stream complete");
        break;
      }
      
      receivedData = true;
      // Decode the chunk and pass it to the callback
      const chunk = decoder.decode(value, { stream: true });
      console.log("Received chunk of length:", chunk.length);
      
      if (chunk.trim()) {
        // Count words to enforce the limit
        const words = chunk.split(/\s+/);
        totalWords += words.length;
        
        if (totalWords > maxWords) {
          console.log(`Word limit reached (${maxWords}), stopping stream`);
          shouldStop = true;
        }
        
        onChunk(chunk);
      }
    }
    
    if (!receivedData) {
      console.warn("No data received from stream");
    }
    
    return { success: receivedData };
  } catch (error) {
    console.error('Error generating answer stream:', error);
    throw error;
  }
};

// Add this function to the api.js file
const getQuestionFromLocalStorage = (questionId) => {
  try {
    const storedQuestions = JSON.parse(localStorage.getItem('storedQuestions') || '{}');
    return storedQuestions[questionId];
  } catch (e) {
    console.error('Error retrieving question from localStorage:', e);
    return null;
  }
};

// Logs API functions
export const fetchLogs = async (logType, date, credentials) => {
  try {
    const response = await api.get(`/logs/${logType}?date=${date}`, {
      headers: {
        'Authorization': `Basic ${credentials}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching logs:', error);
    throw new Error(error.response?.data?.error || error.message || 'Failed to fetch logs');
  }
};

export default api; 