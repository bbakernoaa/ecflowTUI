import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock ecflow before importing the app
sys.modules["ecflow"] = MagicMock()

from ectop import Ectop

def test_app_instantiation():
    """Basic test to check if the App can be instantiated."""
    app = Ectop()
    assert app is not None

@pytest.mark.asyncio
async def test_app_handles_runtime_error():
    """Verify that the app handles a RuntimeError from the client gracefully."""
    # We need to mock the client
    mock_client = MagicMock()
    mock_client.ping.side_effect = RuntimeError("Mock server error")

    with patch("ectop.app.EcflowClient", return_value=mock_client):
        app = Ectop()
        # We use run_test to test Textual apps
        async with app.run_test() as pilot:
            # In on_mount, ping() is called. If it raises RuntimeError, notify is called.
            # We wait for any workers to finish
            await pilot.pause()
            # Check notifications in the app
            # Textual stores notifications in _notifications
            assert len(app._notifications) > 0
            # Check the message of the first notification
            # In newer Textual, notifications are objects with a message attribute (which might be a Renderable)
            notification = list(app._notifications)[0]
            assert "Connection Failed" in str(notification.message)
