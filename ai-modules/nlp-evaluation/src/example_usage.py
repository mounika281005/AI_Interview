"""
==============================================================================
Example Usage: NLP Answer Evaluation Module
==============================================================================

This script demonstrates how to use the NLP-based answer evaluation module
for a mock interview system. Run this file to see evaluation in action.

Usage:
    python example_usage.py

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import json
from answer_evaluator import AnswerEvaluator, evaluate_answer
from scoring_config import (
    WeightProfiles,
    EvaluationPreset,
    get_keywords_for_topic,
    get_all_keywords_for_domain
)


def print_separator(title: str = ""):
    """Print a formatted section separator."""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def example_1_basic_evaluation():
    """
    Example 1: Basic Evaluation
    
    Simple usage with question, answer, and optional keywords.
    """
    print_separator("EXAMPLE 1: BASIC EVALUATION")
    
    # Define the interview question
    question = "What is Object-Oriented Programming?"
    
    # Candidate's answer
    answer = """
    Object-Oriented Programming, commonly known as OOP, is a programming 
    paradigm that organizes software design around data, or objects, rather 
    than functions and logic. An object is a data field that has unique 
    attributes and behavior. OOP focuses on the objects that developers 
    want to manipulate rather than the logic required to manipulate them.
    
    The four main principles of OOP are:
    1. Encapsulation - bundling data and methods that operate on that data
    2. Inheritance - allowing classes to inherit properties from other classes
    3. Polymorphism - ability of objects to take on many forms
    4. Abstraction - hiding complex implementation details
    """
    
    # Expected keywords for this topic
    expected_keywords = [
        "object", "class", "encapsulation", "inheritance", 
        "polymorphism", "abstraction", "paradigm", "data"
    ]
    
    # Create evaluator and evaluate
    evaluator = AnswerEvaluator()
    result = evaluator.evaluate(question, answer, expected_keywords)
    
    # Print results
    print(f"\n📝 Question: {question}")
    print(f"\n🎯 Overall Score: {result.overall_score}/100")
    print(f"📊 Grade: {result.grade}")
    
    print(f"\n📈 Detailed Scores:")
    print(f"   • Relevance: {result.relevance.score}/100")
    print(f"   • Grammar:   {result.grammar.score}/100")
    print(f"   • Fluency:   {result.fluency.score}/100")
    print(f"   • Keywords:  {result.keywords.score}/100")
    
    print(f"\n💪 Strengths:")
    for strength in result.strengths:
        print(f"   ✓ {strength}")
    
    print(f"\n💡 Suggestions:")
    for suggestion in result.suggestions:
        print(f"   → {suggestion}")


def example_2_technical_interview():
    """
    Example 2: Technical Interview with Domain Keywords
    
    Using predefined keywords from the scoring configuration.
    """
    print_separator("EXAMPLE 2: TECHNICAL INTERVIEW")
    
    question = "Explain how you would implement a REST API for user authentication."
    
    answer = """
    To implement a REST API for user authentication, I would use the following approach:
    
    First, I'd create endpoints for registration, login, and logout. For registration,
    users submit their email and password via POST request to /api/auth/register.
    The password is hashed using bcrypt before storing in the database.
    
    For login, the /api/auth/login endpoint validates credentials and returns a JWT
    token. This token is included in the Authorization header for subsequent requests.
    
    I'd implement middleware to verify JWT tokens on protected routes. The token
    contains user ID and expiration time. For logout, we can blacklist tokens or
    use short-lived tokens with refresh token rotation.
    
    Security measures include HTTPS, rate limiting, and input validation to prevent
    SQL injection and XSS attacks.
    """
    
    # Get keywords from predefined dictionary
    api_keywords = get_keywords_for_topic('software_engineering', 'web_development')
    db_keywords = get_keywords_for_topic('software_engineering', 'databases')
    combined_keywords = api_keywords + db_keywords + [
        'jwt', 'token', 'authentication', 'authorization', 'password', 
        'bcrypt', 'hash', 'middleware', 'https', 'security'
    ]
    
    # Use technical weights
    evaluator = AnswerEvaluator()
    # Override weights for technical interview
    evaluator.WEIGHTS = WeightProfiles.TECHNICAL.to_dict()
    
    result = evaluator.evaluate(question, answer, combined_keywords)
    
    print(f"\n📝 Question: {question}")
    print(f"\n🎯 Overall Score: {result.overall_score}/100 (Grade: {result.grade})")
    
    print(f"\n🔑 Keyword Analysis:")
    print(f"   Expected: {len(result.keywords.details['expected'])} keywords")
    print(f"   Found: {len(result.keywords.details['found'])} keywords")
    print(f"   Found keywords: {', '.join(result.keywords.details['found'][:10])}")
    
    if result.keywords.details['missing']:
        print(f"   Missing: {', '.join(result.keywords.details['missing'][:5])}")


def example_3_behavioral_interview():
    """
    Example 3: Behavioral Interview (STAR Method)
    
    Evaluating soft skills and communication.
    """
    print_separator("EXAMPLE 3: BEHAVIORAL INTERVIEW")
    
    question = "Tell me about a time when you had to deal with a difficult team member."
    
    # Good STAR format answer
    good_answer = """
    In my previous role as a software developer, I worked with a team member who 
    frequently missed deadlines and didn't communicate blockers. This was affecting 
    our sprint velocity and team morale.
    
    My task was to address this situation while maintaining a positive team environment.
    I scheduled a one-on-one meeting to understand their perspective.
    
    During the conversation, I discovered they were struggling with the new 
    technology stack but were hesitant to ask for help. I proposed a mentorship 
    arrangement where I could provide guidance, and we set up daily check-ins.
    
    As a result, their productivity improved by 40% over the next month, and they 
    became more engaged in team discussions. This experience taught me the 
    importance of addressing issues early and with empathy.
    """
    
    # Get behavioral keywords
    behavioral_keywords = get_all_keywords_for_domain('behavioral')
    
    evaluator = AnswerEvaluator()
    evaluator.WEIGHTS = WeightProfiles.BEHAVIORAL.to_dict()
    
    result = evaluator.evaluate(question, good_answer, behavioral_keywords)
    
    print(f"\n📝 Question: {question}")
    print(f"\n🎯 Overall Score: {result.overall_score}/100 (Grade: {result.grade})")
    
    print(f"\n📊 Fluency Analysis:")
    print(f"   Word count: {result.fluency.details['word_count']}")
    print(f"   Sentence count: {result.fluency.details['sentence_count']}")
    print(f"   Transition words: {', '.join(result.fluency.details['transition_words_found'])}")
    print(f"   Readability (Flesch): {result.fluency.details['flesch_reading_ease']}")


def example_4_poor_answer_evaluation():
    """
    Example 4: Evaluating a Poor Answer
    
    Shows how the system identifies weaknesses and provides feedback.
    """
    print_separator("EXAMPLE 4: POOR ANSWER EVALUATION")
    
    question = "Explain the difference between SQL and NoSQL databases."
    
    # Poor answer - short, irrelevant, grammar issues
    poor_answer = """
    sql is like tables and nosql is not tables. i think sql is better
    because its more popular. databases store data and u can query them.
    """
    
    expected_keywords = [
        'relational', 'schema', 'structured', 'unstructured', 'scalability',
        'ACID', 'document', 'key-value', 'normalization', 'flexible'
    ]
    
    evaluator = AnswerEvaluator()
    result = evaluator.evaluate(question, poor_answer, expected_keywords)
    
    print(f"\n📝 Question: {question}")
    print(f"\n📄 Answer: {poor_answer.strip()}")
    
    print(f"\n🎯 Overall Score: {result.overall_score}/100 (Grade: {result.grade})")
    
    print(f"\n📈 Detailed Scores:")
    print(f"   • Relevance: {result.relevance.score}/100 - {result.relevance.feedback}")
    print(f"   • Grammar:   {result.grammar.score}/100 - {result.grammar.feedback}")
    print(f"   • Fluency:   {result.fluency.score}/100 - {result.fluency.feedback}")
    print(f"   • Keywords:  {result.keywords.score}/100 - {result.keywords.feedback}")
    
    print(f"\n⚠️ Issues Found:")
    if result.grammar.details.get('errors'):
        for error in result.grammar.details['errors'][:3]:
            print(f"   • {error.get('message', 'Grammar issue')}")
    
    print(f"\n💡 Improvement Suggestions:")
    for suggestion in result.suggestions:
        print(f"   → {suggestion}")


def example_5_json_output():
    """
    Example 5: Getting JSON Output
    
    Demonstrates how to get evaluation results as JSON for API responses.
    """
    print_separator("EXAMPLE 5: JSON OUTPUT")
    
    question = "What is machine learning?"
    
    answer = """
    Machine learning is a subset of artificial intelligence that enables 
    systems to learn and improve from experience without being explicitly 
    programmed. It focuses on developing algorithms that can access data 
    and use it to learn for themselves. The process begins with observations 
    or data, such as examples or direct experience, to look for patterns 
    and make better decisions in the future.
    """
    
    keywords = ['algorithm', 'data', 'model', 'training', 'prediction', 
                'pattern', 'artificial intelligence', 'learning']
    
    # Method 1: Using convenience function
    json_result = evaluate_answer(question, answer, keywords)
    
    print("\n📋 JSON Output (formatted):")
    print(json_result)
    
    # Method 2: Parse JSON for programmatic use
    result_dict = json.loads(json_result)
    print(f"\n📊 Parsed from JSON:")
    print(f"   Overall Score: {result_dict['overall_score']}")
    print(f"   Grade: {result_dict['grade']}")


def example_6_batch_evaluation():
    """
    Example 6: Batch Evaluation of Multiple Answers
    
    Evaluating multiple Q&A pairs in a loop.
    """
    print_separator("EXAMPLE 6: BATCH EVALUATION")
    
    # Sample interview Q&A pairs
    interview_qa = [
        {
            "question": "What is your greatest strength?",
            "answer": "My greatest strength is problem-solving. I enjoy analyzing complex issues and breaking them down into manageable parts. In my previous role, I identified a bottleneck in our deployment pipeline and implemented a solution that reduced deployment time by 60%."
        },
        {
            "question": "Why do you want to work here?",
            "answer": "I want to work here because your company is a leader in AI technology. I'm excited about the opportunity to contribute to innovative projects and learn from talented engineers."
        },
        {
            "question": "What is polymorphism in OOP?",
            "answer": "Polymorphism means many forms. It allows objects of different classes to be treated as objects of a common parent class. For example, a Shape class can have Circle and Rectangle subclasses, each implementing their own draw method."
        }
    ]
    
    evaluator = AnswerEvaluator()
    results = []
    
    print("\n📊 Batch Evaluation Results:\n")
    print(f"{'#':<3} {'Question':<40} {'Score':<8} {'Grade':<6}")
    print("-" * 60)
    
    for i, qa in enumerate(interview_qa, 1):
        result = evaluator.evaluate(qa['question'], qa['answer'])
        results.append(result)
        
        # Truncate question for display
        q_display = qa['question'][:37] + "..." if len(qa['question']) > 40 else qa['question']
        print(f"{i:<3} {q_display:<40} {result.overall_score:<8.1f} {result.grade:<6}")
    
    # Calculate average
    avg_score = sum(r.overall_score for r in results) / len(results)
    print("-" * 60)
    print(f"{'AVG':<3} {'Overall Performance':<40} {avg_score:<8.1f}")


def run_all_examples():
    """Run all example demonstrations."""
    print("\n" + "🚀" * 35)
    print("\n   NLP ANSWER EVALUATION MODULE - DEMO")
    print("\n" + "🚀" * 35)
    
    example_1_basic_evaluation()
    example_2_technical_interview()
    example_3_behavioral_interview()
    example_4_poor_answer_evaluation()
    example_5_json_output()
    example_6_batch_evaluation()
    
    print_separator("DEMO COMPLETE")
    print("\n✅ All examples completed successfully!")
    print("\n📚 Next Steps:")
    print("   1. Install optional dependencies for better accuracy:")
    print("      pip install nltk language-tool-python sentence-transformers")
    print("   2. Customize scoring weights in scoring_config.py")
    print("   3. Add domain-specific keywords for your use case")
    print("   4. Integrate with your interview system API\n")


if __name__ == "__main__":
    run_all_examples()
