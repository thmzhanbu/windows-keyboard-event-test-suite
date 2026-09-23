import pytest

from src.log_handler import LogHandler


@pytest.fixture
def handler(tmp_path):
    with LogHandler(tmp_path / "nested" / "events.log") as value:
        yield value


def test_file_created(handler):
    assert handler.log_path.is_file()


def test_write_flushes_to_disk(handler):
    handler.write("abc")
    handler.flush()
    assert handler.log_path.read_text(encoding="utf-8") == "abc"


def test_reopen_appends(handler):
    handler.write("first")
    handler.close()
    with LogHandler(handler.log_path) as second:
        second.write("second")
    assert handler.read_log() == "firstsecond"


def test_read_flushes_pending_text(handler):
    handler.write("café 日本語 🙂")
    assert handler.read_log() == "café 日本語 🙂"


@pytest.mark.parametrize("closed", [False, True])
def test_clear_log(handler, closed):
    handler.write("pending data")
    if closed:
        handler.close()
    handler.clear_log()
    assert handler.read_log() == ""
    if not closed:
        handler.write("new")
        assert handler.read_log() == "new"


def test_closed_operations_are_safe(handler):
    handler.close()
    handler.write("ignored")
    handler.flush()
    handler.close()
    assert handler.read_log() == ""


def test_filename_without_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with LogHandler("events.log") as handler:
        handler.write("ok")
    assert (tmp_path / "events.log").read_text() == "ok"


def test_missing_log_returns_empty(handler):
    handler.close()
    handler.log_path.unlink()
    assert handler.read_log() == ""


def test_context_closes_on_exception(tmp_path):
    with pytest.raises(RuntimeError):
        with LogHandler(tmp_path / "events.log") as handler:
            handler.write("saved")
            raise RuntimeError("test")
    assert handler._file.closed
    assert handler.read_log() == "saved"
