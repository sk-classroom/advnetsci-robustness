# LLM Quiz Challenge System

An intelligent quiz grading system where students create questions to challenge AI models. Built with DSPy for structured LLM interactions and featuring comprehensive progress tracking and revision guidance.

## 🎯 Overview

This system allows students to:
- Create quiz questions with their correct answers
- Challenge AI models to answer their questions  
- Win by stumping the AI with challenging, course-relevant questions
- Receive detailed feedback and revision guidance

## ✨ Features

### 🤖 AI-Powered Grading
- **DSPy Integration**: Uses structured DSPy signatures for reliable LLM interactions
- **Multi-Model Support**: Works with OpenRouter, OpenAI, Ollama, and other OpenAI-compatible APIs
- **Intelligent Validation**: Automatically validates question quality and appropriateness

### 📊 Progress Tracking
- **Granular Progress Bar**: Shows detailed processing steps (validate → guidance → LLM quiz → evaluate → complete)
- **Real-time Status**: Live updates on current processing stage
- **Performance Metrics**: Processing speed and completion statistics

### 📝 Comprehensive Feedback
- **Clear Pass/Fail Results**: Prominent success/failure indicators
- **Detailed Question Analysis**: Shows student's questions, AI responses, and evaluations
- **Smart Revision Guidance**: Targeted suggestions only for questions needing improvement
- **GitHub Classroom Integration**: Automated pass/fail markers for grading

### 🔧 Flexible Configuration
- **TOML Configuration**: Centralized settings for models, contexts, and parameters
- **Context Integration**: Load course materials from URLs for contextual validation
- **Multiple Output Formats**: JSON results and console display

## 🚀 Quick Start

### Installation

Using uv (recommended):
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the project
uv install
```

Using pip:
```bash
pip install -r llm_quiz/requirements.txt
```

### Basic Usage

1. **Create a quiz file** (`quiz.toml`):
```toml
title = "Network Science Quiz"

[[questions]]
question = "When is the global clustering not a good representation of the network?"
answer = "When the network is degree heterogeneous. Hubs can create many triangles, not representing typical nodes."

[[questions]] 
question = "When is the average path length not a good representation of the network?"
answer = "When the network is degree heterogeneous. Hubs can substantially reduce average path lengths."
```

2. **Run the quiz challenge**:
```bash
uv run python -m llm_quiz.cli \
    --quiz-file quiz.toml \
    --api-key your-api-key \
    --config config.toml
```

## 📋 Configuration

### config.toml Example
```toml
[api]
base_url = "https://openrouter.ai/api/v1"

[models]
quiz_model = "openrouter/google/gemma-3-4b-it"
evaluator_model = "openrouter/google/gemini-2.5-flash-lite"

[context]
urls = [
    "https://raw.githubusercontent.com/course/repo/main/docs/lecture-notes.qmd"
]

[output]
verbose = false
```

### Command Line Options

```bash
# Basic usage
uv run python -m llm_quiz.cli --quiz-file quiz.toml --api-key sk-xxx

# With custom configuration
uv run python -m llm_quiz.cli --quiz-file quiz.toml --api-key sk-xxx --config config.toml

# Save detailed results
uv run python -m llm_quiz.cli --quiz-file quiz.toml --api-key sk-xxx --output results.json

# Enable verbose logging
uv run python -m llm_quiz.cli --quiz-file quiz.toml --api-key sk-xxx --verbose

# Custom models
uv run python -m llm_quiz.cli \
    --quiz-file quiz.toml \
    --api-key sk-xxx \
    --quiz-model gpt-4o-mini \
    --evaluator-model gpt-4o

# Use local Ollama
uv run python -m llm_quiz.cli \
    --quiz-file quiz.toml \
    --base-url http://localhost:11434/v1 \
    --api-key dummy \
    --quiz-model llama2 \
    --evaluator-model llama2
```

## 🏗️ Architecture

### Core Components

1. **DSPy Signatures** (`dspy_signatures.py`): Structured interfaces for LLM interactions
   - `ValidateQuestion`: Validates student questions for quality and relevance
   - `AnswerQuizQuestion`: LLM attempts to answer student questions
   - `EvaluateAnswer`: Compares LLM answers against correct answers
   - `GenerateRevisionGuidance`: Provides improvement suggestions

2. **DSPy Core** (`dspy_core.py`): Main processing engine
   - Question validation and processing
   - LLM interaction management
   - Results compilation and analysis

3. **CLI Interface** (`cli.py`): User-friendly command-line interface
   - Progress tracking and display
   - Results formatting and output
   - Configuration management

### Processing Pipeline

1. **Load Quiz**: Parse TOML quiz file with student questions and answers
2. **Validate Questions**: Check each question for quality and appropriateness  
3. **Generate Guidance**: Create revision suggestions for all questions
4. **LLM Quiz**: AI attempts to answer valid student questions
5. **Evaluate Answers**: Compare AI responses against correct answers
6. **Generate Results**: Compile pass/fail status and detailed feedback

## 🎓 Academic Integration

### GitHub Classroom
The system automatically generates pass/fail markers for GitHub Classroom:
- `STUDENTS_QUIZ_KEIKO_WIN`: Student passes (AI was stumped)  
- `STUDENTS_QUIZ_KEIKO_LOSE`: Student fails (AI answered correctly)

### Grading Criteria
- **Pass**: Student must stump the AI on ALL valid questions (100% success rate)
- **Fail**: AI correctly answers any student question

## 🛠️ Development

### Project Structure
```
llm_quiz/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point  
├── cli.py               # Command-line interface
├── dspy_core.py         # Core processing logic
├── dspy_signatures.py   # DSPy signature definitions
├── test_dspy.py         # Basic functionality tests
├── test_quiz.toml       # Example quiz file
└── requirements.txt     # Python dependencies
```

### Testing
```bash
# Run basic tests
uv run python llm_quiz/test_dspy.py

# Test with sample quiz
uv run python -m llm_quiz.cli --quiz-file llm_quiz/test_quiz.toml --api-key sk-xxx

# Verbose debugging
uv run python -m llm_quiz.cli --quiz-file quiz.toml --api-key sk-xxx --verbose
```

## 🔍 Example Output

```
================================================================================
🎉 RESULT: PASS - You successfully stumped the AI!
================================================================================
📊 Summary: 2/2 questions stumped the AI
Success Rate: 100.0%

Question 1: ✅ You win!
  Your question: When is the global clustering not a good representation?
  Your answer: When the network is degree heterogeneous...
  AI's answer: Global clustering is not good when the network primarily consists...
  Evaluation: The LLM's answer describes local clusters but misses degree heterogeneity...

Question 2: ✅ You win!
  Your question: When is average path length not representative?
  Your answer: When hubs are present, they reduce average paths...
  AI's answer: Average path length isn't reliable in highly clustered networks...
  Evaluation: The LLM discusses clustering but not the key concept of hubs...

✨ All your questions successfully stumped the AI! No revisions needed.
```

## 🤝 Contributing

This system was built for educational use in network science courses. Key design principles:

- **Student-Focused**: Clear feedback helps students improve their questions
- **Flexible Validation**: Accepts course-relevant topics without being overly restrictive
- **Transparent Processing**: Detailed progress tracking and explanations
- **Reliable Results**: DSPy ensures consistent LLM interactions

## 📄 License

This project is designed for academic use in network science education.

---

**Built with DSPy for reliable LLM interactions** 🤖