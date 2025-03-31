from fastapi import APIRouter, HTTPException, Depends, Request
from app.models import (
    JDAnalysisRequest, JDAnalysisResponse,
    QuestionGenerationRequest, QuestionGenerationResponse,
    AnswerEvaluationRequest, AnswerEvaluationResponse,
    AnswerGenerationRequest, AnswerGenerationResponse
)
from app.services.deepseek_service import DeepSeekService
from app.services.jd_service import JDService
import os
import re
import time
import json
from datetime import datetime
from typing import Optional
from fastapi.responses import StreamingResponse
import asyncio
from fastapi.responses import JSONResponse

router = APIRouter()

# Updated dependency to get the singleton JD service from app state
def get_jd_service(request: Request):
    return request.app.state.jd_service

@router.post("/analyze-jd", response_model=JDAnalysisResponse)
async def analyze_jd(request: JDAnalysisRequest, jd_service: JDService = Depends(get_jd_service)):
    """
    Analyze if the text is a job description
    """
    if len(request.jd_text) < 200:
        raise HTTPException(status_code=400, detail="Job description must be at least 200 characters")
    
    start_time = time.time()
    try:
        result = await jd_service.analyze_jd(request.jd_text)
        duration_ms = (time.time() - start_time) * 1000
        
        # Log the user interaction
        if hasattr(jd_service, 'logging_service'):
            jd_service.logging_service.log_user_interaction(
                interaction_type="analyze_jd",
                user_data={"jd_text_length": len(request.jd_text)},
                result=result
            )
            
            # Log the API call
            jd_service.logging_service.log_api_call(
                endpoint="/analyze-jd",
                request_data={"jd_text_length": len(request.jd_text)},
                response_data=result,
                duration_ms=duration_ms
            )
        
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        # Log the error
        if hasattr(jd_service, 'logging_service'):
            jd_service.logging_service.log_user_interaction(
                interaction_type="analyze_jd",
                user_data={"jd_text_length": len(request.jd_text)},
                error=str(e)
            )
            
            # Log the API call error
            jd_service.logging_service.log_api_call(
                endpoint="/analyze-jd",
                request_data={"jd_text_length": len(request.jd_text)},
                error=str(e),
                duration_ms=duration_ms
            )
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_questions(request: QuestionGenerationRequest, jd_service: JDService = Depends(get_jd_service)):
    """
    Generate questions based on the job description
    """
    print(f"Received request to generate {request.question_count} questions")
    print(f"JD text length: {len(request.jd_text)} characters")
    
    if len(request.jd_text) < 200:
        print("JD text too short")
        raise HTTPException(status_code=400, detail="Job description must be at least 200 characters")
    
    if request.question_count < 5 or request.question_count > 50:
        print(f"Invalid question count: {request.question_count}")
        raise HTTPException(status_code=400, detail="Question count must be between 5 and 50")
    
    try:
        questions = await jd_service.generate_questions(request.jd_text, request.question_count)
        
        print(f"Generated {len(questions)} questions (requested {request.question_count})")
        for i, q in enumerate(questions):
            print(f"Question {i+1}: {q.get('text', '')[:50]}...")
        
        # Return empty list if no questions were generated
        if not questions:
            print("No questions were generated")
            return {"questions": []}
            
        return {"questions": questions}
    except Exception as e:
        print(f"Exception in generate_questions endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@router.post("/evaluate-answer", response_model=AnswerEvaluationResponse)
async def evaluate_answer(request: AnswerEvaluationRequest, jd_service: JDService = Depends(get_jd_service)):
    """
    Evaluate a user's answer
    """
    print(f"Evaluating answer for question ID: {request.question_id}")
    print(f"User answer length: {len(request.user_answer)} characters")
    print(f"Reference answer length: {len(request.reference_answer)} characters")
    
    if not request.user_answer.strip():
        raise HTTPException(status_code=400, detail="User answer cannot be empty")
    
    try:
        # Check if we have the question in memory
        question_data = jd_service.questions.get(request.question_id)
        
        # If we don't have the question in memory but the request includes question_text,
        # store it in memory for future use
        if not question_data and hasattr(request, 'question_text') and request.question_text:
            print(f"Storing question from request: {request.question_text[:50]}...")
            jd_service.questions[request.question_id] = {
                "text": request.question_text,
                "reference_answer": request.reference_answer
            }
        
        result = await jd_service.evaluate_answer(
            request.question_id, request.user_answer, request.reference_answer
        )
        print(f"Evaluation result: score={result.get('score')}")
        return result
    except Exception as e:
        print(f"Exception in evaluate_answer endpoint: {str(e)}")
        # Return a fallback response instead of raising an exception
        return {
            "score": 50.0,
            "feedback": "We encountered an issue while evaluating your answer.",
            "improvement_suggestions": "Please try again or provide more details in your answer."
        }

@router.post("/generate-answer", response_model=AnswerGenerationResponse)
async def generate_answer(request: AnswerGenerationRequest, jd_service: JDService = Depends(get_jd_service)):
    """
    Generate an answer for a given question
    """
    print(f"Generating answer for question: {request.question_text[:100]}...")
    
    # Get the word limit from the request, default to 100
    word_limit = getattr(request, 'word_limit', 100)
    print(f"Using word limit: {word_limit}")
    
    try:
        answer = await jd_service.generate_answer(request.question_text)
        
        # Limit the answer to the specified word count
        words = answer.split()
        if len(words) > word_limit:
            answer = ' '.join(words[:word_limit]) + '...'
            print(f"Answer truncated to {word_limit} words")
        
        return {"answer": answer}
    except Exception as e:
        print(f"Exception in generate_answer endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-answer-stream")
async def generate_answer_stream(request: AnswerGenerationRequest, jd_service: JDService = Depends(get_jd_service)):
    """
    Generate an answer for a given question with streaming response
    """
    print(f"Generating streaming answer for question: {request.question_text[:100]}...")
    
    # Get the word limit from the request, default to 100
    word_limit = getattr(request, 'word_limit', 100)
    print(f"Using word limit: {word_limit}")
    
    # First, generate the full answer
    try:
        full_answer = await jd_service.generate_answer(request.question_text)
        print(f"Generated full answer of length {len(full_answer)}")
        
        # Limit the answer to the specified word count
        words = full_answer.split()
        if len(words) > word_limit:
            full_answer = ' '.join(words[:word_limit]) + '...'
            print(f"Answer truncated to {word_limit} words")
        
        # If we have a valid answer, stream it
        if full_answer and len(full_answer) > 20:
            async def stream_answer():
                # Split into sentences for more natural streaming
                sentences = re.split(r'(?<=[.!?])\s+', full_answer)
                
                for sentence in sentences:
                    yield f"{sentence} "
                    await asyncio.sleep(0.2)  # Delay between sentences
            
            return StreamingResponse(
                stream_answer(),
                media_type="text/plain"
            )
        else:
            # If we don't have a valid answer, return a fallback
            print("Warning: Generated answer was too short or empty")
            
            async def fallback_stream():
                fallback = "I couldn't generate a detailed answer at this time. Please try again or write your own answer based on your experience."
                words = fallback.split()
                
                for i in range(0, len(words), 3):
                    chunk = " ".join(words[i:i+3])
                    yield f"{chunk} "
                    await asyncio.sleep(0.1)
            
            return StreamingResponse(
                fallback_stream(),
                media_type="text/plain"
            )
    except Exception as e:
        print(f"Exception in generate_answer_stream endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a fallback response
        async def error_stream():
            error_msg = "I encountered an error while generating an answer. Please try again later or write your own answer."
            words = error_msg.split()
            
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3])
                yield f"{chunk} "
                await asyncio.sleep(0.1)
        
        return StreamingResponse(
            error_stream(),
            media_type="text/plain"
        )

@router.get("/test")
async def test_endpoint():
    """
    Test endpoint to verify API is working
    """
    return {"status": "ok", "message": "API is working"}

@router.get("/test-questions")
async def test_questions(jd_service: JDService = Depends(get_jd_service)):
    """
    Test endpoint to check stored questions
    """
    question_count = len(jd_service.questions)
    question_ids = list(jd_service.questions.keys())
    
    return {
        "question_count": question_count,
        "question_ids": question_ids,
        "questions": jd_service.questions
    }

@router.get("/debug-question/{question_id}")
async def debug_question(question_id: str, jd_service: JDService = Depends(get_jd_service)):
    """
    Debug endpoint to check a specific question
    """
    question_data = jd_service.questions.get(question_id)
    all_keys = list(jd_service.questions.keys())
    
    return {
        "question_found": question_data is not None,
        "question_data": question_data,
        "total_questions": len(jd_service.questions),
        "all_keys": all_keys,
        "key_in_dict": question_id in jd_service.questions
    }

@router.get("/test-answer-generation")
async def test_answer_generation(jd_service: JDService = Depends(get_jd_service)):
    """
    Test endpoint to check answer generation
    """
    test_question = "What experience do you have with Python programming?"
    
    try:
        answer = await jd_service.generate_answer(test_question)
        return {
            "question": test_question,
            "answer": answer,
            "answer_length": len(answer),
            "using_mock": jd_service.deepseek_service.use_mock
        }
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        return {
            "error": str(e),
            "traceback": trace
        }

@router.get("/test-all-answers")
async def test_all_answers(jd_service: JDService = Depends(get_jd_service)):
    """
    Test endpoint to check answer generation for different question types
    """
    test_questions = [
        "What experience do you have with Python programming?",
        "How would you integrate an external API into a web application?",
        "Describe your experience with database design and optimization.",
        "What is your approach to system architecture and design?",
        "How do you ensure code quality and testing in your projects?"
    ]
    
    results = []
    for question in test_questions:
        try:
            answer = await jd_service.generate_answer(question)
            results.append({
                "question": question,
                "answer_preview": answer[:100] + "..." if answer else "No answer generated",
                "answer_length": len(answer) if answer else 0,
                "success": bool(answer and len(answer) > 50)
            })
        except Exception as e:
            results.append({
                "question": question,
                "error": str(e)
            })
    
    return {
        "results": results,
        "using_mock": jd_service.deepseek_service.use_mock
    }

@router.post("/test-question-relevance")
async def test_question_relevance(request: QuestionGenerationRequest, jd_service: JDService = Depends(get_jd_service)):
    """
    Test endpoint to check if generated questions are relevant to the JD
    """
    try:
        # Extract key terms from the JD
        jd_text = request.jd_text.lower()
        key_terms = set()
        
        # Extract potential key terms (this is a simple approach)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', jd_text)
        for word in words:
            if word not in common_words:
                key_terms.add(word)
        
        # Generate questions
        questions = await jd_service.generate_questions(request.jd_text, request.question_count)
        
        # Check relevance of each question
        relevance_scores = []
        for q in questions:
            question_text = q.get('text', '').lower()
            reference_answer = q.get('reference_answer', '').lower()
            
            # Count how many key terms appear in the question and answer
            term_matches = sum(1 for term in key_terms if term in question_text or term in reference_answer)
            
            relevance_scores.append({
                "question": q.get('text'),
                "key_terms_matched": term_matches,
                "relevance_score": min(100, term_matches * 10)  # Simple scoring
            })
        
        return {
            "jd_key_terms": list(key_terms)[:20],  # Show top 20 terms
            "questions": questions,
            "relevance_analysis": relevance_scores,
            "average_relevance": sum(s["relevance_score"] for s in relevance_scores) / len(relevance_scores) if relevance_scores else 0
        }
    except Exception as e:
        return {
            "error": str(e)
        }

# Common English words to filter out
common_words = set([
    "the", "and", "that", "have", "for", "not", "with", "you", "this", "but",
    "his", "from", "they", "she", "will", "would", "there", "their", "what",
    "about", "which", "when", "make", "like", "time", "just", "know", "take",
    "person", "into", "year", "your", "good", "some", "could", "them", "see",
    "other", "than", "then", "now", "look", "only", "come", "its", "over",
    "think", "also", "back", "after", "use", "two", "how", "our", "work",
    "first", "well", "way", "even", "new", "want", "because", "any", "these",
    "give", "day", "most", "can", "are", "is", "be", "has", "was", "were",
    "had", "do", "does", "did", "doing", "done", "should", "must", "may",
    "might", "can", "could", "shall", "will", "would", "should", "must",
    "experience", "role", "job", "candidate", "skill", "ability", "work",
    "team", "project", "develop", "create", "build", "implement", "design",
    "manage", "lead", "communicate", "collaborate", "solve", "problem",
    "solution", "requirement", "responsibility", "qualification", "year"
])

@router.get("/logs/{log_type}")
async def get_logs(log_type: str, request: Request, date: str = None):
    """
    Get logs of a specific type for a specific date
    """
    # Set content type to JSON
    headers = {"Content-Type": "application/json"}
    
    print(f"Logs request received: type={log_type}, date={date}")
    
    # Basic authentication check
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Basic "):
        import base64
        try:
            # Decode the base64 credentials
            credentials = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = credentials.split(":")
            
            print(f"Auth credentials: username={username}")
            
            # Check if credentials are valid
            if username == os.getenv("USER_NAME", "") and password == os.getenv("USER_PASSWORD", ""):
                # Get the logging service
                logging_service = request.app.state.logging_service
                
                # Validate log type
                valid_types = ["api", "llm", "app"]
                if log_type not in valid_types:
                    print(f"Invalid log type: {log_type}")
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"Invalid log type. Must be one of: {', '.join(valid_types)}", "logs": []},
                        headers=headers
                    )
                
                # Get logs for the specified date
                logs = logging_service.get_logs(log_type, date)
                print(f"Found {len(logs)} logs for type={log_type}, date={date}")
                
                return JSONResponse(
                    content={"logs": logs},
                    headers=headers
                )
        except Exception as e:
            print(f"Error processing authentication: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Authentication error: {str(e)}", "logs": []},
                headers=headers
            )
    
    # If authentication fails or is not provided, return 401 Unauthorized
    print("Authentication failed or not provided")
    return JSONResponse(
        status_code=401,
        content={"error": "Unauthorized. Please provide valid credentials.", "logs": []},
        headers=headers
    ) 