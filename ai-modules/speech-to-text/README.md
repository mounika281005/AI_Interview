# Speech-to-Text Module

## Purpose
Converts the candidate's spoken audio responses into text for further analysis.
This is the first step in processing interview answers.

## Structure
```
speech-to-text/
├── src/
│   ├── transcriber/
│   │   ├── whisper_engine.py      # OpenAI Whisper integration
│   │   ├── google_stt.py          # Google Speech-to-Text (backup)
│   │   └── base_transcriber.py    # Abstract base class
│   ├── audio_processing/
│   │   ├── noise_reduction.py     # Audio cleanup
│   │   ├── audio_splitter.py      # Split long audio
│   │   └── format_converter.py    # Convert audio formats
│   ├── models/                    # Pre-trained model weights
│   ├── api/
│   │   └── stt_service.py         # Service API endpoint
│   └── utils/
│       ├── audio_utils.py
│       └── text_cleanup.py        # Post-processing text
├── requirements.txt
└── Dockerfile
```

## Key Features
- Real-time audio streaming transcription
- Support for multiple languages
- Noise reduction & audio enhancement
- Punctuation & formatting
- Confidence scores for transcribed text

## Models Used
- OpenAI Whisper (primary)
- Google Speech-to-Text (fallback)
