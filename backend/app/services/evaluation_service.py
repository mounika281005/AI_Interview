"""
==============================================================================
AI Mock Interview System - NLP Evaluation Service
==============================================================================

Evaluates candidate responses using NLP techniques for relevance,
grammar, fluency, and keyword coverage.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


def debug_log(msg: str, data: Any = None):
    """Helper for consistent debug logging."""
    if data is not None:
        logger.debug(f"{msg}: {data}")
    else:
        logger.debug(msg)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class EvaluationScore:
    """Individual evaluation metric score."""
    score: float  # 0.0 to 100.0
    details: str
    suggestions: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Complete evaluation result for a response."""
    relevance: EvaluationScore
    grammar: EvaluationScore
    fluency: EvaluationScore
    keyword_usage: EvaluationScore
    overall_score: float
    summary: str
    strengths: List[str]
    improvements: List[str]


# =============================================================================
# NLP EVALUATION SERVICE
# =============================================================================

class NLPEvaluationService:
    """
    Service for evaluating interview responses using NLP.
    
    Metrics evaluated:
    - Relevance: How well the response addresses the question
    - Grammar: Grammatical correctness
    - Fluency: Natural language flow and coherence
    - Keyword Usage: Coverage of expected topics/keywords
    
    Usage:
        evaluator = NLPEvaluationService()
        result = await evaluator.evaluate(
            question="Tell me about a challenging project",
            response="I worked on a microservices migration...",
            expected_keywords=["challenge", "solution", "outcome"]
        )
        print(f"Overall: {result.overall_score}")
    """
    
    def __init__(self):
        """Initialize the NLP evaluation service."""
        self.sentence_model = None
        self.grammar_tool = None
        self._initialize()
    
    def _initialize(self):
        """Initialize NLP models and tools."""
        # Initialize sentence transformer for semantic similarity
        try:
            from sentence_transformers import SentenceTransformer
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not installed")
        except Exception as e:
            logger.warning(f"Failed to load sentence transformer: {e}")
        
        # Initialize grammar checker
        try:
            import language_tool_python
            try:
                # Preferred: local LanguageTool server (best quality / privacy).
                self.grammar_tool = language_tool_python.LanguageTool('en-US')
                logger.info("Grammar tool loaded successfully (local)")
            except Exception as local_err:
                # Fallback: public API if local download/server bootstrap fails.
                logger.warning(f"Local grammar tool init failed: {local_err}")
                self.grammar_tool = language_tool_python.LanguageToolPublicAPI('en-US')
                logger.info("Grammar tool loaded successfully (public API fallback)")
        except ImportError:
            logger.warning("language-tool-python not installed")
        except Exception as e:
            logger.warning(f"Failed to load grammar tool: {e}")
        
        # Initialize NLTK
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('stopwords', quiet=True)
            logger.info("NLTK resources loaded successfully")
        except ImportError:
            logger.warning("NLTK not installed")
        except Exception as e:
            logger.warning(f"Failed to load NLTK: {e}")
    
    async def evaluate(
        self,
        question: str,
        response: str,
        expected_keywords: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> EvaluationResult:
        """
        Evaluate a candidate's response.
        
        Args:
            question: The interview question
            response: Candidate's transcribed response
            expected_keywords: Keywords expected in a good response
            context: Additional context (role, skills, etc.)
        
        Returns:
            EvaluationResult with detailed scores
        """
        debug_log("=== EVALUATE RESPONSE ===")
        debug_log("Question", question[:100] + "..." if len(question) > 100 else question)
        debug_log("Response length", len(response) if response else 0)
        debug_log("Expected keywords", expected_keywords)
        
        if not response or not response.strip():
            debug_log("ERROR: Empty response")
            return self._create_empty_result("No response provided")
        
        # Run all evaluations
        loop = asyncio.get_event_loop()
        
        # Evaluate each metric
        relevance = await loop.run_in_executor(
            None, self._evaluate_relevance, question, response, context
        )
        grammar = await loop.run_in_executor(
            None, self._evaluate_grammar, response
        )
        fluency = await loop.run_in_executor(
            None, self._evaluate_fluency, response
        )
        keyword_usage = await loop.run_in_executor(
            None, self._evaluate_keywords, response, expected_keywords or []
        )
        
        # Calculate overall score (weighted average)
        overall_score = (
            relevance.score * 0.35 +
            grammar.score * 0.20 +
            fluency.score * 0.25 +
            keyword_usage.score * 0.20
        )
        
        # Generate summary and feedback
        strengths, improvements = self._analyze_performance(
            relevance, grammar, fluency, keyword_usage
        )
        
        summary = self._generate_summary(overall_score, strengths, improvements)
        
        return EvaluationResult(
            relevance=relevance,
            grammar=grammar,
            fluency=fluency,
            keyword_usage=keyword_usage,
            overall_score=round(overall_score, 1),
            summary=summary,
            strengths=strengths,
            improvements=improvements
        )
    
    def _evaluate_relevance(
        self,
        question: str,
        response: str,
        context: Optional[str]
    ) -> EvaluationScore:
        """Evaluate response relevance to the question."""
        
        if self.sentence_model:
            try:
                # Semantic similarity using sentence embeddings
                question_embedding = self.sentence_model.encode([question])
                response_embedding = self.sentence_model.encode([response])
                
                from sklearn.metrics.pairwise import cosine_similarity
                similarity = cosine_similarity(question_embedding, response_embedding)[0][0]
                
                # Scale similarity to score (0-100)
                # Similarity > 0.5 is considered relevant for Q&A
                score = min(100, max(0, similarity * 150))  # Scale up slightly
                
                details = self._get_relevance_details(score)
                suggestions = self._get_relevance_suggestions(score, question)
                
                return EvaluationScore(
                    score=round(score, 1),
                    details=details,
                    suggestions=suggestions
                )
            except Exception as e:
                logger.warning(f"Semantic similarity failed: {e}")
        
        # Fallback: keyword overlap
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        
        overlap = len(question_words & response_words)
        max_overlap = len(question_words)
        
        if max_overlap > 0:
            score = (overlap / max_overlap) * 100
        else:
            score = 50.0  # Default neutral score
        
        return EvaluationScore(
            score=round(score, 1),
            details=self._get_relevance_details(score),
            suggestions=self._get_relevance_suggestions(score, question)
        )
    
    def _get_relevance_details(self, score: float) -> str:
        """Get description for relevance score."""
        if score >= 80:
            return "Response directly addresses the question with relevant content"
        elif score >= 60:
            return "Response is mostly relevant but could be more focused"
        elif score >= 40:
            return "Response partially addresses the question"
        else:
            return "Response may not adequately address the question"
    
    def _get_relevance_suggestions(self, score: float, question: str) -> List[str]:
        """Get suggestions for improving relevance."""
        suggestions = []
        if score < 80:
            suggestions.append("Focus more directly on answering the specific question asked")
        if score < 60:
            suggestions.append("Use the STAR method (Situation, Task, Action, Result) for behavioral questions")
        if score < 40:
            suggestions.append("Re-read the question and ensure your response addresses its main points")
        return suggestions
    
    def _evaluate_grammar(self, response: str) -> EvaluationScore:
        """Evaluate grammatical correctness."""
        
        if self.grammar_tool:
            try:
                matches = self.grammar_tool.check(response)
                
                # Calculate error rate
                words = len(response.split())
                error_count = len(matches)
                
                if words > 0:
                    error_rate = error_count / words
                    # Score decreases with error rate
                    score = max(0, 100 - (error_rate * 500))  # 20% error rate = 0 score
                else:
                    score = 0
                
                # Categorize errors
                grammar_errors = [m for m in matches if 'GRAMMAR' in str(m.ruleId)]
                spelling_errors = [m for m in matches if 'SPELLING' in str(m.ruleId)]
                
                details = f"Found {len(grammar_errors)} grammar and {len(spelling_errors)} spelling issues"
                
                suggestions = []
                for match in matches[:3]:  # Top 3 issues
                    if match.replacements:
                        suggestions.append(
                            f"Consider: '{match.context}' â†’ '{match.replacements[0]}'"
                        )
                
                return EvaluationScore(
                    score=round(score, 1),
                    details=details,
                    suggestions=suggestions
                )
            except Exception as e:
                logger.warning(f"Grammar check failed: {e}")
        
        # Heuristic fallback (no grammar tool available).
        # Keeps grammar scores dynamic instead of fixed values.
        words = re.findall(r"[A-Za-z']+", response)
        word_count = len(words)
        if word_count == 0:
            return EvaluationScore(
                score=0.0,
                details="No valid text for grammar evaluation",
                suggestions=["Provide a clear response to evaluate grammar"]
            )

        sentences = [s.strip() for s in re.split(r"[.!?]+", response) if s.strip()]
        sentence_count = max(1, len(sentences))

        # Positive components
        length_component = min(20.0, word_count * 0.6)
        starts_upper = sum(1 for s in sentences if s[:1].isupper())
        capitalization_ratio = starts_upper / sentence_count
        capitalization_component = capitalization_ratio * 20.0
        punctuation_component = 15.0 if re.search(r"[.!?]$", response.strip()) else 5.0
        unique_ratio = len({w.lower() for w in words}) / word_count
        diversity_component = min(15.0, max(0.0, (unique_ratio - 0.3) * 50.0))

        # Penalties
        repeat_penalty = max(0.0, (1.0 - unique_ratio) * 18.0)
        short_sentence_penalty = 10.0 if word_count < 8 else 0.0
        runon_penalty = 8.0 if word_count / sentence_count > 35 else 0.0
        lower_start_penalty = (1.0 - capitalization_ratio) * 10.0

        score = (
            25.0
            + length_component
            + capitalization_component
            + punctuation_component
            + diversity_component
            - repeat_penalty
            - short_sentence_penalty
            - runon_penalty
            - lower_start_penalty
        )
        score = max(0.0, min(100.0, score))

        suggestions = []
        if capitalization_ratio < 0.7:
            suggestions.append("Start sentences with capital letters")
        if not re.search(r"[.!?]$", response.strip()):
            suggestions.append("End sentences with proper punctuation")
        if unique_ratio < 0.4:
            suggestions.append("Reduce repetition and use more varied wording")
        if word_count < 8:
            suggestions.append("Provide more complete sentences for better grammar quality")

        return EvaluationScore(
            score=round(score, 1),
            details=(
                "Heuristic grammar check "
                f"(words={word_count}, sentences={sentence_count}, "
                f"capitalization={capitalization_ratio:.2f}, diversity={unique_ratio:.2f})"
            ),
            suggestions=suggestions or ["Use clearer grammar and sentence structure for better clarity"]
        )
    
    def _evaluate_fluency(self, response: str) -> EvaluationScore:
        """Evaluate language fluency and coherence."""
        
        try:
            import nltk
            from nltk import sent_tokenize, word_tokenize
            
            sentences = sent_tokenize(response)
            words = word_tokenize(response)
            
            if not sentences or not words:
                return EvaluationScore(
                    score=0,
                    details="Response is too short to evaluate fluency",
                    suggestions=["Provide a more detailed response"]
                )
            
            # Metrics for fluency
            avg_sentence_length = len(words) / len(sentences)
            word_variety = len(set(words)) / len(words) if words else 0
            
            # Score based on metrics
            # Ideal sentence length: 15-25 words
            length_score = 100 - abs(avg_sentence_length - 20) * 3
            length_score = max(0, min(100, length_score))
            
            # Word variety (type-token ratio)
            variety_score = word_variety * 100
            
            # Response length bonus
            length_bonus = min(20, len(words) / 10)  # Bonus for substantial responses
            
            score = (length_score * 0.4 + variety_score * 0.4 + length_bonus) * 1.2
            score = max(0, min(100, score))
            
            details = f"Average sentence length: {avg_sentence_length:.1f} words, vocabulary variety: {word_variety:.2f}"
            
            suggestions = []
            if avg_sentence_length > 30:
                suggestions.append("Try breaking up longer sentences for clarity")
            if avg_sentence_length < 10:
                suggestions.append("Expand your sentences with more detail")
            if word_variety < 0.4:
                suggestions.append("Use more varied vocabulary")
            
            return EvaluationScore(
                score=round(score, 1),
                details=details,
                suggestions=suggestions
            )
        
        except Exception as e:
            logger.warning(f"Fluency check failed: {e}")
            # Conservative fallback based on response length
            words = response.split()
            word_count = len(words)
            if word_count < 5:
                score = 25.0
            elif word_count < 20:
                score = 40.0
            else:
                score = 50.0
            return EvaluationScore(
                score=score,
                details="Basic fluency check (install NLTK for detailed analysis)",
                suggestions=["Install NLTK for detailed fluency evaluation"]
            )
    
    def _evaluate_keywords(
        self,
        response: str,
        expected_keywords: List[str]
    ) -> EvaluationScore:
        """Evaluate coverage of expected keywords/topics."""
        
        if not expected_keywords:
            return EvaluationScore(
                score=50.0,
                details="No specific keywords defined for this question",
                suggestions=["Keywords not available for comparison"]
            )
        
        response_lower = response.lower()
        
        # Check for each keyword (with variations)
        found_keywords = []
        missing_keywords = []
        
        for keyword in expected_keywords:
            keyword_lower = keyword.lower()
            # Check for keyword or its stem
            if keyword_lower in response_lower or keyword_lower[:-1] in response_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate score
        coverage = len(found_keywords) / len(expected_keywords)
        score = coverage * 100
        
        details = f"Covered {len(found_keywords)}/{len(expected_keywords)} expected topics"
        
        suggestions = []
        if missing_keywords:
            suggestions.append(f"Consider discussing: {', '.join(missing_keywords[:3])}")
        
        return EvaluationScore(
            score=round(score, 1),
            details=details,
            suggestions=suggestions
        )
    
    def _analyze_performance(
        self,
        relevance: EvaluationScore,
        grammar: EvaluationScore,
        fluency: EvaluationScore,
        keywords: EvaluationScore
    ) -> tuple:
        """Analyze scores to identify strengths and areas for improvement."""
        
        scores = {
            "Relevance": relevance.score,
            "Grammar": grammar.score,
            "Fluency": fluency.score,
            "Topic Coverage": keywords.score
        }
        
        # Identify strengths (scores >= 70)
        strengths = [
            f"Strong {name.lower()}" 
            for name, score in scores.items() 
            if score >= 70
        ]
        
        # Identify improvements (scores < 60)
        improvements = [
            f"Improve {name.lower()}" 
            for name, score in scores.items() 
            if score < 60
        ]
        
        # Add specific suggestions
        all_suggestions = (
            relevance.suggestions + 
            grammar.suggestions + 
            fluency.suggestions + 
            keywords.suggestions
        )
        improvements.extend(all_suggestions[:3])  # Top 3 specific suggestions
        
        return strengths, improvements
    
    def _generate_summary(
        self,
        overall_score: float,
        strengths: List[str],
        improvements: List[str]
    ) -> str:
        """Generate an overall performance summary."""
        
        if overall_score >= 80:
            rating = "Excellent"
            message = "Your response was well-structured and comprehensive."
        elif overall_score >= 60:
            rating = "Good"
            message = "Your response addressed the question with room for improvement."
        elif overall_score >= 40:
            rating = "Fair"
            message = "Your response partially met expectations."
        else:
            rating = "Needs Improvement"
            message = "Your response could be improved significantly."
        
        summary = f"{rating} ({overall_score:.1f}/100): {message}"
        
        if strengths:
            summary += f" Strengths: {', '.join(strengths[:2])}."
        if improvements:
            summary += f" Focus on: {improvements[0]}."
        
        return summary
    
    def _create_empty_result(self, reason: str) -> EvaluationResult:
        """Create an empty result for invalid input."""
        empty_score = EvaluationScore(score=0, details=reason, suggestions=[])
        return EvaluationResult(
            relevance=empty_score,
            grammar=empty_score,
            fluency=empty_score,
            keyword_usage=empty_score,
            overall_score=0,
            summary=reason,
            strengths=[],
            improvements=["Provide a response to receive evaluation"]
        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_evaluation_service: Optional[NLPEvaluationService] = None


def get_evaluation_service() -> NLPEvaluationService:
    """Factory function to get evaluation service instance (singleton)."""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = NLPEvaluationService()
    return _evaluation_service

