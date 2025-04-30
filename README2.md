# Langmanus

![Langmanus Logo](./logo.png)

A powerful tool that transforms data migration processes with natural language queries, optimized for SAP environments.

## Key Benefits

- **Time Savings:** Transforms hours of coding into minutes with simple language commands
- **Cost Reduction:** Cuts migration costs by 65% through intelligent automation
- **Knowledge Protection:** Preserves critical transformation expertise beyond staff turnover

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- pnpm

### Installation

#### Backend Setup

1. Clone the repository
   ```bash
   git clone https://github.com/pojha1401/langmanus.git
   cd langmanus
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. create a .env file with
TAVILY_API_KEY
GROQ_API_KEY
GOOGLE_API_KEY

4. Run the backend server
   ```bash
   uv run server.py
   ```
   The API will be available at `http://localhost:5000` by default.

#### Frontend Setup

1. Navigate to the web application directory
   ```bash
   cd langmanus-web
   ```

2. Install dependencies
   install pnpm using 
   ```bash
   npm install -g pnpm@latest-10
   ```
   
   ```bash
   pnpm install
   ```

   Create a .env file with variable
   NEXT_PUBLIC_API_URL = "http://localhost:8080/api"

3. Start the development server
   ```bash
   pnpm dev
   ```
   The application will be available at `http://localhost:3000` by default.

## Features

- **Intelligent Automation:** Generates optimized Python code that adapts to complex SAP data structures
- **Contextual Memory:** Maintains transformation state across sequential operations
- **SAP Specialization:** Built-in domain-specific knowledge of SAP structures
- **Security Integration:** Prevents SQL injection and other security threats

## Usage

Once both backend and frontend are running, you can:

1. Access the web interface at `http://localhost:3000`
2. Use natural language to specify your data transformation needs
3. Review and execute the generated transformation code
4. Export the results for use in your SAP environment

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions and support, please contact [your-email@example.com](mailto:your-email@example.com)