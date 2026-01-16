# NLP Answer Evaluation Module

## Overview

This module provides NLP-based evaluation of interview answers, scoring responses across multiple dimensions:

- **Relevance** (35%) - How well the answer addresses the question
- **Grammar** (20%) - Correctness of language and structure
- **Fluency** (25%) - Coherence, readability, and flow
- **Keywords** (20%) - Coverage of expected technical terms

## Installation

### Required Dependencies

```bash
pip install numpy
```

### Optional Dependencies (Recommended for Better Accuracy)

```bash
# Natural Language Toolkit - for advanced tokenization
pip install nltk

# Grammar checking
pip install language-tool-python

# Semantic similarity (requires ~400MB download)
pip install sentence-transformers
```

### NLTK Data Download

If using NLTK, download required data:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
```

## Quick Start

```python
from answer_evaluator import AnswerEvaluator, evaluate_answer

# Simple usage
question = "What is Object-Oriented Programming?"
answer = "OOP is a programming paradigm based on objects and classes..."
keywords = ["object", "class", "encapsulation", "inheritance"]

# Get JSON result
json_result = evaluate_answer(question, answer, keywords)
print(json_result)
```

## Detailed Usage

```python
from answer_evaluator import AnswerEvaluator

# Create evaluator
evaluator = AnswerEvaluator(use_advanced_models=True)

# Evaluate
result = evaluator.evaluate(
    question="Explain polymorphism in OOP",
    answer="Polymorphism allows objects to take multiple forms...",
    expected_keywords=["polymorphism", "override", "interface"],
    context="Software Engineering Interview"
)

# Access scores
print(f"Overall: {result.overall_score}/100")
print(f"Grade: {result.grade}")
print(f"Relevance: {result.relevance.score}")
print(f"Grammar: {result.grammar.score}")
print(f"Fluency: {result.fluency.score}")
print(f"Keywords: {result.keywords.score}")

# Get suggestions
for suggestion in result.suggestions:
    print(f"- {suggestion}")
```

## Output Format

```json
{
  "question": "What is machine learning?",
  "answer": "Machine learning is...",
  "overall_score": 82.5,
  "grade": "A",
  "scores": {
    "relevance": {
      "score": 85.0,
      "weight": 0.35,
      "feedback": "Excellent! Your answer directly addresses the question."
    },
    "grammar": {
      "score": 90.0,
      "weight": 0.20,
      "feedback": "Excellent grammar! No errors detected."
    },
    "fluency": {
      "score": 75.0,
      "weight": 0.25,
      "feedback": "Good fluency. Consider adding transition words."
    },
    "keywords": {
      "score": 80.0,
      "weight": 0.20,
      "feedback": "Excellent! You've covered most key technical terms."
    }
  },
  "suggestions": ["Great job! Keep practicing to maintain this level."],
  "strengths": ["Strong grammar and spelling", "Good question relevance"]
}
```

## Configuration

### Custom Weights

```python
from scoring_config import WeightProfiles

evaluator = AnswerEvaluator()

# For technical interviews - emphasize keywords
evaluator.WEIGHTS = WeightProfiles.TECHNICAL.to_dict()

# For behavioral interviews - emphasize fluency
evaluator.WEIGHTS = WeightProfiles.BEHAVIORAL.to_dict()
```

### Domain Keywords

```python
from scoring_config import get_keywords_for_topic, get_all_keywords_for_domain

# Get specific topic keywords
oop_keywords = get_keywords_for_topic('software_engineering', 'oop_concepts')

# Get all keywords for a domain
all_ds_keywords = get_all_keywords_for_domain('data_science')
```

## File Structure

```
ai-modules/nlp-evaluation/src/
├── answer_evaluator.py   # Main evaluation module
├── scoring_config.py     # Weights, keywords, configuration
├── example_usage.py      # Usage examples
└── README.md             # This file
```

## Scoring Logic

### Relevance Score
- Uses semantic similarity (if sentence-transformers installed)
- Falls back to keyword overlap (Jaccard similarity)
- Bonus for answering the correct question type (what/how/why)

### Grammar Score
- Uses LanguageTool (if installed) for comprehensive checks
- Falls back to rule-based checking
- Deducts points per error based on severity

### Fluency Score
- Sentence length analysis (variety bonus)
- Flesch-Kincaid readability score
- Transition word detection
- Answer length appropriateness

### Keyword Score
- Percentage of expected keywords found
- Supports lemmatization for flexible matching

## License

MIT License - AI Mock Interview System
