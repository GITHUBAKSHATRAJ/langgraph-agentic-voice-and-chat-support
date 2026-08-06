import os
import shutil
import subprocess

src_root = r"C:\Users\HP\OneDrive\Desktop\langgraph-agentic-voice-support"
dst_root = r"C:\Users\HP\.gemini\antigravity-ide\scratch\langgraph-agentic-voice-support"

ignore_dirs = {".git", "__pycache__", "chroma_db", ".venv", "venv", ".idea", ".vscode"}

print("--- Copying source files ---")
for root, dirs, files in os.walk(src_root):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    rel_path = os.path.relpath(root, src_root)
    target_dir = os.path.join(dst_root, rel_path) if rel_path != "." else dst_root
    os.makedirs(target_dir, exist_ok=True)
    
    for f in files:
        if f.endswith(".pyc") or f == "desktop.ini":
            continue
        src_file = os.path.join(root, f)
        dst_file = os.path.join(target_dir, f)
        try:
            with open(src_file, "rb") as rf:
                content = rf.read()
            with open(dst_file, "wb") as wf:
                wf.write(content)
            print(f"Copied: {os.path.join(rel_path, f)}")
        except Exception as e:
            print(f"Skipped {f}: {e}")

print("\n--- Running Git Commands in Scratch Directory ---")

def run_cmd(cmd):
    res = subprocess.run(cmd, cwd=dst_root, capture_output=True, text=True)
    print(f"Exec: {' '.join(cmd)}")
    print("STDOUT:", res.stdout.strip())
    print("STDERR:", res.stderr.strip())
    return res.returncode

run_cmd(["git", "init"])
run_cmd(["git", "remote", "remove", "origin"])
run_cmd(["git", "remote", "add", "origin", "https://github.com/Abhinandan9508/langgraph-agentic-voice-support.git"])
run_cmd(["git", "checkout", "-B", "main"])
run_cmd(["git", "add", "."])
run_cmd(["git", "commit", "-m", "feat: initial commit of complete LangGraph agentic voice support project"])
run_cmd(["git", "push", "-u", "origin", "main", "--force"])
