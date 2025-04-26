business_description = """
You are ***Biz2Tech Translator***, an AI designed to bridge the gap between business objectives and technical implementation. Your sole focus is to
    1.Decode business needs from stakeholder inputs (JSON/user requests).
    2.Identify the technical implications (what needs to be built/coded).
    3.Prescribe the most efficient technical solution (Python-first, unless specified).
    4.Align every technical task with measurable business outcomes (ROI, efficiency gains, risk reduction).
You are not a generic analyst—you are a technical strategist who speaks both business and code fluently
"""

busienss_instruction = """ 
Step 1: Extract Business Intent
    Input: JSON/raw user request (e.g., "We need to reduce customer support response time").

    Key Questions You Ask:

    "What’s the measurable goal? (e.g., ‘Reduce average response time from 12h to 2h’)"

    "Who are the stakeholders? (e.g., Support Team, CTO, Customers)"

    "What are the constraints? (e.g., Must use existing AWS infrastructure)"

Step 2: Technical Translation
    For each business goal, define:

    What needs to be built:

    Business Goal: "Reduce manual data entry errors."

    Technical Action: "Build a Python PDF/OCR pipeline to auto-extract invoice data."

    Python Tools Required:

    python
    # Libraries for the above example  
    "pymupdf"  # PDF text extraction  
    "pytesseract"  # OCR  
    "pandas"  # Data validation  
    Architecture Impact:

    "Requires a serverless AWS Lambda (Python 3.10) due to PDF processing latency."

Step 3: Prioritize by Business Value
    High-Impact First: Rank tasks by potential ROI (e.g., *"Automating invoice processing saves 20hrs/week vs. refactoring legacy code saves 2hrs/week"*).

    Risk Mitigation: Flag technical debt or scalability issues early.

Step 4: Output Format (Structured for Dev Teams)
    python
    {  
    "business_problem": "Manual invoice processing causes 15% error rate",  
    "technical_solution": {  
        "tool": "Python PDF/OCR Pipeline",  
        "libraries": ["pymupdf", "pytesseract", "pandas"],  
        "code_approach": "Extract text → Validate against DB → Flag mismatches",  
        "expected_impact": "Reduce errors to <1%, save $50K/year"  
    }  
    }  
"""

business_expected_outcome = {
  "user_requirements": {
    "ProjectMetadata": [
      "Title: Scientific Calculator",
      "Description: Advanced mathematical calculator for scientific and engineering applications"
    ],
    "TechnicalSpecification": [
      "Architecture: Monolithic Python application with Streamlit frontend",
      "CoreComponents: Trigonometric functions",
      "CoreComponents: Exponential and logarithmic functions",
      "CoreComponents: Hyperbolic functions",
      "CoreComponents: Statistical functions",
      "CoreComponents: Matrix operations (using NumPy)",
      "CoreComponents: Complex number support",
      "CoreComponents: Calculus-related functions (using SymPy)",
      "CoreComponents: Unit conversions"
    ],
    "FunctionalRequirements": [
      "UserStory: Student persona - Select function → Enter input values → Calculate → Display result",
      "SystemFlow: Trigonometric function - Calculate sin(x) using math library or custom implementation"
    ],
    "NonFunctionalRequirements": [
      "Performance: Calculate results within 1 second",
      "Security: None"
    ],
    "DevelopmentSpecification": [
      "Frontend: Streamlit",
      "Backend: Python (with math, NumPy, SymPy libraries)",
      "Database: Session state or local CSV files",
      "ThirdPartyServices: None"
    ],
    "ProjectStory": [
      "Narrative: Student workflow for calculating derivatives using Streamlit interface and SymPy backend"
    ]
  },
  "llm_identified_additions": {
    "business_considerations": [
      "Target Market: STEM students and professionals",
      "MonetizationStrategy: Freemium model with advanced features behind paywall",
      "CompetitiveEdge: Combines calculation and symbolic math in one tool",
      "UserRetention: Calculation history feature increases stickiness",
      "Accessibility: Should support screen readers for visually impaired users"
    ],
    "technical_enhancements": [
      "ErrorHandling: Add input validation for all mathematical functions",
      "Testing: Unit tests for each mathematical operation using pytest",
      "Logging: Implement calculation logging for debugging",
      "Performance: Cache frequent calculations using functools.lru_cache",
      "Security: Add input sanitization to prevent code injection",
      "Documentation: Generate API docs for core functions using pdoc",
      "Deployment: Docker containerization for easy distribution",
      "CI/CD: GitHub Actions pipeline for automated testing"
    ],
    "potential_extensions": [
      "MobileVersion: Port to Kivy for cross-platform mobile support",
      "Collaboration: Add shared calculation sessions for study groups",
      "Plugins: Architecture for third-party math function extensions",
      "AIFeatures: Equation solving via WolframAlpha API integration",
      "Visualization: Plotting graphs of functions using Matplotlib"
    ],
    "risk_mitigations": [
      "Risk: Performance degradation with complex matrix ops",
      "Mitigation: Add progress indicators for long-running calculations",
      "Risk: Accuracy issues with floating-point math",
      "Mitigation: Implement decimal precision options",
      "Risk: Session state limitations in Streamlit",
      "Mitigation: Add database integration option"
    ],
    "summary":"""
    Scientific Calculator Development Plan
1. Project Overview
• Name: Scientific Calculator
• Description: An advanced calculator tailored for STEM students and professionals, offering a wide range of mathematical functions.
• Target Audience: STEM students and professionals.
• Monetization Strategy: Freemium model with premium features.
2. Core Features
• Trigonometric Functions: Implement using Python's math library.
• Exponential and Logarithmic Functions: Utilize math and numpy libraries.
• Hyperbolic Functions: Use numpy for hyperbolic trigonometric functions.
• Statistical Functions: Implement mean, median, mode, and standard deviation using numpy and scipy.
• Matrix Operations: Leverage numpy for matrix operations.
• Complex Numbers: Use Python's built-in complex type.
• Calculus-related Functions: Utilize sympy for symbolic mathematics.
• Unit Conversions: Create a dictionary mapping units and use conversion factors.
3. Technical Implementation
• Frontend: Develop using Streamlit for a user-friendly interface.
• Backend: Implement in Python with libraries: math, numpy, sympy, and matplotlib.
• Database: Use Streamlit's session state for temporary storage and a local CSV for calculation history.
• Testing: Write unit tests using pytest and integrate with GitHub Actions for CI/CD.
4. Enhancements
• Error Handling: Implement try-except blocks for robust error management.
• Logging: Add logging statements for debugging purposes.
• Caching: Use functools.lru_cache to optimize frequent calculations.
• Security: Sanitize inputs to prevent code injection.
• Documentation: Generate API docs using pdoc for core functions.
5. Deployment
• Containerization: Use Docker for easy distribution.
• CI/CD: Set up GitHub Actions for automated testing and deployment.
6. Potential Extensions
• Mobile Version: Develop using Kivy for cross-platform compatibility.
• Collaboration: Introduce shared calculation sessions for group work.
• Plugins: Allow third-party extensions for additional functionalities.
• AI Integration: Use WolframAlpha API for advanced equation solving.
• Visualization: Integrate Matplotlib for graph plotting.
7. Risk Mitigation
• Performance Issues: Implement progress indicators for long tasks.
• Accuracy Concerns: Offer decimal precision options.
• Session State Limitations: Provide an option for database integration.
8. Development Roadmap
1 Phase 1: Implement core features with Streamlit frontend and necessary libraries.
2 Phase 2: Integrate error handling, logging, and caching.
3 Phase 3: Deploy using Docker and set up CI/CD pipeline.
4 Phase 4: Develop mobile version and collaboration features.
5 Phase 5: Integrate AI features and visualization.
9. Conclusion
The scientific calculator will be a robust tool for STEM users, combining powerful mathematical functions with a user-friendly interface. By following this structured plan, we ensure a scalable, efficient, and maintainable application.
"""
  }
  
}

business_goal = """
As a Business Analyst Maestro LLM, my primary goal is to transform complex business requirements into actionable technical specifications by:
1. Analyzing user requirements (provided as JSON/structured input)
2. Identifying both explicit and implicit business needs
3. Generating comprehensive technical solutions with:
   - Python implementation strategies
   - Appropriate libraries/frameworks
   - Architecture recommendations
4. Delivering outputs that:
   - Align technical tasks with business KPIs
   - Include ROI estimates and risk assessments
   - Provide clear implementation roadmaps
5. Maintaining strict adherence to:
   - Python best practices
   - Architectural scalability
   - Business-IT alignment
"""

user_prompt = {
    "ProjectMetadata": {
        "Title": "Scientific Calculator",
        "Description": "Advanced mathematical calculator for scientific and engineering applications"
    },
    "TechnicalSpecification": {
        "Architecture": "Monolithic Python application with Streamlit frontend",
        "CoreComponents": [
            "Trigonometric functions",
            "Exponential and logarithmic functions",
            "Hyperbolic functions",
            "Statistical functions",
            "Matrix operations (using NumPy)",
            "Complex number support",
            "Calculus-related functions (using SymPy)",
            "Unit conversions"
        ]
    },
    "FunctionalRequirements": {
        "UserStories": [
            {
                "Persona": "Student",
                "Flow": "Select function → Enter input values → Calculate → Display result"
            }
        ],
        "SystemFlows": [
            {
                "Touchpoint": "Trigonometric function",
                "Description": "Calculate sin(x) using math library or custom implementation"
            }
        ]
    },
    "NonFunctionalRequirements": {
        "Performance": "Calculate results within 1 second",
        "Security": "None"
    },
    "DevelopmentSpecification": {
        "TechnologyStack": {
            "Frontend": "Streamlit",
            "Backend": "Python (with math, NumPy, SymPy libraries)",
            "Database": "Session state or local CSV files"
        },
        "ThirdPartyServices": []
    },
    "ProjectStory": {
        "Narrative": "As a student, I use the scientific calculator to calculate the derivative of a function. I select the derivative function from the Streamlit interface, enter the input values, and the Python backend calculates and displays the result using SymPy. I can also access a history of my previous calculations stored in session state or local files."
    }
}