"""
AI Ready File Converter - Desktop Application
Native macOS desktop app using pywebview and FastAPI.
"""

import os
import sys
import socket
import signal
import threading
import time
from pathlib import Path

import webview
import uvicorn


def get_app_data_dir() -> Path:
    """Get the application data directory for storing files."""
    if sys.platform == "darwin":
        # macOS: ~/Library/Application Support/AIReadyConverter
        app_support = Path.home() / "Library" / "Application Support" / "AIReadyConverter"
    elif sys.platform == "win32":
        # Windows: %APPDATA%\AIReadyConverter
        app_data = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
        app_support = Path(app_data) / "AIReadyConverter"
    else:
        # Linux: ~/.local/share/AIReadyConverter
        app_support = Path.home() / ".local" / "share" / "AIReadyConverter"
    
    app_support.mkdir(parents=True, exist_ok=True)
    return app_support


def find_free_port() -> int:
    """Find an available port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def get_resource_path(relative_path: str) -> Path:
    """Get the absolute path to a resource, works for dev and for py2app."""
    if getattr(sys, 'frozen', False):
        # Running in a py2app bundle
        base_path = Path(sys.executable).parent.parent / "Resources"
    else:
        # Running in development
        base_path = Path(__file__).parent
    
    return base_path / relative_path


class ServerThread(threading.Thread):
    """Thread to run the FastAPI server."""
    
    def __init__(self, app, host: str, port: int):
        super().__init__(daemon=True)
        self.app = app
        self.host = host
        self.port = port
        self.server = None
        self._stop_event = threading.Event()
    
    def run(self):
        """Run the uvicorn server."""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning",
            access_log=False,
        )
        self.server = uvicorn.Server(config)
        self.server.run()
    
    def stop(self):
        """Signal the server to stop."""
        self._stop_event.set()
        if self.server:
            self.server.should_exit = True


def wait_for_server(host: str, port: int, timeout: float = 10.0) -> bool:
    """Wait for the server to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (socket.error, socket.timeout):
            time.sleep(0.1)
    return False


def on_window_closed():
    """Handle window close event."""
    # The server thread is a daemon, so it will be killed when the main thread exits
    pass


def main():
    """Main entry point for the desktop application."""
    # Set environment variable to indicate we're running as a desktop app
    os.environ["AI_READY_DESKTOP_MODE"] = "true"
    
    # Set the app data directory
    app_data_dir = get_app_data_dir()
    os.environ["AI_READY_DATA_DIR"] = str(app_data_dir)
    
    # Import the FastAPI app after setting environment variables
    # This ensures the app picks up our configuration
    from main import app
    
    # Find an available port
    port = find_free_port()
    host = "127.0.0.1"
    
    # Start the server in a background thread
    server_thread = ServerThread(app, host, port)
    server_thread.start()
    
    # Wait for server to be ready
    if not wait_for_server(host, port):
        print("Error: Server failed to start", file=sys.stderr)
        sys.exit(1)
    
    # Create the webview window
    window = webview.create_window(
        title="AI Ready File Converter",
        url=f"http://{host}:{port}",
        width=1200,
        height=800,
        min_size=(800, 600),
        resizable=True,
        text_select=True,
    )
    
    # Handle window close
    window.events.closed += on_window_closed
    
    # Start the webview (this blocks until the window is closed)
    webview.start(
        debug=os.environ.get("DEBUG", "").lower() == "true",
        private_mode=False,  # Allow cookies for session management
    )
    
    # Clean up
    server_thread.stop()


if __name__ == "__main__":
    main()
