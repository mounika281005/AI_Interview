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
        
        skills_str = ", ".join(skills)
        categories_str = ", ".join(categories)
        
        prompt = f"""You are an expert technical interviewer. Generate {num_questions} interview questions for the following candidate profile:

Role: {role}
Technical Skills: {skills_str}
Years of Experience: {experience_years}
Difficulty Level: {difficulty}
Question Categories: {categories_str}

For each question, provide:
1. The question text
2. Category (behavioral, technical, or situational)
3. Difficulty level (easy, medium, hard)
4. Expected topics/keywords the candidate should cover
5. Suggested time limit in seconds (60-180)
6. 2-3 follow-up questions

Respond in JSON format as an array of objects with these fields:
- question_text: string
- category: string
- difficulty: string
- expected_topics: array of strings
- time_limit: number
- follow_up_questions: array of strings

Make the questions relevant to the role and experience level. For a candidate with {experience_years} years of experience, focus on:
- {experience_years} <= 2: Fundamentals, learning ability, teamwork
- {experience_years} 3-5: Problem-solving, project ownership, technical depth
- {experience_years} > 5: Leadership, architecture decisions, mentoring

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
        """Parse AI response into GeneratedQuestion objects."""
        try:
            # Try to extract JSON from response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            questions_data = json.loads(content.strip())
            
            questions = []
            for q in questions_data:
                questions.append(GeneratedQuestion(
                    question_text=q.get("question_text", ""),
                    category=q.get("category", "general"),
                    difficulty=q.get("difficulty", "medium"),
                    expected_topics=q.get("expected_topics", []),
                    time_limit=q.get("time_limit", 120),
                    follow_up_questions=q.get("follow_up_questions", [])
                ))
            
            return questions
        
        except (json.JSONDecodeError, KeyError) as e:
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
        
        # If we have technology-specific questions, prioritize them
        if primary_skill and primary_skill in TECHNOLOGY_QUESTIONS:
            tech_questions = TECHNOLOGY_QUESTIONS[primary_skill].copy()
            random.shuffle(tech_questions)
            
            for q in tech_questions[:num_questions]:
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
            
            debug_log(f"Generated {len(questions)} technology-specific questions for {primary_skill}")
        
        # If not enough questions, use default technical questions
        if len(questions) < num_questions and primary_skill:
            default_qs = DEFAULT_TECHNICAL_QUESTIONS.copy()
            random.shuffle(default_qs)
            
            for q in default_qs:
                if len(questions) >= num_questions:
                    break
                question_text = q["question"].format(technology=primary_skill)
                if question_text not in used_questions:
                    used_questions.add(question_text)
                    questions.append(GeneratedQuestion(
                        question_text=question_text,
                        category="technical",
                        difficulty=difficulty,
                        expected_topics=q["keywords"] + [primary_skill],
                        time_limit=120,
                        follow_up_questions=["Can you elaborate?", "What challenges did you face?"],
                        ideal_answer=q.get("ideal", "")
                    ))
        
        # Fill remaining with behavioral/situational if needed
        if len(questions) < num_questions:
            remaining = num_questions - len(questions)
            for i in range(remaining):
                category = "behavioral" if i % 2 == 0 else "situational"
                question = self._generate_template_question(
                    category, role, skills, experience_years, difficulty
                )
                questions.append(question)
        
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


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def get_question_service() -> QuestionGeneratorService:
    """Factory function to get question generator service instance."""
    return QuestionGeneratorService()
