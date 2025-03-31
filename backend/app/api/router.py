from fastapi import APIRouter, Depends, Request, HTTPException
from app.models import (
    JDAnalysisRequest, JDAnalysisResponse,
    QuestionGenerationRequest, QuestionGenerationResponse,
    AnswerEvaluationRequest, AnswerEvaluationResponse,
    AnswerGenerationRequest, AnswerGenerationResponse
)
from app.services.jd_service import JDService
from fastapi.responses import StreamingResponse
import asyncio
import json
import os
from datetime import datetime
from fastapi.responses import JSONResponse

# Create router
router = APIRouter()

# Updated dependency to get the singleton JD service from app state
def get_jd_service(request: Request):
    return request.app.state.jd_service

# Import all the endpoints from endpoints.py
from app.api.endpoints import (
    analyze_jd,
    generate_questions,
    evaluate_answer,
    generate_answer,
    generate_answer_stream,
    debug_question,
    get_logs
)

# Register the endpoints with the router
router.post("/analyze-jd", response_model=JDAnalysisResponse)(analyze_jd)
router.post("/generate-questions", response_model=QuestionGenerationResponse)(generate_questions)
router.post("/evaluate-answer", response_model=AnswerEvaluationResponse)(evaluate_answer)
router.post("/generate-answer", response_model=AnswerGenerationResponse)(generate_answer)
router.post("/generate-answer-stream")(generate_answer_stream)
router.get("/debug-question/{question_id}")(debug_question)
router.get("/logs/{log_type}")(get_logs) 