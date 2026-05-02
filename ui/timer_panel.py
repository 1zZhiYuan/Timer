"""
Timer panel — fully responsive. Fonts & elements scale with window size.
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QWidget, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor

from datetime import date
from core.database import get_or_create_record, get_streak_count
from core.config import Config
from core.theme import PALETTES


def _fmt(s: int) -> str:
    h = s // 3600
    m = (s % 3600) // 60
    s2 = s % 60
    return f"{h:02d}:{m:02d}:{s2:02d}" if h else f"{m:02d}:{s2:02d}"


class _Dot(QWidget):
    """Recording indicator that also scales."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._on = False
        self._t = QTimer(self)
        self._t.timeout.connect(lambda: (setattr(self, '_on', not self._on), self.update()))
        self._sz = 12

    def start(self):
        self._on = True
        self._t.start(800)
        self.update()

    def stop(self):
        self._t.stop()
        self._on = False
        self.update()

    def set_dot_size(self, s: int):
        self._sz = max(8, s)
        self.setFixedSize(self._sz, self._sz)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        d = self._sz - 2
        p.setBrush(QColor("#ef4444" if self._on else "#d1d5db"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(1, 1, d, d)


class TimerPanel(QFrame):
    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    mini_toggled = pyqtSignal(bool)  # True = enter mini mode

    def __init__(self, engine):
        super().__init__()
        self._engine = engine
        self._sec = 0
        self._ref_h = 500
        self._mini = False

        self._dot = _Dot()
        self._time = QLabel("00:00")
        self._time.setObjectName("homeTime")
        self._time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time.setWordWrap(False)

        self._hint = QLabel("")
        self._hint.setObjectName("homeHint")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn = QPushButton("开始专注")
        self._btn.setObjectName("homeBtn")
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.clicked.connect(self._toggle)

        self._btn_reset = QPushButton("重置")
        self._btn_reset.setObjectName("homeBtnReset")
        self._btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_reset.setEnabled(False)
        self._btn_reset.clicked.connect(self._do_reset)

        self._btn_mini = QPushButton("⼝")
        self._btn_mini.setObjectName("homeBtnMini")
        self._btn_mini.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_mini.setToolTip("小化窗口")
        self._btn_mini.clicked.connect(self._on_mini)

        self._today = QLabel("今日 0 分钟")
        self._today.setObjectName("homeStats")
        self._streak = QLabel("")
        self._streak.setObjectName("homeStats")

        self._prog = QFrame()
        self._prog.setObjectName("homeProg")
        self._bar = QFrame(self._prog)
        self._bar.setObjectName("homeBar")

        self._setup()
        self._connect()

    def _setup(self):
        self.setObjectName("timerPanel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lo = QVBoxLayout(self)
        lo.setContentsMargins(20, 10, 20, 10)
        lo.setSpacing(0)

        lo.addStretch(1)

        # Timer row
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.setSpacing(6)
        row.addWidget(self._dot)
        row.addWidget(self._time)
        sp = QWidget()
        sp.setFixedWidth(12)
        row.addWidget(sp)
        lo.addLayout(row)

        lo.addSpacing(8)
        lo.addWidget(self._hint)
        lo.addSpacing(16)

        # Buttons row
        br = QHBoxLayout()
        br.setAlignment(Qt.AlignmentFlag.AlignCenter)
        br.setSpacing(8)
        br.addWidget(self._btn)
        br.addWidget(self._btn_reset)
        br.addWidget(self._btn_mini)
        lo.addLayout(br)

        lo.addSpacing(14)

        # Stats
        self._stats_row = QHBoxLayout()
        self._stats_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stats_row.setSpacing(14)
        self._stats_row.addWidget(self._today)
        self._stats_row.addWidget(self._prog)
        self._stats_row.addWidget(self._streak)
        lo.addLayout(self._stats_row)

        lo.addStretch(2)

    def _connect(self):
        self._engine.tick_signal.connect(self._tick)
        self._engine.daily_updated.connect(self._stats)
        self._engine.state_changed.connect(self._sync_state)

    def _scale(self, h):
        """Scale all elements based on available height."""
        s = h / self._ref_h
        s = max(0.4, min(3.0, s))
        pal = PALETTES.get(Config.theme(), PALETTES["light"])

        # Timer font
        fs = int(120 * s)
        clr = pal["home_time_fg"]
        self._time.setStyleSheet(
            f"font-size: {fs}px; color: {clr}; "
            f"background: transparent; border: none; padding: 0; margin: 0;"
        )

        self._dot.set_dot_size(int(12 * s))

        bf = max(12, int(16 * s))
        self._btn.setMinimumSize(int(160 * s), int(50 * s))
        self._btn.setStyleSheet(f"font-size: {bf}px; padding: {int(4*s)}px {int(28*s)}px; border-radius: {int(25*s)}px;"
                                "background-color: #4f6ef7; color: white; border: none; font-weight: bold; letter-spacing: 2px;")

        self._btn_reset.setMinimumSize(int(70 * s), int(50 * s))
        self._btn_reset.setStyleSheet(
            f"font-size: {bf}px; padding: {int(4*s)}px {int(12*s)}px; border-radius: {int(25*s)}px;"
            "background-color: #6b7280; color: white; border: none; font-weight: bold;")

        self._btn_mini.setFixedSize(int(50 * s), int(50 * s))
        self._btn_mini.setStyleSheet(
            f"font-size: {bf}px; border-radius: {int(25*s)}px;"
            "background-color: transparent; color: #9ca3af; border: 1px solid #d1d5db; font-weight: bold;")

        hf = max(10, int(14 * s))
        self._hint.setStyleSheet(f"font-size: {hf}px; color: #6b7280; padding: 2px 0;")

        sf = max(9, int(12 * s))
        self._today.setStyleSheet(f"font-size: {sf}px; color: #6b7280; background: transparent; border: none; padding: 0;")
        self._streak.setStyleSheet(f"font-size: {sf}px; color: #6b7280; background: transparent; border: none; padding: 0;")

        pw = int(120 * s)
        ph = max(3, int(5 * s))
        self._prog.setFixedSize(pw, ph)
        self._bar.setFixedHeight(ph)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._scale(self.height())

    def set_mini_mode(self, active: bool):
        self._mini = active
        self._hint.setVisible(not active)
        self._btn_reset.setVisible(not active)
        self._today.setVisible(not active)
        self._prog.setVisible(not active)
        self._streak.setVisible(not active)
        self._dot.setVisible(not active)
        self._btn_mini.setVisible(True)
        self._btn_mini.setText("⛶" if active else "⼝")
        self._btn_mini.setToolTip("展开窗口" if active else "小化窗口")

    def _on_mini(self):
        self.mini_toggled.emit(not self._mini)

    def _toggle(self):
        e = self._engine
        if e.is_running and not e.is_paused:
            e.pause()
            self._btn.setText("继续")
            self._hint.setText("已暂停")
            self._dot.stop()
            self.pause_clicked.emit()
        elif e.is_paused:
            e.start()
            self._btn.setText("暂停")
            self._hint.setText("专注中")
            self._dot.start()
            self.start_clicked.emit()
        else:
            e.start()
            self._btn.setText("暂停")
            self._hint.setText("专注中")
            self._dot.start()
            self.start_clicked.emit()

    def _start(self):
        self._engine.start()
        self._btn.setText("暂停")
        self._hint.setText("专注中")
        self._dot.start()

    def _pause(self):
        self._engine.pause()
        self._btn.setText("继续")
        self._hint.setText("已暂停")
        self._dot.stop()

    def _resume(self):
        self._engine.start()
        self._btn.setText("暂停")
        self._hint.setText("专注中")
        self._dot.start()

    def _tick(self, sec):
        self._sec = sec
        self._time.setText(_fmt(sec))

    def _stats(self, total_sec=None):
        if total_sec is None:
            total_sec = get_or_create_record(date.today().isoformat())["total_seconds"]
        mins = total_sec // 60
        self._today.setText(f"今日 {mins} 分钟")
        tgt = Config.daily_target_minutes() * 60
        if tgt > 0:
            pct = min(100, total_sec * 100 // tgt)
            self._bar.setFixedWidth(max(1, self._prog.width() * pct // 100))
        else:
            self._bar.setFixedWidth(0)
        s = get_streak_count()
        self._streak.setText(f"🔥 {s}天" if s else "")

    def _sync_state(self):
        e = self._engine
        if e.is_running and not e.is_paused:
            self._btn.setText("暂停")
            self._hint.setText("专注中")
            self._dot.start()
            self._btn_reset.setEnabled(True)
        elif e.is_paused:
            self._btn.setText("继续")
            self._hint.setText("已暂停")
            self._dot.stop()
            self._btn_reset.setEnabled(True)
        else:
            self._btn.setText("开始专注")
            self._hint.setText("")
            self._dot.stop()
            self._btn_reset.setEnabled(False)
            self._time.setText(_fmt(self._engine.session_seconds))

    def _do_reset(self):
        self._engine.reset()
        self._time.setText("00:00")
        self._hint.setText("")
        self._btn_reset.setEnabled(False)

    def refresh_theme(self):
        self._scale(self.height())

    def refresh(self):
        self._scale(self.height())
        self._stats()
        self._sync_state()
