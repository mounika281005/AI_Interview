"""
==============================================================================
AI Mock Interview System - Question Generation Service
==============================================================================

Generates interview questions using AI (OpenAI GPT or Google Generative AI).

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import json
import random
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from app.config import settings

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
class GeneratedQuestion:
    """Represents a generated interview question."""
    question_text: str
    category: str
    difficulty: str
    expected_topics: List[str]
    time_limit: int  # in seconds
    follow_up_questions: List[str]
    ideal_answer: str = ""  # Expected/ideal answer for evaluation


# =============================================================================
# QUESTION TEMPLATES (Fallback)
# =============================================================================

QUESTION_TEMPLATES = {
    "behavioral": [
        "Tell me about a time when you {scenario}. How did you handle it?",
        "Describe a situation where you had to {scenario}. What was the outcome?",
        "Give me an example of when you {scenario}. What did you learn?",
    ],
    "technical": [
        "Explain how you would {technical_task} using {technology}.",
        "What is your approach to {technical_concept}? Can you explain with an example?",
        "How would you design {system_component}? Walk me through your thought process.",
    ],
    "situational": [
        "If you were faced with {situation}, how would you handle it?",
        "Imagine you are {scenario}. What steps would you take?",
        "What would you do if {challenge}?",
    ],
    "hr": [
        "What are your salary expectations for this {role} position?",
        "Why are you looking to leave your current position?",
        "Where do you see yourself in the next 5 years?",
        "What motivates you to apply for this {role} role?",
        "How do you handle work-life balance?",
        "What kind of work culture do you thrive in?",
        "Why should we hire you over other candidates?",
        "What are your strengths and weaknesses?",
        "Tell me about yourself and why you're a good fit for this role.",
        "Do you have any questions for us about the company or team?",
    ],
}

BEHAVIORAL_SCENARIOS = [
    "faced a tight deadline",
    "dealt with a difficult team member",
    "had to learn a new technology quickly",
    "made a mistake at work",
    "had to prioritize multiple tasks",
    "disagreed with your manager",
    "led a team project",
    "resolved a conflict",
    "went above and beyond",
    "received constructive criticism",
]

# =============================================================================
# TECHNOLOGY-SPECIFIC QUESTION BANKS
# =============================================================================

TECHNOLOGY_QUESTIONS = {
    "Python": [
        {"question": "What are Python decorators and how do you use them? Give an example.", "keywords": ["decorator", "wrapper", "function", "@", "syntax"], "ideal": "Decorators are functions that modify the behavior of other functions. They use the @ syntax and wrap the original function to add functionality like logging, authentication, or caching."},
        {"question": "Explain the difference between lists and tuples in Python.", "keywords": ["mutable", "immutable", "list", "tuple", "performance"], "ideal": "Lists are mutable (can be changed), while tuples are immutable (cannot be changed after creation). Tuples are faster and use less memory. Use tuples for fixed data, lists for dynamic collections."},
        {"question": "What is the Global Interpreter Lock (GIL) in Python?", "keywords": ["GIL", "threading", "concurrency", "CPython", "multiprocessing"], "ideal": "The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode simultaneously. For CPU-bound tasks, use multiprocessing instead of threading."},
        {"question": "How does memory management work in Python?", "keywords": ["garbage collection", "reference counting", "memory", "del", "gc module"], "ideal": "Python uses automatic memory management with reference counting and a cyclic garbage collector. Objects are deallocated when their reference count drops to zero."},
        {"question": "Explain list comprehensions and when to use them.", "keywords": ["list comprehension", "for loop", "filter", "map", "readable"], "ideal": "List comprehensions are a concise way to create lists using a single line of code. They are faster than traditional for loops and should be used for simple transformations and filtering."},
        {"question": "What are *args and **kwargs in Python?", "keywords": ["args", "kwargs", "arguments", "positional", "keyword"], "ideal": "*args allows passing variable number of positional arguments as a tuple. **kwargs allows passing variable number of keyword arguments as a dictionary. They provide flexibility in function definitions."},
        {"question": "Explain Python generators and their benefits.", "keywords": ["generator", "yield", "iterator", "memory efficient", "lazy evaluation"], "ideal": "Generators are functions that use yield to return values one at a time, implementing lazy evaluation. They are memory-efficient for large datasets as they don't store all values in memory."},
        {"question": "What is the difference between deep copy and shallow copy?", "keywords": ["deep copy", "shallow copy", "reference", "nested objects", "copy module"], "ideal": "Shallow copy creates a new object but references the same nested objects. Deep copy creates completely independent copies of all nested objects. Use copy.deepcopy() for deep copies."},
    ],
    "JavaScript": [
        {"question": "Explain the difference between var, let, and const.", "keywords": ["var", "let", "const", "hoisting", "scope", "block"], "ideal": "var is function-scoped and hoisted. let is block-scoped and not hoisted. const is block-scoped, not hoisted, and cannot be reassigned. Prefer const, then let, avoid var."},
        {"question": "What is the event loop in JavaScript?", "keywords": ["event loop", "call stack", "callback queue", "async", "non-blocking"], "ideal": "The event loop continuously checks if the call stack is empty and moves callbacks from the queue to the stack. It enables JavaScript's non-blocking, asynchronous behavior."},
        {"question": "Explain closures in JavaScript with an example.", "keywords": ["closure", "scope", "lexical", "function", "encapsulation"], "ideal": "A closure is a function that has access to its outer function's variables even after the outer function has returned. It's created every time a function is created."},
        {"question": "What is the difference between == and === in JavaScript?", "keywords": ["equality", "strict", "type coercion", "comparison"], "ideal": "== performs type coercion before comparison (loose equality). === checks both value and type without coercion (strict equality). Always prefer === to avoid unexpected behavior."},
        {"question": "Explain promises and async/await in JavaScript.", "keywords": ["promise", "async", "await", "then", "catch", "asynchronous"], "ideal": "Promises represent eventual completion of async operations. async/await is syntactic sugar over promises, making async code look synchronous and easier to read."},
        {"question": "What is hoisting in JavaScript?", "keywords": ["hoisting", "declaration", "var", "function", "temporal dead zone"], "ideal": "Hoisting moves variable and function declarations to the top of their scope during compilation. var declarations are hoisted, but let/const have a temporal dead zone."},
        {"question": "Explain the 'this' keyword in JavaScript.", "keywords": ["this", "context", "bind", "call", "apply", "arrow function"], "ideal": "this refers to the object that is executing the current function. Its value depends on how the function is called. Arrow functions don't have their own this."},
        {"question": "What are higher-order functions in JavaScript?", "keywords": ["higher-order", "callback", "map", "filter", "reduce"], "ideal": "Higher-order functions take functions as arguments or return functions. Examples include map, filter, reduce. They enable functional programming patterns."},
    ],
    "React": [
        {"question": "What is the Virtual DOM and how does it work?", "keywords": ["virtual DOM", "reconciliation", "diffing", "performance", "real DOM"], "ideal": "Virtual DOM is an in-memory representation of the real DOM. React compares virtual DOM changes (diffing) and updates only the changed parts in the real DOM (reconciliation)."},
        {"question": "Explain the difference between state and props.", "keywords": ["state", "props", "mutable", "immutable", "component", "data flow"], "ideal": "Props are read-only data passed from parent to child. State is mutable data managed within a component. Props flow down, state is internal."},
        {"question": "What are React hooks? Name some commonly used hooks.", "keywords": ["hooks", "useState", "useEffect", "useContext", "functional components"], "ideal": "Hooks let you use state and lifecycle features in functional components. Common hooks: useState (state), useEffect (side effects), useContext (context), useRef, useMemo."},
        {"question": "Explain the useEffect hook and its cleanup function.", "keywords": ["useEffect", "side effects", "cleanup", "dependencies", "lifecycle"], "ideal": "useEffect handles side effects like API calls, subscriptions. The cleanup function runs before the next effect or on unmount. Dependencies array controls when it runs."},
        {"question": "What is prop drilling and how can you avoid it?", "keywords": ["prop drilling", "context", "state management", "Redux", "composition"], "ideal": "Prop drilling is passing props through multiple levels of components. Avoid it using Context API, Redux, or component composition patterns."},
        {"question": "Explain React component lifecycle methods.", "keywords": ["lifecycle", "mounting", "updating", "unmounting", "useEffect"], "ideal": "Class components have lifecycle methods: componentDidMount, componentDidUpdate, componentWillUnmount. In functional components, useEffect replaces these."},
        {"question": "What is the purpose of keys in React lists?", "keywords": ["key", "list", "reconciliation", "unique", "performance"], "ideal": "Keys help React identify which items changed, added, or removed in lists. They should be stable, unique identifiers. Don't use array index as key if list can reorder."},
        {"question": "How do you optimize React application performance?", "keywords": ["memo", "useMemo", "useCallback", "lazy loading", "virtualization"], "ideal": "Use React.memo for component memoization, useMemo/useCallback for values/functions, lazy loading with Suspense, virtualization for long lists, avoid unnecessary re-renders."},
    ],
    "Java": [
        {"question": "Explain the difference between JDK, JRE, and JVM.", "keywords": ["JDK", "JRE", "JVM", "bytecode", "compiler"], "ideal": "JVM executes bytecode. JRE includes JVM plus libraries for running Java apps. JDK includes JRE plus development tools like compiler and debugger."},
        {"question": "What is the difference between abstract class and interface?", "keywords": ["abstract", "interface", "implementation", "multiple inheritance", "default methods"], "ideal": "Abstract classes can have state and partial implementation. Interfaces define contracts with no state (before Java 8). Classes can implement multiple interfaces but extend only one class."},
        {"question": "Explain Java's garbage collection mechanism.", "keywords": ["garbage collection", "heap", "GC roots", "generations", "memory"], "ideal": "GC automatically frees memory of unreachable objects. It uses generational collection (Young, Old, Permanent). Objects are tracked from GC roots."},
        {"question": "What are the SOLID principles in Java?", "keywords": ["SOLID", "Single Responsibility", "Open-Closed", "Liskov", "Interface Segregation", "Dependency Inversion"], "ideal": "SOLID: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. They guide object-oriented design for maintainable code."},
        {"question": "Explain the difference between == and equals() in Java.", "keywords": ["equals", "reference", "value", "hashCode", "String"], "ideal": "== compares references (memory addresses). equals() compares values (content). For objects like String, use equals() for content comparison. Override equals() with hashCode()."},
        {"question": "What is multithreading in Java? How do you create threads?", "keywords": ["thread", "Runnable", "synchronized", "concurrent", "executor"], "ideal": "Multithreading allows concurrent execution. Create threads by extending Thread class or implementing Runnable. Use synchronized for thread safety, ExecutorService for thread pools."},
        {"question": "Explain exception handling in Java.", "keywords": ["try", "catch", "finally", "throw", "throws", "checked", "unchecked"], "ideal": "Use try-catch to handle exceptions. finally always executes. Checked exceptions must be declared/handled. Unchecked (RuntimeException) don't require explicit handling."},
        {"question": "What are Java Collections? Explain the hierarchy.", "keywords": ["Collection", "List", "Set", "Map", "ArrayList", "HashMap"], "ideal": "Collections framework provides data structures. Collection interface has List (ordered, duplicates), Set (unique). Map stores key-value pairs. Common: ArrayList, HashSet, HashMap."},
    ],
    "SQL": [
        {"question": "What is the difference between WHERE and HAVING clauses?", "keywords": ["WHERE", "HAVING", "GROUP BY", "aggregate", "filter"], "ideal": "WHERE filters rows before grouping, cannot use aggregates. HAVING filters groups after GROUP BY, used with aggregate functions like COUNT, SUM."},
        {"question": "Explain different types of JOINs in SQL.", "keywords": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "CROSS JOIN"], "ideal": "INNER JOIN returns matching rows from both tables. LEFT JOIN returns all from left + matches. RIGHT JOIN returns all from right + matches. FULL JOIN returns all rows from both."},
        {"question": "What is database normalization? Explain normal forms.", "keywords": ["normalization", "1NF", "2NF", "3NF", "redundancy", "dependency"], "ideal": "Normalization reduces data redundancy. 1NF: atomic values. 2NF: no partial dependencies. 3NF: no transitive dependencies. Higher forms exist but 3NF is commonly sufficient."},
        {"question": "What are indexes and how do they improve performance?", "keywords": ["index", "B-tree", "performance", "query optimization", "primary key"], "ideal": "Indexes are data structures that speed up data retrieval. They work like a book index. Trade-off: faster reads, slower writes. Use on frequently queried columns."},
        {"question": "Explain ACID properties in database transactions.", "keywords": ["ACID", "Atomicity", "Consistency", "Isolation", "Durability"], "ideal": "ACID ensures reliable transactions. Atomicity: all or nothing. Consistency: valid state. Isolation: concurrent transactions don't interfere. Durability: committed data persists."},
        {"question": "What is the difference between DELETE, TRUNCATE, and DROP?", "keywords": ["DELETE", "TRUNCATE", "DROP", "rollback", "DDL", "DML"], "ideal": "DELETE removes rows (DML, can rollback, fires triggers). TRUNCATE removes all rows (DDL, faster, resets identity). DROP removes entire table structure."},
        {"question": "Explain primary key and foreign key constraints.", "keywords": ["primary key", "foreign key", "constraint", "referential integrity", "unique"], "ideal": "Primary key uniquely identifies rows (unique, not null). Foreign key references primary key of another table, enforcing referential integrity between tables."},
        {"question": "What are stored procedures and their advantages?", "keywords": ["stored procedure", "performance", "security", "reusability", "SQL"], "ideal": "Stored procedures are precompiled SQL statements stored in database. Advantages: better performance (cached), security (controlled access), reusability, reduced network traffic."},
    ],
    "Data Structures & Algorithms": [
        {"question": "Explain the difference between Array and LinkedList.", "keywords": ["array", "linked list", "memory", "access time", "insertion"], "ideal": "Arrays have O(1) random access but O(n) insertion/deletion. LinkedLists have O(n) access but O(1) insertion/deletion at known positions. Arrays use contiguous memory."},
        {"question": "What is the time complexity of common sorting algorithms?", "keywords": ["sorting", "O(n log n)", "QuickSort", "MergeSort", "BubbleSort"], "ideal": "BubbleSort: O(n²). QuickSort: O(n log n) average, O(n²) worst. MergeSort: O(n log n) always. HeapSort: O(n log n). Counting/Radix: O(n) for specific cases."},
        {"question": "Explain how a hash table works.", "keywords": ["hash table", "hash function", "collision", "O(1)", "bucket"], "ideal": "Hash tables use a hash function to compute index for key-value pairs. Provides O(1) average lookup. Collisions handled by chaining or open addressing."},
        {"question": "What is the difference between BFS and DFS?", "keywords": ["BFS", "DFS", "queue", "stack", "graph", "traversal"], "ideal": "BFS uses a queue, explores level by level (shortest path). DFS uses stack/recursion, goes deep first. BFS: O(V+E) space for queue. DFS: O(V) for recursion stack."},
        {"question": "Explain the concept of dynamic programming.", "keywords": ["dynamic programming", "memoization", "tabulation", "subproblems", "optimal"], "ideal": "DP solves complex problems by breaking into overlapping subproblems. Memoization (top-down) caches results. Tabulation (bottom-up) builds solution iteratively."},
        {"question": "What is a binary search tree and its operations?", "keywords": ["BST", "binary search", "insert", "delete", "O(log n)"], "ideal": "BST is a tree where left children are smaller, right are larger. Operations (search, insert, delete) are O(log n) average, O(n) worst for unbalanced trees."},
        {"question": "Explain the difference between Stack and Queue.", "keywords": ["stack", "queue", "LIFO", "FIFO", "push", "pop"], "ideal": "Stack is LIFO (Last In First Out) - push/pop from top. Queue is FIFO (First In First Out) - enqueue at rear, dequeue from front. Both have O(1) operations."},
        {"question": "What is Big O notation and why is it important?", "keywords": ["Big O", "time complexity", "space complexity", "algorithm", "scalability"], "ideal": "Big O describes algorithm efficiency as input grows. It measures worst-case time/space complexity. Important for choosing algorithms that scale well with large inputs."},
    ],
    "Machine Learning": [
        {"question": "Explain the difference between supervised and unsupervised learning.", "keywords": ["supervised", "unsupervised", "labeled", "clustering", "classification"], "ideal": "Supervised learning uses labeled data to predict outcomes (classification, regression). Unsupervised learning finds patterns in unlabeled data (clustering, dimensionality reduction)."},
        {"question": "What is overfitting and how do you prevent it?", "keywords": ["overfitting", "regularization", "cross-validation", "dropout", "generalization"], "ideal": "Overfitting is when a model learns noise instead of patterns, performing well on training but poorly on test data. Prevent with regularization, cross-validation, more data, dropout."},
        {"question": "Explain the bias-variance tradeoff.", "keywords": ["bias", "variance", "tradeoff", "underfitting", "overfitting"], "ideal": "High bias = underfitting (simple model). High variance = overfitting (complex model). Goal is to find balance that minimizes total error on unseen data."},
        {"question": "What is cross-validation and why is it used?", "keywords": ["cross-validation", "k-fold", "training", "validation", "generalization"], "ideal": "Cross-validation splits data into k folds, training on k-1 and validating on 1, rotating through all folds. It provides reliable estimate of model performance on unseen data."},
        {"question": "Explain gradient descent and its variants.", "keywords": ["gradient descent", "learning rate", "SGD", "batch", "mini-batch"], "ideal": "Gradient descent optimizes by moving in direction of steepest descent. Variants: Batch (all data), SGD (one sample), Mini-batch (subset). Learning rate controls step size."},
        {"question": "What is the difference between precision and recall?", "keywords": ["precision", "recall", "F1 score", "true positive", "false positive"], "ideal": "Precision = TP/(TP+FP) - accuracy of positive predictions. Recall = TP/(TP+FN) - coverage of actual positives. F1 score is harmonic mean of both."},
        {"question": "Explain how decision trees work.", "keywords": ["decision tree", "split", "entropy", "Gini", "pruning"], "ideal": "Decision trees split data based on features to make predictions. Splits chosen to maximize information gain (reduce entropy) or minimize Gini impurity. Pruning prevents overfitting."},
        {"question": "What is feature engineering and why is it important?", "keywords": ["feature engineering", "feature selection", "transformation", "domain knowledge"], "ideal": "Feature engineering creates/transforms features to improve model performance. It uses domain knowledge to extract meaningful information. Often more impactful than algorithm choice."},
    ],
    "AWS": [
        {"question": "Explain the difference between EC2 and Lambda.", "keywords": ["EC2", "Lambda", "serverless", "scaling", "virtual machine"], "ideal": "EC2 provides virtual machines you manage (OS, scaling). Lambda is serverless - runs code on events, auto-scales, pay per execution. Lambda for short tasks, EC2 for long-running."},
        {"question": "What is S3 and what are its storage classes?", "keywords": ["S3", "storage", "Standard", "Glacier", "bucket", "object"], "ideal": "S3 is object storage service. Classes: Standard (frequent access), Intelligent-Tiering (auto-optimize), Glacier (archive). Objects stored in buckets with unique keys."},
        {"question": "Explain VPC and its components.", "keywords": ["VPC", "subnet", "security group", "NACL", "internet gateway"], "ideal": "VPC is isolated virtual network. Components: subnets (public/private), security groups (instance firewall), NACLs (subnet firewall), internet gateway, NAT gateway."},
        {"question": "What is the difference between RDS and DynamoDB?", "keywords": ["RDS", "DynamoDB", "relational", "NoSQL", "managed"], "ideal": "RDS is managed relational database (MySQL, PostgreSQL). DynamoDB is managed NoSQL (key-value, document). RDS for complex queries, DynamoDB for high-scale simple queries."},
        {"question": "Explain IAM roles and policies.", "keywords": ["IAM", "role", "policy", "permission", "least privilege"], "ideal": "IAM manages access to AWS resources. Policies define permissions (JSON). Roles are assumed by services/users. Follow least privilege principle - grant minimum required permissions."},
        {"question": "What is CloudFormation and Infrastructure as Code?", "keywords": ["CloudFormation", "IaC", "template", "stack", "automation"], "ideal": "CloudFormation is AWS IaC service. Define infrastructure in YAML/JSON templates. Creates/updates stacks of resources. Enables version control, repeatability, automation."},
        {"question": "Explain auto-scaling in AWS.", "keywords": ["auto-scaling", "scaling policy", "load balancer", "target tracking", "health check"], "ideal": "Auto-scaling adjusts EC2 capacity based on demand. Uses scaling policies (target tracking, step, simple). Works with load balancers. Monitors metrics like CPU, requests."},
        {"question": "What is the AWS Well-Architected Framework?", "keywords": ["Well-Architected", "pillars", "reliability", "security", "cost optimization"], "ideal": "Framework with 5 pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization. Guides building secure, high-performing, resilient applications."},
    ],
    "Node.js": [
        {"question": "Explain the Node.js event loop.", "keywords": ["event loop", "non-blocking", "callbacks", "libuv", "single thread"], "ideal": "Event loop handles async operations on a single thread. Uses libuv for I/O. Phases: timers, pending callbacks, poll, check, close. Enables non-blocking I/O."},
        {"question": "What is the difference between require and import?", "keywords": ["require", "import", "CommonJS", "ES modules", "module"], "ideal": "require is CommonJS (synchronous, dynamic). import is ES modules (static, async, tree-shakeable). Node.js supports both. Use import for modern projects."},
        {"question": "Explain middleware in Express.js.", "keywords": ["middleware", "Express", "next", "request", "response"], "ideal": "Middleware functions have access to req, res, next. They execute in order, can modify request/response, end cycle, or call next(). Used for logging, auth, parsing."},
        {"question": "What is npm and package.json?", "keywords": ["npm", "package.json", "dependencies", "scripts", "node_modules"], "ideal": "npm is Node package manager. package.json defines project metadata, dependencies, scripts. npm install reads it to install packages to node_modules."},
        {"question": "Explain streams in Node.js.", "keywords": ["stream", "readable", "writable", "pipe", "buffer"], "ideal": "Streams handle data in chunks, not loading all into memory. Types: Readable, Writable, Duplex, Transform. Use pipe() to connect streams. Efficient for large files."},
        {"question": "What is the purpose of process.nextTick()?", "keywords": ["nextTick", "microtask", "event loop", "setImmediate", "async"], "ideal": "process.nextTick() queues callback to run after current operation, before event loop continues. Higher priority than setImmediate. Use carefully to avoid blocking."},
        {"question": "How do you handle errors in Node.js?", "keywords": ["error handling", "try-catch", "callback", "promise", "uncaughtException"], "ideal": "Use try-catch for sync code, .catch() for promises, error-first callbacks. Handle uncaughtException and unhandledRejection events. Use error middleware in Express."},
        {"question": "Explain clustering in Node.js.", "keywords": ["cluster", "worker", "master", "CPU cores", "load balancing"], "ideal": "Cluster module forks multiple worker processes to utilize all CPU cores. Master manages workers. Built-in load balancing. Each worker runs on separate thread."},
    ],
    "Docker": [
        {"question": "What is Docker and how does it differ from virtual machines?", "keywords": ["Docker", "container", "VM", "lightweight", "kernel"], "ideal": "Docker uses containers sharing host kernel (lightweight, fast). VMs include full OS (heavier, isolated). Containers are portable, start in seconds, use less resources."},
        {"question": "Explain Dockerfile and its common instructions.", "keywords": ["Dockerfile", "FROM", "RUN", "COPY", "CMD", "ENTRYPOINT"], "ideal": "Dockerfile builds images. FROM: base image. RUN: execute commands. COPY/ADD: add files. WORKDIR: set directory. CMD: default command. ENTRYPOINT: main executable."},
        {"question": "What is the difference between CMD and ENTRYPOINT?", "keywords": ["CMD", "ENTRYPOINT", "override", "arguments", "executable"], "ideal": "ENTRYPOINT defines main executable (hard to override). CMD provides default arguments (easily overridden). Best practice: ENTRYPOINT for command, CMD for default args."},
        {"question": "Explain Docker volumes and bind mounts.", "keywords": ["volume", "bind mount", "persistent", "data", "storage"], "ideal": "Volumes are managed by Docker, persist data outside containers. Bind mounts link host directory to container. Volumes preferred for production, bind mounts for development."},
        {"question": "What is Docker Compose and when do you use it?", "keywords": ["Docker Compose", "multi-container", "YAML", "services", "network"], "ideal": "Compose defines multi-container apps in YAML. Manages services, networks, volumes together. Use docker-compose up to start all. Ideal for development and testing."},
        {"question": "Explain Docker networking modes.", "keywords": ["network", "bridge", "host", "none", "overlay"], "ideal": "Bridge: default, containers on private network. Host: uses host network directly. None: no networking. Overlay: multi-host communication for Swarm/Kubernetes."},
        {"question": "What are multi-stage builds in Docker?", "keywords": ["multi-stage", "build", "image size", "FROM", "COPY --from"], "ideal": "Multi-stage uses multiple FROM instructions. Build in one stage, copy artifacts to final stage. Reduces image size by excluding build tools from final image."},
        {"question": "How do you optimize Docker image size?", "keywords": ["optimize", "alpine", "layer", ".dockerignore", "multi-stage"], "ideal": "Use small base images (alpine). Combine RUN commands. Use multi-stage builds. Add .dockerignore. Remove unnecessary files. Order commands for layer caching."},
    ],
}

# Default questions for technologies not in the bank
DEFAULT_TECHNICAL_QUESTIONS = [
    {"question": "Explain the core concepts of {technology}.", "keywords": ["fundamentals", "concepts", "basics"], "ideal": "Explain the fundamental principles, key features, and main use cases of the technology."},
    {"question": "What are the best practices when working with {technology}?", "keywords": ["best practices", "patterns", "guidelines"], "ideal": "Follow established patterns, write clean code, handle errors properly, and document your work."},
    {"question": "Describe a project where you used {technology}.", "keywords": ["project", "experience", "implementation"], "ideal": "Describe the project scope, your role, challenges faced, and how you used the technology to solve problems."},
    {"question": "How do you debug issues in {technology}?", "keywords": ["debugging", "troubleshooting", "problem-solving"], "ideal": "Use logging, debuggers, read error messages carefully, isolate the problem, and test fixes incrementally."},
    {"question": "What are common mistakes to avoid when using {technology}?", "keywords": ["mistakes", "pitfalls", "anti-patterns"], "ideal": "Avoid common anti-patterns, don't ignore errors, follow security best practices, and keep dependencies updated."},
]


# =============================================================================
# QUESTION GENERATOR SERVICE
# =============================================================================

class QuestionGeneratorService:
    """
    Service for generating interview questions using AI.
    
    Supports OpenAI GPT and provides fallback templates for offline use.
    
    Usage:
        generator = QuestionGeneratorService()
        questions = await generator.generate_questions(
            role="Software Engineer",
            skills=["Python", "FastAPI", "PostgreSQL"],
            experience_years=3
        )
    """
    
    def __init__(self):
        """Initialize the question generator service."""
        self.ai_provider = settings.ai_provider
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the AI client based on provider."""
        if self.ai_provider == "openai":
            try:
                import openai
                if settings.openai_api_key:
                    openai.api_key = settings.openai_api_key
                    self.client = openai
                    logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.warning("OpenAI package not installed, using fallback")
        
        elif self.ai_provider == "google":
            try:
                import google.generativeai as genai
                if settings.google_api_key:
                    genai.configure(api_key=settings.google_api_key)
                    self.client = genai.GenerativeModel('gemini-pro')
                    logger.info("Google Generative AI client initialized successfully")
            except ImportError:
                logger.warning("Google Generative AI package not installed, using fallback")
        
        elif self.ai_provider == "huggingface":
            if settings.huggingface_api_key:
                self.client = "huggingface"  # We'll use requests directly
                logger.info("Hugging Face API initialized successfully")
    
    async def generate_questions(
        self,
        role: str,
        skills: List[str],
        experience_years: int,
        difficulty: str = "medium",
        num_questions: int = 5,
        categories: Optional[List[str]] = None
    ) -> List[GeneratedQuestion]:
        """
        Generate interview questions based on profile.
        
        Args:
            role: Target job role (e.g., "Software Engineer")
            skills: List of technical skills
            experience_years: Years of experience
            difficulty: Question difficulty (easy, medium, hard)
            num_questions: Number of questions to generate
            categories: Question categories to include
        
        Returns:
            List of GeneratedQuestion objects
        """
        debug_log("=== GENERATE QUESTIONS ===")
        debug_log("Input params", {
            "role": role,
            "skills": skills,
            "experience_years": experience_years,
            "difficulty": difficulty,
            "num_questions": num_questions,
            "categories": categories
        })
        
        if categories is None:
            categories = ["behavioral", "technical", "situational"]

        # Check if profile is incomplete — use HR fallback prompt
        if self._is_profile_incomplete(skills, experience_years):
            debug_log("Profile is incomplete — using HR fallback prompt")
            if self.client:
                try:
                    prompt = self._create_hr_fallback_prompt(
                        role, skills, difficulty, num_questions
                    )
                    if self.ai_provider == "openai":
                        result = await self._generate_openai(prompt, num_questions)
                    elif self.ai_provider == "google":
                        result = await self._generate_google(prompt, num_questions)
                    elif self.ai_provider == "huggingface":
                        result = await self._generate_huggingface(prompt, num_questions)
                    else:
                        raise ValueError(f"Unknown AI provider: {self.ai_provider}")
                    debug_log("HR fallback AI generation succeeded", {"count": len(result)})
                    return result
                except Exception as e:
                    debug_log("HR fallback AI generation FAILED", str(e))
                    logger.error(f"HR fallback AI generation failed: {e}, using templates")
            # Fallback to HR + behavioral templates for incomplete profiles
            return self._generate_from_templates(
                role, skills or [], experience_years,
                difficulty, num_questions, ["hr", "behavioral"]
            )

        # Try AI generation first
        if self.client:
            try:
                debug_log("Attempting AI generation...")
                result = await self._generate_with_ai(
                    role, skills, experience_years,
                    difficulty, num_questions, categories
                )
                debug_log("AI generation succeeded", {"count": len(result)})
                return result
            except Exception as e:
                debug_log("AI generation FAILED", str(e))
                logger.error(f"AI generation failed: {e}, using fallback")

        # Fallback to template-based generation
        debug_log("Using template-based fallback...")
        result = self._generate_from_templates(
            role, skills, experience_years,
            difficulty, num_questions, categories
        )
        debug_log("Template generation completed", {"count": len(result)})
        return result
    
    async def _generate_with_ai(
        self,
        role: str,
        skills: List[str],
        experience_years: int,
        difficulty: str,
        num_questions: int,
        categories: List[str]
    ) -> List[GeneratedQuestion]:
        """Generate questions using AI provider."""
        
        prompt = self._create_prompt(
            role, skills, experience_years,
            difficulty, num_questions, categories
        )
        
        if self.ai_provider == "openai":
            return await self._generate_openai(prompt, num_questions)
        elif self.ai_provider == "google":
            return await self._generate_google(prompt, num_questions)
        elif self.ai_provider == "huggingface":
            return await self._generate_huggingface(prompt, num_questions)
        
        raise ValueError(f"Unknown AI provider: {self.ai_provider}")
    
    def _build_candidate_json(
        self,
        role: str,
        skills: List[str],
        experience_years: int,
        difficulty: str,
        num_questions: int,
        categories: List[str],
        projects: Optional[List[Dict]] = None,
        work_experience: Optional[List[Dict]] = None,
        education: Optional[List[Dict]] = None,
        summary: Optional[str] = None
    ) -> str:
        """Build candidate profile JSON for the AI prompt."""
        candidate = {
            "role": role,
            "skills": skills if skills else [],
            "experience_years": experience_years,
            "difficulty": difficulty,
            "num_questions": num_questions,
            "categories": categories
        }

        if projects:
            candidate["projects"] = [
                {"name": p.get("name", ""), "description": p.get("description", "")[:200]}
                for p in projects[:5]
            ]

        if work_experience:
            candidate["work_experience"] = [
                {
                    "title": e.get("title", ""),
                    "company": e.get("company", ""),
                    "duration": e.get("duration", "")
                }
                for e in work_experience[:5]
            ]

        if education:
            candidate["education"] = [
                {"degree": e.get("degree", ""), "institution": e.get("institution", "")}
                for e in education[:3]
            ]

        if summary:
            candidate["summary"] = summary[:300]

        return json.dumps(candidate, indent=2)

    def _is_profile_incomplete(
        self,
        skills: List[str],
        experience_years: int = 0,
        work_experience: Optional[List[Dict]] = None,
        projects: Optional[List[Dict]] = None,
    ) -> bool:
        """Check if the candidate profile is too incomplete for a full technical interview.

        Returns True when skills are empty/minimal AND there is no meaningful
        work experience or project data to generate questions from.
        """
        has_skills = bool(skills and len(skills) >= 1)
        has_work = bool(work_experience and len(work_experience) >= 1)
        has_projects = bool(projects and len(projects) >= 1)

        # Profile is incomplete when we have almost nothing to work with
        if not has_skills and not has_work and not has_projects:
            return True

        # Only 1 skill and nothing else — still very thin
        if len(skills or []) <= 1 and not has_work and not has_projects and experience_years == 0:
            return True

        return False

    def _create_hr_fallback_prompt(
        self,
        role: str,
        skills: List[str],
        difficulty: str,
        num_questions: int,
    ) -> str:
        """Create the HR interviewer fallback prompt for incomplete profiles."""
        skills_str = ", ".join(skills) if skills else "none provided"

        prompt = f"""You are an HR interviewer.
The candidate profile is incomplete.
Ask general aptitude and basic technical questions based only on available skills.
Do not mention missing information.
Return {num_questions} questions in JSON array.

Available skills: {skills_str}
Target role: {role}
Difficulty: {difficulty}

Each question object must have these fields:
- question_text: string (the interview question)
- category: string (one of: hr, behavioral, technical)
- difficulty: string ({difficulty})
- expected_topics: array of strings (3-5 keywords the answer should cover)
- time_limit: number (seconds, 60-120)
- follow_up_questions: array of strings (2-3 follow-ups)
- ideal_answer: string (brief outline of what a good answer includes)

Rules:
- Ask general aptitude questions (logical thinking, problem-solving, communication)
- If skills are available, ask basic-level technical questions about them
- Include behavioral/HR questions about motivation, teamwork, adaptability
- Keep questions at an introductory level since the profile is incomplete
- Do NOT assume the candidate has any experience beyond what is listed
- Do NOT mention that the profile is incomplete or that information is missing

Return ONLY a valid JSON array of question objects, no additional text."""

        return prompt

    def _create_prompt(
        self,
        role: str,
        skills: List[str],
        experience_years: int,
        difficulty: str,
        num_questions: int,
        categories: List[str]
    ) -> str:
        """Create the prompt for AI question generation."""

        candidate_json = self._build_candidate_json(
            role, skills, experience_years, difficulty, num_questions, categories
        )

        # Distribute with technical-heavy bias for resume interviews
        questions_per_cat = self._calculate_resume_category_distribution(
            num_questions, categories
        )

        # Build category descriptions for the prompt
        CATEGORY_DESCRIPTIONS = {
            "technical": "technical questions about specific skills, implementation, and coding concepts",
            "behavioral": "behavioral questions using the STAR method about teamwork, leadership, problem-solving, and past experiences",
            "situational": "situational/scenario-based questions about how the candidate would handle hypothetical workplace situations",
            "hr": "HR questions about motivation, salary expectations, career goals, culture fit, and self-awareness",
        }

        category_lines = []
        json_keys = []
        valid_categories = []
        for cat, count in questions_per_cat.items():
            if count <= 0:
                continue
            key = f"{cat}_questions"
            desc = CATEGORY_DESCRIPTIONS.get(cat, f"{cat} questions")
            category_lines.append(f"- {count} {cat} questions → {key}: {desc}")
            json_keys.append(f'  "{key}": [... {count} question objects]')
            valid_categories.append(cat)

        distribution_text = "\n".join(category_lines)
        json_body = ",\n".join(json_keys)
        valid_cats_str = ", ".join(valid_categories)

        prompt = f"""You are an expert interviewer.

Generate interview questions based ONLY on the candidate profile provided.
Do NOT assume extra experience.
Do NOT add technologies not listed in skills.

Rules:
- If experience_years = 0 → ask fresher level questions
- If experience_years 1-3 → intermediate questions
- If experience_years >3 → advanced questions

Total questions to generate: {num_questions}

Question distribution:
{distribution_text}

Each question object must have these fields:
- question_text: string (the interview question)
- category: string (MUST be one of: {valid_cats_str})
- difficulty: string ({difficulty})
- expected_topics: array of strings (3-5 keywords the answer should cover)
- time_limit: number (seconds, 60-180)
- follow_up_questions: array of strings (2-3 follow-ups)
- ideal_answer: string (brief outline of what a good answer includes)

Return JSON format:

{{
{json_body}
}}

IMPORTANT:
- Generate questions ONLY from the skills and role listed below.
- Do NOT invent or assume any skill/technology not in the profile.
- Match difficulty to experience_years strictly.
- The "category" field in EVERY question object MUST be one of: {valid_cats_str}. Do NOT use any other category value.

Candidate Profile:
{candidate_json}

Only respond with valid JSON, no additional text."""

        return prompt
    
    async def _generate_openai(
        self,
        prompt: str,
        num_questions: int
    ) -> List[GeneratedQuestion]:
        """Generate questions using OpenAI GPT."""
        import asyncio
        
        # Run synchronous call in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
        )
        
        content = response.choices[0].message.content
        return self._parse_ai_response(content)
    
    async def _generate_google(
        self,
        prompt: str,
        num_questions: int
    ) -> List[GeneratedQuestion]:
        """Generate questions using Google Generative AI."""
        import asyncio
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.generate_content(prompt)
        )
        
        content = response.text
        return self._parse_ai_response(content)
    
    async def _generate_huggingface(
        self,
        prompt: str,
        num_questions: int
    ) -> List[GeneratedQuestion]:
        """Generate questions using Hugging Face API."""
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {settings.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.huggingface_model,
            "messages": [
                {"role": "system", "content": "You are an expert technical interviewer. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                settings.huggingface_api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Hugging Face API error: {response.status} - {error_text}")
                    raise ValueError(f"Hugging Face API error: {response.status}")
                
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                return self._parse_ai_response(content)

    def _parse_ai_response(self, content: str) -> List[GeneratedQuestion]:
        """Parse AI response into GeneratedQuestion objects.

        Supports two response formats:
        1. Nested: {"technical_questions": [...], "behavioral_questions": [...], ...}
        2. Flat:   [{...}, {...}, ...]

        For nested format, the category is derived from the JSON key (e.g.
        "technical_questions" → "technical"). This ensures the category
        always matches what was requested, regardless of what the AI puts
        in the question's own "category" field.
        """
        try:
            # Try to extract JSON from response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            parsed = json.loads(content.strip())

            questions_list = []

            if isinstance(parsed, dict):
                # Nested format: {"technical_questions": [...], ...}
                # Derive category from the key name (strip "_questions" suffix)
                for key, items in parsed.items():
                    if not isinstance(items, list):
                        continue
                    # e.g. "technical_questions" → "technical",
                    #      "hr_questions" → "hr",
                    #      "behavioral_questions" → "behavioral"
                    category_name = key.replace("_questions", "")
                    for q in items:
                        if isinstance(q, dict):
                            # Force category from the key, not from the AI's field
                            questions_list.append(q | {"category": category_name})
                        elif isinstance(q, str):
                            questions_list.append({
                                "question_text": q,
                                "category": category_name
                            })
            elif isinstance(parsed, list):
                # Flat format: [{...}, {...}, ...]
                questions_list = parsed
            else:
                raise ValueError(f"Unexpected JSON structure: {type(parsed)}")

            questions = []
            for q in questions_list:
                questions.append(GeneratedQuestion(
                    question_text=q.get("question_text", ""),
                    category=q.get("category", "general"),
                    difficulty=q.get("difficulty", "medium"),
                    expected_topics=q.get("expected_topics", []),
                    time_limit=q.get("time_limit", 120),
                    follow_up_questions=q.get("follow_up_questions", []),
                    ideal_answer=q.get("ideal_answer", "")
                ))

            return questions

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise ValueError("Failed to parse AI response")
    
    def _generate_from_templates(
        self,
        role: str,
        skills: List[str],
        experience_years: int,
        difficulty: str,
        num_questions: int,
        categories: List[str]
    ) -> List[GeneratedQuestion]:
        """Generate questions using technology-specific question bank or templates (fallback)."""

        questions = []
        used_questions = set()  # Track used questions to avoid duplicates

        # Get the primary skill/technology
        primary_skill = skills[0] if skills else None

        # Calculate questions per category
        questions_per_category = {}
        total_categories = len(categories) if categories else 1
        base_per_category = num_questions // total_categories
        remainder = num_questions % total_categories

        for i, category in enumerate(categories):
            # Distribute remainder among first categories
            questions_per_category[category] = base_per_category + (1 if i < remainder else 0)

        debug_log(f"Questions per category: {questions_per_category}")

        # Generate questions for each category
        for category, count in questions_per_category.items():
            if category == "technical":
                # Generate technical questions from technology bank or defaults
                if primary_skill and primary_skill in TECHNOLOGY_QUESTIONS:
                    tech_questions = TECHNOLOGY_QUESTIONS[primary_skill].copy()
                    random.shuffle(tech_questions)

                    for q in tech_questions[:count]:
                        if len(questions) >= num_questions:
                            break
                        if q["question"] not in used_questions:
                            used_questions.add(q["question"])
                            questions.append(GeneratedQuestion(
                                question_text=q["question"],
                                category="technical",
                                difficulty=difficulty,
                                expected_topics=q["keywords"],
                                time_limit=120,
                                follow_up_questions=["Can you give a specific example?", "What are the trade-offs?"],
                                ideal_answer=q.get("ideal", "")
                            ))

                    # If not enough from bank, use default technical questions
                    if len([q for q in questions if q.category == "technical"]) < count and primary_skill:
                        default_qs = DEFAULT_TECHNICAL_QUESTIONS.copy()
                        random.shuffle(default_qs)

                        for q in default_qs:
                            if len([q for q in questions if q.category == "technical"]) >= count:
                                break
                            question_text = q["question"].format(technology=primary_skill)
                            if question_text not in used_questions:
                                used_questions.add(question_text)
                                questions.append(GeneratedQuestion(
                                    question_text=question_text,
                                    category="technical",
                                    difficulty=difficulty,
                                    expected_topics=q["keywords"] + [primary_skill] if primary_skill else q["keywords"],
                                    time_limit=120,
                                    follow_up_questions=["Can you elaborate?", "What challenges did you face?"],
                                    ideal_answer=q.get("ideal", "")
                                ))
                else:
                    # No technology-specific questions, use generic technical
                    for i in range(count):
                        if len(questions) >= num_questions:
                            break
                        question = self._generate_template_question(
                            "technical", role, skills, experience_years, difficulty
                        )
                        if question.question_text not in used_questions:
                            used_questions.add(question.question_text)
                            questions.append(question)

            else:
                # Generate behavioral, situational, or HR questions
                for i in range(count):
                    if len(questions) >= num_questions:
                        break
                    question = self._generate_template_question(
                        category, role, skills, experience_years, difficulty
                    )
                    if question.question_text not in used_questions:
                        used_questions.add(question.question_text)
                        questions.append(question)

        debug_log(f"Generated {len(questions)} questions across {len(categories)} categories")
        return questions[:num_questions]
    
    def _generate_template_question(
        self,
        category: str,
        role: str,
        skills: List[str],
        experience_years: int,
        difficulty: str
    ) -> GeneratedQuestion:
        """Generate a single question from templates."""
        
        # For technical category, try to use technology-specific questions first
        if category == "technical" and skills:
            skill = skills[0] if skills else "programming"
            
            # Check if we have specific questions for this technology
            if skill in TECHNOLOGY_QUESTIONS:
                tech_questions = TECHNOLOGY_QUESTIONS[skill]
                # Pick a random question that hasn't been used
                q = random.choice(tech_questions)
                return GeneratedQuestion(
                    question_text=q["question"],
                    category="technical",
                    difficulty=difficulty,
                    expected_topics=q["keywords"],
                    time_limit=120,
                    follow_up_questions=["Can you give a specific example?", "What are the trade-offs?"],
                    ideal_answer=q.get("ideal", "")
                )
            else:
                # Use default technical questions for unknown technologies
                q = random.choice(DEFAULT_TECHNICAL_QUESTIONS)
                return GeneratedQuestion(
                    question_text=q["question"].format(technology=skill),
                    category="technical",
                    difficulty=difficulty,
                    expected_topics=q["keywords"] + [skill],
                    time_limit=120,
                    follow_up_questions=["Can you elaborate?", "What challenges did you face?"],
                    ideal_answer=q.get("ideal", "")
                )
        
        templates = QUESTION_TEMPLATES.get(category, QUESTION_TEMPLATES["behavioral"])
        template = random.choice(templates)
        
        # Fill in template placeholders
        if category == "behavioral":
            scenario = random.choice(BEHAVIORAL_SCENARIOS)
            question_text = template.format(scenario=scenario)
            expected_topics = ["STAR method", "specific example", "outcome", "learning"]
        
        elif category == "technical":
            skill = random.choice(skills) if skills else "programming"
            question_text = template.format(
                technical_task="implement a solution",
                technology=skill,
                technical_concept=f"{skill} best practices",
                system_component="a scalable system"
            )
            expected_topics = [skill, "implementation", "best practices", "trade-offs"]
        
        elif category == "hr":
            question_text = template.format(role=role)
            expected_topics = ["career goals", "motivation", "culture fit", "self-awareness"]

        else:  # situational
            question_text = template.format(
                situation="conflicting requirements from stakeholders",
                scenario=f"the lead {role} on a critical project",
                challenge="a team member consistently missed deadlines"
            )
            expected_topics = ["problem-solving", "communication", "decision-making"]

        # Adjust time limit based on difficulty
        time_limits = {"easy": 90, "medium": 120, "hard": 180}
        time_limit = time_limits.get(difficulty, 120)
        
        # Generate follow-up questions
        follow_ups = [
            "What would you do differently next time?",
            "How did this experience change your approach?",
            "What was the most challenging part?",
        ]
        
        return GeneratedQuestion(
            question_text=question_text,
            category=category,
            difficulty=difficulty,
            expected_topics=expected_topics,
            time_limit=time_limit,
            follow_up_questions=random.sample(follow_ups, min(2, len(follow_ups)))
        )
    
    async def generate_resume_based_questions(
        self,
        resume_data: Dict[str, Any],
        role: str,
        difficulty: str = "medium",
        num_questions: int = 5,
        categories: Optional[List[str]] = None
    ) -> List[GeneratedQuestion]:
        """
        Generate interview questions based on the candidate's resume using AI.

        Creates personalized questions referencing specific experience,
        projects, and skills from the resume.

        Args:
            resume_data: Parsed resume data dictionary
            role: Target job role
            difficulty: Question difficulty
            num_questions: Number of questions to generate
            categories: Question categories to include

        Returns:
            List of personalized GeneratedQuestion objects
        """
        if categories is None:
            categories = ["technical", "behavioral", "situational"]

        # Extract resume information
        extracted_skills = resume_data.get("extracted_skills", [])
        work_experience = resume_data.get("work_experience", [])
        projects = resume_data.get("projects", [])
        education = resume_data.get("education", [])
        summary = resume_data.get("summary", "")
        years_exp = resume_data.get("total_years_experience", 0)

        # Check if resume profile is incomplete — use HR fallback
        if self._is_profile_incomplete(extracted_skills, years_exp, work_experience, projects):
            debug_log("Resume profile is incomplete — using HR fallback prompt")
            if self.client:
                try:
                    prompt = self._create_hr_fallback_prompt(
                        role, extracted_skills, difficulty, num_questions
                    )
                    if self.ai_provider == "openai":
                        result = await self._generate_openai(prompt, num_questions)
                    elif self.ai_provider == "google":
                        result = await self._generate_google(prompt, num_questions)
                    elif self.ai_provider == "huggingface":
                        result = await self._generate_huggingface(prompt, num_questions)
                    else:
                        raise ValueError(f"Unknown AI provider: {self.ai_provider}")
                    debug_log("HR fallback resume AI generation succeeded", {"count": len(result)})
                    return result
                except Exception as e:
                    debug_log("HR fallback resume AI generation FAILED", str(e))
                    logger.error(f"HR fallback resume generation failed: {e}, using templates")
            return self._generate_from_templates(
                role, extracted_skills or [], years_exp,
                difficulty, num_questions, ["hr", "behavioral"]
            )

        # Try AI generation first
        if self.client:
            try:
                debug_log("Attempting AI resume-based question generation...")
                prompt = self._create_resume_prompt(
                    resume_data, role, difficulty, num_questions,
                    categories, extracted_skills, work_experience,
                    projects, education, summary, years_exp
                )
                if self.ai_provider == "openai":
                    result = await self._generate_openai(prompt, num_questions)
                elif self.ai_provider == "google":
                    result = await self._generate_google(prompt, num_questions)
                elif self.ai_provider == "huggingface":
                    result = await self._generate_huggingface(prompt, num_questions)
                else:
                    raise ValueError(f"Unknown AI provider: {self.ai_provider}")
                debug_log("AI resume generation succeeded", {"count": len(result)})
                return result
            except Exception as e:
                debug_log("AI resume generation FAILED", str(e))
                logger.error(f"AI resume generation failed: {e}, using fallback")

        # Fallback to template-based generation
        debug_log("Using template-based fallback for resume questions...")
        questions = []
        questions_per_category = self._calculate_resume_category_distribution(
            num_questions, categories
        )

        for category, count in questions_per_category.items():
            for _ in range(count):
                q = self._generate_resume_based_question(
                    category, resume_data, extracted_skills,
                    work_experience, projects, role, difficulty
                )
                if q:
                    questions.append(q)

        return questions

    def _calculate_resume_category_distribution(
        self,
        num_questions: int,
        categories: List[str]
    ) -> Dict[str, int]:
        """
        Allocate more questions to technical category for resume interviews.

        Target: at least 60% technical questions when technical is requested.
        """
        if not categories:
            return {"technical": num_questions}

        unique_categories = []
        for cat in categories:
            if cat not in unique_categories:
                unique_categories.append(cat)

        if "technical" not in unique_categories:
            base = num_questions // len(unique_categories)
            rem = num_questions % len(unique_categories)
            return {
                cat: base + (1 if i < rem else 0)
                for i, cat in enumerate(unique_categories)
            }

        technical_target = max(1, math.ceil(num_questions * 0.6))
        technical_count = min(num_questions, technical_target)
        remaining = num_questions - technical_count

        distribution = {cat: 0 for cat in unique_categories}
        distribution["technical"] = technical_count

        non_technical = [c for c in unique_categories if c != "technical"]
        if non_technical and remaining > 0:
            base = remaining // len(non_technical)
            rem = remaining % len(non_technical)
            for i, cat in enumerate(non_technical):
                distribution[cat] = base + (1 if i < rem else 0)

        return distribution

    def _create_resume_prompt(
        self,
        resume_data: Dict[str, Any],
        role: str,
        difficulty: str,
        num_questions: int,
        categories: List[str],
        skills: List[str],
        work_experience: List[Dict],
        projects: List[Dict],
        education: List[Dict],
        summary: str,
        years_exp: int
    ) -> str:
        """Create an AI prompt for resume-based question generation."""

        candidate_json = self._build_candidate_json(
            role=role,
            skills=skills[:15],
            experience_years=years_exp,
            difficulty=difficulty,
            num_questions=num_questions,
            categories=categories,
            projects=projects,
            work_experience=work_experience,
            education=education,
            summary=summary
        )

        # Distribute questions evenly across the requested categories
        questions_per_cat = {}
        total_cats = len(categories) if categories else 1
        base = num_questions // total_cats
        remainder = num_questions % total_cats
        for i, cat in enumerate(categories):
            questions_per_cat[cat] = base + (1 if i < remainder else 0)

        # Build category descriptions for the prompt
        CATEGORY_DESCRIPTIONS = {
            "technical": "technical questions about specific skills from the resume",
            "behavioral": "behavioral questions using the STAR method about teamwork, leadership, problem-solving, and past experiences referenced in the resume",
            "situational": "situational/scenario-based questions about how the candidate would handle hypothetical workplace situations relevant to their experience",
            "hr": "HR questions about motivation, salary expectations, career goals, culture fit, and self-awareness",
        }

        category_lines = []
        json_keys = []
        valid_categories = []
        for cat, count in questions_per_cat.items():
            if count <= 0:
                continue
            key = f"{cat}_questions"
            desc = CATEGORY_DESCRIPTIONS.get(cat, f"{cat} questions")
            category_lines.append(f"- {count} {cat} questions → {key}: {desc}")
            json_keys.append(f'  "{key}": [... {count} question objects]')
            valid_categories.append(cat)

        distribution_text = "\n".join(category_lines)
        json_body = ",\n".join(json_keys)
        valid_cats_str = ", ".join(valid_categories)

        prompt = f"""You are an expert interviewer.

Generate interview questions based ONLY on the candidate profile provided.
Do NOT assume extra experience.
Do NOT add technologies not listed in skills.

Rules:
- If experience_years = 0 → ask fresher level questions
- If experience_years 1-3 → intermediate questions
- If experience_years >3 → advanced questions

This is a RESUME-BASED interview. Questions MUST reference the candidate's actual
work experience, projects, skills, and education from the profile below.
Personalize every question — mention specific job titles, company names, project names, and skills.

Total questions to generate: {num_questions}

Question distribution:
{distribution_text}

Each question object must have these fields:
- question_text: string (the interview question — MUST reference resume details)
- category: string (MUST be one of: {valid_cats_str})
- difficulty: string ({difficulty})
- expected_topics: array of strings (3-5 keywords the answer should cover)
- time_limit: number (seconds, 60-180)
- follow_up_questions: array of strings (2-3 follow-ups)
- ideal_answer: string (brief outline of what a good answer includes)

Return JSON format:

{{
{json_body}
}}

IMPORTANT:
- Generate questions ONLY from the skills, projects, and experience listed below.
- Do NOT invent or assume any skill/technology not in the profile.
- Match difficulty to experience_years strictly.
- Reference actual job titles, project names, and companies from the resume.
- The "category" field in EVERY question object MUST be one of: {valid_cats_str}. Do NOT use any other category value.

Candidate Profile:
{candidate_json}

Only respond with valid JSON, no additional text."""

        return prompt

    def _generate_resume_based_question(
        self,
        category: str,
        resume_data: Dict,
        skills: List[str],
        work_exp: List[Dict],
        projects: List[Dict],
        role: str,
        difficulty: str
    ) -> GeneratedQuestion:
        """Generate a single resume-based question."""

        if category == "technical" and skills:
            # Technical questions about specific skills from resume
            skill = random.choice(skills)

            if skill in TECHNOLOGY_QUESTIONS:
                tech_q = random.choice(TECHNOLOGY_QUESTIONS[skill])
                return GeneratedQuestion(
                    question_text=f"I see you have experience with {skill}. {tech_q['question']}",
                    category="technical",
                    difficulty=difficulty,
                    expected_topics=tech_q["keywords"] + [skill, "resume experience"],
                    time_limit=120,
                    follow_up_questions=["How did you use this in your previous role?", "What challenges did you face?"],
                    ideal_answer=tech_q.get("ideal", "")
                )
            else:
                # Generic technical question about the skill
                questions = [
                    f"I noticed {skill} is listed on your resume. Can you describe a challenging problem you solved using {skill}?",
                    f"Tell me about your most significant project using {skill}. What was your role and what did you achieve?",
                    f"How would you rate your proficiency in {skill}? Can you give an example that demonstrates your expertise?",
                    f"What best practices do you follow when working with {skill}?",
                ]
                return GeneratedQuestion(
                    question_text=random.choice(questions),
                    category="technical",
                    difficulty=difficulty,
                    expected_topics=[skill, "project example", "problem solving", "best practices"],
                    time_limit=120,
                    follow_up_questions=["What was the outcome?", "What would you do differently now?"],
                    ideal_answer=""
                )

        elif category == "behavioral" and work_exp:
            # Behavioral questions about work experience
            exp = random.choice(work_exp)
            job_title = exp.get("title", "your previous role")

            questions = [
                f"I see you worked as {job_title}. Tell me about a time when you faced a significant challenge in that role. How did you overcome it?",
                f"During your time as {job_title}, describe a situation where you had to collaborate with a difficult team member.",
                f"What was your biggest achievement as {job_title}? Walk me through how you accomplished it.",
                f"Tell me about a time in your role as {job_title} when you had to learn something new quickly.",
                f"Describe a situation as {job_title} where you had to make a difficult decision with limited information.",
            ]

            return GeneratedQuestion(
                question_text=random.choice(questions),
                category="behavioral",
                difficulty=difficulty,
                expected_topics=["STAR method", "specific example", "outcome", "learning", "work experience"],
                time_limit=120,
                follow_up_questions=["How did your team respond?", "What did you learn from this experience?"],
                ideal_answer=""
            )

        elif category == "behavioral" and projects:
            # Behavioral questions about projects
            project = random.choice(projects)
            project_name = project.get("name", "one of your projects")

            questions = [
                f"I noticed you worked on {project_name}. What was the most challenging aspect of this project?",
                f"Tell me about your role in {project_name}. What were your main contributions?",
                f"What technologies did you use in {project_name} and why did you choose them?",
                f"If you could rebuild {project_name} from scratch, what would you do differently?",
            ]

            return GeneratedQuestion(
                question_text=random.choice(questions),
                category="behavioral",
                difficulty=difficulty,
                expected_topics=["project experience", "technical decisions", "teamwork", "problem solving"],
                time_limit=120,
                follow_up_questions=["What was the impact?", "How did you measure success?"],
                ideal_answer=""
            )

        elif category == "situational":
            # Situational questions related to the target role
            scenarios = [
                f"As a {role}, how would you approach designing a system that needs to handle the technologies you've listed on your resume?",
                f"If you were hired as a {role} and needed to quickly get up to speed on a technology you haven't used before, how would you approach it?",
                f"Imagine you're working as a {role} and you discover a critical bug in production. Walk me through your response process.",
                f"If you joined our team as a {role} and noticed our tech stack uses different tools than what you're familiar with, how would you adapt?",
            ]

            return GeneratedQuestion(
                question_text=random.choice(scenarios),
                category="situational",
                difficulty=difficulty,
                expected_topics=["problem solving", "adaptability", "system design", "decision making"],
                time_limit=120,
                follow_up_questions=["What alternatives would you consider?", "How would you prioritize this?"],
                ideal_answer=""
            )

        else:
            # Fallback to regular question generation
            return self._generate_template_question(
                category, role, skills or [], 0, difficulty
            )

    def generate_follow_up(
        self,
        original_question: str,
        candidate_response: str
    ) -> str:
        """
        Generate a follow-up question based on candidate's response.

        Args:
            original_question: The original question asked
            candidate_response: Candidate's transcribed response

        Returns:
            Follow-up question text
        """
        # Basic follow-up patterns
        follow_up_patterns = [
            "Can you elaborate more on that?",
            "What metrics did you use to measure success?",
            "How did your team respond to this?",
            "What alternatives did you consider?",
            "How would you approach this differently now?",
            "Can you give a specific example?",
            "What was the impact of your decision?",
        ]

        return random.choice(follow_up_patterns)

    async def generate_adaptive_followup_question(
        self,
        original_question: str,
        candidate_response: str,
        resume_data: Dict[str, Any],
        role: str,
        difficulty: str = "medium"
    ) -> GeneratedQuestion:
        """
        Generate an adaptive technical follow-up based on previous answer + resume.
        """
        projects = resume_data.get("projects", []) or []
        skills = resume_data.get("extracted_skills", []) or []

        response_lower = (candidate_response or "").lower()
        question_lower = (original_question or "").lower()

        # Find referenced project from question/answer context
        selected_project = None
        for p in projects:
            name = (p.get("name") or "").strip()
            if not name:
                continue
            if name.lower() in question_lower or name.lower() in response_lower:
                selected_project = p
                break
        if not selected_project and projects:
            selected_project = projects[0]

        project_name = (selected_project or {}).get("name", "your project")
        project_desc = (selected_project or {}).get("description", "")
        project_text = f"{project_name} {project_desc}".lower()

        detected_skills = []
        for s in skills:
            if s and (s.lower() in response_lower or s.lower() in project_text):
                detected_skills.append(s)
        if not detected_skills:
            detected_skills = skills[:3]

        # Heuristic follow-up style based on response content
        if any(k in response_lower for k in ["accuracy", "precision", "recall", "f1", "model", "training"]):
            followup_text = (
                f"In {project_name}, how did you evaluate model performance and "
                f"what trade-offs did you make between accuracy and latency?"
            )
            expected = ["evaluation metrics", "trade-offs", "model tuning", "latency", "deployment"]
        elif any(k in response_lower for k in ["api", "backend", "database", "architecture", "scal"]):
            followup_text = (
                f"For {project_name}, explain the system architecture in detail. "
                f"How did you ensure scalability and reliability?"
            )
            expected = ["architecture", "scalability", "reliability", "bottlenecks", "monitoring"]
        else:
            followup_text = (
                f"Can you walk through a technically difficult issue you faced in {project_name} "
                f"and how you debugged and fixed it?"
            )
            expected = ["root cause analysis", "debugging", "implementation details", "resolution", "lessons learned"]

        if detected_skills:
            expected.extend(detected_skills[:3])

        ideal = (
            "A strong answer should include: 1) concrete technical context, "
            "2) specific design/implementation choices, 3) measurable outcomes, "
            "4) trade-offs considered, and 5) what was improved after learning."
        )

        return GeneratedQuestion(
            question_text=followup_text,
            category="technical",
            difficulty=difficulty,
            expected_topics=list(dict.fromkeys(expected))[:8],
            time_limit=120,
            follow_up_questions=[
                "What would you optimize if you rebuilt it now?",
                "How would this design change at 10x scale?"
            ],
            ideal_answer=ideal
        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def get_question_service() -> QuestionGeneratorService:
    """Factory function to get question generator service instance."""
    return QuestionGeneratorService()
