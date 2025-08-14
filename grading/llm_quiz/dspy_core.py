"""
Simplified LLM Quiz Challenge using DSPy structured output.

This module replaces the complex manual prompt engineering and JSON parsing
with clean DSPy signatures and modules.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json
import urllib.request
import urllib.error

import dspy
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python < 3.11

try:
    from .dspy_signatures import (
        ParseQuestionAndAnswer, ValidateQuestion, AnswerQuizQuestion, 
        EvaluateAnswer, GenerateFeedback, ValidationIssue
    )
except ImportError:
    # Handle relative import for standalone execution
    from dspy_signatures import (
        ParseQuestionAndAnswer, ValidateQuestion, AnswerQuizQuestion, 
        EvaluateAnswer, GenerateFeedback, ValidationIssue
    )

logger = logging.getLogger(__name__)


@dataclass
class QuizQuestion:
    """Represents a single quiz question."""
    question: str
    answer: str
    number: int


@dataclass
class QuizResult:
    """Result for a single question."""
    question: QuizQuestion
    llm_answer: str
    is_valid: bool
    student_wins: bool
    evaluation_explanation: str
    validation_issues: List[str]
    error: Optional[str] = None


@dataclass  
class QuizResults:
    """Complete quiz challenge results."""
    quiz_title: str
    total_questions: int
    valid_questions: int
    invalid_questions: int
    student_wins: int
    llm_wins: int
    success_rate: float
    question_results: List[QuizResult]
    feedback_summary: str
    student_passes: bool
    github_classroom_result: str


class DSPyQuizChallenge:
    """Simplified LLM Quiz Challenge using DSPy structured output."""
    
    def __init__(self, base_url: str, api_key: str, quiz_model: str, evaluator_model: str, 
                 context_urls_file: Optional[str] = None):
        """Initialize the DSPy-based quiz challenge system."""
        
        # Configure DSPy with the provided LLM
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.quiz_model = quiz_model
        self.evaluator_model = evaluator_model
        
        # Set up DSPy LM - we'll create a simple wrapper for the existing API
        self.lm = self._create_dspy_lm()
        dspy.settings.configure(lm=self.lm)
        
        # Load context content if provided
        self.context_content = self._load_context_from_urls_file(context_urls_file) if context_urls_file else None
        
        # Initialize DSPy predictors
        self.question_parser = dspy.Predict(ParseQuestionAndAnswer)
        self.question_validator = dspy.ChainOfThought(ValidateQuestion)
        self.question_answerer = dspy.ChainOfThought(AnswerQuizQuestion)
        self.answer_evaluator = dspy.ChainOfThought(EvaluateAnswer)
        self.feedback_generator = dspy.ChainOfThought(GenerateFeedback)
        
        logger.info(f"DSPy Quiz Challenge initialized with models: quiz={quiz_model}, evaluator={evaluator_model}")
    
    def _create_dspy_lm(self):
        """Create a DSPy LM wrapper for the existing API endpoint."""
        # For now, we'll create a simple DSPy LM that works with OpenAI-compatible APIs
        # This assumes the base_url is OpenAI-compatible
        if "openrouter" in self.base_url.lower():
            # OpenRouter
            return dspy.LM(
                model=self.evaluator_model,
                api_base=self.base_url,
                api_key=self.api_key
            )
        elif "ollama" in self.base_url.lower() or ":11434" in self.base_url.lower():
            # Ollama
            return dspy.LM(
                model=self.evaluator_model,
                api_base=self.base_url,
                api_key=self.api_key  # Ollama might not need this but we'll include it
            )
        else:
            # Default OpenAI-compatible
            return dspy.LM(
                model=self.evaluator_model,
                api_base=self.base_url,
                api_key=self.api_key
            )
    
    def _load_context_from_urls_file(self, urls_file: str) -> Optional[str]:
        """Load context content from URLs file."""
        try:
            with open(urls_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            
            if not urls:
                logger.warning(f"No URLs found in {urls_file}")
                return None
            
            combined_content = []
            for i, url in enumerate(urls, 1):
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'llm-quiz-challenge'})
                    with urllib.request.urlopen(req, timeout=30) as response:
                        content = response.read().decode('utf-8')
                        filename = url.split('/')[-1] if '/' in url else f"content_{i}"
                        combined_content.append(f"# {filename} (from {url})\n\n{content}")
                        logger.info(f"Loaded content from {url}")
                except Exception as e:
                    logger.error(f"Error loading {url}: {e}")
            
            if combined_content:
                return "\n\n" + "="*80 + "\n\n".join(combined_content)
            
        except Exception as e:
            logger.error(f"Error loading context from {urls_file}: {e}")
        
        return None
    
    def load_quiz_from_file(self, quiz_file: Path) -> List[QuizQuestion]:
        """Load quiz from TOML file."""
        try:
            with open(quiz_file, 'rb') as f:
                quiz_data = tomllib.load(f)
            
            questions = []
            for i, q_data in enumerate(quiz_data.get('questions', []), 1):
                questions.append(QuizQuestion(
                    question=q_data.get('question', ''),
                    answer=q_data.get('answer', ''),
                    number=i
                ))
            
            logger.info(f"Loaded {len(questions)} questions from {quiz_file}")
            return questions
            
        except Exception as e:
            logger.error(f"Error loading quiz file {quiz_file}: {e}")
            raise
    
    def parse_raw_input(self, raw_input: str) -> List[QuizQuestion]:
        """Parse quiz questions from raw student input."""
        try:
            # Use DSPy to parse the input - much simpler than manual parsing!
            result = self.question_parser(raw_input=raw_input)
            
            questions = []
            for i, (q, a, has_a) in enumerate(zip(result.questions, result.answers, result.has_answers), 1):
                questions.append(QuizQuestion(
                    question=q,
                    answer=a if has_a else "",
                    number=i
                ))
            
            logger.info(f"Parsed {len(questions)} questions from raw input")
            return questions
            
        except Exception as e:
            logger.error(f"Error parsing raw input: {e}")
            raise
    
    def run_quiz_challenge(self, questions: List[QuizQuestion], quiz_title: str = "Quiz Challenge") -> QuizResults:
        """Run the complete quiz challenge using DSPy structured output."""
        logger.info(f"Starting DSPy quiz challenge with {len(questions)} questions")
        
        question_results = []
        valid_count = 0
        student_wins = 0
        llm_wins = 0
        all_validation_issues = []
        
        for question in questions:
            logger.info(f"Processing question {question.number}: {question.question[:50]}...")
            
            try:
                # Step 1: Validate the question using DSPy
                validation = self.question_validator(
                    question=question.question,
                    answer=question.answer,
                    context_content=self.context_content
                )
                
                if not validation.is_valid:
                    logger.warning(f"Question {question.number} failed validation: {validation.reason}")
                    all_validation_issues.extend([issue.value for issue in validation.issues])
                    
                    result = QuizResult(
                        question=question,
                        llm_answer="Question rejected during validation",
                        is_valid=False,
                        student_wins=False,
                        evaluation_explanation=f"Invalid question: {validation.reason}",
                        validation_issues=[issue.value for issue in validation.issues],
                        error=validation.reason
                    )
                    question_results.append(result)
                    continue
                
                valid_count += 1
                
                # Step 2: Get LLM answer using DSPy
                # We need to switch to the quiz model for this step
                with dspy.context(lm=dspy.LM(model=self.quiz_model, api_base=self.base_url, api_key=self.api_key)):
                    llm_response = self.question_answerer(
                        question=question.question,
                        context_content=self.context_content
                    )
                
                # Step 3: Evaluate the answer using DSPy
                evaluation = self.answer_evaluator(
                    question=question.question,
                    correct_answer=question.answer,
                    llm_answer=llm_response.answer
                )
                
                # Update counters
                if evaluation.student_wins:
                    student_wins += 1
                else:
                    llm_wins += 1
                
                result = QuizResult(
                    question=question,
                    llm_answer=llm_response.answer,
                    is_valid=True,
                    student_wins=evaluation.student_wins,
                    evaluation_explanation=evaluation.explanation,
                    validation_issues=[]
                )
                question_results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing question {question.number}: {e}")
                result = QuizResult(
                    question=question,
                    llm_answer="System error",
                    is_valid=False,
                    student_wins=False,
                    evaluation_explanation=f"System error: {str(e)}",
                    validation_issues=[],
                    error=str(e)
                )
                question_results.append(result)
        
        # Calculate results
        evaluated_questions = student_wins + llm_wins
        success_rate = student_wins / evaluated_questions if evaluated_questions > 0 else 0.0
        student_passes = (valid_count == len(questions) and 
                         evaluated_questions > 0 and 
                         success_rate >= 1.0)
        
        # Generate feedback using DSPy
        try:
            feedback = self.feedback_generator(
                total_questions=len(questions),
                valid_questions=valid_count,
                invalid_questions=len(questions) - valid_count,
                student_wins=student_wins,
                llm_wins=llm_wins,
                validation_issues=all_validation_issues,
                success_rate=success_rate
            )
            feedback_summary = feedback.feedback_summary
            github_result = feedback.github_classroom_marker
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            feedback_summary = f"Quiz completed. {student_wins}/{evaluated_questions} questions stumped the LLM."
            github_result = "STUDENTS_QUIZ_KEIKO_WIN" if student_passes else "STUDENTS_QUIZ_KEIKO_LOSE"
        
        return QuizResults(
            quiz_title=quiz_title,
            total_questions=len(questions),
            valid_questions=valid_count,
            invalid_questions=len(questions) - valid_count,
            student_wins=student_wins,
            llm_wins=llm_wins,
            success_rate=success_rate,
            question_results=question_results,
            feedback_summary=feedback_summary,
            student_passes=student_passes,
            github_classroom_result=github_result
        )
    
    def save_results(self, results: QuizResults, output_file: Path):
        """Save quiz results to JSON file."""
        try:
            results_dict = asdict(results)
            with open(output_file, 'w') as f:
                json.dump(results_dict, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise