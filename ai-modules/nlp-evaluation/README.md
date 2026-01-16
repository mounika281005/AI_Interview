# NLP Evaluation Module

## Purpose
Analyzes the transcribed text to evaluate the quality, relevance, and depth of the candidate's answers using Natural Language Processing.

## Structure
```
nlp-evaluation/
├── src/
│   ├── analyzers/
│   │   ├── semantic_analyzer.py     # Meaning & context analysis
│   │   ├── sentiment_analyzer.py    # Confidence & tone detection
│   │   ├── keyword_extractor.py     # Key concepts identification
│   │   ├── grammar_checker.py       # Language quality check
│   │   └── relevance_scorer.py      # Answer relevance to question
│   ├── embeddings/
│   │   ├── sentence_embeddings.py   # Text vectorization
│   │   └── similarity_calculator.py # Cosine similarity for matching
│   ├── models/
│   │   ├── fine_tuned/              # Custom trained models
│   │   └── pretrained/              # HuggingFace models
│   ├── api/
│   │   └── evaluation_service.py    # Service API endpoint
│   └── utils/
│       ├── text_preprocessor.py     # Clean & normalize text
│       └── tokenizer.py             # Text tokenization
├── requirements.txt
└── Dockerfile
```

## Key Features
- Semantic understanding of answers
- Relevance scoring (how well answer matches question)
- Sentiment & confidence analysis
- Technical keyword extraction
- Grammar & fluency evaluation
- Comparison with ideal answers

## Models Used
- BERT/RoBERTa for semantic analysis
- Sentence-Transformers for embeddings
- Custom fine-tuned models for interview context
