"""
DSPy signatures for the LLM Quiz Challenge.

This module defines structured DSPy signatures that replace complex manual
prompt engineering and JSON parsing with clean, type-safe interactions.
"""

from typing import Literal, List, Optional
import dspy
from enum import Enum


class ValidationIssue(str, Enum):
    """Types of validation issues that can occur with quiz questions."""
    HEAVY_MATH = "heavy_math"
    PROMPT_INJECTION = "prompt_injection"
    ANSWER_QUALITY = "answer_quality"
    CONTEXT_MISMATCH = "context_mismatch"


class ParseQuestionAndAnswer(dspy.Signature):
    """Parse questions and answers from raw student input in various formats."""
    
    raw_input: str = dspy.InputField(desc="Student input containing questions and answers in any format")
    
    questions: List[str] = dspy.OutputField(desc="List of extracted questions")
    answers: List[str] = dspy.OutputField(desc="List of corresponding answers, 'MISSING' if not provided")
    has_answers: List[bool] = dspy.OutputField(desc="Whether each question has a provided answer")


class ValidateQuestion(dspy.Signature):
    """Validate a quiz question and answer for appropriateness and quality."""
    
    question: str = dspy.InputField(desc="The quiz question to validate")
    answer: str = dspy.InputField(desc="The student's provided answer")
    context_content: Optional[str] = dspy.InputField(desc="Course context materials, if available")
    
    is_valid: bool = dspy.OutputField(desc="Whether the question is valid and acceptable")
    issues: List[ValidationIssue] = dspy.OutputField(desc="List of specific validation issues found")
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = dspy.OutputField(desc="Confidence in validation decision")
    reason: str = dspy.OutputField(desc="Brief explanation of the validation decision")


class AnswerQuizQuestion(dspy.Signature):
    """Answer a quiz question using provided context materials."""
    
    question: str = dspy.InputField(desc="The quiz question to answer")
    context_content: Optional[str] = dspy.InputField(desc="Course context materials for reference")
    
    answer: str = dspy.OutputField(desc="Concise but thorough answer to the question (max 300 words)")


class EvaluateAnswer(dspy.Signature):
    """Evaluate an LLM's answer against the correct answer for a quiz question."""
    
    question: str = dspy.InputField(desc="The quiz question")
    correct_answer: str = dspy.InputField(desc="The correct answer provided by the student")
    llm_answer: str = dspy.InputField(desc="The LLM's answer to evaluate")
    
    verdict: Literal["CORRECT", "INCORRECT"] = dspy.OutputField(desc="Whether the LLM's answer is correct")
    student_wins: bool = dspy.OutputField(desc="True if student wins (LLM got it wrong), False if LLM correct")
    explanation: str = dspy.OutputField(desc="Brief explanation of the evaluation decision and reasoning")
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = dspy.OutputField(desc="Confidence level in the evaluation")


class GenerateFeedback(dspy.Signature):
    """Generate comprehensive feedback for students based on quiz results."""
    
    total_questions: int = dspy.InputField(desc="Total number of questions submitted")
    valid_questions: int = dspy.InputField(desc="Number of valid questions")
    invalid_questions: int = dspy.InputField(desc="Number of invalid questions")
    student_wins: int = dspy.InputField(desc="Number of questions where student won")
    llm_wins: int = dspy.InputField(desc="Number of questions where LLM won")
    validation_issues: List[str] = dspy.InputField(desc="List of validation issues encountered")
    success_rate: float = dspy.InputField(desc="Student success rate (0.0 to 1.0)")
    
    feedback_summary: str = dspy.OutputField(desc="Comprehensive feedback summary for the student")
    pass_result: Literal["PASS", "FAIL"] = dspy.OutputField(desc="Whether the student passed the challenge")
    github_classroom_marker: str = dspy.OutputField(desc="GitHub Classroom result marker")
    improvement_tips: List[str] = dspy.OutputField(desc="Specific tips for improvement")