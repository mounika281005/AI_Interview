# LLM Prompt Templates for Question Generation

"""
This module contains all prompt templates used for generating interview questions.
Prompts are designed for optimal LLM performance with clear structure and examples.
"""

# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SYSTEM_PROMPT_QUESTION_GENERATOR = """
You are an expert interview question designer with 15+ years of experience in technical recruiting across multiple industries. Your expertise includes:

- Designing role-specific technical assessments
- Creating behavioral interview questions using STAR methodology
- Developing scenario-based questions that test real-world problem-solving
- Calibrating question difficulty based on experience levels

Your questions should be:
1. Clear and unambiguous
2. Appropriate for the specified experience level
3. Relevant to the job role and required skills
4. Designed to elicit meaningful, evaluable responses
5. Free from bias and inclusive

Experience Level Calibration:
- Entry (0-2 years): Focus on fundamentals, learning ability, potential
- Mid (3-5 years): Focus on practical application, problem-solving, collaboration
- Senior (6-10 years): Focus on system design, leadership, mentoring
- Lead/Principal (10+ years): Focus on architecture, strategy, team building
"""

# =============================================================================
# TECHNICAL QUESTIONS PROMPT
# =============================================================================

TECHNICAL_QUESTIONS_PROMPT = """
Generate {num_questions} technical interview questions for the following role:

**Job Role:** {job_role}
**Required Skills:** {skills}
**Experience Level:** {experience_level}
**Difficulty:** {difficulty}

Requirements for Technical Questions:
1. Test practical knowledge of the specified skills
2. Include a mix of:
   - Conceptual understanding questions
   - Problem-solving questions
   - Code/implementation questions (where applicable)
   - System design questions (for senior roles)
3. Scale complexity appropriately for {experience_level} level
4. Each question should have clear evaluation criteria

For each question, provide:
- The question text
- Category (conceptual/problem-solving/implementation/design)
- Expected answer key points
- Follow-up question suggestion
- Time allocation (in minutes)

Output Format (JSON):
{{
  "technical_questions": [
    {{
      "id": 1,
      "question": "...",
      "category": "conceptual|problem-solving|implementation|design",
      "skill_tested": "specific skill from the list",
      "difficulty": "easy|medium|hard",
      "expected_points": ["point1", "point2", "point3"],
      "follow_up": "...",
      "time_minutes": 5,
      "evaluation_criteria": {{
        "excellent": "description",
        "good": "description",
        "needs_improvement": "description"
      }}
    }}
  ]
}}
"""

# =============================================================================
# HR/BEHAVIORAL QUESTIONS PROMPT
# =============================================================================

HR_QUESTIONS_PROMPT = """
Generate {num_questions} HR/behavioral interview questions for the following role:

**Job Role:** {job_role}
**Required Skills:** {skills}
**Experience Level:** {experience_level}
**Company Culture Traits:** {culture_traits}

Requirements for HR/Behavioral Questions:
1. Use STAR method framework (Situation, Task, Action, Result)
2. Cover these competency areas:
   - Teamwork and collaboration
   - Communication skills
   - Problem-solving approach
   - Adaptability and learning
   - Leadership (for senior roles)
   - Conflict resolution
3. Avoid hypothetical questions - ask for real past experiences
4. Include questions about career motivation and goals

For each question, provide:
- The question text
- Competency being assessed
- Red flags to watch for
- Positive indicators to look for
- Follow-up probes

Output Format (JSON):
{{
  "hr_questions": [
    {{
      "id": 1,
      "question": "...",
      "competency": "teamwork|communication|problem-solving|adaptability|leadership|conflict-resolution",
      "star_focus": "situation|task|action|result",
      "positive_indicators": ["indicator1", "indicator2"],
      "red_flags": ["flag1", "flag2"],
      "follow_up_probes": ["probe1", "probe2"],
      "time_minutes": 5
    }}
  ]
}}
"""

# =============================================================================
# SCENARIO-BASED QUESTIONS PROMPT
# =============================================================================

SCENARIO_QUESTIONS_PROMPT = """
Generate {num_questions} scenario-based interview questions for the following role:

**Job Role:** {job_role}
**Required Skills:** {skills}
**Experience Level:** {experience_level}
**Industry Context:** {industry}

Requirements for Scenario-Based Questions:
1. Present realistic workplace situations relevant to {job_role}
2. Test practical application of skills in context
3. Include scenarios covering:
   - Technical challenges
   - Interpersonal conflicts
   - Time pressure situations
   - Resource constraints
   - Ethical dilemmas (where appropriate)
4. Scenarios should have multiple valid approaches
5. Scale complexity based on {experience_level}

For each scenario, provide:
- The scenario description
- The specific question/challenge
- Key decision points to evaluate
- Multiple acceptable approaches
- What differentiates excellent from good responses

Output Format (JSON):
{{
  "scenario_questions": [
    {{
      "id": 1,
      "scenario": "Detailed scenario description...",
      "question": "Specific question about the scenario",
      "type": "technical|interpersonal|pressure|resource|ethical",
      "skills_tested": ["skill1", "skill2"],
      "decision_points": ["point1", "point2"],
      "acceptable_approaches": [
        {{
          "approach": "description",
          "pros": ["pro1"],
          "cons": ["con1"]
        }}
      ],
      "excellent_response_traits": ["trait1", "trait2"],
      "time_minutes": 10
    }}
  ]
}}
"""

# =============================================================================
# FOLLOW-UP QUESTION PROMPT
# =============================================================================

FOLLOWUP_QUESTION_PROMPT = """
Based on the candidate's response, generate a follow-up question:

**Original Question:** {original_question}
**Candidate's Response:** {candidate_response}
**Skills Being Tested:** {skills}
**Identified Gaps:** {gaps}

Generate a follow-up question that:
1. Probes deeper into areas the candidate mentioned briefly
2. Clarifies any ambiguous points
3. Tests understanding at a deeper level
4. Explores gaps in the response

Output Format (JSON):
{{
  "follow_up": {{
    "question": "...",
    "purpose": "probe|clarify|deepen|explore_gap",
    "target_area": "specific area to explore",
    "expected_insight": "what you hope to learn"
  }}
}}
"""

# =============================================================================
# COMPLETE INTERVIEW SET PROMPT
# =============================================================================

COMPLETE_INTERVIEW_PROMPT = """
Generate a complete interview question set for:

**Job Role:** {job_role}
**Required Skills:** {skills}
**Experience Level:** {experience_level}
**Interview Duration:** {duration_minutes} minutes
**Company Industry:** {industry}
**Company Values:** {company_values}

Generate a balanced set including:
- {num_technical} Technical Questions
- {num_hr} HR/Behavioral Questions  
- {num_scenario} Scenario-Based Questions

Ensure:
1. Questions flow logically from warm-up to challenging
2. No redundancy between questions
3. All key skills are assessed
4. Time allocations sum to interview duration
5. Mix of difficulty levels appropriate for experience

Output a complete interview guide with questions ordered by recommended sequence.
"""

# =============================================================================
# DIFFICULTY CALIBRATION
# =============================================================================

DIFFICULTY_GUIDELINES = {
    "entry": {
        "technical_depth": "Focus on fundamentals and basic concepts. Ask about textbook knowledge and simple practical applications.",
        "scenario_complexity": "Simple, single-issue scenarios. Clear right/wrong approaches.",
        "hr_focus": "Learning ability, enthusiasm, cultural fit, basic teamwork.",
        "example_technical": "Explain the difference between a list and a dictionary in Python.",
        "example_scenario": "Your task is taking longer than expected. How do you handle this?"
    },
    "mid": {
        "technical_depth": "Practical application and trade-offs. Real-world problem solving. Some system design basics.",
        "scenario_complexity": "Multi-factor scenarios requiring prioritization. Competing stakeholder needs.",
        "hr_focus": "Independence, ownership, cross-team collaboration, mentoring juniors.",
        "example_technical": "Design a caching strategy for a high-traffic web application.",
        "example_scenario": "Two team members disagree on technical approach. How do you help resolve this?"
    },
    "senior": {
        "technical_depth": "System design, architecture decisions, scalability. Technical leadership.",
        "scenario_complexity": "Complex organizational scenarios. Long-term strategic thinking.",
        "hr_focus": "Technical vision, team building, stakeholder management, mentorship.",
        "example_technical": "Design a distributed system for processing millions of events per second.",
        "example_scenario": "Your team's project conflicts with another team's priorities. Navigate this situation."
    },
    "lead": {
        "technical_depth": "Enterprise architecture, technology strategy, build vs buy decisions.",
        "scenario_complexity": "Organization-wide impact scenarios. Cultural and technical transformation.",
        "hr_focus": "Vision setting, organizational influence, executive communication, hiring strategy.",
        "example_technical": "How would you evaluate and implement a major technology platform migration?",
        "example_scenario": "The CTO asks you to reduce team size by 20% while maintaining delivery. Approach?"
    }
}
