"""Thread-safe UTF-8 append logging with explicit resource ownership."""

from pathlib import Path
from threading import RLock


class LogHandler:
    def __init__(self, log_path):
        self.log_path = Path(log_path)
        self._lock = RLock()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.log_path.open("a", encoding="utf-8")

    def write(self, data: str):
        with self._lock:
            if not self._file.closed:
                self._file.write(data)

    def flush(self):
        with self._lock:
            if not self._file.closed:
                self._file.flush()

    def close(self):
        with self._lock:
            self._file.close()

    def read_log(self):
        with self._lock:
            self.flush()
            try:
                return self.log_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                return ""

    def clear_log(self):
        with self._lock:
            if not self._file.closed:
                self._file.flush()
                self._file.seek(0)
                self._file.truncate(0)
            elif self.log_path.exists():
                self.log_path.write_text("", encoding="utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
