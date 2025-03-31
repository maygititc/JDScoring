## Job Descriptions (JD) Scoring Using LLM (OpenAI, DeepSeek)

## Project Overview
Create a Single Page Application (SPA) using Python and FastAPI that processes Job Descriptions (JD) with the following multi-step workflow:
1. JD input and validation
2. JD analysis and overview generation
3. Question generation based on JD content
4. Answer evaluation and scoring system

## Technical Requirements

### Backend (FastAPI)
```
- Python 3.9+
- FastAPI framework
- DeepSeek API integration for LLM capabilities
- Pydantic for data validation
- Optional SQLite/PostgreSQL for data persistence
- CORS middleware for SPA integration
```

### Frontend (SPA)
```
- Modern JavaScript framework (React/Vue.js preferred)
- Axios for API communication
- Clean, responsive UI with TailwindCSS or similar
- Progressive enhancement for better UX
```

## Detailed Functional Requirements

### 1. JD Input and Validation
```
- Provide a large text area for JD input
- Implement real-time character count
- Submit button to send JD for analysis
- Backend endpoint (/analyze-jd) that:
  - Validates input is at least 200 characters
  - Uses DeepSeek API to analyze if text is >80% JD content
  - Returns analysis result with confidence percentage
  - Generates a 3-5 sentence overview of the JD
```

### 2. Question Generation
```
- If JD validation passes (>80% confidence):
  - Show dropdown with question count options (5,10,20,30,40,50)
  - Submit button to generate questions (/generate-questions)
  - Backend uses DeepSeek API to:
    - Create relevant questions based on JD content
    - Store correct answers for evaluation
    - Return questions in consistent JSON format
```

### 3. Answer Evaluation
```
- Display generated questions in clean list format
- Each question has:
  - Text area for user response
  - Submit button for individual question evaluation
- Evaluation endpoint (/evaluate-answer) that:
  - Compares user answer with stored correct answer
  - Uses DeepSeek for semantic comparison (not just exact match)
  - Returns correctness score (0-100%) with explanation
  - Updates overall test score
```

### 4. Scoring System
```
- Track and display:
  - Current question score
  - Cumulative test score
  - Time spent per question (optional)
- Visual indicators for performance
- Final summary upon completion
```

## API Specifications

### Endpoints
```
POST /analyze-jd
- Request: { "jd_text": "full job description text" }
- Response: { 
    "is_valid_jd": bool,
    "confidence": float,
    "overview": "generated overview text",
    "error": null|"message" 
}

POST /generate-questions
- Request: { "jd_text": "...", "question_count": int }
- Response: {
    "questions": [
        {
            "id": "uuid",
            "text": "question text",
            "reference_answer": "stored correct answer" 
        }
    ]
}

POST /evaluate-answer
- Request: { 
    "question_id": "uuid",
    "user_answer": "text",
    "reference_answer": "text" 
}
- Response: {
    "score": float,
    "feedback": "explanation of evaluation",
    "improvement_suggestions": "text" 
}
```

## UI/UX Requirements

### Core Components
```
1. JD Input Component:
   - Resizable text area
   - Real-time validation indicators
   - Clear error messages

2. Question Interface:
   - Accordion-style question display
   - Answer submission feedback
   - Score progression visualization

3. Results Dashboard:
   - Summary statistics
   - Export options (PDF/CSV)
   - Retake/Review options
```

## Quality Attributes

```
- Performance: <2s response time for all API calls
- Accessibility: WCAG AA compliant
- Security: Input sanitization, rate limiting
- Error Handling: Clear user feedback for all failure cases
```

## Deployment Considerations

```
- Docker containerization
- Environment variable configuration
- API key management
- Scalability considerations
```

## Example Prompt for DeepSeek Integration

"When analyzing JD text, use this prompt framework:
'Analyze the following text and determine if it constitutes a professional job description. Consider factors like presence of job responsibilities, required qualifications, and company information. Return confidence percentage (0-100%) and a concise 3-sentence overview highlighting key aspects if it is a JD.'"

## Success Metrics

```
- 90%+ accuracy in JD validation
- <5% false positives in question generation
- User satisfaction score >4/5 on answer evaluation
```

## Optional Enhancements

```
1. Session management for multi-user support
2. PDF/Word JD upload parsing
3. Question difficulty tagging
4. Time tracking per question
5. Comparative analytics across multiple JDs
```