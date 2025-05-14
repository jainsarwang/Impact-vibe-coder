# Project Documentation: Impact-vibe-coder

## 1. Background

In the rapidly evolving landscape of software development and information processing, there's a growing demand for tools and frameworks that can automate complex, multi-step tasks. Traditional approaches often involve significant manual effort, leading to longer development cycles and increased cognitive load on individuals. Impact-vibe-coder emerges as a solution to address these challenges by leveraging the power of Large Language Models (LLMs) and autonomous agent-based systems.

## 2. Scope

The Impact-vibe-coder project aims to create an intelligent framework capable of:

*   Understanding and interpreting user requests for software development or research tasks.
*   Automating the planning, research, code generation, and reporting phases of a project.
*   Orchestrating a team of specialized AI agents to perform specific sub-tasks.
*   Interacting with external tools and services (web browsing, file system, command-line).
*   Providing a structured output, including generated code, project directories, and reports.
*   Exposing its capabilities through an API for integration with other systems or user interfaces.

## 3. Goals

The primary goals of the Impact-vibe-coder project are:

*   **Automation:** To significantly automate repetitive and time-consuming aspects of software development and research.
*   **Productivity:** To enhance the productivity of developers and researchers by offloading tasks to AI agents.
*   **Acceleration:** To accelerate project timelines by streamlining workflows and enabling parallel task execution where appropriate.
*   **Complexity Management:** To assist in managing and executing complex projects by breaking them down into manageable, agent-driven tasks.
*   **Consistency:** To improve the consistency of outputs by using predefined prompts and structured agent interactions.
*   **Flexibility:** To provide a flexible framework that can be adapted and extended with new agents, tools, and capabilities.

## 4. Customer Approach

Impact-vibe-coder is designed to serve users (e.g., developers, project managers, researchers) who need to accomplish complex tasks that can be broken down into a sequence of information processing and generation steps.

*   **Input:** The "customer" interacts with the system by providing a high-level user request or query through the API.
*   **Interaction (Iterative):** The system, particularly through its `Coordinator Node`, may engage in a dialogue (if designed for it, though current structure suggests more direct execution) or present intermediate plans/results. The `Supervisor Node` and `Coder Master Node` manage internal iterations.
*   **Output:** The system delivers tangible outputs such as:
    *   Generated source code organized into a project structure.
    *   Research summaries and reports.
    *   Created project files and directories.
    *   A final report or confirmation of task completion.
*   **Feedback Loop:** While not explicitly detailed in the file structure, a mature system would incorporate a feedback loop where user validation of outputs could refine future operations.

## 5. Technology Used

The project leverages a modern stack of technologies:

*   **Programming Language:** Python
*   **Core Framework:** LangGraph (for building stateful, multi-agent applications)
*   **LLM Orchestration:** LangChain (for agent creation, tool integration, prompt management)
*   **Large Language Models (LLMs):**
    *   OpenAI (via `ChatOpenAI`)
    *   Google Gemini (via `ChatGoogleGenerativeAI`)
    *   Groq (via `ChatOpenAI` with Groq API)
*   **API Development:** FastAPI
*   **Data Handling:** Pydantic (for data validation and settings management)
*   **Web Crawling:** `jina-client`, `readabilipy`, `markdownify`
*   **Environment Management:** `dotenv`
*   **Concurrency:** `ThreadPoolExecutor`
*   **Standard Libraries:** `json`, `logging`, `os`, `subprocess`, `re`, `zipfile`, etc.

## 6. Solution (High-Level Overview)

Impact-vibe-coder implements an agent-based workflow system. User requests are processed through a graph of interconnected nodes, each representing a specific agent or logical step. A `Supervisor` agent orchestrates the overall flow, delegating tasks to specialized agents like researchers, planners, and a `Coder Master`. The `Coder Master` further delegates coding tasks to a team of specialized coder agents (e.g., `Model Coder`, `Frontend Coder`). These agents utilize LLMs, predefined prompts, and a suite of tools to accomplish their tasks, ultimately generating the desired output.

## 7. Benefits

Adopting the Impact-vibe-coder framework offers several potential benefits:

*   **Increased Efficiency:** Automates significant portions of the development and research lifecycle.
*   **Reduced Manual Error:** LLM-driven generation with structured prompts can reduce human error in repetitive tasks.
*   **Faster Turnaround Times:** Streamlined workflows and potential for parallel processing can lead to quicker project completion.
*   **Scalability for Complex Tasks:** Breaks down large, complex problems into smaller, manageable parts handled by specialized agents.
*   **Focus on Higher-Value Work:** Frees up human developers and researchers to focus on strategic thinking, creativity, and complex problem-solving rather than routine tasks.
*   **Knowledge Consolidation:** Prompts and agent configurations can codify best practices and domain knowledge.
*   **Extensibility:** The modular design allows for the addition of new agents, tools, and LLMs as requirements evolve.

## 8. Challenges / Business Problem Solved

Impact-vibe-coder aims to address several common challenges in software development and knowledge work:

*   **Slow Development Cycles:** Manual coding, research, and planning are time-consuming.
    *   **Our Solution:** Automates these tasks using AI agents.
*   **Repetitive Task Overload:** Developers and researchers spend considerable time on routine tasks (e.g., boilerplate code, basic web searches, report formatting).
    *   **Our Solution:** Specialized agents handle these routine tasks efficiently.
*   **High Cognitive Load:** Managing complex project requirements, interdependencies, and codebases can be overwhelming.
    *   **Our Solution:** The system breaks down complexity, with planner and supervisor agents managing the workflow.
*   **Difficulty in Scaling Teams/Effort:** Onboarding new team members or scaling efforts for large projects can be challenging.
    *   **Our Solution:** Provides an AI-driven workforce that can be "scaled" by invoking more agent processes (within system limits).
*   **Ensuring Consistency:** Maintaining consistent coding styles, directory structures, or report formats across a project or team.
    *   **Our Solution:** Utilizes templates and predefined agent instructions to promote consistency.
*   **Information Silos:** Knowledge required for specific tasks might be distributed or not easily accessible.
    *   **Our Solution:** The `Research Node` and `Browser Node` can centralize information gathering.

## 9. Our Solution (Detailed Architecture)

The Impact-vibe-coder solution is architected as a multi-layered, agent-driven system:

1.  **Input & API Layer (`api/app.py`):**
    *   Accepts user requests via FastAPI endpoints.
    *   Initiates the workflow through the `Workflow Service`.

2.  **Service Layer (`service/workflow_service.py`):**
    *   Manages the invocation of the main agent workflow (`workflow.py`).

3.  **Core Workflow Orchestration (`workflow.py`, `graph/builder.py`):**
    *   The `run_agent_workflow` function sets up and executes a LangGraph `StateGraph`.
    *   The graph defines a sequence of operations managed by nodes:
        *   **`Coordinator Node`**: Initial point of contact, processes user input for the graph.
        *   **`Planner Node`**: Generates a high-level strategic plan.
        *   **`Supervisor Node`**: Central orchestrator, routes tasks to appropriate worker nodes based on the plan and current state.
        *   **Worker Nodes (`Research`, `Browser`, `Directory Generator`, `Code Planner`, `Reporter`):** Perform specialized, non-coding tasks.
        *   **`Coder Master Node`**: Manages the entire code generation lifecycle. It receives coding plans and delegates to specialized coders.
        *   **Specialized Coder Nodes (`Model Coder`, `Controller Coder`, etc.):** Each responsible for generating specific types of code (e.g., database models, API controllers, frontend components). They use a generic `coder` function that handles LLM interaction, JSON parsing, and file writing.

4.  **Agent Implementation (`agents/agents.py`, `graph/nodes.py`):**
    *   Agents are built using LangChain, combining LLMs with prompts and tools.
    *   Node functions in `graph/nodes.py` define the logic for each agent's turn, including prompt application, tool usage, and state updates.

5.  **Shared Services & Utilities:**
    *   **LLM Management (`llms/llm.py`):** Provides access to various LLMs.
    *   **Prompt Engineering (`prompts/`):** A library of markdown-based prompt templates and Python functions to apply them.
    *   **Tooling (`tools/`):** A suite of tools for web interaction, file system operations, code execution, and project packaging.
    *   **Configuration (`config/`):** Manages environment variables, agent settings, and LLM mappings.
    *   **Utilities (`utils/`):** Helper functions for JSON repair, command execution, etc.

## 10. Features

Based on the project structure, key features include:

*   **Automated Task Planning:** Generation of high-level and code-specific plans.
*   **Autonomous Web Research:** Ability to browse websites and crawl content for information gathering.
*   **Automated Directory & File Structure Generation:** Creates project skeletons based on requirements.
*   **Specialized Code Generation:**
    *   Model (e.g., ORM, data classes) generation.
    *   Controller/Handler logic generation.
    *   API Route definition generation.
    *   Business logic/Service layer generation.
    *   Utility/Helper function generation.
    *   Configuration file generation.
    *   Test case generation.
    *   Frontend component generation.
    *   Database schema/migration script generation (inferred from `db_coder`).
*   **File Writing & Management:** Agents can write generated code and other content to files.
*   **Command Execution:** Ability to run shell commands (e.g., for project setup, running linters/tests).
*   **Project Packaging:** Capability to zip project directories.
*   **Python Code Execution:** In-line execution of Python scripts for analysis or utility tasks.
*   **Modular Agent Architecture:** Easily extensible with new specialized agents.
*   **Configurable LLM Usage:** Supports multiple LLM providers (OpenAI, Gemini, Groq).
*   **API Access:** Provides an interface for programmatic interaction (FastAPI).
*   **Debug Logging:** Offers detailed logging for troubleshooting.
*   **JSON Repair:** Robust handling of potentially malformed JSON outputs from LLMs.
*   **Markdown-based Prompting:** Clear and maintainable prompt templates.

## 11. Results and Impact (Potential)

*While specific metrics require empirical testing, the potential results and impact of Impact-vibe-coder are significant:*

*   **Drastic Reduction in Development Time:** For well-defined tasks, the system could reduce the time from concept to first draft code by a substantial margin.
*   **Increased Developer Throughput:** Developers can manage and oversee more projects or features by delegating initial generation and routine tasks.
*   **Improved Code Quality & Consistency (Potentially):** By encoding best practices in prompts and agent logic, the system can help maintain a consistent quality bar, especially for boilerplate and common patterns.
*   **Faster Prototyping:** Rapidly generate functional prototypes for new ideas or features.
*   **Lower Barrier to Entry for Complex Tasks:** Assists less experienced developers in tackling complex architectures by providing structured, generated starting points.
*   **Enhanced Innovation:** By automating mundane tasks, it frees up human intellect for more innovative and creative problem-solving.
*   **New Service Offerings:** Could form the basis of new automated development or content generation services.

**Note:** The actual impact will depend on the quality of prompts, the capabilities of the chosen LLMs, the robustness of the agent logic, and the complexity of the tasks assigned. Continuous refinement and evaluation will be crucial.