#!/bin/bash

# Quiz Test Runner Script
# Handles intelligent quiz grading with file timestamp checking and result caching
# Usage: ./run_quiz_test.sh --config config.toml --quiz-file quiz.toml --api-key API_KEY [--output results.json]

set -e  # Exit on any error

# Parse command line arguments
CONFIG=""
QUIZ_FILE=""
API_KEY=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG="$2"
            shift 2
            ;;
        --quiz-file)
            QUIZ_FILE="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$CONFIG" || -z "$QUIZ_FILE" || -z "$API_KEY" ]]; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 --config CONFIG --quiz-file QUIZ_FILE --api-key API_KEY [--output OUTPUT]"
    exit 1
fi

# Set default output if not provided
if [[ -z "$OUTPUT" ]]; then
    OUTPUT="./assignment/quiz_results.json"
fi

echo "🎯 Quiz Test Runner Starting..."
echo "📋 Config: $CONFIG"
echo "📝 Quiz file: $QUIZ_FILE"
echo "💾 Output: $OUTPUT"

# Function to extract questions and answers from TOML file
extract_toml_content() {
    python3 -c "
import tomllib
import json
import sys

try:
    with open('$1', 'rb') as f:
        data = tomllib.load(f)
    # Create a sorted list of question-answer pairs
    qa_pairs = sorted([(q.get('question', ''), q.get('answer', '')) for q in data.get('questions', [])])
    print(json.dumps(qa_pairs, separators=(',', ':')))
except Exception as e:
    print('[]', file=sys.stderr)
    sys.exit(1)
"
}

# Check if results file exists and determine what to do
if [[ ! -f "$OUTPUT" ]]; then
    echo "📂 No results file found - running LLM quiz for first time"
else
    echo "📁 Results file found - checking if quiz content has changed"

    # Extract current questions and answers from TOML file
    CURRENT_CONTENT=$(extract_toml_content "$QUIZ_FILE")

    # Extract questions and answers from stored results
    STORED_CONTENT=$(jq -c '[.question_results[] | [.question, .correct_answer]] | sort' "$OUTPUT" 2>/dev/null || echo "[]")
    echo "📝 Previous content: $STORED_CONTENT"
    echo "📝 Current content: $CURRENT_CONTENT"

    if [[ "$CURRENT_CONTENT" != "$STORED_CONTENT" ]]; then
        echo "🔄 Quiz content has changed - re-running grading"
        echo "🗑️ Removing old results file"
        rm -f "$OUTPUT"
    else
        echo "📋 Quiz content unchanged - checking if student passed"

        # Check if student stumped all LLMs using jq
        if jq -e '.student_passes == true' "$OUTPUT" > /dev/null 2>&1; then
            echo "🎉 STUDENT PASSED: Stumped LLMs in all questions!"
            echo "✅ Skipping grading and awarding full points"
            exit 0
        else
            echo "❌ STUDENT FAILED: Did not stump LLMs in all questions"
            exit 1
        fi
    fi
fi


# Run the quiz grading
echo "🚀 Starting LLM quiz grading..."
uv run python -m grading.llm_quiz \
    --config "$CONFIG" \
    --quiz-file "$QUIZ_FILE" \
    --api-key "$API_KEY" \
    --output "$OUTPUT" 

# Check the result
if [[ -f "$OUTPUT" ]]; then
    echo "✅ Quiz grading completed successfully"
    echo "💾 Results saved to: $OUTPUT"

    # Show final result
    if jq -e '.student_passes == true' "$OUTPUT" > /dev/null 2>&1; then
        echo "🎉 FINAL RESULT: Student PASSED!"
    else
        echo "📊 FINAL RESULT: Student did not pass this attempt"
    fi
else
    echo "❌ Error: Quiz grading failed - no results file generated"
    exit 1
fi

echo "🏁 Quiz test runner completed"
