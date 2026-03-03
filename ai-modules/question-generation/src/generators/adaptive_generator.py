"""
Adaptive Question Generator

Generates questions that adapt based on:
1. Previous answers from the candidate
2. Identified skill gaps
3. Time remaining in interview
4. Difficulty progression
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class CandidateContext:
    """Context built from candidate's responses."""
    answered_questions: List[Dict]  # List of {question, response, score}
    identified_strengths: List[str]
    identified_gaps: List[str]
    current_difficulty_level: float  # 0.0 to 1.0
    time_remaining_minutes: int
    skills_tested: List[str]
    skills_untested: List[str]


@dataclass
class AdaptiveQuestion:
    """Question with adaptive metadata."""
    question: str
    type: str
    target_skill: str
    difficulty: float
    reason_selected: str  # Why this question was chosen
    builds_on: Optional[str]  # Previous question this relates to


class AdaptiveQuestionGenerator:
    """
    Generates questions that adapt to candidate performance.
    
    Algorithm:
    1. Analyze previous responses for strengths/gaps
    2. Prioritize untested skills
    3. Adjust difficulty based on performance
    4. Generate contextual follow-ups
    5. Balance question types for remaining time
    """
    
    def __init__(self, llm_provider, base_generator):
        self.llm = llm_provider
        self.base_generator = base_generator
        self.difficulty_adjustment_rate = 0.2
    
    def analyze_responses(
        self, 
        answered_questions: List[Dict]
    ) -> CandidateContext:
        """
        Analyze all responses to build candidate context.
        
        Pseudo-code:
        FOR each answered_question:
            score = answered_question.score
            skill = answered_question.skill_tested
            
            IF score >= 0.8:
                ADD skill TO identified_strengths
                INCREASE current_difficulty
            ELIF score <= 0.4:
                ADD skill TO identified_gaps
                DECREASE current_difficulty
            
            ADD skill TO skills_tested
        
        skills_untested = all_required_skills - skills_tested
        RETURN CandidateContext
        """
        pass
    
    def select_next_question_strategy(
        self, 
        context: CandidateContext
    ) -> str:
        """
        Determine strategy for next question.
        
        Strategies:
        - 'probe_gap': Dig deeper into identified weakness
        - 'confirm_strength': Verify strength with harder question
        - 'explore_new': Test untested skill
        - 'scenario_integration': Combine multiple skills in scenario
        """
        # If significant gaps, probe them
        if len(context.identified_gaps) >= 2:
            return 'probe_gap'
        
        # If untested skills and time permits
        if context.skills_untested and context.time_remaining_minutes > 15:
            return 'explore_new'
        
        # If strong performance, increase difficulty
        if context.current_difficulty_level > 0.7:
            return 'confirm_strength'
        
        # Default to integrative scenario
        return 'scenario_integration'
    
    async def generate_adaptive_question(
        self,
        context: CandidateContext,
        job_role: str
    ) -> AdaptiveQuestion:
        """
        Generate next question based on candidate context.
        
        Pseudo-code:
        strategy = SELECT_NEXT_QUESTION_STRATEGY(context)
        
        IF strategy == 'probe_gap':
            target_skill = SELECT_HIGHEST_PRIORITY_GAP(context.identified_gaps)
            difficulty = context.current_difficulty - 0.1  # Slightly easier
            prompt = BUILD_GAP_PROBE_PROMPT(target_skill, context)
        
        ELIF strategy == 'confirm_strength':
            target_skill = SELECT_FROM_STRENGTHS(context.identified_strengths)
            difficulty = context.current_difficulty + 0.2  # Harder
            prompt = BUILD_STRENGTH_CONFIRM_PROMPT(target_skill, difficulty)
        
        ELIF strategy == 'explore_new':
            target_skill = context.skills_untested[0]
            difficulty = context.current_difficulty  # Same level
            prompt = BUILD_NEW_SKILL_PROMPT(target_skill)
        
        ELSE:  # scenario_integration
            target_skills = SELECT_MULTIPLE_SKILLS(context)
            difficulty = context.current_difficulty
            prompt = BUILD_INTEGRATION_PROMPT(target_skills)
        
        question = LLM.generate(prompt)
        RETURN AdaptiveQuestion(question, strategy, target_skill, difficulty)
        """
        pass
    
    def calculate_difficulty_adjustment(
        self,
        recent_scores: List[float]
    ) -> float:
        """
        Calculate how much to adjust difficulty.
        
        Uses exponential moving average of recent scores.
        """
        if not recent_scores:
            return 0.5  # Start at medium
        
        weights = [0.4, 0.3, 0.2, 0.1]  # Recent scores weighted more
        weighted_sum = sum(
            score * weight 
            for score, weight in zip(recent_scores[-4:], weights[:len(recent_scores)])
        )
        weight_total = sum(weights[:len(recent_scores)])
        
        return weighted_sum / weight_total


# =============================================================================
# ADAPTIVE PROMPT TEMPLATES
# =============================================================================

GAP_PROBE_PROMPT = """
The candidate showed weakness in {skill} based on their response:
"{previous_response}"

Generate a follow-up question that:
1. Approaches the concept from a different angle
2. Is slightly easier to build confidence
3. Tests foundational understanding
4. Gives candidate opportunity to demonstrate knowledge

Job Role: {job_role}
Difficulty: {difficulty}/10

Output a single question with expected answer points.
"""

STRENGTH_CONFIRM_PROMPT = """
The candidate showed strong understanding of {skill}.
Their response demonstrated: {demonstrated_points}

Generate a more challenging question that:
1. Tests advanced/edge-case knowledge
2. Requires applying the skill in complex scenarios
3. May combine with other skills: {related_skills}
4. Differentiates good from excellent candidates

Job Role: {job_role}
Target Difficulty: {difficulty}/10 (challenging)

Output a single question with evaluation criteria.
"""

SKILL_INTEGRATION_PROMPT = """
Create a scenario question that integrates these skills:
{skills_list}

The scenario should:
1. Present a realistic {industry} workplace situation
2. Require synthesizing multiple skills to solve
3. Have multiple valid approaches
4. Be appropriate for {experience_level} level

Context from interview so far:
- Candidate strengths: {strengths}
- Areas to develop: {gaps}

Output a scenario with question, decision points, and evaluation criteria.
"""
