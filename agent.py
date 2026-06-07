import os

SERVER = os.getenv("PUZZLE_SERVER", "http://127.0.0.1:5050")

import ollama
import requests
from requests.exceptions import RequestException

def list_levels():
  try:
    r = requests.get(f"{SERVER}/levels", timeout=5)
    r.raise_for_status()
    return r.json()
  except RequestException as e:
    print(f"Failed to fetch levels from {SERVER}: {e}")
    return []


def get_level(level_id):
  try:
    r = requests.get(f"{SERVER}/level/{level_id}", timeout=5)
    if r.status_code != 200:
      return None
    return r.json()
  except RequestException as e:
    print(f"Failed to fetch level {level_id}: {e}")
    return None


def submit_attempt(level_id, attempt):
  r = requests.post(f"{SERVER}/submit", json={"level_id": level_id, "attempt": attempt}, timeout=15)
  r.raise_for_status()
  return r.json()


def submit_files(level_id, files: dict):
  """Submit a dict of filename->content to the server for script-based validation."""
  r = requests.post(f"{SERVER}/submit", json={"level_id": level_id, "files": files}, timeout=15)
  r.raise_for_status()
  return r.json()


def ask_hint_via_ollama(level):
  # Ask the model for a hint without revealing the answer
  prompt = (
    "You are a helpful tutor for C and Linux puzzles. "
    "The user is working on this puzzle:\n\n"
    f"Title: {level['title']}\nDescription: {level['description']}\n\n"
    "Provide a concise hint or a small step the user can try next. "
    "Do NOT reveal the flag or exact command; avoid giving full step-by-step answers. "
  )
  messages = [{"role": "user", "content": prompt}]
  res = ollama.chat(model="llama3.2", messages=messages)
  return res.message.content


def print_levels(levels):
  print("\nAvailable levels:")
  for lvl in levels:
    print(f"  {lvl['id']}: {lvl['title']}")


def read_files_from_paths():
  print("This level requires source files. Provide local file paths to upload.")
  files = {}
  while True:
    path = input("Enter local path to a source file (or blank to finish): ").strip()
    if not path:
      break
    try:
      with open(path, "r") as f:
        files[os.path.basename(path)] = f.read()
    except Exception as e:
      print("Failed to read file:", e)
  return files


def handle_attempt(choice, lvl):
  if lvl.get("validator") == "script":
    files = read_files_from_paths()
    if not files:
      print("No files provided; canceling attempt.")
      return False
    try:
      res = submit_files(choice, files)
    except Exception as e:
      print("Submission failed:", e)
      return False
  else:
    attempt = input("Enter your answer/command: ").strip()
    try:
      res = submit_attempt(choice, attempt)
    except Exception as e:
      print("Submission failed:", e)
      return False
  if res.get("correct"):
    print("Correct! Level solved.")
    return True
  print("Incorrect or tests failed.")
  if res.get("output"):
    print(res["output"])
  return False


def handle_level(choice):
  lvl = get_level(choice)
  if not lvl:
    print("Level not found.")
    return
  print(f"\n{lvl['title']}\n{lvl['description']}\n")
  while True:
    cmd = input("Options: (a)ttempt, (h)int, (b)ack: ").strip().lower()
    if cmd in ("b", "back"):
      return
    if cmd in ("h", "hint"):
      try:
        print("Hint:\n", ask_hint_via_ollama(lvl))
      except Exception as e:
        print("Hint failed:", e)
      continue
    if cmd in ("a", "attempt"):
      if handle_attempt(choice, lvl):
        return
      continue
    print("Unknown option — choose 'a', 'h', or 'b'.")


def main():
  print("Interactive Puzzle Agent — connect to the puzzle server and request hints.")
  while True:
    print_levels(list_levels())
    choice = input("Choose level id (or 'q' to quit): ").strip()
    if choice.lower() in ("q", "quit", "exit"):
      break
    handle_level(choice)


if __name__ == "__main__":
  main()
