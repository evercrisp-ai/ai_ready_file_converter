"""
AI Ready File Converter - Desktop Application
Native macOS desktop app using pywebview and FastAPI.
"""

# #region agent log
import json as _json
import os as _os
from datetime import datetime as _datetime
_LOG_PATH = "/Users/benscooper/ai-ready-file-converter/.cursor/debug.log"
def _dbg(loc, msg, data, hyp):
    try:
        with open(_LOG_PATH, "a") as f:
            f.write(_json.dumps({"location": loc, "message": msg, "data": data, "hypothesisId": hyp, "timestamp": _datetime.now().isoformat(), "sessionId": "debug-session"}) + "\n")
    except Exception as e:
        pass
# #endregion

# #region agent log
_dbg("desktop_app.py:1", "App starting - basic imports", {"frozen": getattr(__import__('sys'), 'frozen', False)}, "A")
# #endregion

import os
import sys
import socket
import signal
import threading
import time
from pathlib import Path

# #region agent log
_dbg("desktop_app.py:18", "Standard imports successful, attempting webview import", {"sys_path": sys.path[:5]}, "C")
# #endregion

try:
    import webview
    # #region agent log
    _dbg("desktop_app.py:22", "webview import SUCCESS", {"webview_version": getattr(webview, '__version__', 'unknown')}, "C")
    # #endregion
except Exception as e:
    # #region agent log
    _dbg("desktop_app.py:22", "webview import FAILED", {"error": str(e), "error_type": type(e).__name__}, "C")
    # #endregion
    raise

try:
    import uvicorn
    # #region agent log
    _dbg("desktop_app.py:28", "uvicorn import SUCCESS", {}, "D")
    # #endregion
except Exception as e:
    # #region agent log
    _dbg("desktop_app.py:28", "uvicorn import FAILED", {"error": str(e), "error_type": type(e).__name__}, "D")
    # #endregion
    raise


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
            loop="asyncio",  # Use standard asyncio, not uvloop (uvloop doesn't work in py2app bundle)
        )
        self.server = uvicorn.Server(config)
        # #region agent log
        _dbg("desktop_app.py:run", "Starting uvicorn server", {"host": self.host, "port": self.port}, "D")
        # #endregion
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
    # #region agent log
    _dbg("desktop_app.py:main:1", "main() entry point reached", {}, "A")
    # #endregion
    
    # Set environment variable to indicate we're running as a desktop app
    os.environ["AI_READY_DESKTOP_MODE"] = "true"
    
    # Set the app data directory
    app_data_dir = get_app_data_dir()
    os.environ["AI_READY_DATA_DIR"] = str(app_data_dir)
    
    # #region agent log
    _dbg("desktop_app.py:main:2", "Environment set, attempting main import", {"app_data_dir": str(app_data_dir), "sys_path": sys.path[:5]}, "A")
    # #endregion
    
    # Import the FastAPI app after setting environment variables
    # This ensures the app picks up our configuration
    try:
        from main import app
        # #region agent log
        _dbg("desktop_app.py:main:3", "main import SUCCESS", {}, "A")
        # #endregion
    except Exception as e:
        # #region agent log
        import traceback
        _dbg("desktop_app.py:main:3", "main import FAILED", {"error": str(e), "error_type": type(e).__name__, "traceback": traceback.format_exc()}, "A")
        # #endregion
        raise
    
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
