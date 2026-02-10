"""
Main Application class for ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header, Input

from ectop.client import EcflowClient
from ectop.widgets.content import MainContent
from ectop.widgets.modals.variables import VariableTweaker
from ectop.widgets.modals.why import WhyInspector
from ectop.widgets.search import SearchBox
from ectop.widgets.sidebar import SuiteTree

# --- Configuration ---
ECFLOW_HOST = "localhost"
ECFLOW_PORT = 3141


class Ectop(App):
    """A Textual-based TUI for monitoring and controlling ecFlow."""

    CSS = """
    Screen {
        background: #1a1b26;
    }

    /* Left Sidebar (Tree) */
    #sidebar {
        width: 30%;
        height: 100%;
        border-right: solid #565f89;
        background: #16161e;
    }

    Tree {
        background: #16161e;
        color: #a9b1d6;
        padding: 1;
    }

    /* Right Content (Tabs) */
    #main_content {
        width: 70%;
        height: 100%;
    }

    TabbedContent {
        height: 100%;
    }

    /* Content Areas */
    RichLog {
        background: #24283b;
        color: #c0caf5;
        border: none;
    }

    .code_view {
        background: #24283b;
        padding: 1;
        width: 100%;
        height: auto;
    }

    #search_box {
        dock: top;
        display: none;
        background: #24283b;
        color: #c0caf5;
        border: tall #565f89;
    }

    #search_box.visible {
        display: block;
    }

    #why_container {
        padding: 1 2;
        background: #1a1b26;
        border: thick #565f89;
        width: 60%;
        height: 60%;
    }

    #why_title {
        text-align: center;
        background: #565f89;
        color: white;
        margin-bottom: 1;
    }

    #confirm_container {
        padding: 1 2;
        background: #1a1b26;
        border: thick #565f89;
        width: 40%;
        height: 20%;
    }

    #confirm_message {
        text-align: center;
        margin-bottom: 1;
    }

    #confirm_actions {
        align: center middle;
    }

    #confirm_actions Button {
        margin: 0 1;
    }

    #var_container {
        padding: 1 2;
        background: #1a1b26;
        border: thick #565f89;
        width: 80%;
        height: 80%;
    }

    #var_title {
        text-align: center;
        background: #565f89;
        color: white;
        margin-bottom: 1;
    }

    #var_input.hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh Tree"),
        Binding("l", "load_node", "Load Logs/Script"),
        Binding("s", "suspend", "Suspend"),
        Binding("u", "resume", "Resume"),
        Binding("k", "kill", "Kill"),
        Binding("f", "force", "Force Complete"),
        Binding("/", "search", "Search"),
        Binding("w", "why", "Why?"),
        Binding("e", "edit_script", "Edit & Rerun"),
        Binding("t", "toggle_live", "Toggle Live Log"),
        Binding("v", "variables", "Variables"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SearchBox(placeholder="Search nodes...", id="search_box")
        yield Horizontal(
            Container(SuiteTree("ecFlow Server", id="suite_tree"), id="sidebar"),
            MainContent(id="main_content"),
        )
        yield Footer()

    @work(exclusive=True, thread=True)
    def on_mount(self) -> None:
        """
        Connect to ecFlow and load the initial tree.

        This method is run as a background worker to prevent blocking the UI
        during the initial connection and synchronization.
        """
        try:
            self.ecflow_client = EcflowClient(ECFLOW_HOST, ECFLOW_PORT)
            self.ecflow_client.ping()
            self.action_refresh()
            self.set_interval(2.0, self._live_log_tick)
        except Exception as e:
            self.notify(f"Connection Failed: {e}", severity="error", timeout=10)
            tree = self.query_one("#suite_tree", SuiteTree)
            self.call_from_thread(setattr, tree.root, "label", "[red]Connection Failed (Check Host/Port)[/]")

    @work(exclusive=True, thread=True)
    def action_refresh(self) -> None:
        """
        Fetch suites from server and rebuild the tree in a background thread.
        """
        tree = self.query_one("#suite_tree", SuiteTree)
        try:
            self.ecflow_client.sync_local()
            defs = self.ecflow_client.get_defs()
            # Update UI from thread
            self.call_from_thread(tree.update_tree, self.ecflow_client.host, self.ecflow_client.port, defs)
            self.notify("Tree Refreshed")
        except Exception as e:
            self.notify(f"Refresh Error: {e}", severity="error")

    def get_selected_path(self) -> str | None:
        """
        Helper to get the ecFlow path of the selected node.

        Returns
        -------
        str | None
            The absolute path of the selected node, or None if no node is selected.
        """
        node = self.query_one("#suite_tree", SuiteTree).cursor_node
        return node.data if node else None

    @work(exclusive=True, thread=True)
    def action_load_node(self) -> None:
        """
        Fetch Output, Script, and Job files for the selected node in a background thread.
        """
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return

        self.notify(f"Loading files for {path}...")
        content_area = self.query_one("#main_content", MainContent)

        # 1. Output Log
        try:
            content = self.ecflow_client.file(path, "jobout")
            self.call_from_thread(content_area.update_log, content)
        except Exception:
            self.call_from_thread(content_area.show_error, "#log_output", "File type 'jobout' not found (Has the task run yet?)")

        # 2. Script
        try:
            content = self.ecflow_client.file(path, "script")
            self.call_from_thread(content_area.update_script, content)
        except Exception:
            self.call_from_thread(content_area.show_error, "#view_script", "File type 'script' not available.")

        # 3. Job
        try:
            content = self.ecflow_client.file(path, "job")
            self.call_from_thread(content_area.update_job, content)
        except Exception:
            self.call_from_thread(content_area.show_error, "#view_job", "File type 'job' not available.")

    @work(exclusive=True, thread=True)
    def _run_client_command(self, command_name: str, path: str | None) -> None:
        """
        Generic helper to run ecflow commands in a background thread.

        Parameters
        ----------
        command_name : str
            The name of the EcflowClient method to call.
        path : str | None
            The absolute path of the node to act upon.
        """
        if not path:
            return
        try:
            getattr(self.ecflow_client, command_name)(path)
            self.notify(f"{command_name.replace('_', ' ').capitalize()}: {path}")
            self.action_refresh()
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def action_suspend(self) -> None:
        """Suspend the selected node."""
        self._run_client_command("suspend", self.get_selected_path())

    def action_resume(self) -> None:
        """Resume the selected node."""
        self._run_client_command("resume", self.get_selected_path())

    def action_kill(self) -> None:
        """Kill the selected node."""
        self._run_client_command("kill", self.get_selected_path())

    def action_force(self) -> None:
        """Force complete the selected node."""
        self._run_client_command("force_complete", self.get_selected_path())

    def action_toggle_live(self) -> None:
        """Toggle live log updating."""
        content_area = self.query_one("#main_content", MainContent)
        content_area.is_live = not content_area.is_live
        state = "ON" if content_area.is_live else "OFF"
        self.notify(f"Live Log: {state}")
        if content_area.is_live:
            content_area.active = "tab_output"

    @work(exclusive=True, thread=True)
    def _live_log_tick(self):
        """Periodic tick to update live logs if enabled."""
        content_area = self.query_one("#main_content", MainContent)
        if content_area.is_live and content_area.active == "tab_output":
            path = self.get_selected_path()
            if path:
                try:
                    # In a real app we might want to fetch only the end,
                    # but for now we'll follow the requirement to fetch and compare length
                    content = self.ecflow_client.file(path, "jobout")
                    self.call_from_thread(content_area.update_log, content, append=True)
                except Exception:
                    pass

    def action_why(self) -> None:
        """Inspect why the selected node is in its current state."""
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return
        self.push_screen(WhyInspector(path, self.ecflow_client))

    def action_variables(self) -> None:
        """View and edit variables for the selected node."""
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return
        self.push_screen(VariableTweaker(path, self.ecflow_client))

    @work(exclusive=True, thread=True)
    def action_edit_script(self):
        """Fetch, edit, and update a script in a background thread with TUI suspension."""
        path = self.get_selected_path()
        if not path:
            self.notify("No node selected", severity="warning")
            return

        import os
        import subprocess
        import tempfile

        try:
            content = self.ecflow_client.file(path, "script")
            with tempfile.NamedTemporaryFile(suffix=".ecf", delete=False, mode="w") as f:
                f.write(content)
                temp_path = f.name

            editor = os.environ.get("EDITOR", "vi")

            # suspend must be called from the main thread if possible,
            # but in Textual it's often okay to call from a worker that handles the subprocess.
            # However, self.suspend() specifically needs to stop the event loop.
            with self.suspend():
                subprocess.run([editor, temp_path])

            with open(temp_path) as f:
                new_content = f.read()

            os.unlink(temp_path)

            if new_content != content:
                self.ecflow_client.alter(path, "change", "script", new_content)
                self.notify("Script updated on server")
                # Prompt for re-queue
                self.call_from_thread(self._prompt_requeue, path)
            else:
                self.notify("No changes detected")

        except Exception as e:
            self.notify(f"Edit Error: {e}", severity="error")

    def _prompt_requeue(self, path: str) -> None:
        """
        Prompt the user to re-queue a node.

        Parameters
        ----------
        path : str
            The absolute path of the node to re-queue.
        """
        from ectop.widgets.modals.confirm import ConfirmModal

        # _run_client_command is a worker, so it's safe to call from the callback
        self.push_screen(ConfirmModal(f"Re-queue {path} now?", lambda: self._run_client_command("requeue", path)))

    def action_search(self) -> None:
        """
        Show the search box and focus it.
        """
        search_box = self.query_one("#search_box", SearchBox)
        search_box.add_class("visible")
        search_box.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle search submission.

        Parameters
        ----------
        event : Input.Submitted
            The event representing the input submission.
        """
        if event.input.id == "search_box":
            query = event.value
            if query:
                tree = self.query_one("#suite_tree", SuiteTree)
                if tree.find_and_select(query):
                    # Keep focus on search box to allow cycling with Enter
                    pass
                else:
                    self.notify(f"No match found for '{query}'", severity="warning")

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handle live search as the user types.

        Parameters
        ----------
        event : Input.Changed
            The event representing the input change.
        """
        if event.input.id == "search_box":
            query = event.value
            if query:
                tree = self.query_one("#suite_tree", SuiteTree)
                tree.find_and_select(query)
