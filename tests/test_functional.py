import json
from pathlib import Path

import pytest

from falcon import cli


class TestExample:
    def test_search_path_on_examples(
        self,
        examples: tuple[Path, Path, Path],
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Output result for safest path search on examples.

        Parameters:
            capsys: Pytest fixture to capture output.
        """
        config, input_, answer = examples
        cli.main([str(config), str(input_)])
        captured = capsys.readouterr()
        with answer.open() as f:
            odds = json.load(f).get("odds")
        assert str(odds) in captured.out
