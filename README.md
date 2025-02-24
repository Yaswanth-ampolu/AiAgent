
# Local AI Code Agent

## Overview
`local_code_ai_agent.py` is a Windows-focused, local AI-powered Python code agent that utilizes Ollama's locally installed models (e.g., `codellama`, `llama3`) to:
1. Generate a step-by-step **plan** for a given request.
2. **Generate Python code** based on the plan.
3. Save the generated code to a file.
4. Request user permission to **execute the code**.

This tool aims to enhance security by using dual confirmation before running code and saving the generated code in a `.py` file for transparency. It is designed with minimal external dependencies and supports Windows environments.

## Requirements

- **Python 3.x** installed.
- **Ollama** installed and accessible via your system's PATH.
- A local Ollama model (e.g., `codellama:7b`, `llama3`) pulled and ready for use.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Yaswanth-ampolu/local-code-ai-agent.git
cd local-code-ai-agent
```

### 2. Create and activate a virtual environment
Ensure that your project dependencies are isolated:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
You will need `ollama`, `python-dotenv`, `colorama`, and `json` libraries. Run the following:
```bash
pip install ollama python-dotenv colorama json
```

## Usage

### Example Command
To run the AI agent with a simple task (e.g., generate Python code to print numbers till 20), use:
```bash
python local_code_ai_agent.py "write a python code that prints numbers till 20"
```

### Process
1. **Plan Phase**: The agent generates a step-by-step plan for your request.
2. **Code Phase**: It generates the actual Python code.
3. **Confirmation**: You are asked to review and confirm before executing the code.
4. **Execution**: If confirmed, the generated code is executed.

## Security

- **Dual Confirmation**: The agent asks for confirmation twice before executing any code.
- **Code Review**: The generated code is saved in `generated_script.py` for review before running.

## License
This project is licensed under the MIT License.
