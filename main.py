#!/usr/bin/env python3
"""
Timer — Windows 桌面轻量学习计时统计工具。
纯本地、无联网、无管控限制，只做计时 + 统计 + 复盘。
"""
import sys
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.icon import make_icon
from ui.main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("Timer")
    app.setOrganizationName("TimerApp")

    # Set app icon
    app_icon = make_icon(256)
    app.setWindowIcon(app_icon)

    window = MainWindow(app_icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
