"""Tests for the `cli` module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from falcon import cli, debug
from falcon.debug import _interpreter_name_version, get_version


@patch("falcon.cli.init")
@patch("falcon.cli.PathService", new=Mock())
def test_main(mock_init: Mock) -> None:
    """Basic CLI test."""
    with patch("falcon.cli.get_service"):
        assert cli.main(["config-no_db.json", "empire.json"]) == 0
    mock_init.assert_called_once_with("config-no_db.json", "empire.json")


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-h"])
    captured = capsys.readouterr()
    assert "give-me-the-odds" in captured.out


def test_get_version() -> None:
    """Get version."""
    assert get_version() != "0.0.0"
    assert get_version("package-not-found") == "0.0.0"


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    """Show version.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-V"])
    captured = capsys.readouterr()
    assert debug.get_version() in captured.out


@patch("falcon.debug.sys")
def test_interpreter_name_version(mock_sys: Mock) -> None:
    mock_sys.implementation.name = "pytest"
    mock_sys.implementation.version = Mock(
        major=1,
        minor=2,
        micro=3,
        releaselevel="candidate",
        serial="0123",
    )
    assert _interpreter_name_version() == ("pytest", "1.2.3c0123")

    del mock_sys.implementation
    assert _interpreter_name_version() == ("", "0.0.0")


def test_show_debug_info(capsys: pytest.CaptureFixture) -> None:
    """Show debug information.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["--debug-info"])
    captured = capsys.readouterr().out.lower()
    assert "python" in captured
    assert "system" in captured
    assert "environment" in captured
    assert "packages" in captured
