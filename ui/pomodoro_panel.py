"""
Pomodoro panel — customizable focus/break timer with notification alerts.
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSpinBox, QFrame, QGroupBox, QFormLayout, QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import json
from datetime import date, datetime
from core.config import Config
from core.database import save_pomodoro_session, get_or_create_record, update_daily_seconds, get_pomodoro_sessions
from core.theme import PALETTES


class PomodoroPanel(QFrame):
    def __init__(self):
        super().__init__()
        self._focus_m = Config.pomodoro_focus()
        self._break_m = Config.pomodoro_break()
        self._remaining = self._focus_m * 60
        self._is_focus = True
        self._running = False
        self._completed = self._load_today_count()
        self._ref_h = 500
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._setup_ui()

    def _load_today_count(self) -> int:
        try:
            sessions = get_pomodoro_sessions(date.today().isoformat(), date.today().isoformat())
            return sum(s["completed_count"] for s in sessions)
        except Exception:
            return 0

    def _setup_ui(self):
        self.setObjectName("pomodoroPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        t = QLabel("番茄钟")
        t.setObjectName("panelTitle")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(t)

        # Scroll area for all content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("pomodoroScroll")
        scroll.viewport().setObjectName("pomodoroScroll")

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(10)
        cl.setContentsMargins(12, 8, 12, 12)

        self._time_label = QLabel(self._fmt(self._remaining))
        self._time_label.setObjectName("pomodoroDisplay")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._time_label)

        self._state_label = QLabel("🍅 专注时间")
        self._state_label.setObjectName("pomodoroState")
        self._state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._state_label)

        self._count_label = QLabel("今日完成: 0 个番茄")
        self._count_label.setObjectName("pomodoroCount")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._count_label)

        btns = QHBoxLayout()
        btns.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btns.setSpacing(10)
        self._btn_start = QPushButton("开始番茄")
        self._btn_start.setObjectName("btnPrimary")
        self._btn_start.setMinimumSize(120, 40)
        self._btn_start.clicked.connect(self._toggle)
        self._btn_skip = QPushButton("跳过")
        self._btn_skip.setObjectName("btnSecondary")
        self._btn_skip.setMinimumSize(80, 40)
        self._btn_skip.setEnabled(False)
        self._btn_skip.clicked.connect(self._skip)
        self._btn_reset = QPushButton("重置")
        self._btn_reset.setObjectName("btnSecondary")
        self._btn_reset.setMinimumSize(80, 40)
        self._btn_reset.setEnabled(False)
        self._btn_reset.clicked.connect(self._do_reset)
        btns.addWidget(self._btn_start)
        btns.addWidget(self._btn_skip)
        btns.addWidget(self._btn_reset)
        cl.addLayout(btns)

        sg = QGroupBox("番茄钟设置")
        sg.setObjectName("settingsGroup")
        fm = QFormLayout(sg)
        self._focus_spin = QSpinBox()
        self._focus_spin.setRange(1, 120)
        self._focus_spin.setValue(self._focus_m)
        self._focus_spin.setSuffix(" 分钟")
        self._focus_spin.valueChanged.connect(self._on_focus_changed)
        fm.addRow("专注时长:", self._focus_spin)
        self._break_spin = QSpinBox()
        self._break_spin.setRange(1, 60)
        self._break_spin.setValue(self._break_m)
        self._break_spin.setSuffix(" 分钟")
        self._break_spin.valueChanged.connect(self._on_break_changed)
        fm.addRow("休息时长:", self._break_spin)
        cl.addWidget(sg)
        cl.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

    def _scale(self, h):
        s = h / self._ref_h
        s = max(0.5, min(2.0, s))
        fs = int(48 * s)
        # Use theme palette for colors
        pal = PALETTES.get(Config.theme(), PALETTES["light"])
        clr = pal["pomo_fg"]
        bg = pal["pomo_bg"]
        bdr = pal["pomo_border"]
        radius = 18
        pad = 22 if bdr == "transparent" else 18
        bdr_style = "none" if bdr == "transparent" else f"1px solid {bdr}"
        self._time_label.setStyleSheet(
            f"font-size: {fs}px; color: {clr}; background-color: {bg}; "
            f"border-radius: {radius}px; padding: {pad}px 10px; border: {bdr_style};")

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._scale(self.height())

    def _fmt(self, s: int) -> str:
        return f"{s // 60:02d}:{s % 60:02d}"

    def _toggle(self):
        if not self._running:
            self._running = True
            self._btn_start.setText("暂停")
            self._btn_skip.setEnabled(True)
            self._btn_reset.setEnabled(True)
            self._timer.start(1000)
        else:
            self._running = False
            self._btn_start.setText("继续")
            self._btn_reset.setEnabled(True)
            self._timer.stop()

    def _tick(self):
        self._remaining -= 1
        self._time_label.setText(self._fmt(self._remaining))
        if self._remaining <= 0:
            self._timer.stop()
            self._running = False
            self._on_complete()

    def _on_complete(self):
        today = date.today().isoformat()
        if self._is_focus:
            self._completed += 1
            save_pomodoro_session(today, self._focus_m, self._break_m, 1)
            # Also add focus time to daily study record
            focus_secs = self._focus_m * 60
            record = get_or_create_record(today)
            new_total = record["total_seconds"] + focus_secs
            intervals = json.loads(record.get("session_intervals", "[]"))
            intervals.append({
                "start": datetime.now().isoformat(),
                "seconds": focus_secs,
                "source": "pomodoro",
            })
            update_daily_seconds(today, new_total, json.dumps(intervals))
            self._count_label.setText(f"今日完成: {self._completed} 个番茄")
            self._is_focus = False
            self._remaining = self._break_m * 60
            self._state_label.setText("☕ 休息时间")
            self._time_label.setText(self._fmt(self._remaining))
            self._btn_start.setText("开始休息")
            self._btn_skip.setText("跳过休息")
            self._notify()
        else:
            self._is_focus = True
            self._remaining = self._focus_m * 60
            self._state_label.setText("🍅 专注时间")
            self._time_label.setText(self._fmt(self._remaining))
            self._btn_start.setText("开始番茄")
            self._btn_skip.setText("跳过")
            self._btn_skip.setEnabled(False)
            self._notify()

    def _skip(self):
        self._timer.stop()
        self._running = False
        self._remaining = 1
        self._btn_reset.setEnabled(False)
        self._tick()

    def _do_reset(self):
        self._timer.stop()
        self._running = False
        self._btn_start.setText("开始番茄" if self._is_focus else "开始休息")
        self._remaining = self._focus_m * 60 if self._is_focus else self._break_m * 60
        self._time_label.setText(self._fmt(self._remaining))
        self._btn_skip.setEnabled(False)
        self._btn_reset.setEnabled(False)

    def _notify(self):
        try:
            from plyer import notification
            msg = "专注结束，休息一下吧！" if not self._is_focus else "休息结束，开始新的专注！"
            notification.notify(title="Timer - 番茄钟", message=msg, timeout=5)
        except Exception:
            pass
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

    def _on_focus_changed(self, v: int):
        self._focus_m = v
        Config.set_pomodoro_focus(v)
        if self._is_focus and not self._running:
            self._remaining = v * 60
            self._time_label.setText(self._fmt(self._remaining))

    def _on_break_changed(self, v: int):
        self._break_m = v
        Config.set_pomodoro_break(v)
        if not self._is_focus and not self._running:
            self._remaining = v * 60
            self._time_label.setText(self._fmt(self._remaining))

    def refresh(self):
        self._focus_m = Config.pomodoro_focus()
        self._break_m = Config.pomodoro_break()
        self._focus_spin.setValue(self._focus_m)
        self._break_spin.setValue(self._break_m)
        # Reload today's completed count from DB
        self._completed = self._load_today_count()
        self._count_label.setText(f"今日完成: {self._completed} 个番茄")
        self._scale(self.height())
