"""
==============================================================================
NLP-Based Answer Evaluation Module for Mock Interview System
==============================================================================

This module evaluates interview answers using Natural Language Processing
techniques to assess:
    1. Relevance - How well the answer addresses the question
    2. Grammar - Correctness of sentence structure and grammar
    3. Fluency - Coherence and flow of the response
    4. Keywords - Presence of relevant technical terms

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import re
import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import Counter

# ============================================================================
# OPTIONAL: Import advanced NLP libraries if available
# ============================================================================
# These provide better results but the module works without them

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️ NLTK not installed. Using basic tokenization.")
    print("   Install with: pip install nltk")

try:
    import language_tool_python
    GRAMMAR_TOOL_AVAILABLE = True
except ImportError:
    GRAMMAR_TOOL_AVAILABLE = False
    print("⚠️ language_tool_python not installed. Using basic grammar check.")
    print("   Install with: pip install language-tool-python")

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ sentence-transformers not installed. Using keyword-based relevance.")
    print("   Install with: pip install sentence-transformers")


# ============================================================================
# DATA CLASSES FOR STRUCTURED RESULTS
# ============================================================================

@dataclass
class ScoreBreakdown:
    """Detailed breakdown of a single evaluation metric."""
    score: float           # Score from 0-100
    max_score: float       # Maximum possible score (100)
    weight: float          # Weight in final calculation
    feedback: str          # Human-readable feedback
    details: Dict          # Additional scoring details


@dataclass
class EvaluationResult:
    """Complete evaluation result for an interview answer."""
    question: str
    answer: str
    overall_score: float
    grade: str
    relevance: ScoreBreakdown
    grammar: ScoreBreakdown
    fluency: ScoreBreakdown
    keywords: ScoreBreakdown
    suggestions: List[str]
    strengths: List[str]
    

# ============================================================================
# MAIN EVALUATOR CLASS
# ============================================================================

class AnswerEvaluator:
    """
    NLP-based evaluator for interview answers.
    
    This class analyzes interview responses across multiple dimensions
    and provides detailed feedback with numeric scores.
    
    Usage:
        evaluator = AnswerEvaluator()
        result = evaluator.evaluate(question, answer, expected_keywords)
        print(result.to_json())
    """
    
    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        'relevance': 0.35,   # Most important - is the answer on-topic?
        'grammar': 0.20,     # Language correctness
        'fluency': 0.25,     # Coherence and readability
        'keywords': 0.20     # Technical term coverage
    }
    
    # Grade thresholds
    GRADE_THRESHOLDS = [
        (90, 'A+', 'Excellent'),
        (80, 'A', 'Very Good'),
        (70, 'B+', 'Good'),
        (60, 'B', 'Satisfactory'),
        (50, 'C', 'Needs Improvement'),
        (40, 'D', 'Poor'),
        (0, 'F', 'Unsatisfactory')
    ]
    
    def __init__(self, use_advanced_models: bool = True):
        """
        Initialize the evaluator.
        
        Args:
            use_advanced_models: If True, use transformer models for better
                                 relevance scoring (requires more memory)
        """
        self.use_advanced_models = use_advanced_models
        self._initialize_nlp_tools()
    
    def _initialize_nlp_tools(self):
        """Initialize NLP tools and models."""
        # Initialize NLTK resources
        if NLTK_AVAILABLE:
            try:
                self.stopwords = set(stopwords.words('english'))
                self.lemmatizer = WordNetLemmatizer()
            except LookupError:
                # Download required NLTK data
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                self.stopwords = set(stopwords.words('english'))
                self.lemmatizer = WordNetLemmatizer()
        else:
            # Basic English stopwords fallback
            self.stopwords = {
                'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                'through', 'during', 'before', 'after', 'above', 'below',
                'between', 'under', 'again', 'further', 'then', 'once',
                'here', 'there', 'when', 'where', 'why', 'how', 'all',
                'each', 'few', 'more', 'most', 'other', 'some', 'such',
                'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
                'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because',
                'until', 'while', 'this', 'that', 'these', 'those', 'i',
                'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves', 'he',
                'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                'it', 'its', 'itself', 'they', 'them', 'their', 'theirs'
            }
            self.lemmatizer = None
        
        # Initialize grammar checker
        if GRAMMAR_TOOL_AVAILABLE:
            try:
                self.grammar_tool = language_tool_python.LanguageTool('en-US')
            except Exception as e:
                print(f"⚠️ Grammar tool initialization failed: {e}")
                self.grammar_tool = None
        else:
            self.grammar_tool = None
        
        # Initialize sentence transformer for semantic similarity
        if SENTENCE_TRANSFORMERS_AVAILABLE and self.use_advanced_models:
            try:
                # Use a lightweight but effective model
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"⚠️ Sentence transformer failed to load: {e}")
                self.sentence_model = None
        else:
            self.sentence_model = None
    
    # ========================================================================
    # MAIN EVALUATION METHOD
    # ========================================================================
    
    def evaluate(
        self,
        question: str,
        answer: str,
        expected_keywords: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> EvaluationResult:
        """
        Evaluate an interview answer against multiple criteria.
        
        Args:
            question: The interview question text
            answer: The candidate's answer text
            expected_keywords: List of technical terms expected in the answer
            context: Additional context (job role, topic, etc.)
        
        Returns:
            EvaluationResult with scores, feedback, and suggestions
        """
        # Validate inputs
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        if not answer or not answer.strip():
            raise ValueError("Answer cannot be empty")
        
        # Clean and normalize text
        question = self._clean_text(question)
        answer = self._clean_text(answer)
        
        # Extract keywords from question if not provided
        if expected_keywords is None:
            expected_keywords = self._extract_keywords_from_question(question)
        
        # ====================================================================
        # SCORE EACH DIMENSION
        # ====================================================================
        
        relevance_score = self._evaluate_relevance(question, answer, context)
        grammar_score = self._evaluate_grammar(answer)
        fluency_score = self._evaluate_fluency(answer)
        keywords_score = self._evaluate_keywords(answer, expected_keywords)
        
        # ====================================================================
        # CALCULATE OVERALL SCORE
        # ====================================================================
        
        overall_score = (
            relevance_score.score * self.WEIGHTS['relevance'] +
            grammar_score.score * self.WEIGHTS['grammar'] +
            fluency_score.score * self.WEIGHTS['fluency'] +
            keywords_score.score * self.WEIGHTS['keywords']
        )
        
        # Determine grade
        grade = self._get_grade(overall_score)
        
        # Generate suggestions and identify strengths
        suggestions = self._generate_suggestions(
            relevance_score, grammar_score, fluency_score, keywords_score
        )
        strengths = self._identify_strengths(
            relevance_score, grammar_score, fluency_score, keywords_score
        )
        
        return EvaluationResult(
            question=question,
            answer=answer,
            overall_score=round(overall_score, 2),
            grade=grade,
            relevance=relevance_score,
            grammar=grammar_score,
            fluency=fluency_score,
            keywords=keywords_score,
            suggestions=suggestions,
            strengths=strengths
        )
    
    # ========================================================================
    # RELEVANCE EVALUATION
    # ========================================================================
    
    def _evaluate_relevance(
        self,
        question: str,
        answer: str,
        context: Optional[str] = None
    ) -> ScoreBreakdown:
        """
        Evaluate how relevant the answer is to the question.
        
        Uses semantic similarity if transformers available,
        otherwise falls back to keyword overlap.
        
        Scoring Logic:
            - Semantic similarity score (0-100) if transformers available
            - Keyword overlap ratio * 100 otherwise
            - Bonus for answering the specific question type (what/how/why)
        """
        details = {}
        
        if self.sentence_model is not None:
            # =================================================================
            # ADVANCED: Semantic Similarity using Sentence Transformers
            # =================================================================
            # Encode question and answer into dense vectors
            question_embedding = self.sentence_model.encode(question, convert_to_tensor=True)
            answer_embedding = self.sentence_model.encode(answer, convert_to_tensor=True)
            
            # Calculate cosine similarity
            similarity = util.cos_sim(question_embedding, answer_embedding).item()
            
            # Convert to 0-100 scale (similarity is between -1 and 1)
            base_score = max(0, (similarity + 1) / 2 * 100)
            
            details['method'] = 'semantic_similarity'
            details['cosine_similarity'] = round(similarity, 4)
        else:
            # =================================================================
            # FALLBACK: Keyword Overlap Method
            # =================================================================
            question_tokens = self._tokenize_and_clean(question)
            answer_tokens = self._tokenize_and_clean(answer)
            
            # Calculate Jaccard similarity
            if len(question_tokens) == 0:
                base_score = 50  # Default if question has no content words
            else:
                overlap = len(question_tokens & answer_tokens)
                union = len(question_tokens | answer_tokens)
                jaccard = overlap / union if union > 0 else 0
                base_score = jaccard * 100
            
            details['method'] = 'keyword_overlap'
            details['overlap_count'] = len(question_tokens & answer_tokens)
        
        # =================================================================
        # BONUS: Check if answer addresses question type
        # =================================================================
        question_type = self._detect_question_type(question)
        answer_addresses_type = self._answer_matches_question_type(answer, question_type)
        
        type_bonus = 10 if answer_addresses_type else 0
        
        # Calculate final score (cap at 100)
        final_score = min(100, base_score + type_bonus)
        
        details['question_type'] = question_type
        details['addresses_question_type'] = answer_addresses_type
        
        # Generate feedback
        if final_score >= 80:
            feedback = "Excellent! Your answer directly addresses the question."
        elif final_score >= 60:
            feedback = "Good relevance. Consider focusing more on the specific question asked."
        elif final_score >= 40:
            feedback = "Partial relevance. Some points don't directly answer the question."
        else:
            feedback = "Low relevance. Please re-read the question and address it directly."
        
        return ScoreBreakdown(
            score=round(final_score, 2),
            max_score=100,
            weight=self.WEIGHTS['relevance'],
            feedback=feedback,
            details=details
        )
    
    # ========================================================================
    # GRAMMAR EVALUATION
    # ========================================================================
    
    def _evaluate_grammar(self, answer: str) -> ScoreBreakdown:
        """
        Evaluate grammar and sentence structure.
        
        Uses LanguageTool if available, otherwise uses rule-based checks.
        
        Scoring Logic:
            - Start with 100 points
            - Deduct points for each error based on severity
            - Minimum score is 0
        """
        details = {'errors': []}
        
        if self.grammar_tool is not None:
            # =================================================================
            # ADVANCED: Use LanguageTool for comprehensive grammar check
            # =================================================================
            matches = self.grammar_tool.check(answer)
            
            # Calculate deductions based on error severity
            deductions = 0
            error_list = []
            
            for match in matches:
                # Categorize error severity
                if match.ruleId.startswith('MORFOLOGIK'):
                    severity = 'spelling'
                    deduction = 2
                elif 'COMMA' in match.ruleId or 'WHITESPACE' in match.ruleId:
                    severity = 'punctuation'
                    deduction = 1
                elif 'AGREEMENT' in match.ruleId:
                    severity = 'agreement'
                    deduction = 3
                else:
                    severity = 'grammar'
                    deduction = 2
                
                deductions += deduction
                error_list.append({
                    'message': match.message,
                    'context': match.context,
                    'severity': severity,
                    'suggestion': match.replacements[:3] if match.replacements else []
                })
            
            details['errors'] = error_list[:10]  # Limit to 10 errors
            details['total_errors'] = len(matches)
            details['method'] = 'language_tool'
            
        else:
            # =================================================================
            # FALLBACK: Rule-based grammar checking
            # =================================================================
            errors = self._basic_grammar_check(answer)
            deductions = len(errors) * 3  # 3 points per error
            
            details['errors'] = errors[:10]
            details['total_errors'] = len(errors)
            details['method'] = 'rule_based'
        
        # Calculate score (minimum 0)
        final_score = max(0, 100 - deductions)
        
        # Generate feedback
        error_count = details['total_errors']
        if error_count == 0:
            feedback = "Excellent grammar! No errors detected."
        elif error_count <= 2:
            feedback = "Good grammar with minor issues. Review the highlighted errors."
        elif error_count <= 5:
            feedback = "Several grammar issues found. Consider proofreading your answer."
        else:
            feedback = "Multiple grammar errors detected. Focus on sentence structure and spelling."
        
        return ScoreBreakdown(
            score=round(final_score, 2),
            max_score=100,
            weight=self.WEIGHTS['grammar'],
            feedback=feedback,
            details=details
        )
    
    def _basic_grammar_check(self, text: str) -> List[Dict]:
        """
        Basic rule-based grammar checking (fallback method).
        
        Checks for common errors:
            - Double spaces
            - Missing capitalization
            - Common spelling mistakes
            - Subject-verb agreement patterns
        """
        errors = []
        
        # Check for double spaces
        if '  ' in text:
            errors.append({
                'message': 'Double spaces detected',
                'severity': 'punctuation'
            })
        
        # Check sentence capitalization
        sentences = self._split_sentences(text)
        for i, sent in enumerate(sentences):
            if sent and sent[0].islower():
                errors.append({
                    'message': f'Sentence {i+1} should start with a capital letter',
                    'severity': 'capitalization'
                })
        
        # Check for common errors
        common_errors = {
            r'\bi am\b': 'Consider using "I am" (capitalize I)',
            r'\bits\s+a\s+': 'Check usage of "its" vs "it\'s"',
            r'\byour\s+welcome\b': 'Should be "you\'re welcome"',
            r'\btheir\s+is\b': 'Should be "there is"',
            r'\bcould\s+of\b': 'Should be "could have"',
            r'\bshould\s+of\b': 'Should be "should have"',
        }
        
        text_lower = text.lower()
        for pattern, message in common_errors.items():
            if re.search(pattern, text_lower):
                errors.append({
                    'message': message,
                    'severity': 'grammar'
                })
        
        return errors
    
    # ========================================================================
    # FLUENCY EVALUATION
    # ========================================================================
    
    def _evaluate_fluency(self, answer: str) -> ScoreBreakdown:
        """
        Evaluate fluency, coherence, and readability.
        
        Scoring Components:
            1. Sentence length variety (not too uniform)
            2. Readability score (Flesch-Kincaid)
            3. Coherence markers (transition words)
            4. Answer completeness (not too short/long)
        """
        details = {}
        
        sentences = self._split_sentences(answer)
        words = self._tokenize_simple(answer)
        
        num_sentences = len(sentences)
        num_words = len(words)
        
        # =================================================================
        # 1. SENTENCE LENGTH ANALYSIS (25 points max)
        # =================================================================
        if num_sentences > 0:
            sentence_lengths = [len(self._tokenize_simple(s)) for s in sentences]
            avg_sentence_length = sum(sentence_lengths) / num_sentences
            
            # Ideal sentence length is 15-20 words
            if 10 <= avg_sentence_length <= 25:
                length_score = 25
            elif 5 <= avg_sentence_length < 10 or 25 < avg_sentence_length <= 35:
                length_score = 15
            else:
                length_score = 5
            
            # Bonus for variety
            if num_sentences >= 3:
                length_variance = max(sentence_lengths) - min(sentence_lengths)
                if length_variance >= 5:  # Good variety
                    length_score = min(25, length_score + 5)
        else:
            length_score = 0
            avg_sentence_length = 0
        
        details['avg_sentence_length'] = round(avg_sentence_length, 2)
        details['sentence_count'] = num_sentences
        
        # =================================================================
        # 2. READABILITY SCORE (25 points max)
        # =================================================================
        # Simplified Flesch Reading Ease approximation
        if num_sentences > 0 and num_words > 0:
            syllables = sum(self._count_syllables(w) for w in words)
            
            # Flesch Reading Ease formula
            flesch = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (syllables / num_words)
            flesch = max(0, min(100, flesch))  # Clamp to 0-100
            
            # Convert to our scale (we want 60-70 Flesch = ideal for professional)
            if 50 <= flesch <= 80:
                readability_score = 25
            elif 30 <= flesch < 50 or 80 < flesch <= 90:
                readability_score = 15
            else:
                readability_score = 10
        else:
            flesch = 0
            readability_score = 0
        
        details['flesch_reading_ease'] = round(flesch, 2)
        
        # =================================================================
        # 3. COHERENCE MARKERS (25 points max)
        # =================================================================
        transition_words = {
            'however', 'therefore', 'furthermore', 'moreover', 'additionally',
            'consequently', 'meanwhile', 'nevertheless', 'nonetheless',
            'for example', 'for instance', 'in addition', 'on the other hand',
            'in conclusion', 'to summarize', 'first', 'second', 'third',
            'finally', 'next', 'then', 'also', 'besides', 'thus', 'hence',
            'similarly', 'likewise', 'in contrast', 'although', 'even though',
            'because', 'since', 'as a result', 'specifically', 'particularly'
        }
        
        answer_lower = answer.lower()
        transitions_found = [t for t in transition_words if t in answer_lower]
        
        if len(transitions_found) >= 3:
            coherence_score = 25
        elif len(transitions_found) >= 1:
            coherence_score = 15
        else:
            coherence_score = 5
        
        details['transition_words_found'] = transitions_found
        
        # =================================================================
        # 4. ANSWER COMPLETENESS (25 points max)
        # =================================================================
        # Ideal answer length: 50-300 words for interview responses
        if 50 <= num_words <= 300:
            completeness_score = 25
        elif 30 <= num_words < 50 or 300 < num_words <= 500:
            completeness_score = 15
        elif 15 <= num_words < 30:
            completeness_score = 10
        else:
            completeness_score = 5
        
        details['word_count'] = num_words
        
        # =================================================================
        # FINAL SCORE
        # =================================================================
        final_score = length_score + readability_score + coherence_score + completeness_score
        
        # Generate feedback
        if final_score >= 80:
            feedback = "Excellent fluency! Your answer is well-structured and easy to follow."
        elif final_score >= 60:
            feedback = "Good fluency. Consider adding transition words for better flow."
        elif final_score >= 40:
            feedback = "Fair fluency. Try varying sentence length and using connecting phrases."
        else:
            feedback = "Needs improvement. Focus on complete sentences and logical flow."
        
        return ScoreBreakdown(
            score=round(final_score, 2),
            max_score=100,
            weight=self.WEIGHTS['fluency'],
            feedback=feedback,
            details=details
        )
    
    # ========================================================================
    # KEYWORD EVALUATION
    # ========================================================================
    
    def _evaluate_keywords(
        self,
        answer: str,
        expected_keywords: List[str]
    ) -> ScoreBreakdown:
        """
        Evaluate presence of expected technical keywords.
        
        Scoring Logic:
            - Calculate percentage of expected keywords found
            - Bonus for using keywords in proper context
        """
        if not expected_keywords:
            return ScoreBreakdown(
                score=75,  # Default score if no keywords specified
                max_score=100,
                weight=self.WEIGHTS['keywords'],
                feedback="No specific keywords were expected for this question.",
                details={'expected': [], 'found': [], 'missing': []}
            )
        
        answer_lower = answer.lower()
        
        # Check for each keyword (including partial matches)
        found_keywords = []
        missing_keywords = []
        
        for keyword in expected_keywords:
            keyword_lower = keyword.lower()
            
            # Check for exact or partial match
            if keyword_lower in answer_lower:
                found_keywords.append(keyword)
            elif self.lemmatizer and NLTK_AVAILABLE:
                # Try lemmatized version
                lemma = self.lemmatizer.lemmatize(keyword_lower)
                if lemma in answer_lower:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate score
        if len(expected_keywords) > 0:
            coverage = len(found_keywords) / len(expected_keywords)
            final_score = coverage * 100
        else:
            final_score = 100
        
        # Generate feedback
        if final_score >= 80:
            feedback = "Excellent! You've covered most key technical terms."
        elif final_score >= 60:
            feedback = f"Good keyword usage. Consider mentioning: {', '.join(missing_keywords[:3])}"
        elif final_score >= 40:
            feedback = f"Some key terms missing. Include: {', '.join(missing_keywords[:5])}"
        else:
            feedback = f"Most expected keywords missing. Review: {', '.join(missing_keywords)}"
        
        return ScoreBreakdown(
            score=round(final_score, 2),
            max_score=100,
            weight=self.WEIGHTS['keywords'],
            feedback=feedback,
            details={
                'expected': expected_keywords,
                'found': found_keywords,
                'missing': missing_keywords,
                'coverage_percentage': round(final_score, 2)
            }
        )
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def _tokenize_simple(self, text: str) -> List[str]:
        """Simple word tokenization."""
        # Remove punctuation and split on whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.lower().split()
    
    def _tokenize_and_clean(self, text: str) -> set:
        """Tokenize and remove stopwords, returning a set."""
        if NLTK_AVAILABLE:
            tokens = word_tokenize(text.lower())
        else:
            tokens = self._tokenize_simple(text)
        
        # Remove stopwords and short words
        clean_tokens = {
            t for t in tokens 
            if t not in self.stopwords and len(t) > 2 and t.isalpha()
        }
        return clean_tokens
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        if NLTK_AVAILABLE:
            return sent_tokenize(text)
        else:
            # Basic sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (approximation)."""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        
        if len(word) == 0:
            return 0
        
        if word[0] in vowels:
            count += 1
        
        for i in range(1, len(word)):
            if word[i] in vowels and word[i-1] not in vowels:
                count += 1
        
        # Adjust for silent 'e'
        if word.endswith('e') and count > 1:
            count -= 1
        
        return max(1, count)
    
    def _detect_question_type(self, question: str) -> str:
        """Detect the type of question (what, how, why, etc.)."""
        question_lower = question.lower().strip()
        
        if question_lower.startswith('what'):
            return 'what'
        elif question_lower.startswith('how'):
            return 'how'
        elif question_lower.startswith('why'):
            return 'why'
        elif question_lower.startswith('when'):
            return 'when'
        elif question_lower.startswith('where'):
            return 'where'
        elif question_lower.startswith('who'):
            return 'who'
        elif question_lower.startswith(('can you', 'could you', 'would you')):
            return 'request'
        elif question_lower.startswith(('is ', 'are ', 'do ', 'does ', 'did ')):
            return 'yes_no'
        elif question_lower.startswith('describe'):
            return 'describe'
        elif question_lower.startswith('explain'):
            return 'explain'
        else:
            return 'general'
    
    def _answer_matches_question_type(self, answer: str, question_type: str) -> bool:
        """Check if answer structure matches question type."""
        answer_lower = answer.lower()
        
        type_indicators = {
            'what': ['is', 'are', 'means', 'refers to', 'defined as'],
            'how': ['by', 'through', 'using', 'first', 'then', 'steps', 'process'],
            'why': ['because', 'since', 'reason', 'due to', 'as a result', 'therefore'],
            'when': ['when', 'during', 'after', 'before', 'while', 'time'],
            'describe': ['is', 'has', 'contains', 'includes', 'features'],
            'explain': ['means', 'works', 'because', 'therefore', 'process'],
            'yes_no': ['yes', 'no', 'definitely', 'absolutely', 'not really'],
        }
        
        if question_type in type_indicators:
            indicators = type_indicators[question_type]
            return any(ind in answer_lower for ind in indicators)
        
        return True  # Default to true for general questions
    
    def _extract_keywords_from_question(self, question: str) -> List[str]:
        """Extract potential keywords from the question."""
        tokens = self._tokenize_and_clean(question)
        
        # Filter out common question words
        question_words = {'what', 'how', 'why', 'when', 'where', 'who', 
                          'explain', 'describe', 'tell', 'give', 'example'}
        
        keywords = [t for t in tokens if t not in question_words]
        return list(keywords)[:10]  # Limit to 10 keywords
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        for threshold, grade, _ in self.GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return 'F'
    
    def _generate_suggestions(
        self,
        relevance: ScoreBreakdown,
        grammar: ScoreBreakdown,
        fluency: ScoreBreakdown,
        keywords: ScoreBreakdown
    ) -> List[str]:
        """Generate improvement suggestions based on scores."""
        suggestions = []
        
        # Relevance suggestions
        if relevance.score < 70:
            suggestions.append("Read the question carefully and ensure your answer directly addresses it.")
        
        # Grammar suggestions
        if grammar.score < 70:
            error_count = grammar.details.get('total_errors', 0)
            suggestions.append(f"Review grammar and spelling - {error_count} issues found.")
        
        # Fluency suggestions
        if fluency.score < 70:
            if fluency.details.get('word_count', 0) < 50:
                suggestions.append("Provide a more detailed response with examples.")
            if len(fluency.details.get('transition_words_found', [])) < 2:
                suggestions.append("Use transition words (however, therefore, for example) to improve flow.")
        
        # Keyword suggestions
        if keywords.score < 70:
            missing = keywords.details.get('missing', [])[:3]
            if missing:
                suggestions.append(f"Include key terms: {', '.join(missing)}")
        
        # If no specific suggestions, provide general encouragement
        if not suggestions:
            suggestions.append("Great job! Keep practicing to maintain this level.")
        
        return suggestions
    
    def _identify_strengths(
        self,
        relevance: ScoreBreakdown,
        grammar: ScoreBreakdown,
        fluency: ScoreBreakdown,
        keywords: ScoreBreakdown
    ) -> List[str]:
        """Identify strong points in the answer."""
        strengths = []
        
        if relevance.score >= 80:
            strengths.append("Excellent question relevance")
        if grammar.score >= 80:
            strengths.append("Strong grammar and spelling")
        if fluency.score >= 80:
            strengths.append("Well-structured and coherent response")
        if keywords.score >= 80:
            strengths.append("Good use of technical terminology")
        
        return strengths
    
    # ========================================================================
    # OUTPUT METHODS
    # ========================================================================
    
    def to_json(self, result: EvaluationResult) -> str:
        """Convert evaluation result to JSON string."""
        
        def serialize(obj):
            if isinstance(obj, ScoreBreakdown):
                return asdict(obj)
            return obj
        
        result_dict = {
            'question': result.question,
            'answer': result.answer,
            'overall_score': result.overall_score,
            'grade': result.grade,
            'scores': {
                'relevance': serialize(result.relevance),
                'grammar': serialize(result.grammar),
                'fluency': serialize(result.fluency),
                'keywords': serialize(result.keywords)
            },
            'suggestions': result.suggestions,
            'strengths': result.strengths
        }
        
        return json.dumps(result_dict, indent=2)


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def evaluate_answer(
    question: str,
    answer: str,
    expected_keywords: Optional[List[str]] = None
) -> str:
    """
    Convenience function to evaluate an answer and return JSON.
    
    Args:
        question: The interview question
        answer: The candidate's answer
        expected_keywords: Optional list of expected technical terms
    
    Returns:
        JSON string with evaluation results
    """
    evaluator = AnswerEvaluator()
    result = evaluator.evaluate(question, answer, expected_keywords)
    return evaluator.to_json(result)


# ============================================================================
# MAIN - EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example usage
    question = "What is Object-Oriented Programming and explain its main principles?"
    
    answer = """Object-Oriented Programming, or OOP, is a programming paradigm that 
    organizes code around objects rather than functions. The main principles are 
    encapsulation, inheritance, polymorphism, and abstraction. Encapsulation means 
    bundling data and methods together. Inheritance allows classes to inherit 
    properties from parent classes. Polymorphism enables objects to take multiple 
    forms. Abstraction hides complex implementation details."""
    
    expected_keywords = [
        'encapsulation', 'inheritance', 'polymorphism', 'abstraction',
        'objects', 'classes', 'paradigm'
    ]
    
    # Evaluate
    evaluator = AnswerEvaluator()
    result = evaluator.evaluate(question, answer, expected_keywords)
    
    # Print results
    print("\n" + "=" * 70)
    print("NLP ANSWER EVALUATION RESULTS")
    print("=" * 70)
    
    print(f"\n📝 Question: {result.question[:80]}...")
    print(f"📄 Answer: {result.answer[:80]}...")
    
    print(f"\n{'=' * 70}")
    print(f"OVERALL SCORE: {result.overall_score}/100 (Grade: {result.grade})")
    print(f"{'=' * 70}")
    
    print(f"\n📊 DETAILED SCORES:")
    print(f"   Relevance: {result.relevance.score}/100 (weight: {result.relevance.weight})")
    print(f"   Grammar:   {result.grammar.score}/100 (weight: {result.grammar.weight})")
    print(f"   Fluency:   {result.fluency.score}/100 (weight: {result.fluency.weight})")
    print(f"   Keywords:  {result.keywords.score}/100 (weight: {result.keywords.weight})")
    
    print(f"\n💪 STRENGTHS:")
    for s in result.strengths:
        print(f"   ✓ {s}")
    
    print(f"\n💡 SUGGESTIONS:")
    for s in result.suggestions:
        print(f"   → {s}")
    
    print(f"\n📋 JSON OUTPUT:")
    print(evaluator.to_json(result))
