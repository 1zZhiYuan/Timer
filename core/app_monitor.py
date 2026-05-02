"""
Background app usage monitor for Windows.
Tracks the active foreground window and categorizes it.
"""
import time
from datetime import date
from PyQt6.QtCore import QThread, pyqtSignal

from core.database import record_app_usage

# Common study / work app keywords
STUDY_KEYWORDS = [
    "code", "visual studio", "cursor", "windsurf", "jetbrains", "idea", "pycharm",
    "webstorm", "vscode", "sublime", "notepad++", "vim", "neovim", "emacs",
    "terminal", "cmd", "powershell", "wsl", "putty",
    "chrome", "edge", "firefox", "browser", "opera",
    "word", "excel", "powerpoint", "office", "onenote", "notion", "obsidian",
    "pdf", "acrobat", "foxit",
    "python", "jupyter", "anaconda", "matlab", "rstudio",
    "typora", "markdown",
    "wechat", "tencent meeting", "dingtalk", "lark", "feishu", "slack",
    "postman", "mysql workbench", "navicat",
]

ENTERTAINMENT_KEYWORDS = [
    "game", "steam", "epic", "league of legends", "lol", "dota", "valorant",
    "overwatch", "genshin", "honkai", "nvidia", "geforce",
    "bilibili", "youtube", "netflix", "spotify", "music",
    "tiktok", "douyin", "kugou", "qqmusic", "wangyi",
    "video", "movie", "player", "mpv", "vlc", "potplayer",
]


def categorize_app(app_name: str) -> str:
    name = app_name.lower()
    for kw in STUDY_KEYWORDS:
        if kw in name:
            return "study"
    for kw in ENTERTAINMENT_KEYWORDS:
        if kw in name:
            return "entertainment"
    return "other"


def get_foreground_window_info():
    """Get the active foreground window's process name and title."""
    try:
        import win32gui
        import win32process
        import psutil

        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None, None
        window_title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            app_name = process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            app_name = "unknown"
        return app_name, window_title
    except ImportError:
        return None, None


class AppMonitor(QThread):
    """Background thread that polls foreground window every N seconds."""
    monitoring_stopped = pyqtSignal()

    def __init__(self, interval_seconds: int = 3, parent=None):
        super().__init__(parent)
        self._interval = interval_seconds
        self._running = False
        self._current_app = None
        self._current_title = None
        self._accumulator = 0  # seconds accumulated for current app

    def run(self):
        self._running = True
        while self._running:
            app_name, window_title = get_foreground_window_info()
            if app_name and self._current_app == app_name:
                self._accumulator += self._interval
            else:
                # flush previous app
                if self._current_app and self._accumulator > 0:
                    self._flush()
                self._current_app = app_name
                self._current_title = window_title
                self._accumulator = self._interval if app_name else 0

            time.sleep(self._interval)

    def _flush(self):
        if not self._current_app or self._accumulator < self._interval:
            return
        today = date.today().isoformat()
        category = categorize_app(self._current_app)
        record_app_usage(
            record_date=today,
            app_name=self._current_app,
            window_title=self._current_title or "",
            seconds_delta=self._accumulator,
            category=category,
        )

    def stop(self):
        self._running = False
        if self._current_app and self._accumulator > 0:
            self._flush()
        self.monitoring_stopped.emit()
