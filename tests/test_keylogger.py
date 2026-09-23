from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.keylogger import Keylogger, windows_listener_factory


@pytest.fixture
def logger(tmp_path):
    factory = MagicMock()
    with Keylogger(tmp_path / "events.log", listener_factory=factory) as value:
        yield value


def test_character_captured(logger):
    logger.on_press(SimpleNamespace(char="a"))
    assert logger.get_buffer() == ["a"]


def test_characters_in_order(logger):
    for char in "hello🙂":
        logger.on_press(SimpleNamespace(char=char))
    assert logger.get_buffer() == list("hello🙂")
    assert logger.handler.read_log() == "hello🙂"


@pytest.mark.parametrize("name", ["shift", "enter", "f1", "space"])
def test_special_keys(logger, name):
    logger.on_press(SimpleNamespace(name=name))
    assert logger.get_buffer() == [f"[{name}]"]


@pytest.mark.parametrize("key", [SimpleNamespace(char=None), object(),
                                  SimpleNamespace(char="")])
def test_unknown_keys_ignored(logger, key):
    logger.on_press(key)
    assert logger.get_buffer() == []
    assert logger.handler.read_log() == ""


def test_buffer_copy_and_clear(logger):
    logger.on_press(SimpleNamespace(char="x"))
    copy = logger.get_buffer()
    copy.append("external")
    assert logger.get_buffer() == ["x"]
    logger.clear_buffer()
    assert logger.get_buffer() == []
    assert logger.handler.read_log() == "x"


def test_start_stop_uses_injected_listener(logger):
    factory = logger._listener_factory
    logger.start()
    logger.start()
    factory.assert_called_once_with(on_press=logger.on_press)
    factory.return_value.start.assert_called_once()
    assert logger._running
    logger.stop()
    factory.return_value.stop.assert_called_once()
    factory.return_value.join.assert_called_once()
    assert logger.listener is None
    assert not logger._running
    assert logger.handler._file.closed


def test_stop_persists_and_ignores_late_callbacks(logger):
    logger.on_press(SimpleNamespace(char="q"))
    logger.stop()
    logger.stop()
    logger.on_press(SimpleNamespace(char="late"))
    assert logger.handler.read_log() == "q"
    assert logger.get_buffer() == ["q"]
    with pytest.raises(RuntimeError, match="closed"):
        logger.start()


def test_failed_start_closes_resources(logger):
    logger._listener_factory.return_value.start.side_effect = RuntimeError("hook failed")
    logger._listener_factory.return_value.ident = None
    with pytest.raises(RuntimeError, match="hook failed"):
        logger.start()
    assert logger.handler._file.closed
    assert not logger._running


@pytest.mark.parametrize("interval", [0, -1, float("inf"), float("nan")])
def test_invalid_interval(tmp_path, interval):
    with pytest.raises(ValueError):
        Keylogger(tmp_path / "events.log", interval)
    assert not (tmp_path / "events.log").exists()


def test_periodic_flush(tmp_path):
    flushed = Event()
    with Keylogger(tmp_path / "events.log", 0.01,
                   listener_factory=MagicMock()) as logger:
        original = logger.handler.flush

        def flush():
            original()
            flushed.set()

        logger.handler.flush = flush
        logger.on_press(SimpleNamespace(char="pending"))
        logger.start()
        assert flushed.wait(2), "Background flush did not run"
        assert logger.handler.log_path.read_text() == "pending"
    assert not logger._worker.is_alive()


def test_default_backend_rejects_non_windows(monkeypatch):
    monkeypatch.setattr("src.keylogger.sys.platform", "darwin")
    with pytest.raises(RuntimeError, match="Windows"):
        windows_listener_factory(on_press=lambda key: None)


def test_listener_join_failure_still_closes_log(logger):
    logger.start()
    logger._listener_factory.return_value.join.side_effect = RuntimeError("callback failed")
    with pytest.raises(RuntimeError, match="callback failed"):
        logger.stop()
    assert logger.handler._file.closed
    assert not logger._worker.is_alive()


def test_background_flush_failure_reported(tmp_path):
    logger = Keylogger(tmp_path / "events.log", 0.01,
                       listener_factory=MagicMock())
    logger.handler.flush = MagicMock(side_effect=OSError("disk full"))
    try:
        logger.start()
        logger._worker.join(timeout=2)
        assert not logger._worker.is_alive()
        with pytest.raises(RuntimeError, match="Periodic log flush failed") as error:
            logger.stop()
        assert isinstance(error.value.__cause__, OSError)
        assert logger.handler._file.closed
    finally:
        logger._flush_error = None
        logger.stop()
