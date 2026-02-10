"""
ecFlow Client Wrapper for ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

import ecflow

# --- State Icons ---
STATE_MAP: dict[str, str] = {
    "unknown": "⚪",
    "complete": "🟢",
    "queued": "🔵",
    "aborted": "🔴",
    "submitted": "🟡",
    "active": "🔥",
    "suspended": "🟠",
}


class EcflowClient:
    """
    A wrapper around ecflow.Client providing simplified access and error handling.

    Parameters
    ----------
    host : str
        The hostname of the ecFlow server.
    port : int
        The port of the ecFlow server.
    """

    def __init__(self, host: str = "localhost", port: int = 3141) -> None:
        self.host: str = host
        self.port: int = port
        self.client: ecflow.Client = ecflow.Client(host, port)

    def ping(self) -> None:
        """
        Pings the ecFlow server.

        Raises
        ------
        RuntimeError
            If the server is unreachable or another network error occurs.
        """
        try:
            self.client.ping()
        except RuntimeError as e:
            raise RuntimeError(f"Failed to ping server {self.host}:{self.port}: {e}") from e

    def sync_local(self) -> None:
        """
        Synchronizes the local definition with the server.

        Raises
        ------
        RuntimeError
            If synchronization fails.
        """
        try:
            self.client.sync_local()
        except RuntimeError as e:
            raise RuntimeError(f"Failed to sync with server {self.host}:{self.port}: {e}") from e

    def get_defs(self) -> ecflow.Defs | None:
        """
        Returns the current definitions from the client.

        Returns
        -------
        ecflow.Defs | None
            The current definitions, or None if not available.
        """
        return self.client.get_defs()

    def file(self, path: str, file_type: str) -> str:
        """
        Fetches a file (log, script, etc.) from the server for a given node path.

        Parameters
        ----------
        path : str
            The absolute path to the node.
        file_type : str
            The type of file to fetch (e.g., 'jobout', 'script', 'job').

        Returns
        -------
        str
            The content of the file.

        Raises
        ------
        RuntimeError
            If the file cannot be fetched.
        """
        try:
            return self.client.file(path, file_type)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to fetch {file_type} for {path}: {e}") from e

    def suspend(self, path: str) -> None:
        """
        Suspends a node.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the command fails.
        """
        try:
            self.client.suspend(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to suspend {path}: {e}") from e

    def resume(self, path: str) -> None:
        """
        Resumes a suspended node.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the command fails.
        """
        try:
            self.client.resume(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to resume {path}: {e}") from e

    def kill(self, path: str) -> None:
        """
        Kills a running node.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the command fails.
        """
        try:
            self.client.kill(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to kill {path}: {e}") from e

    def force_complete(self, path: str) -> None:
        """
        Forces a node to complete state.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the command fails.
        """
        try:
            self.client.force_complete(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to force complete {path}: {e}") from e

    def alter(self, path: str, alter_type: str, name: str, value: str = "") -> None:
        """
        Alters a node attribute.

        Parameters
        ----------
        path : str
            The absolute path to the node.
        alter_type : str
            The type of alteration (e.g., 'change', 'add_variable').
        name : str
            The name of the attribute or variable.
        value : str, optional
            The new value.

        Raises
        ------
        RuntimeError
            If the command fails.
        """
        try:
            self.client.alter(path, alter_type, name, value)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to alter {path} ({alter_type} {name}): {e}") from e

    def requeue(self, path: str) -> None:
        """
        Re-queues a node.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the command fails.
        """
        try:
            self.client.requeue(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to requeue {path}: {e}") from e
