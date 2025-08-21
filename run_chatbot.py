import subprocess
import sys
import os

def main():
    """
    Executes the Streamlit chatbot application using a subprocess.

    This script ensures that the Streamlit app is run with the correct path
    and from the project's root directory, which helps in resolving
    module paths correctly.
    """
    # Get the directory where this script is located (the project root)
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Add the 'src' directory to the Python path
    src_path = os.path.join(project_root, "src")
    
    # Construct the full, absolute path to the chatbot application script
    app_path = os.path.join(project_root, "src", "chatbot", "chatbot_app.py")

    if not os.path.exists(app_path):
        print(f"Error: Chatbot application not found at {app_path}", file=sys.stderr)
        sys.exit(1)

    command = [sys.executable, "-m", "streamlit", "run", app_path]

    print(f"Starting chatbot application...")
    print(f"Running command: {' '.join(command)}")

    try:
        # We run the command from the project root to ensure `src` is in the Python path
        env = os.environ.copy()
        env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
        subprocess.run(command, check=True, cwd=project_root, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'streamlit' command not found.", file=sys.stderr)
        print("Please ensure Streamlit is installed in your environment (`pip install streamlit`).", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
