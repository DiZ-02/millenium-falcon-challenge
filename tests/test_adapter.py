from unittest.mock import Mock, patch

import pytest

from falcon.adapter import Job
from falcon.models import Falcon


def test_from_config_set_too_big_autonomy() -> None:
    with pytest.raises(ValueError, match=r"autonomy=\d+ must be less then \d+."):
        Job.from_config(
            Falcon(
                autonomy=2**30,
            ),
        )


@patch("falcon.adapter.DbService")
def test_generate_graph_load_too_many_nodes(mock_db: Mock) -> None:
    mock_db.return_value = Mock()
    mock_db.return_value.get_nodes.return_value = 2**15 * [""]

    with pytest.raises(ValueError, match=r"number_of_nodes=\d+ must be less than \d+."):
        Job.from_config(Falcon()).generate_graph()


def test_get_odds_without_running_search_path() -> None:
    with pytest.raises(ValueError, match="Result is null, please run path search."):
        Job.from_config(Falcon()).get_odds()
