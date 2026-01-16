# Question Generation Module

## Purpose
Dynamically generates relevant interview questions based on job role, difficulty level, and previous answers. Uses AI to create personalized interview experiences.

## Structure
```
question-generation/
├── src/
│   ├── generators/
│   │   ├── llm_generator.py         # LLM-based question generation
│   │   ├── template_generator.py    # Template-based questions
│   │   ├── followup_generator.py    # Follow-up questions based on answers
│   │   └── adaptive_generator.py    # Difficulty-adjusted questions
│   ├── templates/
│   │   ├── technical/               # Technical question templates
│   │   ├── behavioral/              # Behavioral question templates
│   │   ├── situational/             # Situational question templates
│   │   └── role_specific/           # Job-specific templates
│   ├── question_bank/
│   │   ├── loader.py                # Load questions from DB
│   │   ├── categorizer.py           # Categorize questions
│   │   └── difficulty_ranker.py     # Rank by difficulty
│   ├── api/
│   │   └── question_service.py      # Service API endpoint
│   └── utils/
│       ├── prompt_builder.py        # Build LLM prompts
│       └── question_validator.py    # Validate generated questions
├── requirements.txt
└── Dockerfile
```

## Key Features
- Dynamic question generation using GPT/LLaMA
- Role-specific question customization
- Adaptive difficulty adjustment
- Follow-up question generation
- Question deduplication
- Support for multiple interview types

## Question Types
- Technical (coding, system design)
- Behavioral (STAR method)
- Situational (hypothetical scenarios)
- Role-specific (domain knowledge)
