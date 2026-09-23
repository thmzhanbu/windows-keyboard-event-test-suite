from importlib.metadata import PackageNotFoundError

import diagnose


def test_writable_directory_created(tmp_path):
    path = tmp_path / "logs"
    assert diagnose.check_logs(path)
    assert list(path.iterdir()) == []


def test_file_in_place_of_directory(tmp_path):
    path = tmp_path / "file"
    path.write_text("preserved")
    assert not diagnose.check_logs(path)
    assert path.read_text() == "preserved"


def test_missing_package(monkeypatch, capsys):
    def missing(name):
        raise PackageNotFoundError(name)
    monkeypatch.setattr(diagnose, "version", missing)
    assert not diagnose.check_packages()
    assert "pip install" in capsys.readouterr().out


def test_live_preflight_rejects_non_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(diagnose.sys, "platform", "darwin")
    monkeypatch.setattr(diagnose, "ROOT", tmp_path)
    monkeypatch.setattr(diagnose, "check_packages", lambda live: True)
    assert diagnose.main(["--live"]) == 1


def test_default_preflight(monkeypatch, tmp_path):
    monkeypatch.setattr(diagnose, "ROOT", tmp_path)
    assert diagnose.main([]) == 0
