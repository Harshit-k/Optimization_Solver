"""
utils/session.py
Stores the full pipeline state so nothing is lost between steps.
Saves to a timestamped JSON file at the end.
"""

import json
import os
from datetime import datetime


class Session:
    def __init__(self):
        self._data = {}
        self._timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def set(self, key: str, value):
        self._data[key] = value

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def save(self, directory: str = ".") -> str:
        os.makedirs(directory, exist_ok=True)
        filename = f"session_{self._timestamp}.json"
        path = os.path.join(directory, filename)
        with open(path, "w") as f:
            json.dump(self._data, f, indent=2)
        return path
