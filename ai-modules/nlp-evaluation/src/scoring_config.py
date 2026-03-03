"""
==============================================================================
Scoring Configuration for NLP Answer Evaluation
==============================================================================

This module contains configurable scoring parameters, keyword dictionaries
for different interview domains, and utility functions for score calculation.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


# ============================================================================
# SCORING WEIGHTS CONFIGURATION
# ============================================================================

@dataclass
class ScoringWeights:
    """Configurable weights for different scoring dimensions."""
    relevance: float = 0.35
    grammar: float = 0.20
    fluency: float = 0.25
    keywords: float = 0.20
    
    def __post_init__(self):
        """Validate that weights sum to 1.0."""
        total = self.relevance + self.grammar + self.fluency + self.keywords
        if not (0.99 <= total <= 1.01):  # Allow small floating point error
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format."""
        return {
            'relevance': self.relevance,
            'grammar': self.grammar,
            'fluency': self.fluency,
            'keywords': self.keywords
        }


# ============================================================================
# PREDEFINED WEIGHT PROFILES
# ============================================================================

class WeightProfiles:
    """Predefined weight configurations for different interview types."""
    
    # Standard balanced evaluation
    BALANCED = ScoringWeights(
        relevance=0.35,
        grammar=0.20,
        fluency=0.25,
        keywords=0.20
    )
    
    # Technical interviews - keywords matter more
    TECHNICAL = ScoringWeights(
        relevance=0.30,
        grammar=0.15,
        fluency=0.20,
        keywords=0.35
    )
    
    # Behavioral interviews - fluency and relevance matter more
    BEHAVIORAL = ScoringWeights(
        relevance=0.40,
        grammar=0.15,
        fluency=0.35,
        keywords=0.10
    )
    
    # Communication-focused - grammar and fluency emphasized
    COMMUNICATION = ScoringWeights(
        relevance=0.25,
        grammar=0.30,
        fluency=0.35,
        keywords=0.10
    )


# ============================================================================
# DOMAIN-SPECIFIC KEYWORD DICTIONARIES
# ============================================================================

KEYWORD_DICTIONARIES: Dict[str, Dict[str, List[str]]] = {
    
    # ========================================================================
    # SOFTWARE ENGINEERING
    # ========================================================================
    "software_engineering": {
        "oop_concepts": [
            "encapsulation", "inheritance", "polymorphism", "abstraction",
            "class", "object", "interface", "method", "constructor",
            "destructor", "getter", "setter", "private", "public", "protected"
        ],
        "design_patterns": [
            "singleton", "factory", "observer", "strategy", "decorator",
            "adapter", "facade", "proxy", "builder", "prototype",
            "mvc", "mvvm", "repository", "dependency injection"
        ],
        "data_structures": [
            "array", "linked list", "stack", "queue", "tree", "graph",
            "hash table", "heap", "binary tree", "b-tree", "trie",
            "set", "map", "dictionary", "priority queue"
        ],
        "algorithms": [
            "sorting", "searching", "dynamic programming", "recursion",
            "big o", "time complexity", "space complexity", "greedy",
            "divide and conquer", "backtracking", "bfs", "dfs"
        ],
        "databases": [
            "sql", "nosql", "normalization", "index", "query", "join",
            "primary key", "foreign key", "acid", "transaction",
            "mongodb", "postgresql", "mysql", "redis"
        ],
        "web_development": [
            "html", "css", "javascript", "react", "angular", "vue",
            "rest", "api", "http", "https", "authentication",
            "frontend", "backend", "full stack", "responsive"
        ],
        "devops": [
            "docker", "kubernetes", "ci/cd", "jenkins", "git",
            "deployment", "container", "microservices", "cloud",
            "aws", "azure", "gcp", "terraform", "ansible"
        ]
    },
    
    # ========================================================================
    # DATA SCIENCE / MACHINE LEARNING
    # ========================================================================
    "data_science": {
        "ml_fundamentals": [
            "supervised learning", "unsupervised learning", "classification",
            "regression", "clustering", "feature engineering", "training",
            "testing", "validation", "cross validation", "overfitting",
            "underfitting", "bias", "variance", "hyperparameter"
        ],
        "algorithms_ml": [
            "linear regression", "logistic regression", "decision tree",
            "random forest", "svm", "knn", "naive bayes", "neural network",
            "deep learning", "gradient descent", "backpropagation"
        ],
        "deep_learning": [
            "cnn", "rnn", "lstm", "transformer", "attention", "bert",
            "gpt", "encoder", "decoder", "embedding", "activation",
            "dropout", "batch normalization", "convolution", "pooling"
        ],
        "tools_frameworks": [
            "python", "tensorflow", "pytorch", "keras", "scikit-learn",
            "pandas", "numpy", "matplotlib", "jupyter", "spark"
        ],
        "nlp": [
            "tokenization", "stemming", "lemmatization", "word embedding",
            "sentiment analysis", "named entity", "pos tagging",
            "text classification", "language model", "transformer"
        ],
        "statistics": [
            "mean", "median", "mode", "standard deviation", "variance",
            "correlation", "hypothesis testing", "p-value", "confidence interval",
            "probability", "distribution", "normal distribution"
        ]
    },
    
    # ========================================================================
    # BEHAVIORAL / SOFT SKILLS
    # ========================================================================
    "behavioral": {
        "leadership": [
            "team", "leadership", "delegation", "motivation", "mentoring",
            "decision making", "conflict resolution", "collaboration",
            "communication", "initiative", "responsibility"
        ],
        "problem_solving": [
            "analyze", "approach", "solution", "challenge", "obstacle",
            "creative", "critical thinking", "troubleshoot", "debug",
            "root cause", "systematic", "methodology"
        ],
        "teamwork": [
            "collaborate", "team player", "support", "contribute",
            "coordination", "feedback", "consensus", "diverse",
            "stakeholder", "cross-functional"
        ],
        "communication": [
            "explain", "present", "document", "clarify", "listen",
            "articulate", "concise", "clear", "technical writing",
            "audience", "stakeholder communication"
        ],
        "adaptability": [
            "flexible", "adapt", "change", "learn", "growth mindset",
            "resilience", "pivot", "agile", "evolving", "new technology"
        ]
    },
    
    # ========================================================================
    # PROJECT MANAGEMENT
    # ========================================================================
    "project_management": {
        "methodologies": [
            "agile", "scrum", "kanban", "waterfall", "sprint",
            "iteration", "ceremony", "standup", "retrospective",
            "planning", "estimation", "velocity"
        ],
        "tools_processes": [
            "jira", "confluence", "trello", "roadmap", "backlog",
            "epic", "user story", "acceptance criteria", "milestone",
            "deliverable", "timeline", "gantt"
        ],
        "skills": [
            "stakeholder", "requirement", "scope", "risk management",
            "budget", "resource allocation", "prioritization",
            "negotiation", "status report", "escalation"
        ]
    }
}


# ============================================================================
# GRADE THRESHOLDS CONFIGURATION
# ============================================================================

@dataclass
class GradeThreshold:
    """Configuration for a single grade threshold."""
    min_score: float
    grade: str
    label: str
    feedback_prefix: str


DEFAULT_GRADE_THRESHOLDS: List[GradeThreshold] = [
    GradeThreshold(90, 'A+', 'Excellent', 'Outstanding response!'),
    GradeThreshold(80, 'A', 'Very Good', 'Great answer!'),
    GradeThreshold(70, 'B+', 'Good', 'Well done!'),
    GradeThreshold(60, 'B', 'Satisfactory', 'Good effort.'),
    GradeThreshold(50, 'C', 'Needs Improvement', 'Consider improving.'),
    GradeThreshold(40, 'D', 'Poor', 'Significant improvement needed.'),
    GradeThreshold(0, 'F', 'Unsatisfactory', 'Please review and try again.')
]


# ============================================================================
# FLUENCY CONFIGURATION
# ============================================================================

# Transition words for coherence detection
TRANSITION_WORDS = {
    'addition': ['also', 'furthermore', 'moreover', 'additionally', 'besides', 'in addition'],
    'contrast': ['however', 'nevertheless', 'nonetheless', 'although', 'on the other hand', 'in contrast'],
    'cause_effect': ['therefore', 'consequently', 'thus', 'hence', 'as a result', 'because'],
    'sequence': ['first', 'second', 'third', 'next', 'then', 'finally', 'lastly'],
    'example': ['for example', 'for instance', 'specifically', 'particularly', 'such as'],
    'summary': ['in conclusion', 'to summarize', 'overall', 'in summary', 'to conclude']
}

# Ideal answer length ranges (in words)
ANSWER_LENGTH_CONFIG = {
    'short': {'min': 20, 'max': 50, 'ideal': 35},      # Quick factual answers
    'medium': {'min': 50, 'max': 150, 'ideal': 100},   # Standard interview answers
    'long': {'min': 150, 'max': 300, 'ideal': 225},    # Detailed explanations
    'extended': {'min': 300, 'max': 500, 'ideal': 400} # Comprehensive responses
}

# Sentence length guidelines
SENTENCE_CONFIG = {
    'min_ideal': 10,   # Minimum ideal words per sentence
    'max_ideal': 25,   # Maximum ideal words per sentence
    'variety_bonus_threshold': 5  # Minimum variance for variety bonus
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_keywords_for_topic(domain: str, topic: str) -> List[str]:
    """
    Get keywords for a specific domain and topic.
    
    Args:
        domain: The interview domain (e.g., 'software_engineering')
        topic: The specific topic (e.g., 'oop_concepts')
    
    Returns:
        List of keywords, or empty list if not found
    """
    if domain in KEYWORD_DICTIONARIES:
        return KEYWORD_DICTIONARIES[domain].get(topic, [])
    return []


def get_all_keywords_for_domain(domain: str) -> List[str]:
    """
    Get all keywords for a domain (all topics combined).
    
    Args:
        domain: The interview domain
    
    Returns:
        Combined list of all keywords in the domain
    """
    if domain in KEYWORD_DICTIONARIES:
        all_keywords = []
        for topic_keywords in KEYWORD_DICTIONARIES[domain].values():
            all_keywords.extend(topic_keywords)
        return list(set(all_keywords))  # Remove duplicates
    return []


def get_grade_for_score(score: float, thresholds: Optional[List[GradeThreshold]] = None) -> GradeThreshold:
    """
    Get the grade threshold for a given score.
    
    Args:
        score: The numeric score (0-100)
        thresholds: Optional custom thresholds
    
    Returns:
        GradeThreshold object with grade information
    """
    thresholds = thresholds or DEFAULT_GRADE_THRESHOLDS
    
    for threshold in thresholds:
        if score >= threshold.min_score:
            return threshold
    
    return thresholds[-1]  # Return lowest grade


def calculate_weighted_score(
    scores: Dict[str, float],
    weights: Optional[ScoringWeights] = None
) -> float:
    """
    Calculate weighted overall score from individual scores.
    
    Args:
        scores: Dictionary with keys: relevance, grammar, fluency, keywords
        weights: Optional custom weights (uses BALANCED if not provided)
    
    Returns:
        Weighted average score
    """
    weights = weights or WeightProfiles.BALANCED
    
    weighted_score = (
        scores.get('relevance', 0) * weights.relevance +
        scores.get('grammar', 0) * weights.grammar +
        scores.get('fluency', 0) * weights.fluency +
        scores.get('keywords', 0) * weights.keywords
    )
    
    return round(weighted_score, 2)


def get_all_transition_words() -> set:
    """Get all transition words as a flat set."""
    all_words = set()
    for category_words in TRANSITION_WORDS.values():
        all_words.update(category_words)
    return all_words


# ============================================================================
# CONFIGURATION PRESETS
# ============================================================================

class EvaluationPreset:
    """Preconfigured evaluation settings for different scenarios."""
    
    @staticmethod
    def technical_python_interview() -> Dict:
        """Settings for Python technical interview."""
        return {
            'weights': WeightProfiles.TECHNICAL,
            'keywords': get_all_keywords_for_domain('software_engineering'),
            'answer_length': ANSWER_LENGTH_CONFIG['medium']
        }
    
    @staticmethod
    def data_science_interview() -> Dict:
        """Settings for data science interview."""
        return {
            'weights': WeightProfiles.TECHNICAL,
            'keywords': get_all_keywords_for_domain('data_science'),
            'answer_length': ANSWER_LENGTH_CONFIG['long']
        }
    
    @staticmethod
    def behavioral_interview() -> Dict:
        """Settings for behavioral interview."""
        return {
            'weights': WeightProfiles.BEHAVIORAL,
            'keywords': get_all_keywords_for_domain('behavioral'),
            'answer_length': ANSWER_LENGTH_CONFIG['long']
        }
    
    @staticmethod
    def quick_screening() -> Dict:
        """Settings for quick screening questions."""
        return {
            'weights': WeightProfiles.BALANCED,
            'keywords': [],
            'answer_length': ANSWER_LENGTH_CONFIG['short']
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SCORING CONFIGURATION MODULE")
    print("=" * 60)
    
    # Show weight profiles
    print("\n📊 Available Weight Profiles:")
    print(f"   BALANCED:      {WeightProfiles.BALANCED.to_dict()}")
    print(f"   TECHNICAL:     {WeightProfiles.TECHNICAL.to_dict()}")
    print(f"   BEHAVIORAL:    {WeightProfiles.BEHAVIORAL.to_dict()}")
    print(f"   COMMUNICATION: {WeightProfiles.COMMUNICATION.to_dict()}")
    
    # Show available domains
    print(f"\n📚 Available Keyword Domains:")
    for domain in KEYWORD_DICTIONARIES.keys():
        topics = list(KEYWORD_DICTIONARIES[domain].keys())
        print(f"   {domain}: {len(topics)} topics")
    
    # Example keyword lookup
    print(f"\n🔑 Example - OOP Keywords:")
    oop_keywords = get_keywords_for_topic('software_engineering', 'oop_concepts')
    print(f"   {oop_keywords[:5]}...")
    
    # Example grade calculation
    print(f"\n📝 Example Grade Calculation:")
    test_score = 75.5
    grade = get_grade_for_score(test_score)
    print(f"   Score: {test_score} → Grade: {grade.grade} ({grade.label})")
