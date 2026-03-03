# Unit Tests for AI Mock Interview System

This folder contains all unit and integration tests for the backend API.

## 📁 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini               # Pytest configuration
├── requirements-test.txt    # Test dependencies
├── test_users.py            # User API tests
├── test_interviews.py       # Interview API tests
├── test_feedback.py         # Feedback API tests
├── test_nlp_evaluator.py    # NLP service tests
└── test_stt_service.py      # Speech-to-text service tests
```

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
cd backend
pip install -r tests/requirements-test.txt
```

### 2. Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### 3. Run Specific Test Files

```bash
# Run user tests only
pytest tests/test_users.py

# Run interview tests only
pytest tests/test_interviews.py

# Run feedback tests only
pytest tests/test_feedback.py
```

### 4. Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_users.py::TestUserRegistration

# Run a specific test function
pytest tests/test_users.py::TestUserRegistration::test_register_success
```

## 📋 Test Categories

### User Tests (`test_users.py`)

| Test | Description |
|------|-------------|
| `test_register_success` | Successful user registration |
| `test_register_duplicate_email` | Reject duplicate email |
| `test_login_success` | Successful login |
| `test_login_wrong_password` | Reject wrong password |
| `test_get_profile_authenticated` | Get profile when logged in |
| `test_update_profile` | Update user profile |

### Interview Tests (`test_interviews.py`)

| Test | Description |
|------|-------------|
| `test_create_session_success` | Create interview session |
| `test_get_sessions_list` | List user's sessions |
| `test_generate_questions_success` | Generate questions |
| `test_upload_audio_success` | Upload audio recording |
| `test_complete_session_success` | Complete a session |

### Feedback Tests (`test_feedback.py`)

| Test | Description |
|------|-------------|
| `test_calculate_scores_success` | Calculate session scores |
| `test_generate_feedback_success` | Generate AI feedback |
| `test_get_history_success` | Get feedback history |
| `test_get_dashboard_success` | Get dashboard data |

### NLP Evaluator Tests (`test_nlp_evaluator.py`)

| Test | Description |
|------|-------------|
| `test_evaluate_relevant_answer` | Score relevant answers |
| `test_evaluate_irrelevant_answer` | Detect irrelevant answers |
| `test_evaluate_with_grammar_errors` | Detect grammar issues |
| `test_generate_strengths_feedback` | Generate positive feedback |

### STT Service Tests (`test_stt_service.py`)

| Test | Description |
|------|-------------|
| `test_transcribe_audio_success` | Successful transcription |
| `test_transcribe_empty_audio` | Handle silent audio |
| `test_supported_audio_formats` | Check format support |

## 🔧 Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
asyncio_mode = auto
addopts = -v --tb=short
```

### Environment Variables for Tests

Create a `.env.test` file:

```env
DATABASE_URL=sqlite+aiosqlite:///:memory:
SECRET_KEY=test-secret-key-for-testing
DEBUG=true
```

## 📊 Coverage Report

Generate a coverage report:

```bash
# Terminal report
pytest --cov=app --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 🏷️ Test Markers

```bash
# Run only async tests
pytest -m asyncio

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run slow tests
pytest -m slow
```

## 💡 Writing New Tests

### Example Test Structure

```python
import pytest
from httpx import AsyncClient

class TestMyFeature:
    """Tests for my feature."""
    
    @pytest.mark.asyncio
    async def test_my_feature_success(self, client: AsyncClient, auth_headers):
        """Test that my feature works correctly."""
        response = await client.post(
            "/api/v1/my-endpoint",
            headers=auth_headers,
            json={"key": "value"}
        )
        
        assert response.status_code == 200
        assert response.json()["key"] == "value"
```

### Using Fixtures

Available fixtures in `conftest.py`:

- `client` - Async HTTP client for API testing
- `test_session` - Database session for test data
- `test_user` - Pre-created test user
- `auth_headers` - Authorization headers for authenticated requests
- `test_session_data` - Pre-created interview session
- `test_question` - Pre-created interview question

## 🐛 Debugging Tests

```bash
# Run with print statements visible
pytest -s

# Run with full traceback
pytest --tb=long

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```
