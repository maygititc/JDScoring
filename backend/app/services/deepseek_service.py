import os
import httpx
from typing import Dict, Any, List, Tuple
import json
import re
import time
import asyncio

class DeepSeekService:
    def __init__(self):
        # Get API key from OS environment variable
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        if not self.api_key:
            print("WARNING: DEEPSEEK_API_KEY environment variable is not set")
            # For development/testing, you can use a mock response
            self.use_mock = True
        else:
            self.use_mock = False
    
    async def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        if self.use_mock:
            print("Using mock response (no API key provided)")
            start_time = time.time()
            mock_response = self._get_mock_response(messages)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log the mock API call
            if hasattr(self, 'logging_service'):
                operation = self._determine_operation(messages)
                self.logging_service.log_deepseek_api(
                    operation=operation,
                    request_data={"messages": messages, "temperature": temperature},
                    response_data=mock_response,
                    duration_ms=duration_ms,
                    is_mock=True
                )
            
            return mock_response
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        print(f"Calling DeepSeek API with payload: {payload}")
        
        try:
            start_time = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                if response.status_code != 200:
                    error_text = response.text
                    print(f"DeepSeek API error: Status {response.status_code}, Response: {error_text}")
                    
                    # Log the failed API call
                    if hasattr(self, 'logging_service'):
                        operation = self._determine_operation(messages)
                        self.logging_service.log_deepseek_api(
                            operation=operation,
                            request_data={"messages": messages, "temperature": temperature},
                            error=f"Status {response.status_code}: {error_text}",
                            duration_ms=duration_ms,
                            is_mock=False
                        )
                    
                    raise Exception(f"DeepSeek API error: {error_text}")
                    
                response_data = response.json()
                
                # Log the successful API call
                if hasattr(self, 'logging_service'):
                    operation = self._determine_operation(messages)
                    self.logging_service.log_deepseek_api(
                        operation=operation,
                        request_data={"messages": messages, "temperature": temperature},
                        response_data=response_data,
                        duration_ms=duration_ms,
                        is_mock=False
                    )
                
                return response_data
        except Exception as e:
            print(f"Exception during API call: {str(e)}")
            
            # Log the exception
            if hasattr(self, 'logging_service'):
                operation = self._determine_operation(messages)
                self.logging_service.log_deepseek_api(
                    operation=operation,
                    request_data={"messages": messages, "temperature": temperature},
                    error=str(e),
                    is_mock=False
                )
            
            raise
    
    def _get_mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate mock responses for testing without an API key"""
        user_message = next((m["content"] for m in messages if m["role"] == "user"), "")
        
        if "generate" in user_message.lower() and "questions" in user_message.lower():
            # Try to extract the requested question count
            count_match = re.search(r'generate exactly (\d+)', user_message)
            question_count = int(count_match.group(1)) if count_match else 5
            
            # Extract the job description to generate more relevant mock questions
            jd_match = re.search(r'Job Description:\s*(.*?)(?:\n\s*Return your response|$)', user_message, re.DOTALL)
            jd_text = jd_match.group(1).strip() if jd_match else ""
            
            print(f"Generating mock response with {question_count} questions for JD: {jd_text[:100]}...")
            
            # Generate mock questions based on keywords in the JD
            mock_questions = []
            
            # Extract keywords from the JD
            jd_lower = jd_text.lower()
            keywords = []
            
            if "python" in jd_lower:
                keywords.append("Python")
            if "javascript" in jd_lower or "js" in jd_lower:
                keywords.append("JavaScript")
            if "react" in jd_lower:
                keywords.append("React")
            if "node" in jd_lower:
                keywords.append("Node.js")
            if "api" in jd_lower or "rest" in jd_lower:
                keywords.append("API")
            if "database" in jd_lower or "sql" in jd_lower:
                keywords.append("database")
            if "cloud" in jd_lower or "aws" in jd_lower or "azure" in jd_lower:
                keywords.append("cloud")
            if "docker" in jd_lower or "container" in jd_lower:
                keywords.append("Docker")
            if "agile" in jd_lower or "scrum" in jd_lower:
                keywords.append("Agile")
            if "test" in jd_lower or "qa" in jd_lower:
                keywords.append("testing")
            
            # If no keywords were found, use some defaults
            if not keywords:
                keywords = ["programming", "development", "software", "teamwork", "problem-solving"]
            
            # Generate questions based on the keywords
            for i in range(1, question_count + 1):
                # Cycle through the keywords
                keyword = keywords[(i-1) % len(keywords)]
                
                mock_questions.append({
                    "text": f"What experience do you have with {keyword} and how have you applied it in your previous roles?",
                    "reference_answer": f"A strong answer would demonstrate practical experience with {keyword}, including specific projects, challenges overcome, and measurable results achieved. The candidate should show both technical understanding and practical application of {keyword} in relevant contexts."
                })
            
            # Create the mock response
            mock_content = {
                "questions": mock_questions
            }
            
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(mock_content, indent=2)
                        }
                    }
                ]
            }
        elif "analyze" in user_message.lower() and "job description" in user_message.lower():
            # Mock response for JD analysis
            return {
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                                "is_valid": true,
                                "confidence": 95.5,
                                "overview": "This job description is for a Full Stack Developer position requiring Python, FastAPI, and frontend skills. The role involves building a system for processing job descriptions with LLM capabilities."
                            }
                            """
                        }
                    }
                ]
            }
        elif "evaluate" in user_message.lower() and "answer" in user_message.lower():
            # Mock response for answer evaluation
            return {
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                                "score": 85,
                                "feedback": "Your answer demonstrates good understanding of the core concepts.",
                                "improvement_suggestions": "Consider adding more specific examples from your experience."
                            }
                            """
                        }
                    }
                ]
            }
        elif "provide a comprehensive" in user_message.lower() and "answer" in user_message.lower():
            # Extract the question from the prompt
            question_match = re.search(r'Question:\s*(.*?)(?:\n|Your answer should:|$)', user_message, re.DOTALL)
            question = question_match.group(1).strip() if question_match else "the interview question"
            
            print(f"Generating mock answer for question: {question[:50]}...")
            
            # Generate a more specific mock answer based on keywords in the question
            question_lower = question.lower()
            
            if "python" in question_lower or "programming" in question_lower or "code" in question_lower:
                mock_answer = """
                I have extensive experience with Python programming, having used it for over 5 years in both professional and personal projects.
                
                In my professional work, I've developed several backend services using Python with frameworks like Flask and FastAPI. For example, I built a RESTful API service that processed and analyzed large datasets using pandas and numpy, which improved data processing speed by 40%.
                
                I'm proficient with Python's core libraries and follow best practices like PEP 8 style guidelines, type hinting, and comprehensive testing with pytest. I've also worked with asynchronous programming using asyncio for high-performance applications.
                """
            elif "api" in question_lower or "integration" in question_lower or "service" in question_lower:
                mock_answer = """
                I have significant experience integrating and working with external APIs in various projects. My approach typically follows these steps:
                
                1. First, I thoroughly review the API documentation to understand the endpoints, authentication methods, and data formats.
                
                2. For authentication, I implement secure handling of API keys or tokens, typically storing them as environment variables rather than hardcoding them in the application.
                
                3. I create a dedicated service layer or client class that encapsulates all API interactions, which helps maintain clean separation of concerns in the codebase.
                """
            elif "database" in question_lower or "sql" in question_lower or "data" in question_lower:
                mock_answer = """
                I have extensive experience working with both SQL and NoSQL databases. With SQL databases like PostgreSQL and MySQL, I'm proficient in designing normalized schemas, writing optimized queries, and implementing proper indexing strategies.
                
                For NoSQL solutions, I've worked with MongoDB for document storage, Redis for caching and message brokering, and Elasticsearch for full-text search capabilities. I understand the trade-offs between different database types and how to choose the right tool for specific requirements.
                """
            elif "architecture" in question_lower or "design" in question_lower or "system" in question_lower:
                mock_answer = """
                I approach system architecture and design with a focus on scalability, maintainability, and performance. I'm familiar with various architectural patterns including microservices, event-driven architecture, and layered architecture.
                
                When designing systems, I start by understanding the requirements and constraints, then break down the problem into manageable components. I consider factors like expected load, data flow, security requirements, and future extensibility.
                """
            else:
                mock_answer = """
                Based on my experience and expertise, I would approach this by first understanding the core requirements and constraints of the problem.
                
                In my previous roles, I've tackled similar challenges by breaking down complex problems into manageable components and implementing systematic solutions. For example, when working on a project that required optimizing performance, I conducted thorough analysis to identify bottlenecks and implemented targeted improvements that resulted in a 35% efficiency gain.
                """
            
            print(f"Generated mock answer: {mock_answer[:100]}...")
            
            return {
                "choices": [
                    {
                        "message": {
                            "content": mock_answer.strip()
                        }
                    }
                ]
            }
        else:
            # Default mock response
            return {
                "choices": [
                    {
                        "message": {
                            "content": "I'm not sure how to respond to that."
                        }
                    }
                ]
            }
    
    async def analyze_jd(self, jd_text: str) -> Tuple[bool, float, str]:
        """
        Analyze if the text is a job description and return confidence score and overview
        """
        prompt = f"""
        Analyze the following text and determine if it constitutes a professional job description. 
        Consider factors like presence of job responsibilities, required qualifications, and company information. 
        Return confidence percentage (0-100%) and a concise 3-sentence overview highlighting key aspects if it is a JD.
        
        Text to analyze:
        {jd_text}
        
        Return your response in JSON format with the following structure:
        {{
            "is_valid_jd": true/false,
            "confidence": 0-100,
            "overview": "3-sentence overview if valid"
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that analyzes job descriptions."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self._call_api(messages, temperature=0.3)
        content = response["choices"][0]["message"]["content"]
        
        try:
            result = json.loads(content)
            return (
                result["is_valid_jd"],
                result["confidence"],
                result["overview"] if result["is_valid_jd"] else ""
            )
        except (json.JSONDecodeError, KeyError):
            # Fallback parsing if the model doesn't return valid JSON
            is_valid = "true" in content.lower() and "false" not in content.lower()
            confidence = 0.0
            overview = ""
            
            # Try to extract confidence
            confidence_match = re.search(r'confidence"?\s*:\s*(\d+\.?\d*)', content)
            if confidence_match:
                confidence = float(confidence_match.group(1))
            
            # Try to extract overview
            overview_match = re.search(r'overview"?\s*:\s*"([^"]+)"', content)
            if overview_match:
                overview = overview_match.group(1)
                
            return is_valid, confidence, overview
    
    async def generate_questions(self, jd_text: str, question_count: int) -> List[Dict[str, str]]:
        """
        Generate questions based on the job description
        """
        prompt = f"""
        Based on the following job description, generate exactly {question_count} relevant interview questions 
        that would help assess a candidate's fit for this role. For each question, also provide a 
        reference answer that would be considered correct.
        
        The questions should:
        1. Be directly related to the specific skills, technologies, and requirements mentioned in the job description
        2. Cover both technical skills and soft skills required for the role
        3. Include questions about specific technologies mentioned in the JD
        4. Include questions about relevant experience for the role
        5. Be specific and tailored to this exact job, not generic interview questions
        
        Job Description:
        {jd_text}
        
        Return your response in JSON format with the following structure:
        {{
            "questions": [
                {{
                    "text": "question 1",
                    "reference_answer": "reference answer 1"
                }},
                {{
                    "text": "question 2",
                    "reference_answer": "reference answer 2"
                }},
                ...
            ]
        }}
        
        Important: Please generate exactly {question_count} questions, no more and no less.
        Important: Make sure each question is directly relevant to the specific job description provided.
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that helps generate relevant interview questions based on job descriptions."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._call_api(messages, temperature=0.5)
            content = response["choices"][0]["message"]["content"]
            
            print(f"Raw response from question generation: {content[:200]}...")
            
            try:
                result = json.loads(content)
                if "questions" in result and isinstance(result["questions"], list):
                    questions = result["questions"]
                    print(f"Parsed {len(questions)} questions from JSON response (requested {question_count})")
                    
                    # If we got fewer questions than requested, log a warning
                    if len(questions) < question_count:
                        print(f"Warning: Generated fewer questions ({len(questions)}) than requested ({question_count})")
                    
                    return questions
                else:
                    print("Invalid response format - missing 'questions' array")
                    # Try to extract questions with regex as fallback
                    return self._extract_questions_fallback(content)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing JSON response: {e}")
                # Fallback parsing if the model doesn't return valid JSON
                return self._extract_questions_fallback(content)
        except Exception as e:
            print(f"API call error: {e}")
            return []
        
    def _extract_questions_fallback(self, content: str) -> List[Dict[str, str]]:
        """
        Fallback method to extract questions if JSON parsing fails
        """
        questions = []
        # Try to find question/answer pairs with regex
        
        # Look for patterns like "text": "question", "reference_answer": "answer"
        pattern = r'"text"\s*:\s*"([^"]*)"\s*,\s*"reference_answer"\s*:\s*"([^"]*)"'
        matches = re.findall(pattern, content)
        
        for question, answer in matches:
            questions.append({
                "text": question,
                "reference_answer": answer
            })
        
        # If we still don't have questions, try another approach
        if not questions:
            # Look for numbered questions (1. Question)
            q_pattern = r'(\d+\.\s*[^?]+\?)'
            a_pattern = r'(?:Answer|Reference Answer):\s*([^\n]+)'
            
            q_matches = re.findall(q_pattern, content)
            a_matches = re.findall(a_pattern, content)
            
            # Pair questions with answers if possible
            for i, question in enumerate(q_matches):
                answer = a_matches[i] if i < len(a_matches) else "No reference answer provided."
                questions.append({
                    "text": question.strip(),
                    "reference_answer": answer.strip()
                })
        
        print(f"Extracted {len(questions)} questions using fallback method")
        return questions
    
    async def evaluate_answer(self, question: str, user_answer: str, reference_answer: str) -> Tuple[float, str, str]:
        """
        Evaluate a user's answer against a reference answer
        """
        prompt = f"""
        Evaluate the user's answer to the following interview question. Compare it semantically with 
        the reference answer and provide a score from 0 to 100, feedback, and suggestions for improvement.
        
        Question: {question}
        Reference Answer: {reference_answer}
        User Answer: {user_answer}
        
        Return your response in JSON format with the following structure:
        {{
            "score": 0-100,
            "feedback": "detailed feedback on the answer",
            "improvement_suggestions": "suggestions for improvement"
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that evaluates interview answers."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._call_api(messages, temperature=0.3)
            content = response["choices"][0]["message"]["content"]
            
            print(f"Raw evaluation response: {content[:200]}...")
            
            try:
                result = json.loads(content)
                return (
                    result["score"],
                    result["feedback"],
                    result["improvement_suggestions"]
                )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing evaluation JSON: {e}")
                # Try to extract with regex as fallback
                return self._extract_evaluation_fallback(content)
        except Exception as e:
            print(f"Error in evaluate_answer: {e}")
            # Return default values
            return 70.0, "Your answer covers some key points.", "Consider adding more specific examples and technical details."

    def _extract_evaluation_fallback(self, content: str) -> Tuple[float, str, str]:
        """Extract evaluation data using regex if JSON parsing fails"""
        import re
        
        # Try to extract score
        score_match = re.search(r'score"?\s*:?\s*(\d+)', content, re.IGNORECASE)
        score = float(score_match.group(1)) if score_match else 50.0
        
        # Try to extract feedback
        feedback_match = re.search(r'feedback"?\s*:?\s*"([^"]+)', content, re.IGNORECASE)
        feedback = feedback_match.group(1) if feedback_match else "Feedback could not be extracted."
        
        # Try to extract improvement suggestions
        suggestions_match = re.search(r'improvement_suggestions"?\s*:?\s*"([^"]+)', content, re.IGNORECASE)
        suggestions = suggestions_match.group(1) if suggestions_match else "Try to be more specific and provide examples."
        
        return score, feedback, suggestions 

    async def generate_answer(self, question_text: str) -> str:
        """
        Generate an answer for a given question
        """
        prompt = f"""
        Please provide a comprehensive and well-structured answer to the following interview question:
        
        Question: {question_text}
        
        Your answer should:
        - Be detailed and thorough
        - Include specific examples where appropriate
        - Demonstrate technical knowledge and expertise
        - Be structured in a clear and logical way
        
        Answer:
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that helps job candidates prepare for interviews by generating high-quality answers to interview questions."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            print(f"Calling API to generate answer for question: {question_text[:50]}...")
            response = await self._call_api(messages, temperature=0.7)
            
            # Debug the raw response
            print(f"Raw response type: {type(response)}")
            print(f"Raw response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
            
            if not isinstance(response, dict) or "choices" not in response:
                print(f"Invalid response format: {response}")
                return "Error: Received invalid response format from the API."
            
            if not response["choices"] or not isinstance(response["choices"], list):
                print(f"No choices in response: {response}")
                return "Error: No answer choices in the response."
            
            content = response["choices"][0]["message"]["content"]
            print(f"Raw content from API: {content[:100]}...")
            
            # Clean up the response
            answer = content.strip()
            
            # Remove any "Answer:" prefix if present
            if answer.lower().startswith("answer:"):
                answer = answer[7:].strip()
            
            return answer
        except Exception as e:
            print(f"Error in generate_answer: {str(e)}")
            import traceback
            traceback.print_exc()
            return "I couldn't generate an answer at this time. Please try again later or write your own answer." 

    def _determine_operation(self, messages: List[Dict[str, str]]) -> str:
        """Determine the operation type based on the messages content"""
        user_message = next((m["content"] for m in messages if m["role"] == "user"), "")
        
        if "generate" in user_message.lower() and "questions" in user_message.lower():
            return "generate_questions"
        elif "evaluate" in user_message.lower() and "answer" in user_message.lower():
            return "evaluate_answer"
        elif "analyze" in user_message.lower() and "job description" in user_message.lower():
            return "analyze_jd"
        elif "provide" in user_message.lower() and "answer" in user_message.lower():
            return "generate_answer"
        else:
            return "unknown_operation" 

    async def generate_answer_stream(self, question_text: str):
        """
        Generate an answer for a given question with streaming
        """
        prompt = f"""
        Please provide a comprehensive and well-structured answer to the following interview question:
        
        Question: {question_text}
        
        Your answer should:
        - Be detailed and thorough
        - Include specific examples where appropriate
        - Demonstrate technical knowledge and expertise
        - Be structured in a clear and logical way
        
        Answer:
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that helps job candidates prepare for interviews by generating high-quality answers to interview questions."},
            {"role": "user", "content": prompt}
        ]
        
        if self.use_mock:
            print("Using mock response for streaming answer generation")
            # For mock responses, simulate streaming by yielding chunks of text
            mock_answer = self._get_mock_answer_for_question(question_text)
            
            # Clean up the mock answer
            mock_answer = mock_answer.strip()
            
            # Split into sentences for more natural streaming
            sentences = re.split(r'(?<=[.!?])\s+', mock_answer)
            
            for sentence in sentences:
                yield sentence + " "
                await asyncio.sleep(0.2)  # Slightly longer delay between sentences
            
            return
        
        try:
            print("Calling real API for streaming answer generation")
            # For real API, we'll use the non-streaming API and simulate streaming
            # In a production environment, you would use the actual streaming API
            full_answer = await self.generate_answer(question_text)
            
            if not full_answer or len(full_answer) < 20:
                print(f"Error: Generated answer too short: {full_answer}")
                raise ValueError("Generated answer is too short or empty")
            
            print(f"Successfully generated full answer of length {len(full_answer)}")
            
            # Split into sentences for more natural streaming
            sentences = re.split(r'(?<=[.!?])\s+', full_answer)
            
            for sentence in sentences:
                yield sentence + " "
                await asyncio.sleep(0.2)  # Slightly longer delay between sentences
            
        except Exception as e:
            print(f"Error in generate_answer_stream: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Generate a fallback answer
            fallback = "I couldn't generate an answer at this time due to a technical issue. Please try again later or write your own answer based on your experience and knowledge."
            
            # Stream the fallback answer
            words = fallback.split()
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3])
                yield chunk + " "
                await asyncio.sleep(0.1)

    def _get_mock_answer_for_question(self, question_text: str) -> str:
        """Generate a mock answer based on the question content"""
        question_lower = question_text.lower()
        
        if "python" in question_lower or "programming" in question_lower:
            return """
            I have extensive experience with Python programming, having used it for over 5 years in both professional and personal projects.
            
            In my professional work, I've developed several backend services using Python with frameworks like Flask and FastAPI. For example, I built a RESTful API service that processed and analyzed large datasets using pandas and numpy, which improved data processing speed by 40%.
            
            I'm proficient with Python's core libraries and follow best practices like PEP 8 style guidelines, type hinting, and comprehensive testing with pytest. I've also worked with asynchronous programming using asyncio for high-performance applications.
            """
        elif "api" in question_lower or "integration" in question_lower:
            return """
            I have significant experience integrating and working with external APIs in various projects. My approach typically follows these steps:
            
            1. First, I thoroughly review the API documentation to understand the endpoints, authentication methods, and data formats.
            
            2. For authentication, I implement secure handling of API keys or tokens, typically storing them as environment variables rather than hardcoding them in the application.
            
            3. I create a dedicated service layer or client class that encapsulates all API interactions, which helps maintain clean separation of concerns in the codebase.
            """
        else:
            return """
            Based on my experience and expertise, I would approach this by first understanding the core requirements and constraints of the problem.
            
            In my previous roles, I've tackled similar challenges by breaking down complex problems into manageable components and implementing systematic solutions. For example, when working on a project that required optimizing performance, I conducted thorough analysis to identify bottlenecks and implemented targeted improvements that resulted in a 35% efficiency gain.
            """ 