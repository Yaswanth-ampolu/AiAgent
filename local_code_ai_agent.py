import os
import sys
import subprocess
import tempfile
import textwrap
import json

# --------------- CONFIGURATION --------------- #
OLLAMA_MODEL = "codellama:7b"  # or "llama3" or whichever local model you pulled
PLAN_SYSTEM_PROMPT = textwrap.dedent("""
    You are an AI agent that generates a step-by-step plan for a given file or folder creation request.
    You must detail each step and justify your choices (e.g., using os.makedirs or pathlib) 
    for a Windows environment.
""").strip()

CODE_SYSTEM_PROMPT = textwrap.dedent("""
    You are an AI agent that writes Python code based on the plan and user request.
    - Use standard Python libraries only (no 3rd-party).
    - Include helpful comments.
    - Handle edge cases (existing directories, permission issues).
    - Paths must be Windows-friendly (use os.path.join or similar).
""").strip()


def query_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """
    Sends a prompt to Ollama via subprocess, returning the generated text as a string.
    """
    try:
        proc = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",  # Ensures correct encoding
            errors="replace"    # Replaces problematic characters instead of failing
        )
        out, err = proc.communicate(input=prompt)
        if err:
            # Not all text in 'err' is necessarily an error, but we print it if needed
            print(f"[DEBUG] Ollama STDERR: {err}", file=sys.stderr)

        if proc.returncode != 0:
            # If Ollama command fails, notify user
            print(f"[ERROR] Ollama process exited with code {proc.returncode}", file=sys.stderr)
            sys.exit(1)

        return out.strip()

    except FileNotFoundError:
        print("Error: Ollama not found. Ensure it's installed and on PATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error while querying Ollama: {e}", file=sys.stderr)
        sys.exit(1)


def plan_phase(user_request: str) -> str:
    """
    Generate a plan from Ollama for the given user request.
    """
    # We feed the system prompt plus the user request
    full_prompt = f"{PLAN_SYSTEM_PROMPT}\n\nUser request:\n{user_request}\n\nPlan:"
    print("[INFO] Generating plan with Ollama...")
    plan_response = query_ollama(full_prompt)
    return plan_response


def save_prompt_to_file(plan_text: str, code_text: str, user_request: str, filename: str = "generated_prompt.json"):
    """
    Saves the generated plan and code to a JSON file.
    """
    data = {
        "user_request": user_request,
        "plan": plan_text,
        "generated_code": code_text
    }

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[INFO] Prompts saved to {filename}")
    except Exception as e:
        print(f"[ERROR] Could not save prompts to file: {e}")


def detect_language(user_request: str) -> str:
    """
    Detects the programming language from the user request.
    Currently, it defaults to Python.
    """
    return "python"  # Always using Python for execution


def code_phase(plan_text: str, user_request: str) -> str:
    """
    Generates Python code using Ollama based on the plan.
    """
    full_prompt = (
        f"You are an AI that generates Python code based on the given plan and request.\n"
        f"Plan:\n{plan_text}\n\n"
        f"User request:\n{user_request}\n\n"
        "Generate a clean, executable Python script without markdown formatting, backticks, or extra explanations.\n"
        "Ensure it works within the current directory and checks for existing files before writing.\n\n"
        "Python Code:\n"
    )

    print("[INFO] Generating Python code with Ollama...")
    code_response = query_ollama(full_prompt)

    # Remove accidental Markdown formatting
    clean_code = code_response.replace("```python", "").replace("```", "").strip()
    
    return clean_code


def save_code_to_file(code_text: str, filename: str = "generated_script.py") -> None:
    """
    Saves the generated code to `generated_script.py`, always overwriting the previous version.
    """
    filename = os.path.abspath("generated_script.py")  # **Force correct filename**

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_text + "\n")
        print(f"[INFO] Code saved to {filename}")
    except Exception as e:
        print(f"[ERROR] Could not write to {filename}: {e}")


def execute_script(script_path: str):
    """
    Executes the Python script after generation.
    """
    script_path = os.path.abspath(script_path)
    print(f"[INFO] Running the script at: {script_path}")

    if not script_path.endswith(".py"):
        print("[ERROR] The generated script does not have a valid Python extension.")
        return

    try:
        subprocess.run([sys.executable, script_path], check=True)
        print("[INFO] Script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Script execution failed with code {e.returncode}: {e}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while running the script: {e}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} \"Your request here\"")
        sys.exit(1)

    user_request = sys.argv[1]

    # Ensure the script works in the current directory
    working_dir = os.getcwd()
    print(f"[INFO] Working in directory: {working_dir}")

    # 1) PLAN PHASE
    plan_text = plan_phase(user_request)
    print("\n=== PLAN PHASE OUTPUT ===")
    print(plan_text)
    print("=== END PLAN PHASE OUTPUT ===\n")

    confirm_plan = input("Do you want to proceed with code generation based on this plan? (Y/N) ").strip().lower()
    if confirm_plan != 'y':
        print("[INFO] User aborted after Plan Phase.")
        sys.exit(0)

    # 2) CODE PHASE
    code_text = code_phase(plan_text, user_request)
    print("\n=== CODE PHASE OUTPUT ===")
    print(code_text)
    print("=== END CODE PHASE OUTPUT ===\n")

    # Save prompts and generated code
    save_prompt_to_file(plan_text, code_text, user_request)

    # **Always overwrite generated_script.py**
    generated_filename = "generated_script.py"
    save_code_to_file(code_text, generated_filename)

    confirm_code = input(f"Review the file '{generated_filename}'. Proceed with execution? (Y/N) ").strip().lower()
    if confirm_code != 'y':
        print("[INFO] User aborted before script execution.")
        sys.exit(0)

    # Execute the Python script
    execute_script(generated_filename)

    print("[INFO] Done.")


if __name__ == "__main__":
    main()
