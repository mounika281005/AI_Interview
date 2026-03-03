"""
Tests for NLP Evaluator Service

Tests cover:
- Answer evaluation scoring
- Relevance calculation
- Grammar checking
- Feedback generation
"""

import pytest
from unittest.mock import patch, MagicMock


class TestAnswerEvaluation:
    """Tests for the NLP answer evaluator."""
    
    def test_evaluate_relevant_answer(self):
        """Test evaluation of a relevant answer."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        question = "Tell me about your experience with Python programming."
        answer = "I have 5 years of experience with Python. I've used it for web development with Django and FastAPI, data analysis with pandas, and automation scripts. I'm comfortable with both object-oriented and functional programming paradigms in Python."
        expected_topics = ["Python", "experience", "projects"]
        
        result = evaluator.evaluate(question, answer, expected_topics)
        
        assert "relevance_score" in result
        assert "completeness_score" in result
        assert "grammar_score" in result
        assert result["relevance_score"] >= 0.5  # Should be relevant
        assert result["completeness_score"] >= 0.5  # Covers expected topics
    
    def test_evaluate_irrelevant_answer(self):
        """Test evaluation of an irrelevant answer."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        question = "What are your salary expectations?"
        answer = "I really enjoy hiking and outdoor activities. Last weekend I went camping with friends."
        expected_topics = ["salary", "compensation", "expectations"]
        
        result = evaluator.evaluate(question, answer, expected_topics)
        
        assert result["relevance_score"] < 0.5  # Should be irrelevant
    
    def test_evaluate_empty_answer(self):
        """Test evaluation of an empty answer."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        question = "Describe a challenging project you worked on."
        answer = ""
        expected_topics = ["project", "challenge", "solution"]
        
        result = evaluator.evaluate(question, answer, expected_topics)
        
        assert result["completeness_score"] == 0
    
    def test_evaluate_with_grammar_errors(self):
        """Test evaluation detects grammar issues."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        question = "Describe your leadership experience."
        answer = "I has led many team before. We was working on big project and I makes sure everyone do their job good. The project it was successful."
        expected_topics = ["leadership", "team", "experience"]
        
        result = evaluator.evaluate(question, answer, expected_topics)
        
        assert "grammar_score" in result
        # Grammar score should be lower due to errors
        assert result["grammar_score"] < 0.9
    
    def test_evaluate_confidence_detection(self):
        """Test confidence level detection in answers."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        # Confident answer
        confident_answer = "I am confident in my ability to deliver results. I have successfully completed similar projects before."
        
        # Uncertain answer
        uncertain_answer = "Um, I think I might be able to do this, maybe. I'm not sure, but perhaps I could try."
        
        question = "Can you handle this responsibility?"
        expected_topics = ["responsibility", "capability"]
        
        confident_result = evaluator.evaluate(question, confident_answer, expected_topics)
        uncertain_result = evaluator.evaluate(question, uncertain_answer, expected_topics)
        
        assert confident_result.get("confidence_score", 0.5) >= uncertain_result.get("confidence_score", 0.5)
    
    def test_evaluate_topic_coverage(self):
        """Test topic coverage calculation."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        question = "Describe your experience with React, Node.js, and databases."
        full_coverage = "I have extensive experience with React for frontend development, Node.js for backend APIs, and I've worked with both SQL databases like PostgreSQL and NoSQL databases like MongoDB."
        partial_coverage = "I know React pretty well."
        
        expected_topics = ["React", "Node.js", "database"]
        
        full_result = evaluator.evaluate(question, full_coverage, expected_topics)
        partial_result = evaluator.evaluate(question, partial_coverage, expected_topics)
        
        assert full_result["completeness_score"] > partial_result["completeness_score"]


class TestFeedbackGeneration:
    """Tests for feedback message generation."""
    
    def test_generate_strengths_feedback(self):
        """Test generation of strengths in feedback."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        scores = {
            "relevance_score": 0.9,
            "completeness_score": 0.85,
            "grammar_score": 0.95,
            "confidence_score": 0.8,
            "overall_score": 0.88
        }
        
        feedback = evaluator.generate_feedback(scores)
        
        assert "strengths" in feedback
        assert len(feedback["strengths"]) > 0
    
    def test_generate_weakness_feedback(self):
        """Test generation of areas to improve in feedback."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        scores = {
            "relevance_score": 0.4,
            "completeness_score": 0.3,
            "grammar_score": 0.5,
            "confidence_score": 0.4,
            "overall_score": 0.4
        }
        
        feedback = evaluator.generate_feedback(scores)
        
        assert "weaknesses" in feedback or "areas_to_improve" in feedback
    
    def test_rating_classification(self):
        """Test overall rating classification."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        excellent_scores = {"overall_score": 0.92}
        good_scores = {"overall_score": 0.75}
        average_scores = {"overall_score": 0.55}
        poor_scores = {"overall_score": 0.30}
        
        assert evaluator.get_rating(excellent_scores["overall_score"]) in ["Excellent", "Outstanding"]
        assert evaluator.get_rating(good_scores["overall_score"]) in ["Good", "Above Average"]
        assert evaluator.get_rating(average_scores["overall_score"]) in ["Average", "Satisfactory"]
        assert evaluator.get_rating(poor_scores["overall_score"]) in ["Needs Improvement", "Poor", "Below Average"]


class TestScoreNormalization:
    """Tests for score normalization and aggregation."""
    
    def test_score_range(self):
        """Test that all scores are within valid range."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        question = "Any question here"
        answer = "Any answer here"
        expected_topics = []
        
        result = evaluator.evaluate(question, answer, expected_topics)
        
        for key, value in result.items():
            if key.endswith("_score"):
                assert 0 <= value <= 1, f"{key} should be between 0 and 1"
    
    def test_overall_score_calculation(self):
        """Test overall score is properly weighted average."""
        from app.services.nlp_evaluator import AnswerEvaluator
        
        evaluator = AnswerEvaluator()
        
        question = "Tell me about yourself."
        answer = "I am a software developer with experience in multiple technologies."
        expected_topics = ["experience", "background"]
        
        result = evaluator.evaluate(question, answer, expected_topics)
        
        # Overall score should be reasonable average of components
        individual_scores = [
            result.get("relevance_score", 0),
            result.get("completeness_score", 0),
            result.get("grammar_score", 0),
        ]
        
        avg = sum(individual_scores) / len(individual_scores)
        # Overall should be close to average (allowing for weighted calculation)
        assert abs(result.get("overall_score", 0) - avg) < 0.3
