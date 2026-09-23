# Interview preparation

## A 45-second project explanation

“I completed a guided Python testing lab in a Windows 11 virtual machine. The project separates keyboard-event handling from file logging and uses automated tests to check normal behavior, invalid input, and simulated failures. I ran 36 tests successfully and saved the results alongside environment diagnostics and screenshots. The tests use synthetic events and mock listeners, so the evidence demonstrates the program's logic and cleanup behavior. It does not demonstrate real Windows keyboard capture. My main learning was how to isolate dependencies, handle files reliably, investigate command errors, and make the results reproducible and easy to review.”

## Questions to practice

### 1. How does an event move through the program?

[`Keylogger.on_press`](../src/keylogger.py) extracts a character or a special-key name. It passes the resulting text to `LogHandler.write` and adds it to an in-memory list. [`LogHandler`](../src/log_handler.py) manages the UTF-8 file. `get_buffer()` returns a copy, so modifying that returned list cannot change the internal buffer. `clear_buffer()` clears memory only; it does not erase the saved log. The buffer-copy test verifies both behaviors.

### 2. How did you test keyboard events without typing or collecting real input?

The constructor accepts `listener_factory`, which is dependency injection: the caller supplies the component that creates a listener. The fixture in [`test_keylogger.py`](../tests/test_keylogger.py) supplies `MagicMock`, while event tests call `on_press` with a `SimpleNamespace` containing a character or key name. The lifecycle test checks that the mock listener is started and stopped as expected. This makes tests repeatable and avoids requiring desktop keyboard access. A mock cannot prove that the real Windows listener will behave correctly.

### 3. How did you keep file tests independent and clean up resources?

[`test_log_handler.py`](../tests/test_log_handler.py) uses pytest's `tmp_path` to give each test a separate temporary directory. Context managers close handlers after each fixture or test, including when an exception occurs. The missing-file test explicitly closes the handler before deleting its file. This matters on Windows, where an open file handle can prevent deletion. `Keylogger.stop()` also uses nested `finally` blocks so a listener-join failure still leads to worker cleanup and file closure.

### 4. What happens with special keys and Unicode?

[`on_press`](../src/keylogger.py) records names such as `[shift]`, `[enter]`, `[f1]`, and `[space]`. Unknown or empty values are ignored. Tests verify these representations, and the current tests exercise Unicode text through UTF-8 logging. This is an event record, not a reconstruction of the final text in an editor: Backspace is not implemented as deleting a previous character. Real keyboard layouts, dead keys, modifier combinations, and input-method editors still need integration testing.

### 5. Why are there locks, and what do they not guarantee?

The callback and periodic flush worker can access shared state. `Keylogger` protects its buffer and closed state with an `RLock`; `LogHandler` protects operations on its file. A reentrant lock also lets `read_log()` call `flush()` while already holding the same lock. These are protections within an instance. They do not coordinate separate processes or separate handlers targeting one file. Concurrent `start()` and `stop()` calls are not fully synchronized, and the existing tests are not a concurrency stress test.

### 6. Does flushing mean the data is permanently safe?

No. [`flush()`](../src/log_handler.py) moves Python's buffered data toward the operating system, and a normal `close()` also flushes buffered output. Neither proves that data survives a power failure; this project does not call `os.fsync`. `test_periodic_flush` confirms that text becomes readable through another file read. The simulated disk-full test checks error reporting during `stop()`. It does not reproduce an actual full disk, and a background flush failure does not immediately stop the listener.

### 7. What do the 36 passing tests and preflight checks prove?

The Windows screenshots show 10 log-handler, 21 event-handling, and 5 diagnostic tests passing. These verify the cases written into the suite; the count is not a coverage percentage. [`diagnose.py`](../diagnose.py) checks Python, package metadata, source imports, and directory writability. Its `--live` option additionally checks Windows and the installed `pynput` distribution. It does not import the real backend or start a listener. Actual capture, long-running performance, bounded memory, and bounded shutdown remain unverified.

### 8. What did you troubleshoot?

An installation command omitted `-m`, causing Python to look for a file named `pip`. The corrected form, `python.exe -m pip`, runs pip as a module in the selected environment. A later report check found diagnostics but no test summary; the earlier screenshot shows a malformed `tests-v` argument. I reran the corrected command, saved the output, and searched the report for both `36 passed` and `All checks passed`. `Tee-Object` helped display and save the result; the evidence does not establish output redirection as the cause of the earlier failure.

## How does this relate to your earlier prototype?

“The earlier script helped me learn `pynput` callbacks, special-key handling, append-mode file writing, timestamps, and an Escape stop condition. The later guided lab applies related concepts in separate event-handling and storage components, with mocks and automated tests. It does not import the old script, and it does not retain timestamps or the Escape shortcut. I describe it as a progression in learning and testability rather than claiming a direct integration or complete feature parity.”

The [source comparison](project-evolution.md) provides concrete examples. The macOS permission-warning screenshot and the local log cannot establish a successful capture session tied to that exact run.

## Resume wording

- Completed a guided Windows 11 Python testing lab with 36 passing automated tests covering simulated keyboard events, file logging, lifecycle cleanup, and diagnostic failures.
- Documented validation with Windows lab screenshots and a saved test report, explaining the limits of mocked tests and preflight checks.

Before an interview, practice tracing one event and explaining one failure test without reading these notes. Present this as guided learning with documented execution; use specific code explanations to demonstrate understanding rather than claiming production deployment or independently designed expertise.
