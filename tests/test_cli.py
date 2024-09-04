"""Tests for the `cli` module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from falcon import cli, debug


@patch("falcon.cli.init")
def test_main(mock_init: Mock) -> None:
    """Basic CLI test."""
    mock_init.side_effect = SystemExit(0)
    with pytest.raises(SystemExit):
        assert cli.main(["database.db", "input.txt"]) == 0
    mock_init.assert_called_once_with("database.db", "input.txt")


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-h"])
    captured = capsys.readouterr()
    assert "give-me-the-odds" in captured.out


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    """Show version.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-V"])
    captured = capsys.readouterr()
    assert debug.get_version() in captured.out


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
