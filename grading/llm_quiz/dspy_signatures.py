"""
DSPy signatures for the LLM Quiz Challenge.

This module defines structured DSPy signatures that replace complex manual
prompt engineering and JSON parsing with clean, type-safe interactions.
"""

from enum import Enum
from typing import List, Literal, Optional

import dspy


class ValidationIssue(str, Enum):
    """Types of validation issues that can occur with quiz questions."""

    HEAVY_MATH = "heavy_math"
    PROMPT_INJECTION = "prompt_injection"
    ANSWER_QUALITY = "answer_quality"
    CONTEXT_MISMATCH = (
        "context_mismatch"  # Only use when question is completely unrelated to course topic
    )
    VAGUE_QUESTION = "vague_question"  # Question lacks specificity or clarity
    AMBIGUOUS_WORDING = "ambiguous_wording"  # Question has multiple interpretations
    INCOMPLETE_CONTEXT = "incomplete_context"  # Question lacks sufficient context to answer clearly


class ParseQuestionAndAnswer(dspy.Signature):
    """Parse questions and answers from raw student input in various formats."""

    raw_input: str = dspy.InputField(
        desc="Student input containing questions and answers in any format"
    )

    questions: List[str] = dspy.OutputField(desc="List of extracted questions")
    answers: List[str] = dspy.OutputField(
        desc="List of corresponding answers, 'MISSING' if not provided"
    )
    has_answers: List[bool] = dspy.OutputField(desc="Whether each question has a provided answer")


class ValidateQuestion(dspy.Signature):
    """Validate a student's quiz question and their provided correct answer.

    Questions should be considered valid if they are generally relevant to the course topic
    (network science, small-world networks, etc.) even if they don't reference specific
    details from the context. Only flag context_mismatch if the question is completely
    unrelated to the course subject matter.
    
    Pay special attention to question clarity and specificity:
    - Flag vague_question if the question lacks specificity or is too general
    - Flag ambiguous_wording if the question has multiple valid interpretations
    - Flag incomplete_context if the question lacks sufficient context to answer clearly
    - Questions should be precise, unambiguous, and clearly worded"""

    question: str = dspy.InputField(desc="The student's quiz question to validate")
    answer: str = dspy.InputField(desc="The student's provided correct answer")
    context_content: Optional[str] = dspy.InputField(desc="Course context materials, if available")

    is_valid: bool = dspy.OutputField(desc="Whether the question is valid and acceptable")
    issues: List[ValidationIssue] = dspy.OutputField(
        desc="List of specific validation issues found (check for vague_question, ambiguous_wording, incomplete_context)"
    )
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = dspy.OutputField(
        desc="Confidence in validation decision"
    )
    reason: str = dspy.OutputField(desc="Brief explanation of the validation decision")
    revision_suggestions: List[str] = dspy.OutputField(
        desc="Specific suggestions for improving the question if invalid"
    )
    difficulty_assessment: Literal["TOO_EASY", "APPROPRIATE", "TOO_HARD"] = dspy.OutputField(
        desc="Assessment of question difficulty level"
    )
    clarity_score: Literal["CLEAR", "SOMEWHAT_CLEAR", "UNCLEAR"] = dspy.OutputField(
        desc="Assessment of question clarity and specificity"
    )


class AnswerQuizQuestion(dspy.Signature):
    """LLM attempts to answer a student's quiz question using provided context materials."""

    question: str = dspy.InputField(desc="The student's quiz question for LLM to answer")
    context_content: Optional[str] = dspy.InputField(desc="Course context materials for reference")

    answer: str = dspy.OutputField(
        desc="Concise but thorough answer to the question (max 300 words)"
    )


class EvaluateAnswer(dspy.Signature):
    """Evaluate an LLM's answer against the student's correct answer."""

    question: str = dspy.InputField(desc="The student's quiz question")
    correct_answer: str = dspy.InputField(desc="The student's provided correct answer")
    llm_answer: str = dspy.InputField(desc="The LLM's attempt at answering the student's question")

    verdict: Literal["CORRECT", "INCORRECT"] = dspy.OutputField(
        desc="Whether the LLM's answer is correct"
    )
    student_wins: bool = dspy.OutputField(
        desc="True if student wins (LLM got it wrong), False if LLM correct"
    )
    explanation: str = dspy.OutputField(
        desc="Brief explanation of the evaluation decision and reasoning"
    )
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = dspy.OutputField(
        desc="Confidence level in the evaluation"
    )
    improvement_suggestions: List[str] = dspy.OutputField(
        desc="Suggestions for making the question more challenging if LLM answered correctly"
    )


class GenerateRevisionGuidance(dspy.Signature):
    """Generate detailed revision guidance for student's quiz questions that need improvement.
    
    Focus especially on clarity and specificity issues:
    - Provide specific guidance for making vague questions more precise
    - Suggest ways to eliminate ambiguous wording
    - Recommend adding context when questions are incomplete
    - Give concrete examples of clearer question formulations"""

    question: str = dspy.InputField(desc="The student's quiz question")
    answer: str = dspy.InputField(desc="The student's provided correct answer")
    validation_issues: List[str] = dspy.InputField(desc="Issues found during validation")
    llm_response: Optional[str] = dspy.InputField(
        desc="LLM's attempt at answering if question was processed"
    )
    evaluation_result: Optional[str] = dspy.InputField(
        desc="Evaluation result if question was processed"
    )
    context_topics: List[str] = dspy.InputField(desc="Main topics covered in the context materials")

    revision_priority: Literal["HIGH", "MEDIUM", "LOW"] = dspy.OutputField(
        desc="Priority level for revising this question"
    )
    specific_issues: List[str] = dspy.OutputField(
        desc="Detailed list of specific problems with the question"
    )
    concrete_suggestions: List[str] = dspy.OutputField(
        desc="Step-by-step suggestions for improvement, focusing on clarity and specificity"
    )
    example_improvements: List[str] = dspy.OutputField(
        desc="Concrete examples of how to rewrite parts of the question for better clarity"
    )
    difficulty_adjustment: str = dspy.OutputField(
        desc="How to adjust difficulty level appropriately"
    )
    context_alignment: str = dspy.OutputField(
        desc="How to better align question with provided context materials"
    )
    clarity_improvements: List[str] = dspy.OutputField(
        desc="Specific suggestions for making the question clearer and more precise"
    )


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
    pass_result: Literal["PASS", "FAIL"] = dspy.OutputField(
        desc="Whether the student passed the challenge"
    )
    github_classroom_marker: str = dspy.OutputField(desc="GitHub Classroom result marker")
    improvement_tips: List[str] = dspy.OutputField(desc="Specific tips for improvement")
