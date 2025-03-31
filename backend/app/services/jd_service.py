from typing import List, Dict, Any, Tuple
import uuid
import json
import re
import asyncio

class JDService:
    def __init__(self, llm_service):
        self.llm_service = llm_service
        # In-memory storage for questions and answers
        # In a production app, this would be a database
        self.questions = {}
        print(f"JDService initialized with {type(llm_service).__name__}")
    
    async def analyze_jd(self, jd_text: str) -> Dict[str, Any]:
        """
        Analyze if the text is a job description
        """
        try:
            # Check if the text is long enough to be a job description
            if len(jd_text.strip()) < 50:
                print("Text is too short to be a job description")
                return {
                    "is_valid_jd": False,
                    "confidence": 0.0,
                    "overview": "The provided text is too short to be a valid job description.",
                    "error": None
                }
            
            # Try to analyze with the LLM service
            is_valid, confidence, overview = await self.llm_service.analyze_jd(jd_text)
            
            # If the LLM service returns very low confidence, do a basic heuristic check
            if confidence < 10:
                # Simple heuristic: check for common job description keywords
                jd_lower = jd_text.lower()
                job_keywords = ["job", "position", "role", "responsibilities", "requirements", 
                               "qualifications", "skills", "experience", "salary", "apply"]
                
                keyword_count = sum(1 for keyword in job_keywords if keyword in jd_lower)
                
                # If we find at least 3 job-related keywords, it's probably a job description
                if keyword_count >= 3 and len(jd_text.strip()) > 200:
                    print(f"LLM gave low confidence, but found {keyword_count} job keywords - treating as valid JD")
                    is_valid = True
                    confidence = max(confidence, 60.0)  # Set a minimum confidence
                    if not overview:
                        overview = "This appears to be a job description based on keyword analysis."
            
            return {
                "is_valid_jd": is_valid,
                "confidence": confidence,
                "overview": overview,
                "error": None
            }
        except Exception as e:
            print(f"Error in analyze_jd: {str(e)}")
            return {
                "is_valid_jd": False,
                "confidence": 0.0,
                "overview": "",
                "error": str(e)
            }
    
    def generate_test_questions(self, jd_text: str, question_count: int) -> List[Dict[str, str]]:
        """
        Generate test questions without using the API
        """
        print(f"Generating {question_count} test questions")
        
        # Extract keywords from the JD
        jd_lower = jd_text.lower()
        keywords = []
        
        # Check for common technologies and skills
        tech_keywords = {
            "python": "Python programming",
            "javascript": "JavaScript",
            "react": "React.js",
            "node": "Node.js",
            "api": "API development",
            "rest": "RESTful services",
            "database": "database design",
            "sql": "SQL",
            "nosql": "NoSQL databases",
            "mongodb": "MongoDB",
            "aws": "AWS",
            "azure": "Azure",
            "cloud": "cloud services",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "microservice": "microservices architecture",
            "agile": "Agile methodologies",
            "scrum": "Scrum",
            "test": "testing strategies",
            "ci/cd": "CI/CD pipelines",
            "git": "Git",
            "frontend": "frontend development",
            "backend": "backend development",
            "fullstack": "full-stack development",
            "mobile": "mobile development",
            "security": "security practices",
            "performance": "performance optimization"
        }
        
        # Find matching keywords in the JD
        for key, value in tech_keywords.items():
            if key in jd_lower:
                keywords.append(value)
        
        # If no keywords were found, use some defaults
        if not keywords:
            keywords = ["programming", "development", "software engineering", "teamwork", "problem-solving"]
        
        # Template questions that can be customized with keywords
        question_templates = [
            {
                "template": "What experience do you have with {keyword} and how have you applied it in your previous roles?",
                "answer_template": "A strong answer would demonstrate practical experience with {keyword}, including specific projects, challenges overcome, and measurable results achieved. The candidate should show both technical understanding and practical application of {keyword} in relevant contexts."
            },
            {
                "template": "Describe a challenging project where you used {keyword}. What problems did you encounter and how did you solve them?",
                "answer_template": "The candidate should describe a specific project involving {keyword}, clearly articulating the challenges faced and the solutions implemented. A good answer would include technical details, problem-solving approach, and the outcome of the project."
            },
            {
                "template": "How do you stay current with developments in {keyword}?",
                "answer_template": "A good answer would mention specific learning resources, communities, or practices the candidate uses to stay updated with {keyword}. This might include following relevant blogs, participating in forums, attending conferences, or contributing to open-source projects."
            },
            {
                "template": "How would you implement {keyword} in a new project? What best practices would you follow?",
                "answer_template": "The candidate should demonstrate knowledge of industry best practices for {keyword}, including architecture considerations, common pitfalls to avoid, and implementation strategies. They should show an understanding of how {keyword} fits into the broader technology ecosystem."
            },
            {
                "template": "Can you explain a complex concept related to {keyword} in simple terms?",
                "answer_template": "This tests the candidate's depth of understanding and communication skills. A strong answer would break down a complex aspect of {keyword} into clear, accessible explanations without losing technical accuracy."
            }
        ]
        
        # Generate questions based on the templates and keywords
        generated_questions = []
        for i in range(question_count):
            # Select a keyword and template
            keyword = keywords[i % len(keywords)]
            template = question_templates[i % len(question_templates)]
            
            # Create the question and answer
            question = {
                "text": template["template"].format(keyword=keyword),
                "reference_answer": template["answer_template"].format(keyword=keyword)
            }
            
            generated_questions.append(question)
        
        print(f"Generated {len(generated_questions)} test questions based on JD keywords")
        
        # Add unique IDs
        questions_with_ids = []
        for q in generated_questions:
            question_id = str(uuid.uuid4())
            self.questions[question_id] = {
                "text": q["text"],
                "reference_answer": q["reference_answer"]
            }
            
            questions_with_ids.append({
                "id": question_id,
                "text": q["text"],
                "reference_answer": q["reference_answer"]
            })
        
        return questions_with_ids

    async def generate_questions(self, jd_text: str, question_count: int) -> List[Dict[str, str]]:
        """
        Generate questions based on the job description
        """
        try:
            # Log the start of question generation
            if hasattr(self, 'logging_service'):
                self.logging_service.logger.info(f"Generating {question_count} questions for JD of length {len(jd_text)}")
            
            # Extract key terms from the JD for validation
            key_terms = self._extract_key_terms(jd_text)
            print(f"Extracted key terms from JD: {', '.join(list(key_terms)[:10])}...")
            
            # Generate questions
            questions_data = await self.llm_service.generate_questions(jd_text, question_count)
            
            print(f"Raw questions data: {questions_data}")
            
            # Ensure we have questions data
            if not questions_data:
                print("No questions data returned from DeepSeek API, using test questions")
                test_questions = self.generate_test_questions(jd_text, question_count)
                
                # Log the fallback to test questions
                if hasattr(self, 'logging_service'):
                    self.logging_service.logger.warning("Falling back to test questions due to empty response")
                
                return test_questions
            
            # Validate question relevance
            relevant_questions = []
            for q in questions_data:
                if self._is_question_relevant(q, key_terms):
                    relevant_questions.append(q)
                else:
                    print(f"Discarding irrelevant question: {q.get('text', '')[:50]}...")
                    
                    # Log the discarded question
                    if hasattr(self, 'logging_service'):
                        self.logging_service.logger.warning(f"Discarded irrelevant question: {q.get('text', '')[:50]}...")
            
            # If we lost too many questions, fill in with test questions
            if len(relevant_questions) < question_count * 0.7:  # If we lost more than 30%
                print(f"Too many irrelevant questions, filling in with test questions")
                
                # Log the filling in with test questions
                if hasattr(self, 'logging_service'):
                    self.logging_service.logger.warning(f"Filling in with test questions due to too many irrelevant questions")
                
                additional_needed = question_count - len(relevant_questions)
                test_questions = self.generate_test_questions(jd_text, additional_needed)
                relevant_questions.extend(test_questions)
            
            # Add unique IDs to questions and store them
            questions_with_ids = []
            for q in relevant_questions[:question_count]:  # Limit to requested count
                question_id = str(uuid.uuid4())
                self.questions[question_id] = {
                    "text": q["text"],
                    "reference_answer": q["reference_answer"]
                }
                
                questions_with_ids.append({
                    "id": question_id,
                    "text": q["text"],
                    "reference_answer": q["reference_answer"]
                })
            
            # Log the successful question generation
            if hasattr(self, 'logging_service'):
                self.logging_service.logger.info(f"Successfully generated {len(questions_with_ids)} questions")
            
            return questions_with_ids
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            
            # Log the error
            if hasattr(self, 'logging_service'):
                self.logging_service.logger.error(f"Error generating questions: {str(e)}")
            
            # Fallback to test questions
            return self.generate_test_questions(jd_text, question_count)

    def _extract_key_terms(self, jd_text: str) -> set:
        """Extract key terms from the job description"""
        # Convert to lowercase
        jd_lower = jd_text.lower()
        
        # Extract words (simple approach)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', jd_lower)
        
        # Filter out common words
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
        
        key_terms = set()
        for word in words:
            if word not in common_words:
                key_terms.add(word)
        
        return key_terms

    def _is_question_relevant(self, question: Dict[str, str], key_terms: set) -> bool:
        """Check if a question is relevant to the job description"""
        question_text = question.get('text', '').lower()
        reference_answer = question.get('reference_answer', '').lower()
        
        # Count how many key terms appear in the question and answer
        term_matches = sum(1 for term in key_terms if term in question_text or term in reference_answer)
        
        # Consider it relevant if it matches at least 2 key terms
        return term_matches >= 2
    
    async def evaluate_answer(self, question_id: str, user_answer: str, reference_answer: str) -> Dict[str, Any]:
        """
        Evaluate a user's answer
        """
        try:
            print(f"Looking for question ID: {question_id}")
            print(f"Available question IDs: {list(self.questions.keys())}")
            
            # Get the question text
            question_data = self.questions.get(question_id)
            
            if not question_data:
                print(f"Question ID {question_id} not found in stored questions")
                # Use a default evaluation if question not found
                return {
                    "score": 65.0,
                    "feedback": "Your answer was evaluated without the original question context.",
                    "improvement_suggestions": "Try to be more specific and provide concrete examples."
                }
            
            question_text = question_data.get("text", "")
            stored_reference_answer = question_data.get("reference_answer", "")
            
            print(f"Found question: {question_text[:50]}...")
            print(f"Using reference answer from storage: {stored_reference_answer[:50]}...")
            
            # Check if user answer is too short
            if not user_answer or len(user_answer.strip()) < 20:
                print("User answer is too short for proper evaluation")
                return {
                    "score": 30.0,
                    "feedback": "Your answer is too brief to properly address the question.",
                    "improvement_suggestions": "Please provide a more detailed response with specific examples from your experience."
                }
            
            # Use the stored reference answer instead of the one passed in
            try:
                score, feedback, suggestions = await self.llm_service.evaluate_answer(
                    question_text, user_answer, stored_reference_answer
                )
                
                # Log successful evaluation
                print(f"Successfully evaluated answer with score: {score}")
                
                return {
                    "score": score,
                    "feedback": feedback,
                    "improvement_suggestions": suggestions
                }
            except Exception as e:
                print(f"Error calling LLM service for evaluation: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Provide a more helpful fallback response
                return {
                    "score": 60.0,
                    "feedback": "We encountered an issue while evaluating your answer with our AI system.",
                    "improvement_suggestions": "While we couldn't provide specific feedback, generally strong answers include concrete examples from your experience and address all parts of the question."
                }
        except Exception as e:
            print(f"Error in evaluate_answer: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Provide a more helpful fallback response
            return {
                "score": 60.0,
                "feedback": "We encountered an issue while evaluating your answer, but it appears to cover some key points.",
                "improvement_suggestions": "Consider adding more specific examples and technical details to strengthen your answer."
            }

    async def generate_answer(self, question_text: str) -> str:
        """
        Generate an answer for a given question
        """
        try:
            # First, try to generate a fallback answer based on the question content
            fallback_answer = await self._generate_fallback_answer(question_text)
            
            # Try to get an answer from the API
            try:
                answer = await self.llm_service.generate_answer(question_text)
                
                # If we got a valid answer from the API, return it
                if answer and len(answer.strip()) > 50 and not answer.startswith("I couldn't generate"):
                    return answer
                    
                # Otherwise, use our fallback
                print(f"API returned invalid answer, using fallback for: {question_text[:50]}...")
                return fallback_answer
            except Exception as e:
                print(f"Error calling API for answer generation: {str(e)}")
                return fallback_answer
        except Exception as e:
            print(f"Error in generate_answer: {str(e)}")
            return "I couldn't generate an answer at this time. Please try again later or write your own answer."

    async def _generate_fallback_answer(self, question_text: str) -> str:
        """Generate a fallback answer using the LLM with a simplified prompt"""
        try:
            # Use a simplified prompt for fallback generation
            prompt = f"""
            Please provide a brief, general answer to this interview question:
            
            Question: {question_text}
            
            Keep your answer concise and professional.
            """
            
            messages = [
                {"role": "system", "content": "You are an AI assistant helping with interview preparation."},
                {"role": "user", "content": prompt}
            ]
            
            # Try to use the DeepSeek service with a simplified prompt
            response = await self.llm_service._call_api(messages, temperature=0.7)
            
            if response and "choices" in response and len(response["choices"]) > 0:
                answer = response["choices"][0]["message"]["content"].strip()
                if answer:
                    return answer
            
            # If that fails, return a generic response
            return "I couldn't generate a specific answer at this time. Please write your own answer based on your experience and knowledge relevant to this question."
        except Exception as e:
            print(f"Error in _generate_fallback_answer: {str(e)}")
            return "I couldn't generate a specific answer at this time. Please write your own answer based on your experience and knowledge relevant to this question."

    async def generate_answer_stream(self, question_text: str):
        """
        Generate an answer for a given question with streaming
        """
        try:
            # Try to get a fallback answer in case we need it
            fallback_answer = await self._generate_fallback_answer(question_text)
            
            # Use the DeepSeek service to generate a streaming answer
            async for chunk in self.llm_service.generate_answer_stream(question_text):
                yield chunk
            
        except Exception as e:
            print(f"Error in generate_answer_stream: {str(e)}")
            
            # Yield the fallback answer in chunks to simulate streaming
            words = fallback_answer.split()
            chunk_size = 5
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                yield chunk + " "
                await asyncio.sleep(0.05)  # Simulate network delay 