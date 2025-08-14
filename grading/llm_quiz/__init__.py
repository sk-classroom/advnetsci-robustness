"""
LLM Quiz Challenge Library

A library for creating and evaluating quiz challenges where students try to stump AI models.
"""

# Main interfaces
from .challenge import LLMQuizChallenge
from .core import LLMQuizChallenge as LLMQuizChallengeOld  # Keep old interface for compatibility

# Core components for advanced usage
from .llm_client import LLMClient
from .quiz_runner import QuizRunner, QuizResults, QuizQuestion, QuestionResult
from .validator import QuestionValidator, ValidationResult, ValidationIssue
from .content_loader import ContentLoader, ContentSource
from .results_analyzer import ResultsAnalyzer

__version__ = "2.0.0"
__all__ = [
    # Main interface
    "LLMQuizChallenge",
    
    # Compatibility
    "LLMQuizChallengeOld",
    
    # Core components
    "LLMClient",
    "QuizRunner", 
    "QuizResults",
    "QuizQuestion",
    "QuestionResult",
    "QuestionValidator",
    "ValidationResult", 
    "ValidationIssue",
    "ContentLoader",
    "ContentSource",
    "ResultsAnalyzer"
]