# Shared Utilities

## Purpose
Contains shared code, types, constants, and utilities used across multiple modules to avoid duplication and ensure consistency.

## Structure
```
shared/
├── types/
│   ├── interview_types.py       # Interview-related types
│   ├── user_types.py            # User-related types
│   ├── ai_types.py              # AI module types
│   └── api_types.py             # API request/response types
├── constants/
│   ├── error_codes.py           # Standardized error codes
│   ├── interview_constants.py   # Interview configurations
│   └── scoring_constants.py     # Scoring thresholds
├── utils/
│   ├── logger.py                # Centralized logging
│   ├── validators.py            # Common validators
│   ├── formatters.py            # Data formatters
│   └── helpers.py               # General helpers
└── exceptions/
    ├── base_exception.py        # Base exception class
    ├── api_exceptions.py        # API-related exceptions
    └── ai_exceptions.py         # AI module exceptions
```

## Key Benefits
- Code reusability across modules
- Consistent type definitions
- Centralized error handling
- Standardized logging format
