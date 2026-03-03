"""
Question Generator - Core Implementation

This module implements the role-specific interview question generator
using LLM-based generation with structured prompts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from enum import Enum
import json
import asyncio
from abc import ABC, abstractmethod


# =============================================================================
# DATA MODELS
# =============================================================================

class ExperienceLevel(Enum):
    ENTRY = "entry"          # 0-2 years
    MID = "mid"              # 3-5 years
    SENIOR = "senior"        # 6-10 years
    LEAD = "lead"            # 10+ years


class QuestionCategory(Enum):
    TECHNICAL = "technical"
    HR = "hr"
    SCENARIO = "scenario"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class TechnicalQuestion:
    """Technical interview question structure."""
    id: int
    question: str
    category: str  # conceptual, problem-solving, implementation, design
    skill_tested: str
    difficulty: Difficulty
    expected_points: List[str]
    follow_up: str
    time_minutes: int
    evaluation_criteria: Dict[str, str]


@dataclass
class HRQuestion:
    """HR/Behavioral interview question structure."""
    id: int
    question: str
    competency: str
    star_focus: str
    positive_indicators: List[str]
    red_flags: List[str]
    follow_up_probes: List[str]
    time_minutes: int


@dataclass
class ScenarioQuestion:
    """Scenario-based interview question structure."""
    id: int
    scenario: str
    question: str
    type: str
    skills_tested: List[str]
    decision_points: List[str]
    acceptable_approaches: List[Dict]
    excellent_response_traits: List[str]
    time_minutes: int


@dataclass
class GeneratorInput:
    """Input parameters for question generation."""
    job_role: str
    skills: List[str]
    experience_level: ExperienceLevel
    num_technical: int = 5
    num_hr: int = 3
    num_scenario: int = 2
    industry: str = "Technology"
    company_values: List[str] = field(default_factory=lambda: ["Innovation", "Collaboration"])
    interview_duration_minutes: int = 60


@dataclass
class GeneratorOutput:
    """Output from question generation."""
    job_role: str
    experience_level: str
    technical_questions: List[TechnicalQuestion]
    hr_questions: List[HRQuestion]
    scenario_questions: List[ScenarioQuestion]
    total_time_minutes: int
    generation_metadata: Dict


# =============================================================================
# LLM PROVIDER INTERFACE
# =============================================================================

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate response from LLM."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        # In production: self.client = OpenAI(api_key=api_key)
    
    async def generate(self, prompt: str, system_prompt: str) -> str:
        """
        Generate response using OpenAI API.
        
        Production implementation:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
        """
        # Placeholder for actual API call
        pass


class LlamaProvider(LLMProvider):
    """Local LLaMA provider implementation."""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        # In production: self.model = load_llama_model(model_path)
    
    async def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate response using local LLaMA model."""
        # Placeholder for actual model inference
        pass


# =============================================================================
# PROMPT BUILDER
# =============================================================================

class PromptBuilder:
    """Builds optimized prompts for question generation."""
    
    def __init__(self):
        from prompts.prompt_templates import (
            SYSTEM_PROMPT_QUESTION_GENERATOR,
            TECHNICAL_QUESTIONS_PROMPT,
            HR_QUESTIONS_PROMPT,
            SCENARIO_QUESTIONS_PROMPT,
            DIFFICULTY_GUIDELINES
        )
        self.system_prompt = SYSTEM_PROMPT_QUESTION_GENERATOR
        self.technical_template = TECHNICAL_QUESTIONS_PROMPT
        self.hr_template = HR_QUESTIONS_PROMPT
        self.scenario_template = SCENARIO_QUESTIONS_PROMPT
        self.difficulty_guidelines = DIFFICULTY_GUIDELINES
    
    def _get_difficulty_context(self, level: ExperienceLevel) -> str:
        """Get difficulty calibration context for experience level."""
        guidelines = self.difficulty_guidelines.get(level.value, {})
        return f"""
        Difficulty Calibration for {level.value.upper()} level:
        - Technical Depth: {guidelines.get('technical_depth', '')}
        - Scenario Complexity: {guidelines.get('scenario_complexity', '')}
        - HR Focus: {guidelines.get('hr_focus', '')}
        """
    
    def build_technical_prompt(self, input_data: GeneratorInput) -> str:
        """Build prompt for technical questions."""
        difficulty = self._map_experience_to_difficulty(input_data.experience_level)
        
        return self.technical_template.format(
            num_questions=input_data.num_technical,
            job_role=input_data.job_role,
            skills=", ".join(input_data.skills),
            experience_level=input_data.experience_level.value,
            difficulty=difficulty
        )
    
    def build_hr_prompt(self, input_data: GeneratorInput) -> str:
        """Build prompt for HR/behavioral questions."""
        return self.hr_template.format(
            num_questions=input_data.num_hr,
            job_role=input_data.job_role,
            skills=", ".join(input_data.skills),
            experience_level=input_data.experience_level.value,
            culture_traits=", ".join(input_data.company_values)
        )
    
    def build_scenario_prompt(self, input_data: GeneratorInput) -> str:
        """Build prompt for scenario-based questions."""
        return self.scenario_template.format(
            num_questions=input_data.num_scenario,
            job_role=input_data.job_role,
            skills=", ".join(input_data.skills),
            experience_level=input_data.experience_level.value,
            industry=input_data.industry
        )
    
    def _map_experience_to_difficulty(self, level: ExperienceLevel) -> str:
        """Map experience level to difficulty distribution."""
        mapping = {
            ExperienceLevel.ENTRY: "60% easy, 30% medium, 10% hard",
            ExperienceLevel.MID: "20% easy, 50% medium, 30% hard",
            ExperienceLevel.SENIOR: "10% easy, 40% medium, 50% hard",
            ExperienceLevel.LEAD: "0% easy, 30% medium, 70% hard"
        }
        return mapping.get(level, "33% each")


# =============================================================================
# QUESTION GENERATOR
# =============================================================================

class QuestionGenerator:
    """
    Main question generator class.
    Orchestrates prompt building, LLM calls, and response parsing.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.prompt_builder = PromptBuilder()
    
    async def generate(self, input_data: GeneratorInput) -> GeneratorOutput:
        """
        Generate complete interview question set.
        
        Args:
            input_data: GeneratorInput with job role, skills, experience level
            
        Returns:
            GeneratorOutput with all question categories
        """
        # Generate all question types in parallel
        technical_task = self._generate_technical(input_data)
        hr_task = self._generate_hr(input_data)
        scenario_task = self._generate_scenarios(input_data)
        
        technical, hr, scenarios = await asyncio.gather(
            technical_task, hr_task, scenario_task
        )
        
        # Calculate total time
        total_time = (
            sum(q.time_minutes for q in technical) +
            sum(q.time_minutes for q in hr) +
            sum(q.time_minutes for q in scenarios)
        )
        
        return GeneratorOutput(
            job_role=input_data.job_role,
            experience_level=input_data.experience_level.value,
            technical_questions=technical,
            hr_questions=hr,
            scenario_questions=scenarios,
            total_time_minutes=total_time,
            generation_metadata={
                "skills_covered": input_data.skills,
                "industry": input_data.industry,
                "company_values": input_data.company_values
            }
        )
    
    async def _generate_technical(
        self, input_data: GeneratorInput
    ) -> List[TechnicalQuestion]:
        """Generate technical questions."""
        prompt = self.prompt_builder.build_technical_prompt(input_data)
        response = await self.llm.generate(
            prompt, 
            self.prompt_builder.system_prompt
        )
        return self._parse_technical_response(response)
    
    async def _generate_hr(
        self, input_data: GeneratorInput
    ) -> List[HRQuestion]:
        """Generate HR/behavioral questions."""
        prompt = self.prompt_builder.build_hr_prompt(input_data)
        response = await self.llm.generate(
            prompt,
            self.prompt_builder.system_prompt
        )
        return self._parse_hr_response(response)
    
    async def _generate_scenarios(
        self, input_data: GeneratorInput
    ) -> List[ScenarioQuestion]:
        """Generate scenario-based questions."""
        prompt = self.prompt_builder.build_scenario_prompt(input_data)
        response = await self.llm.generate(
            prompt,
            self.prompt_builder.system_prompt
        )
        return self._parse_scenario_response(response)
    
    def _parse_technical_response(self, response: str) -> List[TechnicalQuestion]:
        """Parse LLM response into TechnicalQuestion objects."""
        try:
            data = json.loads(response)
            questions = []
            for q in data.get("technical_questions", []):
                questions.append(TechnicalQuestion(
                    id=q["id"],
                    question=q["question"],
                    category=q["category"],
                    skill_tested=q["skill_tested"],
                    difficulty=Difficulty(q["difficulty"]),
                    expected_points=q["expected_points"],
                    follow_up=q["follow_up"],
                    time_minutes=q["time_minutes"],
                    evaluation_criteria=q["evaluation_criteria"]
                ))
            return questions
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse technical questions: {e}")
    
    def _parse_hr_response(self, response: str) -> List[HRQuestion]:
        """Parse LLM response into HRQuestion objects."""
        try:
            data = json.loads(response)
            questions = []
            for q in data.get("hr_questions", []):
                questions.append(HRQuestion(
                    id=q["id"],
                    question=q["question"],
                    competency=q["competency"],
                    star_focus=q["star_focus"],
                    positive_indicators=q["positive_indicators"],
                    red_flags=q["red_flags"],
                    follow_up_probes=q["follow_up_probes"],
                    time_minutes=q["time_minutes"]
                ))
            return questions
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse HR questions: {e}")
    
    def _parse_scenario_response(self, response: str) -> List[ScenarioQuestion]:
        """Parse LLM response into ScenarioQuestion objects."""
        try:
            data = json.loads(response)
            questions = []
            for q in data.get("scenario_questions", []):
                questions.append(ScenarioQuestion(
                    id=q["id"],
                    scenario=q["scenario"],
                    question=q["question"],
                    type=q["type"],
                    skills_tested=q["skills_tested"],
                    decision_points=q["decision_points"],
                    acceptable_approaches=q["acceptable_approaches"],
                    excellent_response_traits=q["excellent_response_traits"],
                    time_minutes=q["time_minutes"]
                ))
            return questions
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse scenario questions: {e}")


# =============================================================================
# PSEUDO-CODE: MAIN ALGORITHM
# =============================================================================

"""
PSEUDO-CODE: Question Generation Algorithm

FUNCTION generate_interview_questions(job_role, skills, experience_level):
    
    # Step 1: Validate Input
    VALIDATE job_role is not empty
    VALIDATE skills is non-empty list
    VALIDATE experience_level in [entry, mid, senior, lead]
    
    # Step 2: Determine Question Distribution
    difficulty_weights = MAP_EXPERIENCE_TO_DIFFICULTY(experience_level)
    question_counts = CALCULATE_QUESTION_COUNTS(interview_duration)
    
    # Step 3: Build Prompts with Context
    system_context = LOAD_SYSTEM_PROMPT()
    
    technical_prompt = BUILD_PROMPT(
        template = TECHNICAL_TEMPLATE,
        variables = {job_role, skills, difficulty_weights}
    )
    
    hr_prompt = BUILD_PROMPT(
        template = HR_TEMPLATE,
        variables = {job_role, experience_level, company_values}
    )
    
    scenario_prompt = BUILD_PROMPT(
        template = SCENARIO_TEMPLATE,
        variables = {job_role, skills, industry_context}
    )
    
    # Step 4: Generate Questions (Parallel)
    PARALLEL:
        technical_response = LLM.generate(system_context, technical_prompt)
        hr_response = LLM.generate(system_context, hr_prompt)
        scenario_response = LLM.generate(system_context, scenario_prompt)
    
    # Step 5: Parse and Validate Responses
    technical_questions = PARSE_JSON(technical_response)
    hr_questions = PARSE_JSON(hr_response)
    scenario_questions = PARSE_JSON(scenario_response)
    
    # Step 6: Post-Processing
    all_questions = COMBINE(technical, hr, scenario)
    all_questions = REMOVE_DUPLICATES(all_questions)
    all_questions = VALIDATE_COVERAGE(all_questions, skills)
    all_questions = ORDER_BY_FLOW(all_questions)
    
    # Step 7: Return Structured Output
    RETURN {
        technical_questions,
        hr_questions,
        scenario_questions,
        metadata: {total_time, skills_covered, difficulty_distribution}
    }

END FUNCTION
"""


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def main():
    """Example usage of the Question Generator."""
    
    # Initialize provider (use your API key)
    provider = OpenAIProvider(api_key="your-api-key", model="gpt-4")
    
    # Create generator
    generator = QuestionGenerator(llm_provider=provider)
    
    # Define input
    input_data = GeneratorInput(
        job_role="Senior Backend Engineer",
        skills=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes"],
        experience_level=ExperienceLevel.SENIOR,
        num_technical=5,
        num_hr=3,
        num_scenario=2,
        industry="FinTech",
        company_values=["Innovation", "Security", "Customer Focus"],
        interview_duration_minutes=60
    )
    
    # Generate questions
    output = await generator.generate(input_data)
    
    # Print results
    print(f"Generated questions for: {output.job_role}")
    print(f"Experience Level: {output.experience_level}")
    print(f"Total Interview Time: {output.total_time_minutes} minutes")
    print(f"\nTechnical Questions: {len(output.technical_questions)}")
    print(f"HR Questions: {len(output.hr_questions)}")
    print(f"Scenario Questions: {len(output.scenario_questions)}")


if __name__ == "__main__":
    asyncio.run(main())
