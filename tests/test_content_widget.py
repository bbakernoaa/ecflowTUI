# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Tests for the MainContent widget.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from textual.widgets import RichLog, Static

from ectop.widgets.content import MainContent


@pytest.fixture
def content_widget() -> MainContent:
    """
    Fixture to create a MainContent widget.

    Returns
    -------
    MainContent
        The widget instance.
    """
    return MainContent()


def test_content_initialization(content_widget: MainContent) -> None:
    """
    Test that the MainContent initializes correctly.

    Parameters
    ----------
    content_widget : MainContent
        The widget to test.

    Returns
    -------
    None
    """
    assert content_widget.is_live is False
    assert content_widget.last_log_size == 0
    assert "tab_output" in content_widget._content_cache


def test_update_log(content_widget: MainContent) -> None:
    """
    Test updating the log content and cache.

    Parameters
    ----------
    content_widget : MainContent
        The widget to test.

    Returns
    -------
    None
    """
    with patch("textual.widgets.RichLog.write"), patch("textual.widgets.RichLog.clear"):
        # Mocking the widget retrieval
        mock_log = MagicMock(spec=RichLog)
        content_widget.query_one = MagicMock(return_value=mock_log)

        content_widget.update_log("Initial log content")
        assert content_widget._content_cache["tab_output"] == "Initial log content"
        mock_log.clear.assert_called_once()
        mock_log.write.assert_called_with("Initial log content")


def test_update_script(content_widget: MainContent) -> None:
    """
    Test updating the script content and cache.

    Parameters
    ----------
    content_widget : MainContent
        The widget to test.

    Returns
    -------
    None
    """
    mock_static = MagicMock(spec=Static)
    content_widget.query_one = MagicMock(return_value=mock_static)

    content_widget.update_script("echo 'hello'")
    assert content_widget._content_cache["tab_script"] == "echo 'hello'"
    mock_static.update.assert_called_once()


def test_search_feedback(content_widget: MainContent) -> None:
    """
    Test the search notification logic.

    Parameters
    ----------
    content_widget : MainContent
        The widget to test.

    Returns
    -------
    None
    """
    content_widget._content_cache["tab_output"] = "line 1\nline 2 with error\nline 3 error"

    # Mocking the active property and app property
    with patch.object(MainContent, "active", new_callable=PropertyMock) as mock_active, patch.object(
        MainContent, "app", new_callable=PropertyMock
    ) as mock_app_prop:
        mock_active.return_value = "tab_output"
        mock_app = MagicMock()
        mock_app_prop.return_value = mock_app

        # Mock event
        mock_event = MagicMock()
        mock_event.input.id = "content_search"
        mock_event.value = "error"

        content_widget.on_input_submitted(mock_event)

        # Should find 2 matches
        msg = "Found 2 matches for 'error' in output"
        mock_app.notify.assert_called_with(msg)
