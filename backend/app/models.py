from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid

class JDAnalysisRequest(BaseModel):
    jd_text: str = Field(..., min_length=200)

class JDAnalysisResponse(BaseModel):
    is_valid_jd: bool
    confidence: float
    overview: str
    error: Optional[str] = None

class QuestionGenerationRequest(BaseModel):
    jd_text: str
    question_count: int = Field(..., ge=5, le=50)

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    reference_answer: str

class QuestionGenerationResponse(BaseModel):
    questions: List[Question]

class AnswerEvaluationRequest(BaseModel):
    question_id: str
    user_answer: str
    reference_answer: str
    question_text: Optional[str] = None

class AnswerEvaluationResponse(BaseModel):
    score: float
    feedback: str
    improvement_suggestions: str

class AnswerGenerationRequest(BaseModel):
    question_text: str

class AnswerGenerationResponse(BaseModel):
    answer: str 