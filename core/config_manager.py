import json
import os
import sys
from pathlib import Path

def get_data_dir() -> Path:
    if getattr(sys, 'frozen', False):
        if sys.platform == 'darwin':
            data_dir = Path.home() / "Library" / "Application Support" / "SmartScanner"
        elif sys.platform == 'win32':
            data_dir = Path(os.environ.get("APPDATA", Path.home())) / "SmartScanner"
        else:
            data_dir = Path.home() / ".smartscanner"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    return Path.cwd()

def load_config() -> dict:
    config_path = get_data_dir() / "config.json"
    if not config_path.exists() and getattr(sys, 'frozen', False):
        try:
            bundled_path = Path(sys._MEIPASS) / "config.json"
            if bundled_path.exists():
                import shutil
                shutil.copy(bundled_path, config_path)
        except Exception as e:
            print(f"Error initializing config from bundle: {e}")

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    return {}

def save_config(settings: dict):
    config_path = get_data_dir() / "config.json"
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_target_folder() -> str:
    config = load_config()
    return config.get("target_folder", "")

