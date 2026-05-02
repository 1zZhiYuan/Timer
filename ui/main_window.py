"""
Main window — bottom nav + stacked pages. Compact, adaptive.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSystemTrayIcon, QMenu, QApplication, QStyle, QStyleFactory,
    QDialog, QLabel, QStackedWidget, QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from datetime import date, timedelta
from core.timer_engine import TimerEngine
from core.app_monitor import AppMonitor
from core.config import Config
from core.theme import get_style
from core.database import init_db, get_records_in_range, get_streak_count
from ui.timer_panel import TimerPanel
from ui.calendar_panel import CalendarPanel
from ui.stats_panel import StatsPanel
from ui.pomodoro_panel import PomodoroPanel
from ui.settings_panel import SettingsPanel


_NAV = [("⏱", "计时"), ("📅", "日历"), ("📊", "报表"), ("🍅", "番茄"), ("⚙", "设置")]


class _WeeklySummary(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("本周总结")
        self.setMinimumSize(320, 220)
        layout = QVBoxLayout(self)
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        records = get_records_in_range(monday.isoformat(), today.isoformat())
        mins = [r["total_seconds"] // 60 for r in records]
        total = sum(mins)
        avg = total // max(len(mins), 1)
        best = max(mins) if mins else 0
        streak = get_streak_count()

        for t in [
            f"📅 {monday.isoformat()} ~ {today.isoformat()}", "",
            f"⏱ 总学习时长  {total // 60}h{total % 60}m",
            f"📈 日均  {avg} 分钟",
            f"🏆 最佳单日  {best} 分钟",
            f"🔥 连续达标  {streak} 天" if streak else "",
        ]:
            if t:
                l = QLabel(t)
                l.setStyleSheet("font-size:14px;padding:3px 0;")
                layout.addWidget(l)
        layout.addStretch()
        b = QPushButton("知道了")
        b.setObjectName("btnPrimary")
        b.clicked.connect(self.accept)
        layout.addWidget(b)


class MainWindow(QMainWindow):
    def __init__(self, app_icon=None):
        super().__init__()
        self._app_icon = app_icon
        self.setWindowTitle("Timer - by:ZhiYuan")
        self.setMinimumSize(640, 480)
        self.resize(800, 520)

        init_db()
        self._engine = TimerEngine()
        self._monitor = AppMonitor(3)
        if Config.app_monitor_enabled():
            self._monitor.start()

        self._sed_timer = QTimer(self)
        self._sed_timer.timeout.connect(self._check_sedentary)
        if Config.sedentary_enabled():
            self._sed_timer.start(Config.sedentary_interval() * 60 * 1000)

        self._ref_timer = QTimer(self)
        self._ref_timer.timeout.connect(self._refresh_all)
        self._ref_timer.start(30000)

        self._setup_ui()
        self._setup_tray()
        self._apply_theme(Config.theme())
        self._center()
        QTimer.singleShot(1500, self._check_weekly)

    def _setup_ui(self):
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        root = QWidget()
        self.setCentralWidget(root)
        lo = QVBoxLayout(root)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        self._stack = QStackedWidget()
        lo.addWidget(self._stack, stretch=1)

        self._timer_panel = TimerPanel(self._engine)
        self._timer_panel.mini_toggled.connect(self._toggle_mini)
        self._calendar_panel = CalendarPanel()
        self._stats_panel = StatsPanel()
        self._pomodoro_panel = PomodoroPanel()
        self._settings_panel = SettingsPanel()
        self._settings_panel.theme_changed.connect(self._apply_theme)

        self._stack.addWidget(self._timer_panel)
        self._stack.addWidget(self._calendar_panel)
        self._stack.addWidget(self._stats_panel)
        self._stack.addWidget(self._pomodoro_panel)
        self._stack.addWidget(self._settings_panel)
        self._stack.setCurrentIndex(0)

        # Nav bar
        self._nav_bar = QFrame()
        self._nav_bar.setObjectName("navBar")
        self._nav_bar.setFixedHeight(60)
        hb = QHBoxLayout(self._nav_bar)
        hb.setContentsMargins(0, 0, 0, 0)
        hb.setSpacing(0)

        self._nav_btns = []
        for i, (ico, txt) in enumerate(_NAV):
            b = QPushButton(ico)
            b.setObjectName("navBtn")
            b.setToolTip(txt)
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda checked, idx=i: self._switch(idx))
            hb.addWidget(b)
            self._nav_btns.append(b)
        self._nav_btns[0].setChecked(True)
        lo.addWidget(self._nav_bar)
        self._refresh_all()

    def _switch(self, idx):
        self._stack.setCurrentIndex(idx)
        for i, b in enumerate(self._nav_btns):
            b.setChecked(i == idx)

    def _toggle_mini(self, enter_mini: bool):
        if enter_mini:
            self._saved_geo = self.geometry()
            self._stack.setCurrentIndex(0)
            self._nav_bar.setVisible(False)
            self._timer_panel.set_mini_mode(True)
            self.setWindowTitle("⏱ Timer - by:ZhiYuan")
            self.setMinimumSize(0, 0)
            self.resize(280, 200)
            self._timer_panel._scale(self._timer_panel.height())
        else:
            self._nav_bar.setVisible(True)
            self._timer_panel.set_mini_mode(False)
            self.setWindowTitle("Timer - by:ZhiYuan")
            self.setMinimumSize(640, 480)
            if hasattr(self, '_saved_geo'):
                self.setGeometry(self._saved_geo)
            else:
                self.resize(800, 520)
            self._timer_panel._scale(self._timer_panel.height())

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self._tray = QSystemTrayIcon(self)
        if self._app_icon:
            self._tray.setIcon(self._app_icon)
        else:
            self._tray.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self._tray.setToolTip("Timer")
        m = QMenu()
        a = QAction("显示窗口", self)
        a.triggered.connect(self._show)
        m.addAction(a)
        self._tray_tog = QAction("开始计时", self)
        self._tray_tog.triggered.connect(self._tray_toggle)
        m.addAction(self._tray_tog)
        m.addSeparator()
        q = QAction("退出", self)
        q.triggered.connect(self._quit)
        m.addAction(q)
        self._tray.setContextMenu(m)
        self._tray.activated.connect(
            lambda r: self._show() if r == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self._tray.show()

    def _tray_toggle(self):
        e = self._engine
        if e.is_running and not e.is_paused:
            self._timer_panel._pause()
            self._tray_tog.setText("继续计时")
        elif e.is_paused:
            self._timer_panel._resume()
            self._tray_tog.setText("暂停计时")
        else:
            self._timer_panel._start()
            self._tray_tog.setText("暂停计时")

    def _show(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        if hasattr(self, '_tray') and self._tray.isVisible():
            event.ignore()
            self.hide()
        else:
            self._cleanup()
            event.accept()

    def _center(self):
        s = QApplication.primaryScreen().geometry()
        self.move((s.width() - self.width()) // 2, (s.height() - self.height()) // 2)

    def _apply_theme(self, theme):
        self.setStyleSheet(get_style(theme))
        self._timer_panel.refresh_theme()
        self._calendar_panel.refresh()
        self._stats_panel.refresh()
        self._pomodoro_panel.refresh()

    def _refresh_all(self):
        self._timer_panel.refresh()
        self._calendar_panel.refresh()
        self._stats_panel.refresh()
        self._pomodoro_panel.refresh()
        if hasattr(self, '_tray_tog'):
            e = self._engine
            self._tray_tog.setText(
                "暂停计时" if e.is_running and not e.is_paused else
                "继续计时" if e.is_paused else "开始计时")

    def _check_sedentary(self):
        if self._engine.is_running and not self._engine.is_paused:
            try:
                from plyer import notification
                notification.notify(title="Timer",
                    message=f"已专注 {self._engine.session_seconds // 60} 分钟，起来活动一下",
                    timeout=6)
            except Exception:
                pass

    def _check_weekly(self):
        wn = date.today().isocalendar()[1]
        if wn != getattr(self, '_lw', -1):
            self._lw = wn
            _WeeklySummary(self).exec()

    def _cleanup(self):
        if hasattr(self, '_monitor') and self._monitor.isRunning():
            self._monitor.stop()
            self._monitor.wait(2000)

    def _quit(self):
        self._cleanup()
        if hasattr(self, '_tray'):
            self._tray.hide()
        QApplication.quit()
