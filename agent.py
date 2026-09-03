import os

import requests
from requests.exceptions import RequestException

import achievements
import cli
import game_systems
import leaderboard
import learning_paths
import storage

SERVER = os.getenv("PUZZLE_SERVER", "http://127.0.0.1:5050")
HINT_MODELS_ENV = "LUX_OLLAMA_MODELS"
HINT_MODEL_ENV = "LUX_OLLAMA_MODEL"


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
    r = requests.post(
        f"{SERVER}/submit", json={"level_id": level_id, "attempt": attempt}, timeout=15
    )
    r.raise_for_status()
    return r.json()


def submit_files(level_id, files: dict):
    """Submit a dict of filename->content to the server for script-based validation."""
    r = requests.post(f"{SERVER}/submit", json={"level_id": level_id, "files": files}, timeout=15)
    r.raise_for_status()
    return r.json()


def _configured_hint_models():
    preferred = os.getenv(HINT_MODEL_ENV, "").strip()
    configured = os.getenv(HINT_MODELS_ENV, "").strip()
    defaults = ["llama3.2", "qwen2.5-coder:7b", "mistral", "phi3"]
    models = []
    if preferred:
        models.append(preferred)
    if configured:
        models.extend([item.strip() for item in configured.split(",") if item.strip()])
    if not models:
        models = defaults
    if preferred and preferred not in models:
        models.insert(0, preferred)
    # preserve order while removing duplicates
    deduped = []
    for model in models:
        if model not in deduped:
            deduped.append(model)
    return deduped


def _safe_hint_text(text: str):
    compact = " ".join((text or "").strip().split())
    if not compact:
        return ""
    sentences = []
    for chunk in compact.replace("!", ".").replace("?", ".").split("."):
        chunk = chunk.strip()
        if chunk:
            sentences.append(chunk)
        if len(sentences) >= 2:
            break
    hint = ". ".join(sentences) if sentences else compact
    if len(hint) > 220:
        hint = hint[:217].rstrip() + "..."
    return hint


def _attempt_summary_for_level(state, level_id):
    stats = storage.get_level_attempt_stats(state, level_id)
    if not stats:
        return "No prior attempts recorded."
    pieces = [f"{stats.get('attempts', 0)} attempts"]
    if stats.get("incorrect"):
        pieces.append(f"{stats['incorrect']} incorrect")
    if stats.get("last_outcome"):
        pieces.append(f"last outcome: {stats['last_outcome']}")
    return ", ".join(pieces)


def _build_hint_prompt(level, state=None):
    state = state or storage.load_state()
    tags = ", ".join(level.get("tags", []))
    progress = storage.get_progress_summary(state)
    attempt_summary = _attempt_summary_for_level(state, level.get("id"))
    solved_sample = ", ".join(progress.get("recent_solved") or []) or "none"
    return (
        "You are a careful tutoring assistant for Lux puzzle practice. "
        "Give one short hint only. Do not reveal the solution, flag, exact command, or full code. "
        "Prefer a next step, concept reminder, or debugging direction. "
        "Keep the hint concise and practical.\n\n"
        f"Title: {level['title']}\n"
        f"Description: {level['description']}\n"
        f"Category: {level.get('category', 'uncategorized')}\n"
        f"Difficulty: {level.get('difficulty', 'unknown')}\n"
        f"Tags: {tags or 'none'}\n"
        f"Solved progress: {progress.get('solved_count', 0)} solved, "
        f"current streak {progress.get('current_streak', 0)}, "
        f"best streak {progress.get('longest_streak', 0)}\n"
        f"Recent solved levels: {solved_sample}\n"
        f"Attempt history for this level: {attempt_summary}\n"
    )


def ask_hint_via_ollama(level, state=None):
    try:
        import ollama
    except Exception as e:
        raise RuntimeError("Ollama is not available: " + str(e))

    prompt = _build_hint_prompt(level, state=state)
    messages = [{"role": "user", "content": prompt}]
    last_error = None
    for model in _configured_hint_models():
        try:
            res = ollama.chat(model=model, messages=messages)
            content = getattr(getattr(res, "message", None), "content", "")
            hint = _safe_hint_text(content)
            if hint:
                return hint
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError(f"Unable to generate a hint with Ollama: {last_error}")


def print_levels(levels, solved_set=None, state=None):
    print("\nAvailable levels:")
    ordered = cli.sort_levels(levels, solved_set)
    for lvl in ordered:
        print("  ", cli.format_level_line(lvl, solved_set))
    if state is None:
        try:
            state = storage.load_state()
        except Exception:
            state = None
    if state:
        print("\nProgress:")
        print("  " + cli.format_progress_summary(state, levels))
    # show achievement summary
    try:
        ach = state.get("achievements", {})
        if ach:
            print("\nAchievements:")
            for k, v in ach.items():
                print(f"  - {v.get('title', '?')} ({k}) unlocked: {v.get('unlocked_at')}")
    except Exception:
        pass


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


def _persist_attempt_state(state, choice, lvl, attempt_preview, correct):
    storage.record_attempt(
        state,
        choice,
        correct=correct,
        title=lvl.get("title"),
        difficulty=lvl.get("difficulty"),
        category=lvl.get("category"),
        attempt_preview=attempt_preview,
    )
    if correct:
        stats = storage.get_level_attempt_stats(state, choice)
        storage.mark_solved(
            state,
            choice,
            attempts=stats.get("attempts", 1),
            title=lvl.get("title"),
            difficulty=lvl.get("difficulty"),
            category=lvl.get("category"),
        )
        try:
            game_systems.on_level_solved(state, lvl)
        except Exception:
            pass
        try:
            levels = list_levels()
        except Exception:
            levels = []
        newly = achievements.evaluate_achievements(state, levels)
        try:
            leaderboard.upsert_local_entry(state, levels)
        except Exception:
            pass
        if newly:
            print("New achievements unlocked:")
            for a in newly:
                print(f"  - {a.get('title')} ({a.get('id')})")
    storage.save_state(state)


def _submit_text_attempt(choice, lvl):
    attempt = input("Enter your answer/command: ").strip()
    try:
        res = submit_attempt(choice, attempt)
    except Exception as e:
        print("Submission failed:", e)
        return False
    state = storage.load_state()
    if res.get("correct"):
        print("Correct! Level solved.")
        try:
            _persist_attempt_state(state, choice, lvl, attempt, True)
        except Exception:
            pass
        return True
    try:
        _persist_attempt_state(state, choice, lvl, attempt, False)
    except Exception:
        pass
    print("Incorrect or tests failed.")
    if res.get("output"):
        print(res["output"])
    return False


def _submit_script_attempt(choice, lvl):
    files = read_files_from_paths()
    if not files:
        print("No files provided; canceling attempt.")
        return False
    try:
        res = submit_files(choice, files)
    except Exception as e:
        print("Submission failed:", e)
        return False
    state = storage.load_state()
    if res.get("correct"):
        print("Correct! Level solved.")
        try:
            _persist_attempt_state(state, choice, lvl, None, True)
        except Exception:
            pass
        return True
    try:
        _persist_attempt_state(state, choice, lvl, None, False)
    except Exception:
        pass
    print("Incorrect or tests failed.")
    if res.get("output"):
        print(res["output"])
    return False


def handle_attempt(choice, lvl):
    if lvl.get("validator") == "script":
        return _submit_script_attempt(choice, lvl)
    return _submit_text_attempt(choice, lvl)


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
                print("Hint:\n", ask_hint_via_ollama(lvl, state=storage.load_state()))
            except Exception as e:
                print("Hint failed:", e)
            continue
        if cmd in ("a", "attempt"):
            if handle_attempt(choice, lvl):
                return
            continue
        print("Unknown option — choose 'a', 'h', or 'b'.")


def _handle_menu_choice(choice, state, levels):
    lowered = choice.lower()
    if lowered in ("ach", "achievements"):
        ach = state.get("achievements", {})
        if not ach:
            print("No achievements unlocked yet.")
        else:
            print("Achievements:")
            for k, v in ach.items():
                print(f"  - {v.get('title', '?')} ({k}) unlocked: {v.get('unlocked_at')}")
        return True
    if lowered in ("stats", "progress"):
        print(cli.format_progress_summary(state, levels))
        return True
    if lowered in ("reset-ach", "reset-achievements"):
        confirm = input("Are you sure you want to reset all achievements? type 'yes' to confirm: ")
        if confirm.strip().lower() == "yes":
            state["achievements"] = {}
            storage.save_state(state)
            print("Achievements cleared.")
        else:
            print("Reset cancelled.")
        return True
    if lowered in ("path", "learning-path", "recommend"):
        try:
            path = learning_paths.build_learning_path(state, levels)
            print(path.get("summary"))
            print("Recommended levels:")
            for item in path.get("recommended_levels", []):
                print(
                    f"  - {item.get('id')}: {item.get('title')} "
                    f"({item.get('category')} · {item.get('difficulty')})"
                )
        except Exception as exc:
            print("Learning path unavailable:", exc)
        return True
    if lowered in ("daily",):
        try:
            daily = game_systems.daily_challenge_status(state, levels)
            level = daily.get("level", {})
            print(
                f"Daily challenge ({daily.get('date')}): {level.get('id')} - {level.get('title')}"
            )
            print("Completed today:" if daily.get("completed_today") else "Not completed yet.")
        except Exception as exc:
            print("Daily challenge unavailable:", exc)
        return True
    return False


def main():
    print("Interactive Puzzle Agent — connect to the puzzle server and request hints.")
    while True:
        state = storage.load_state()
        levels = list_levels()
        print_levels(levels, storage.get_solved_levels(state), state=state)
        print(
            "Options: enter a level id to open it, 'ach' to list achievements, "
            "'stats' for progress, 'path' for recommendations, "
            "'daily' for today's challenge, 'reset-ach' to clear achievements, "
            "or 'q' to quit."
        )
        choice = input("Choose level id (or 'q' to quit): ").strip()
        if choice.lower() in ("q", "quit", "exit"):
            break
        if _handle_menu_choice(choice, state, levels):
            continue
        handle_level(choice)


if __name__ == "__main__":
    main()
