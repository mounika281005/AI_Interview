# Role-Specific Interview Question Generator

## Complete Implementation Guide

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUESTION GENERATOR ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   API REQUEST   │
                              │                 │
                              │ • Job Role      │
                              │ • Skills        │
                              │ • Experience    │
                              └────────┬────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            QUESTION SERVICE API                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  POST /api/questions/generate                                        │   │
│  │  POST /api/questions/follow-up                                       │   │
│  │  GET  /api/questions/templates                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROMPT BUILDER                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │   Technical   │  │      HR       │  │   Scenario    │                   │
│  │   Template    │  │   Template    │  │   Template    │                   │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘                   │
│          │                  │                  │                            │
│          └──────────────────┼──────────────────┘                            │
│                             ▼                                               │
│              ┌─────────────────────────────┐                                │
│              │   Difficulty Calibration    │                                │
│              │   • Entry: 60% easy         │                                │
│              │   • Mid: 50% medium         │                                │
│              │   • Senior: 50% hard        │                                │
│              │   • Lead: 70% hard          │                                │
│              └─────────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LLM PROVIDER                                      │
│  ┌───────────────────────┐         ┌───────────────────────┐               │
│  │      OpenAI GPT-4     │   OR    │    Local LLaMA        │               │
│  │  • API-based          │         │  • Self-hosted        │               │
│  │  • High quality       │         │  • Privacy-focused    │               │
│  │  • JSON mode          │         │  • Cost-effective     │               │
│  └───────────────────────┘         └───────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE PARSER                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Parse JSON response                                               │   │
│  │  • Validate question structure                                       │   │
│  │  • Map to typed objects (TechnicalQuestion, HRQuestion, etc.)       │   │
│  │  • Handle parsing errors gracefully                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  API RESPONSE   │
                              │                 │
                              │ • Technical Qs  │
                              │ • HR Questions  │
                              │ • Scenarios     │
                              │ • Metadata      │
                              └─────────────────┘
```

---

## 2. Prompt Design Strategy

### 2.1 System Prompt (Sets AI Behavior)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM PROMPT DESIGN                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ROLE DEFINITION                                                             │
│  "You are an expert interview question designer with 15+ years of           │
│   experience in technical recruiting across multiple industries..."         │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY CRITERIA                                                            │
│  1. Clear and unambiguous                                                   │
│  2. Appropriate for experience level                                        │
│  3. Relevant to job role and skills                                         │
│  4. Designed to elicit evaluable responses                                  │
│  5. Free from bias and inclusive                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  EXPERIENCE LEVEL CALIBRATION                                                │
│  • Entry (0-2 yrs):  Fundamentals, learning ability, potential              │
│  • Mid (3-5 yrs):    Practical application, problem-solving                 │
│  • Senior (6-10 yrs): System design, leadership, mentoring                  │
│  • Lead (10+ yrs):   Architecture, strategy, team building                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Question Generation Prompt Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROMPT TEMPLATE STRUCTURE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. TASK INSTRUCTION                                                         │
│     "Generate {num_questions} technical interview questions for..."         │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. CONTEXT VARIABLES                                                        │
│     **Job Role:** {job_role}                                                │
│     **Required Skills:** {skills}                                           │
│     **Experience Level:** {experience_level}                                │
│     **Difficulty:** {difficulty}                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. REQUIREMENTS SPECIFICATION                                               │
│     • Test practical knowledge of specified skills                          │
│     • Include mix of question types                                         │
│     • Scale complexity appropriately                                        │
│     • Provide clear evaluation criteria                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. OUTPUT FORMAT (JSON Schema)                                              │
│     {                                                                        │
│       "technical_questions": [                                              │
│         {                                                                    │
│           "id": 1,                                                          │
│           "question": "...",                                                │
│           "category": "conceptual|problem-solving|...",                     │
│           "expected_points": ["..."],                                       │
│           "evaluation_criteria": {...}                                      │
│         }                                                                    │
│       ]                                                                      │
│     }                                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Pseudo-Code Algorithm

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUESTION GENERATION ALGORITHM                             │
└─────────────────────────────────────────────────────────────────────────────┘

FUNCTION generate_interview_questions(job_role, skills, experience_level):
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │  STEP 1: INPUT VALIDATION                                           │
    ├─────────────────────────────────────────────────────────────────────┤
    │  VALIDATE job_role is not empty                                     │
    │  VALIDATE skills is non-empty list                                  │
    │  VALIDATE experience_level in [entry, mid, senior, lead]            │
    │  IF validation fails: RAISE ValidationError                         │
    └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  STEP 2: CONFIGURE DIFFICULTY                                        │
    ├─────────────────────────────────────────────────────────────────────┤
    │  difficulty_weights = {                                             │
    │    entry:  {easy: 60%, medium: 30%, hard: 10%}                      │
    │    mid:    {easy: 20%, medium: 50%, hard: 30%}                      │
    │    senior: {easy: 10%, medium: 40%, hard: 50%}                      │
    │    lead:   {easy: 0%,  medium: 30%, hard: 70%}                      │
    │  }                                                                   │
    │  selected_weights = difficulty_weights[experience_level]            │
    └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  STEP 3: BUILD PROMPTS                                               │
    ├─────────────────────────────────────────────────────────────────────┤
    │  system_prompt = LOAD_SYSTEM_PROMPT()                               │
    │                                                                      │
    │  technical_prompt = FORMAT_TEMPLATE(                                │
    │    TECHNICAL_TEMPLATE,                                              │
    │    {job_role, skills, experience_level, difficulty_weights}         │
    │  )                                                                   │
    │                                                                      │
    │  hr_prompt = FORMAT_TEMPLATE(                                       │
    │    HR_TEMPLATE,                                                     │
    │    {job_role, experience_level, company_values}                     │
    │  )                                                                   │
    │                                                                      │
    │  scenario_prompt = FORMAT_TEMPLATE(                                 │
    │    SCENARIO_TEMPLATE,                                               │
    │    {job_role, skills, industry}                                     │
    │  )                                                                   │
    └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  STEP 4: PARALLEL LLM GENERATION                                     │
    ├─────────────────────────────────────────────────────────────────────┤
    │  PARALLEL EXECUTE:                                                  │
    │    technical_response = LLM.generate(system_prompt, technical_prompt)│
    │    hr_response = LLM.generate(system_prompt, hr_prompt)             │
    │    scenario_response = LLM.generate(system_prompt, scenario_prompt) │
    │                                                                      │
    │  AWAIT all responses                                                │
    └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  STEP 5: PARSE RESPONSES                                             │
    ├─────────────────────────────────────────────────────────────────────┤
    │  TRY:                                                               │
    │    technical_questions = PARSE_JSON(technical_response)             │
    │    hr_questions = PARSE_JSON(hr_response)                           │
    │    scenario_questions = PARSE_JSON(scenario_response)               │
    │  CATCH JsonParseError:                                              │
    │    RETRY with different temperature OR RAISE error                  │
    │                                                                      │
    │  VALIDATE each question has required fields                         │
    │  CONVERT to typed objects (TechnicalQuestion, HRQuestion, etc.)     │
    └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  STEP 6: POST-PROCESSING                                             │
    ├─────────────────────────────────────────────────────────────────────┤
    │  all_questions = COMBINE(technical, hr, scenario)                   │
    │                                                                      │
    │  # Remove similar questions                                         │
    │  all_questions = DEDUPLICATE_BY_SIMILARITY(all_questions, threshold=0.8)│
    │                                                                      │
    │  # Ensure all skills are tested                                     │
    │  coverage = CHECK_SKILL_COVERAGE(all_questions, skills)             │
    │  IF coverage < 100%:                                                │
    │    GENERATE additional questions for uncovered skills               │
    │                                                                      │
    │  # Order questions logically                                        │
    │  all_questions = ORDER_BY_FLOW(all_questions)                       │
    │    # warm-up → technical → scenario → behavioral → closing          │
    └─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  STEP 7: RETURN RESULT                                               │
    ├─────────────────────────────────────────────────────────────────────┤
    │  RETURN GeneratorOutput {                                           │
    │    technical_questions: [...],                                      │
    │    hr_questions: [...],                                             │
    │    scenario_questions: [...],                                       │
    │    total_time_minutes: SUM(all question times),                     │
    │    metadata: {skills_covered, difficulty_distribution}              │
    │  }                                                                   │
    └─────────────────────────────────────────────────────────────────────┘

END FUNCTION
```

---

## 4. Example Input/Output

### Input

```json
{
  "job_role": "Senior Backend Engineer",
  "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes"],
  "experience_level": "senior",
  "num_technical": 5,
  "num_hr": 3,
  "num_scenario": 2,
  "industry": "FinTech",
  "company_values": ["Innovation", "Security", "Customer Focus"]
}
```

### Output (Summary)

```json
{
  "job_role": "Senior Backend Engineer",
  "experience_level": "senior",
  "total_time_minutes": 58,
  
  "technical_questions": [
    {
      "question": "Design a high-throughput payment processing system...",
      "category": "design",
      "skill_tested": "System Design",
      "difficulty": "hard",
      "expected_points": ["Microservices", "Message queues", "ACID compliance"],
      "time_minutes": 12
    }
    // ... 4 more questions
  ],
  
  "hr_questions": [
    {
      "question": "Tell me about a time when you had to make a significant technical decision that other senior engineers disagreed with...",
      "competency": "leadership",
      "positive_indicators": ["Gathered data", "Listened to others"],
      "red_flags": ["Pulled rank", "Dismissed opinions"]
    }
    // ... 2 more questions
  ],
  
  "scenario_questions": [
    {
      "scenario": "During a routine deployment on Friday afternoon, the payment processing service starts returning errors...",
      "question": "Walk me through exactly how you would handle this situation...",
      "skills_tested": ["Leadership", "System Design", "Communication"],
      "decision_points": ["Rollback vs investigate", "Stakeholder communication"]
    }
    // ... 1 more scenario
  ]
}
```

---

## 5. Files Created

| File | Purpose |
|------|---------|
| [src/prompts/prompt_templates.py](src/prompts/prompt_templates.py) | All LLM prompt templates |
| [src/generators/question_generator.py](src/generators/question_generator.py) | Core generator implementation |
| [src/generators/adaptive_generator.py](src/generators/adaptive_generator.py) | Adaptive question generation |
| [src/api/question_service.py](src/api/question_service.py) | FastAPI service endpoints |
| [examples/sample_input_output.json](examples/sample_input_output.json) | Complete example I/O |

---

## 6. Key Design Decisions

### Why Parallel Generation?
- Technical, HR, and scenario questions are independent
- Reduces total generation time by ~3x
- Each prompt is optimized for its category

### Why Structured JSON Output?
- Ensures consistent parsing
- Enables validation
- Makes questions directly usable in the interview flow

### Why Experience-Based Difficulty Calibration?
- Entry-level candidates need confidence-building questions
- Senior candidates need challenging, differentiating questions
- Prevents frustration or boredom

### Why Include Evaluation Criteria?
- Enables consistent scoring across interviewers
- Provides immediate feedback to candidates
- Supports AI-based answer evaluation
