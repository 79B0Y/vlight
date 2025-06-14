import os
import json
import logging

BASE_DIR = os.path.expanduser("~/.vlight/state")

def ensure_dir():
    os.makedirs(BASE_DIR, exist_ok=True)

def save_state(device_id, state):
    ensure_dir()
    with open(os.path.join(BASE_DIR, f"{device_id}.json"), "w") as f:
        json.dump(state, f)

def load_state(device_id):
    path = os.path.join(BASE_DIR, f"{device_id}.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        logging.getLogger("vlight").warning(f"Invalid state file {path}: {e}")
        try:
            os.remove(path)
        except OSError:
            pass
        return None
