# Tests

## Purpose
Contains all test suites for unit tests, integration tests, and end-to-end tests across all modules.

## Structure
```
tests/
├── unit/
│   ├── backend/                 # Backend unit tests
│   ├── ai_modules/              # AI module unit tests
│   │   ├── speech_to_text/
│   │   ├── nlp_evaluation/
│   │   ├── question_generation/
│   │   └── scoring_feedback/
│   └── database/                # Database unit tests
├── integration/
│   ├── api_tests/               # API integration tests
│   ├── ai_pipeline_tests/       # AI pipeline tests
│   └── db_tests/                # Database integration tests
├── e2e/
│   ├── interview_flow_tests/    # Full interview flow tests
│   └── user_journey_tests/      # User journey tests
├── fixtures/
│   ├── sample_audio/            # Test audio files
│   ├── sample_responses/        # Sample interview responses
│   └── mock_data/               # Mock database data
├── conftest.py                  # Pytest configuration
└── pytest.ini                   # Pytest settings
```

## Running Tests
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/unit/ai_modules/

# Run with coverage
pytest --cov=src tests/
```
