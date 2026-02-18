# #############################################################################
# WARNING: If you modify features, API, or usage, you MUST update the
# documentation immediately.
# #############################################################################
"""
Tests for the StatusBar widget.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

from __future__ import annotations

from ectop.widgets.statusbar import StatusBar


def test_statusbar_initialization() -> None:
    """
    Test that the StatusBar initializes with default values.

    Returns
    -------
    None
    """
    bar = StatusBar()
    assert bar.server_info == "Disconnected"
    assert bar.last_sync == "Never"
    assert bar.status == "Unknown"


def test_statusbar_update() -> None:
    """
    Test that the StatusBar updates correctly.

    Returns
    -------
    None
    """
    bar = StatusBar()
    bar.update_status("test-host", 1234, "RUNNING")
    assert bar.server_info == "test-host:1234"
    assert bar.status == "RUNNING"
    assert bar.last_sync != "Never"


def test_statusbar_render() -> None:
    """
    Test that the StatusBar renders with correct colors based on status.

    Returns
    -------
    None
    """
    bar = StatusBar()

    # Running status (Green)
    bar.update_status("host", 3141, "RUNNING")
    rendered = bar.render()
    assert "RUNNING" in str(rendered)

    # Halted status (Orange)
    bar.update_status("host", 3141, "HALTED")
    rendered = bar.render()
    assert "HALTED" in str(rendered)

    # Error status (Red)
    bar.update_status("host", 3141, "Error")
    rendered = bar.render()
    assert "Error" in str(rendered)
