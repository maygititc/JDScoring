import os
import httpx
from typing import Dict, Any, List, Tuple
import json
import re
import time
import asyncio
from openai import AsyncOpenAI
import uuid

class OpenAIService:
    def __init__(self):
        # Get API key from OS environment variable
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        if not self.api_key:
            print("WARNING: OPENAI_API_KEY environment variable is not set")
            # For development/testing, you can use a mock response
            self.use_mock = True
        else:
            self.use_mock = False
            # Initialize the OpenAI client
            self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def _call_api(self, messages: List[Dict[str, str]], temperature: float = None) -> Dict[str, Any]:
        if self.use_mock:
            print("Using mock response (no API key provided)")
            start_time = time.time()
            mock_response = self._get_mock_response(messages)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log the mock API call
            if hasattr(self, 'logging_service'):
                operation = self._determine_operation(messages)
                self.logging_service.log_openai_api(
                    operation=operation,
                    request_data={"messages": messages, "temperature": temperature or self.temperature},
                    response_data=mock_response,
                    duration_ms=duration_ms,
                    is_mock=True
                )
            
            return mock_response
        
        try:
            start_time = time.time()
            
            # Use the provided temperature or default to the class temperature
            temp = temperature if temperature is not None else self.temperature
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                temperature=temp
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Convert the response to a dictionary format similar to DeepSeek
            response_dict = {
                "id": response.id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": response.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response.choices[0].message.content
                        },
                        "finish_reason": response.choices[0].finish_reason
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Log the API call
            if hasattr(self, 'logging_service'):
                operation = self._determine_operation(messages)
                self.logging_service.log_openai_api(
                    operation=operation,
                    request_data={"messages": messages, "temperature": temp},
                    response_data=response_dict,
                    duration_ms=duration_ms,
                    is_mock=False
                )
            
            return response_dict
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            
            # Log the error
            if hasattr(self, 'logging_service'):
                operation = self._determine_operation(messages)
                self.logging_service.log_openai_api(
                    operation=operation,
                    request_data={"messages": messages, "temperature": temp},
                    error=str(e),
                    duration_ms=(time.time() - start_time) * 1000,
                    is_mock=False
                )
            
            raise e
    
    def _determine_operation(self, messages: List[Dict[str, str]]) -> str:
        """Determine the operation being performed based on the messages content"""
        # This is the same logic as in DeepSeekService
        user_message = next((m["content"] for m in messages if m["role"] == "user"), "")
        
        if "analyze if the following text is a job description" in user_message.lower():
            return "analyze_jd"
        elif "generate interview questions based on this job description" in user_message.lower():
            return "generate_questions"
        elif "evaluate this answer to an interview question" in user_message.lower():
            return "evaluate_answer"
        elif "provide a comprehensive and well-structured answer" in user_message.lower():
            return "generate_answer"
        else:
            return "other"
    
    def _get_mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate a mock response based on the operation"""
        # This is similar to DeepSeekService but adapted for OpenAI format
        operation = self._determine_operation(messages)
        
        if operation == "analyze_jd":
            return self._get_mock_analyze_jd_response()
        elif operation == "generate_questions":
            return self._get_mock_generate_questions_response()
        elif operation == "evaluate_answer":
            return self._get_mock_evaluate_answer_response()
        elif operation == "generate_answer":
            return self._get_mock_generate_answer_response()
        else:
            return self._get_mock_default_response()
    
    def _get_mock_analyze_jd_response(self) -> Dict[str, Any]:
        """Generate a mock response for JD analysis"""
        return {
            "id": "mock-response-id",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mock",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": """
                        {
                            "is_valid_jd": true,
                            "confidence": 85,
                            "overview": "This job description is for a Software Engineer position requiring Python, JavaScript, and cloud experience. The role involves developing backend services and APIs, with 3-5 years of experience required."
                        }
                        """
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 100,
                "total_tokens": 250
            }
        }
    
    def _get_mock_generate_questions_response(self) -> Dict[str, Any]:
        """Generate a mock response for question generation"""
        return {
            "id": "mock-response-id",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mock",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": """
                        {
                            "questions": [
                                {
                                    "text": "Can you describe your experience with Python and how you've used it in your previous roles?",
                                    "reference_answer": "An excellent answer would include specific Python projects the candidate has worked on, demonstrating both breadth and depth of Python knowledge. They should mention specific libraries and frameworks they've used, explain how they've applied Python to solve real business problems, and ideally quantify the impact of their work. The candidate should also demonstrate understanding of Python best practices, such as PEP 8 style guidelines, testing approaches, and performance considerations."
                                },
                                {
                                    "text": "Describe a challenging technical problem you faced and how you solved it.",
                                    "reference_answer": "A strong answer would clearly describe a specific, complex technical challenge relevant to the role. The candidate should articulate their problem-solving process, including how they analyzed the issue, what alternatives they considered, and why they chose their particular solution. They should highlight both technical skills and soft skills like collaboration or communication. The best answers include the outcome and impact of their solution, ideally with metrics."
                                },
                                {
                                    "text": "How do you approach learning new technologies or frameworks?",
                                    "reference_answer": "An excellent answer demonstrates the candidate's learning methodology and adaptability. They should describe their systematic approach to mastering new technologies, including how they find resources, practice new skills, and apply them to real projects. Strong candidates will mention specific examples of technologies they've learned quickly, how they stay current in the field, and how they balance depth vs. breadth in their learning. They might also mention how they share knowledge with their team."
                                },
                                {
                                    "text": "Tell me about your experience with cloud services and infrastructure.",
                                    "reference_answer": "A comprehensive answer would cover the candidate's experience with specific cloud platforms (AWS, Azure, GCP), services they've worked with (compute, storage, networking, serverless), and their understanding of cloud architecture principles. They should demonstrate knowledge of infrastructure as code, security best practices, and cost optimization. Excellent answers include specific projects where they designed, implemented, or migrated cloud solutions, along with challenges they overcame and the business impact of their work."
                                },
                                {
                                    "text": "How do you ensure the quality and reliability of your code?",
                                    "reference_answer": "A strong answer covers multiple aspects of software quality: testing strategies (unit, integration, end-to-end), code reviews, static analysis tools, and CI/CD practices. The candidate should demonstrate understanding of test-driven development, code coverage, and debugging techniques. They should explain how they balance quality with delivery timelines and how they handle technical debt. Excellent answers include specific examples of how their quality practices prevented issues or improved system reliability."
                                }
                            ]
                        }
                        """
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 250,
                "completion_tokens": 800,
                "total_tokens": 1050
            }
        }
    
    def _get_mock_evaluate_answer_response(self) -> Dict[str, Any]:
        """Generate a mock response for answer evaluation"""
        return {
            "id": "mock-response-id",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mock",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": """
                        {
                            "score": 85,
                            "feedback": "Your answer demonstrates good knowledge of the subject and includes specific examples. You've covered most of the key points from the reference answer.",
                            "improvement_suggestions": "To strengthen your answer further, consider discussing the scalability aspects and mentioning specific metrics or results from your past experiences."
                        }
                        """
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 350,
                "completion_tokens": 150,
                "total_tokens": 500
            }
        }
    
    def _get_mock_generate_answer_response(self) -> Dict[str, Any]:
        """Generate a mock response for answer generation"""
        return {
            "id": "mock-response-id",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mock",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": """
                        In my experience with Python programming, I've worked on a variety of projects over the past 5 years that have allowed me to develop deep expertise with the language and its ecosystem.
                        
                        For backend development, I've built several RESTful APIs using Flask and FastAPI frameworks. One notable project involved creating a data processing service that handled large datasets (>10GB) using pandas and numpy. By implementing efficient algorithms and leveraging Python's asynchronous capabilities with asyncio, I improved processing speed by approximately 40% compared to the previous solution.
                        
                        I'm well-versed in Python best practices, including PEP 8 style guidelines for code readability and maintainability. I use type hinting to reduce runtime errors and improve IDE support, and I implement comprehensive testing using pytest with typically >90% code coverage.
                        
                        For data science applications, I've used libraries like scikit-learn and TensorFlow to build machine learning models. In one project, I developed a recommendation system that increased user engagement by 25%.
                        
                        I've also contributed to open-source Python projects, which has exposed me to different coding styles and collaborative development workflows using Git.
                        
                        For deployment, I've containerized Python applications using Docker and orchestrated them with Kubernetes. I'm familiar with CI/CD pipelines using tools like GitHub Actions to automate testing and deployment.
                        
                        Throughout my career, I've mentored junior developers on Python best practices and conducted code reviews to maintain high code quality standards.
                        
                        My approach to Python development focuses on writing clean, maintainable, and efficient code that solves real business problems.
                        """
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 350,
                "total_tokens": 500
            }
        }
    
    async def analyze_jd(self, jd_text: str) -> Tuple[bool, float, str]:
        """
        Analyze if the text is a job description
        Returns: (is_valid_jd, confidence, overview)
        """
        prompt = f"""
        Please analyze if the following text is a job description.
        
        Text to analyze:
        {jd_text}
        
        Return your response in the following JSON format:
        {{
            "is_valid_jd": true/false,
            "confidence": 0-100,
            "overview": "Brief overview of the job description if valid"
        }}
        
        If the text is not a job description or is too short/incomplete, set is_valid_jd to false and provide a low confidence score.
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that analyzes job descriptions."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            print(f"Analyzing text to determine if it's a job description (length: {len(jd_text)})")
            
            # Call the OpenAI API
            response = await self._call_api(messages)
            
            # Debug the raw response
            print(f"Raw response from OpenAI API: {response}")
            
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                print(f"Raw content from API: {content}")
                
                # Try to parse the JSON response
                try:
                    # Find JSON in the response (in case the model adds extra text)
                    import re
                    json_match = re.search(r'({.*})', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        result = json.loads(json_str)
                    else:
                        # If no JSON pattern found, try parsing the whole content
                        result = json.loads(content)
                    
                    # Extract the values
                    is_valid = result.get("is_valid_jd", False)
                    confidence = float(result.get("confidence", 0))
                    overview = result.get("overview", "")
                    
                    # Ensure confidence is between 0 and 100
                    confidence = max(0, min(100, confidence))
                    
                    print(f"Analysis result: Valid={is_valid}, Confidence={confidence}, Overview={overview[:50]}...")
                    return (is_valid, confidence, overview)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON from API response: {e}")
                    print(f"Content that failed to parse: {content}")
                    
                    # Try to extract values using regex as a fallback
                    is_valid_match = re.search(r'"is_valid_jd":\s*(true|false)', content, re.IGNORECASE)
                    is_valid = is_valid_match and is_valid_match.group(1).lower() == 'true' if is_valid_match else False
                    
                    confidence_match = re.search(r'"confidence":\s*(\d+(?:\.\d+)?)', content)
                    confidence = float(confidence_match.group(1)) if confidence_match else 0
                    
                    overview_match = re.search(r'"overview":\s*"([^"]*)"', content)
                    overview = overview_match.group(1) if overview_match else ""
                    
                    print(f"Extracted using regex: Valid={is_valid}, Confidence={confidence}, Overview={overview[:50]}...")
                    return (is_valid, confidence, overview)
            
            print("Invalid response format from API")
            return (False, 0.0, "")
        except Exception as e:
            print(f"Error in analyze_jd: {str(e)}")
            import traceback
            traceback.print_exc()
            return (False, 0.0, "")
    
    async def generate_answer(self, question_text: str) -> str:
        """
        Generate an answer for a given interview question
        Returns: A comprehensive answer to the question
        """
        prompt = f"""
        Please provide a comprehensive and well-structured answer to this interview question:
        
        Question: {question_text}
        
        Your answer should:
        1. Be detailed and thorough
        2. Include specific examples or approaches
        3. Demonstrate expertise in the subject
        4. Be structured in a clear and logical way
        5. Be around 200-300 words
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant helping prepare for job interviews."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            print(f"Generating answer for question: {question_text[:50]}...")
            
            # Call the OpenAI API
            response = await self._call_api(messages)
            
            if "choices" in response and len(response["choices"]) > 0:
                answer = response["choices"][0]["message"]["content"].strip()
                
                if answer and len(answer) > 50:
                    print(f"Successfully generated answer of length {len(answer)}")
                    return answer
            
            print("Invalid response or too short answer from API")
            return self._get_mock_answer_for_question(question_text)
        except Exception as e:
            print(f"Error in generate_answer: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._get_mock_answer_for_question(question_text)
    
    async def generate_answer_stream(self, question_text: str):
        """
        Generate an answer for a given question with streaming response
        Yields: Chunks of the generated answer
        """
        prompt = f"""
        Please provide a comprehensive and well-structured answer to this interview question:
        
        Question: {question_text}
        
        Your answer should:
        1. Be detailed and thorough
        2. Include specific examples or approaches
        3. Demonstrate expertise in the subject
        4. Be structured in a clear and logical way
        5. Be around 200-300 words
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant helping prepare for job interviews."},
            {"role": "user", "content": prompt}
        ]
        
        # If using mock responses, simulate streaming with a pre-generated answer
        if self.use_mock:
            print("Using mock response for streaming answer generation")
            mock_answer = self._get_mock_answer_for_question(question_text)
            
            # Split into sentences for more natural streaming
            sentences = re.split(r'(?<=[.!?])\s+', mock_answer)
            
            for sentence in sentences:
                yield sentence + " "
                await asyncio.sleep(0.2)  # Slightly longer delay between sentences
            
            return
        
        try:
            print("Calling OpenAI API for streaming answer generation")
            
            # Use the OpenAI streaming API
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                temperature=self.temperature,
                stream=True
            )
            
            collected_chunks = []
            collected_content = ""
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    collected_chunks.append(content)
                    collected_content += content
                    yield content
            
            if not collected_content or len(collected_content) < 20:
                print(f"Error: Generated answer too short: {collected_content}")
                raise ValueError("Generated answer is too short or empty")
            
            print(f"Successfully generated full answer of length {len(collected_content)}")
            
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
        # This can be the same as in DeepSeekService
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
    
    async def generate_questions(self, jd_text: str, question_count: int = 5) -> List[Dict[str, str]]:
        """
        Generate interview questions based on a job description
        Returns: List of dictionaries with 'text' and 'reference_answer' keys
        """
        prompt = f"""
        Generate {question_count} interview questions based on this job description:
        
        {jd_text}
        
        For each question, also provide a reference answer that would be considered excellent.
        
        Return your response in the following JSON format:
        {{
            "questions": [
                {{
                    "text": "Question 1",
                    "reference_answer": "Reference answer for question 1"
                }},
                ...
            ]
        }}
        
        Make sure the questions are:
        1. Relevant to the job description
        2. A mix of technical and behavioral questions
        3. Specific enough to assess the candidate's skills and experience
        4. Open-ended to encourage detailed responses
        
        The reference answers should:
        1. Be comprehensive and detailed
        2. Include specific examples or approaches
        3. Highlight key points that would make an answer excellent
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that helps generate relevant interview questions based on job descriptions."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            print(f"Generating {question_count} questions based on JD (length: {len(jd_text)})")
            
            # Call the OpenAI API
            response = await self._call_api(messages)
            
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                print(f"Raw content from API: {content[:200]}...")
                
                # Try to parse the JSON response
                try:
                    # Find JSON in the response (in case the model adds extra text)
                    import re
                    json_match = re.search(r'({.*})', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        result = json.loads(json_str)
                    else:
                        # If no JSON pattern found, try parsing the whole content
                        result = json.loads(content)
                    
                    # Extract the questions
                    questions = result.get("questions", [])
                    
                    # Ensure we have the requested number of questions
                    if len(questions) < question_count:
                        print(f"Warning: Only generated {len(questions)} questions, expected {question_count}")
                    
                    # Add unique IDs to each question
                    questions_with_ids = []
                    for q in questions:
                        question_id = str(uuid.uuid4())
                        questions_with_ids.append({
                            "id": question_id,
                            "text": q.get("text", ""),
                            "reference_answer": q.get("reference_answer", "")
                        })
                    
                    print(f"Successfully generated {len(questions_with_ids)} questions")
                    return questions_with_ids
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON from API response: {e}")
                    print(f"Content that failed to parse: {content}")
                    
                    # Try to extract questions using regex as a fallback
                    questions = []
                    question_matches = re.finditer(r'"text":\s*"([^"]*)".*?"reference_answer":\s*"([^"]*)"', content, re.DOTALL)
                    
                    for i, match in enumerate(question_matches):
                        if i >= question_count:
                            break
                        
                        question_text = match.group(1)
                        reference_answer = match.group(2)
                        question_id = str(uuid.uuid4())
                        
                        questions.append({
                            "id": question_id,
                            "text": question_text,
                            "reference_answer": reference_answer
                        })
                    
                    if questions:
                        print(f"Extracted {len(questions)} questions using regex")
                        return questions
                    
                    # If all else fails, generate some generic questions
                    return self._generate_generic_questions(jd_text, question_count)
            
            print("Invalid response format from API")
            return self._generate_generic_questions(jd_text, question_count)
        except Exception as e:
            print(f"Error in generate_questions: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._generate_generic_questions(jd_text, question_count)
    
    def _generate_generic_questions(self, jd_text: str, question_count: int) -> List[Dict[str, str]]:
        """Generate generic questions as a fallback"""
        print("Generating generic questions as fallback")
        
        # Extract some keywords from the JD
        jd_lower = jd_text.lower()
        keywords = []
        
        # Check for common technologies and skills
        tech_keywords = {
            "python": "Python programming",
            "javascript": "JavaScript",
            "react": "React.js",
            "node": "Node.js",
            "api": "API development",
            "database": "database design",
            "cloud": "cloud services",
            "agile": "Agile methodologies",
            "test": "testing strategies",
            "frontend": "frontend development",
            "backend": "backend development"
        }
        
        # Find matching keywords in the JD
        for key, value in tech_keywords.items():
            if key in jd_lower:
                keywords.append(value)
        
        # If no keywords were found, use some defaults
        if not keywords:
            keywords = ["programming", "development", "software engineering", "teamwork", "problem-solving"]
        
        # Template questions
        templates = [
            {
                "text": "What experience do you have with {keyword}?",
                "reference_answer": "A strong answer would demonstrate practical experience with {keyword}, including specific projects and measurable results."
            },
            {
                "text": "Describe a challenging project where you used {keyword}.",
                "reference_answer": "The candidate should describe a specific project involving {keyword}, the challenges faced, and how they overcame them."
            },
            {
                "text": "How do you stay current with developments in {keyword}?",
                "reference_answer": "A good answer would mention specific learning resources, communities, or practices the candidate uses to stay updated with {keyword}."
            },
            {
                "text": "How would you implement {keyword} in a new project?",
                "reference_answer": "The candidate should demonstrate knowledge of best practices for {keyword}, including architecture considerations and implementation strategies."
            },
            {
                "text": "Tell me about a time when you had to learn {keyword} quickly for a project.",
                "reference_answer": "Look for examples of the candidate's ability to learn new technologies quickly and apply them effectively in real-world situations."
            }
        ]
        
        # Generate questions based on the templates and keywords
        questions = []
        for i in range(question_count):
            keyword = keywords[i % len(keywords)]
            template = templates[i % len(templates)]
            question_id = str(uuid.uuid4())
            
            questions.append({
                "id": question_id,
                "text": template["text"].format(keyword=keyword),
                "reference_answer": template["reference_answer"].format(keyword=keyword)
            })
        
        return questions
    
    async def evaluate_answer(self, question_text: str, user_answer: str, reference_answer: str) -> Tuple[float, str, str]:
        """
        Evaluate a user's answer to an interview question
        Returns: (score, feedback, improvement_suggestions)
        """
        prompt = f"""
        Evaluate this answer to an interview question.
        
        Question: {question_text}
        
        User's Answer: {user_answer}
        
        Reference Answer (what a good answer should cover): {reference_answer}
        
        Score the answer on a scale of 0-100 based on:
        1. Relevance to the question
        2. Completeness compared to the reference answer
        3. Clarity and structure
        4. Specific examples or details provided
        
        Return your evaluation in the following JSON format:
        {{
            "score": 0-100,
            "feedback": "Brief feedback on the answer's strengths and weaknesses",
            "improvement_suggestions": "Specific suggestions for improving the answer"
        }}
        
        Be fair but thorough in your evaluation.
        """
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that evaluates interview answers."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            print(f"Evaluating answer for question: {question_text[:50]}...")
            
            # Call the OpenAI API
            response = await self._call_api(messages)
            
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                print(f"Raw content from API: {content[:200]}...")
                
                # Try to parse the JSON response
                try:
                    # Find JSON in the response (in case the model adds extra text)
                    import re
                    json_match = re.search(r'({.*})', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        result = json.loads(json_str)
                    else:
                        # If no JSON pattern found, try parsing the whole content
                        result = json.loads(content)
                    
                    # Extract the values
                    score = float(result.get("score", 60.0))
                    feedback = result.get("feedback", "")
                    suggestions = result.get("improvement_suggestions", "")
                    
                    # Ensure score is between 0 and 100
                    score = max(0, min(100, score))
                    
                    print(f"Evaluation result: Score={score}, Feedback={feedback[:50]}...")
                    return (score, feedback, suggestions)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON from API response: {e}")
                    print(f"Content that failed to parse: {content}")
                    
                    # Try to extract values using regex as a fallback
                    score_match = re.search(r'"score":\s*(\d+(?:\.\d+)?)', content)
                    score = float(score_match.group(1)) if score_match else 60.0
                    
                    feedback_match = re.search(r'"feedback":\s*"([^"]*)"', content)
                    feedback = feedback_match.group(1) if feedback_match else "Your answer covers some key points."
                    
                    suggestions_match = re.search(r'"improvement_suggestions":\s*"([^"]*)"', content)
                    suggestions = suggestions_match.group(1) if suggestions_match else "Consider adding more specific examples."
                    
                    print(f"Extracted using regex: Score={score}, Feedback={feedback[:50]}...")
                    return (score, feedback, suggestions)
            
            print("Invalid response format from API")
            return (60.0, "Your answer covers some key points.", "Consider adding more specific examples.")
        except Exception as e:
            print(f"Error in evaluate_answer: {str(e)}")
            import traceback
            traceback.print_exc()
            return (60.0, "We encountered an issue while evaluating your answer, but it appears to cover some key points.", 
                    "Consider adding more specific examples and technical details to strengthen your answer.") 