# Code and command walkthrough

This guide explains the important parts of the implementation. The complete executable files are in [src](../src), [tests](../tests), and [diagnose.py](../diagnose.py). Code excerpts below are explanations of those files, not additional modules to create.

## 1. Keep file handling separate

In [log_handler.py](../src/log_handler.py):

```python
self.log_path = Path(log_path)
self.log_path.parent.mkdir(parents=True, exist_ok=True)
self._file = self.log_path.open("a", encoding="utf-8")
```

`Path` manages filenames. `mkdir` creates missing parent folders. Append mode (`a`) preserves earlier log content instead of replacing it, and UTF-8 supports non-English text. A filename such as `events.log` also works because its parent resolves to the current directory.

`write()` adds text to the open file. Python may buffer it in memory; `flush()` passes buffered text to the operating system, while `close()` flushes and releases the file handle. This is useful on Windows because an open handle can prevent deletion. It is not a promise of disk persistence after power loss.

```python
with LogHandler(path) as handler:
    handler.write("hello")
```

The context manager calls `close()` when the block ends, including when an exception occurs. A test verifies cleanup on that failure path.

## 2. Clear an open file correctly

```python
self._file.flush()
self._file.seek(0)
self._file.truncate(0)
```

Flushing first prevents old buffered text from reappearing after a clear. Seeking moves the cursor to the beginning; truncating removes the contents. The parameterized clear test checks both open and closed files, then checks that an open handler can write new text.

## 3. Normalize a key event

In [keylogger.py](../src/keylogger.py):

```python
try:
    char = key.char
except AttributeError:
    name = getattr(key, "name", None)
    char = f"[{name}]" if isinstance(name, str) and name else None
```

A character event supplies `.char`. A named special key supplies a readable label such as `[shift]`. Invalid or empty values are ignored. This is an event log: `[backspace]` would be a token, not an instruction to erase an earlier character.

```python
self.handler.write(char)
self._buffer.append(char)
```

Writing happens before the in-memory event is added. If a direct write raises an exception, this sequence does not add a misleading successful buffer entry. The file and buffer still are not a database transaction, and delayed storage failures are possible.

`get_buffer()` returns a copy so callers cannot change internal state by editing the returned list. `clear_buffer()` clears memory only; it does not delete the file.

## 4. Inject a listener to make testing independent

```python
self._listener_factory = listener_factory or windows_listener_factory
```

The normal factory constructs a Windows `pynput` listener only when `start()` is called. Tests pass a `MagicMock` factory instead. This substitution is dependency injection: the event module uses the supplied dependency without needing to know whether it is a real listener or a test double.

In [test_keylogger.py](../tests/test_keylogger.py):

```python
factory = MagicMock()
with Keylogger(tmp_path / "events.log", listener_factory=factory) as value:
    yield value
```

The fixture gives each test a separate log and ensures shutdown afterward. Assertions such as `start.assert_called_once()` verify how our code uses the listener interface. They do not prove that a real Windows hook starts successfully.

## 5. Test input without typing

```python
logger.on_press(SimpleNamespace(char="a"))
assert logger.get_buffer() == ["a"]
```

`SimpleNamespace` supplies the small event shape the handler expects. Calling the handler directly makes the test reproducible and independent of typing speed, focus, and hardware. Other cases check order, special keys, unknown events, and persisted file text.

```python
@pytest.mark.parametrize("name", ["shift", "enter", "f1", "space"])
def test_special_keys(logger, name):
    logger.on_press(SimpleNamespace(name=name))
    assert logger.get_buffer() == [f"[{name}]"]
```

One test function runs four cases. That is why the number of collected tests is larger than the number of test functions.

## 6. Flush periodically and shut down cleanly

```python
while not self._stop_event.wait(self.flush_interval):
    self.handler.flush()
```

This excerpt shows the worker's scheduling pattern; the full method also catches and stores exceptions. `Event.wait()` provides an interruptible delay. Stop signals the event so shutdown need not wait for a whole interval. The timing test uses another event to wait for observed flushing, rather than assuming a fixed sleep is sufficient.

Shutdown rejects late callbacks, stops and joins the listener, joins the worker, and closes the log through `finally` blocks. A simulated join failure test confirms the file still closes. A simulated disk-full error is saved by the worker and reported at `stop()`. It is not automatic disk-error recovery.

`RLock` protects shared file/buffer operations. It allows a method such as `read_log()` to call another locked method such as `flush()` on the same thread. It does not make concurrent calls to `start()` and `stop()` supported, or coordinate separate processes.

## 7. Check prerequisites before investigating code

In [diagnose.py](../diagnose.py), `version(package)` checks installed distribution metadata. A temporary file checks actual write access, and `importlib.import_module()` checks that project modules load.

`main()` returns `0` for success and `1` for failure. Scripts and CI can use these exit codes without trying to interpret printed text. `--live` adds platform and package checks; it neither imports the `pynput` backend nor starts capture.

The tests deliberately simulate a missing package and a non-Windows platform. Expected failures should produce a helpful result rather than crash the diagnostic tool.

## 8. Understand the commands

| Command | Why it is used |
|---|---|
| `py -m venv .venv` | Creates a project-specific Python environment. |
| `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` | Installs packages into that exact environment. `-m` tells Python to run the pip module. |
| `.\.venv\Scripts\python.exe -m pytest tests/ -v` | Discovers tests and displays each test name and result. |
| `--tb=short` | Keeps failure tracebacks concise while preserving the failed assertion and location. |
| `.\.venv\Scripts\python.exe diagnose.py --live` | Checks Windows prerequisites without recording input. |
| `Select-String ... -Pattern "36 passed\|All checks passed"` | Checks that the saved report contains both completion markers. |

The initial `python.exe pip install ...` command failed because Python interpreted `pip` as a filename. Adding `-m` correctly runs the installed module. The saved report was also checked independently of earlier terminal output: a visible prior success does not prove that success was written to the file.

## 9. Make results easy to reproduce

[requirements.txt](../requirements.txt) records dependency ranges, [pyproject.toml](../pyproject.toml) specifies test discovery, and [.gitignore](../.gitignore) excludes environments, caches, and local logs. The Windows screenshot environment used pytest 9.1.1; the separately labeled macOS verification uses the exact versions recorded in its report. A passing run applies to that code and environment, not every Python/Windows combination.

The [CI workflow](../.github/workflows/tests.yml) automates the same checks on Windows and Linux for each pushed revision. `checkout` retrieves the code and `setup-python` selects Python 3.14, following the official [checkout](https://github.com/actions/checkout) and [setup-python](https://github.com/actions/setup-python) usage. The workflow uses read-only repository permissions and a ten-minute job limit. It never starts the real listener. Review the run attached to the commit before claiming that revision passed CI.
