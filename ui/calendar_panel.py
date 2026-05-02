"""
Calendar panel — monthly grid showing daily study time /达标.
Click a day for detail (app usage breakdown).
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGridLayout, QFrame, QDialog, QTextEdit, QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette

from datetime import date, datetime, timedelta
from core.database import get_month_records, get_or_create_record, get_app_usage
from core.config import Config
from core.theme import PALETTES
import json


def _fmt(secs: int) -> str:
    m = secs // 60
    return f"{m}分钟" if m > 0 else ""


class DayCell(QFrame):
    def __init__(self, day: int, rd: str, total_sec: int, target_sec: int, is_today: bool, scale: float = 1.0, parent=None):
        super().__init__(parent)
        self.record_date = rd
        self.total_seconds = total_sec
        self.target_seconds = target_sec
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        mins = total_sec // 60
        t_mins = target_sec // 60 if target_sec > 0 else 0
        done = t_mins > 0 and mins >= t_mins
        partial = t_mins > 0 and 0 < mins < t_mins

        # Scale sizes
        base_size = max(36, int(48 * scale))
        day_font = max(8, int(9 * scale))
        min_font = max(6, int(7 * scale))
        check_font = max(8, int(9 * scale))

        # Theme-aware colors
        is_dark = Config.theme() == "dark"
        pal = PALETTES.get(Config.theme(), PALETTES["light"])
        normal_bg = pal["card_bg"]
        normal_border = pal["card_border"] if pal["card_border"] != "transparent" else "#d1d5db"
        today_border = pal["accent"]
        hover_bg = pal["hover_bg"]

        if is_dark:
            done_bg = "#14532d"
            partial_bg = "#713f12"
            today_bg = "#1e3a5f"
        else:
            done_bg = "#d1fae5"
            partial_bg = "#fef3c7"
            today_bg = "#eef2ff"

        # Determine cell bg
        if done:
            bg = done_bg
            border = f"1px solid {normal_border}"
        elif partial:
            bg = partial_bg
            border = f"1px solid {normal_border}"
        elif is_today:
            bg = today_bg
            border = f"2px solid {today_border}"
        else:
            bg = normal_bg
            border = f"1px solid {normal_border}"

        self.setStyleSheet(f"""
            DayCell {{
                background-color: {bg};
                border: {border};
                border-radius: 8px;
                padding: 4px;
            }}
            DayCell:hover {{
                background-color: {hover_bg};
            }}
        """)

        self.setMinimumSize(base_size, base_size)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        marg = max(1, int(2 * scale))
        layout.setContentsMargins(marg, marg, marg, marg)

        if day <= 0:
            return

        dl = QLabel(str(day))
        dl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dl.setFont(QFont("", day_font, QFont.Weight.Bold))
        layout.addWidget(dl)

        if mins > 0:
            tl = QLabel(f"{mins}m" if mins < 100 else "99+")
            tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tl.setStyleSheet(f"font-size: {min_font}pt; color: #6b7280;")
            layout.addWidget(tl)

        if done:
            ml = QLabel("✓")
            ml.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ml.setStyleSheet(f"color: #22c55e; font-weight: bold; font-size: {check_font}pt;")
            layout.addWidget(ml)


class DayDetailDialog(QDialog):
    def __init__(self, rd: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{rd} 学习详情")
        self.setMinimumSize(420, 320)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Fetch fresh data from DB
        record = get_or_create_record(rd)
        total_sec = record["total_seconds"]
        intervals = json.loads(record.get("session_intervals", "[]"))

        info = QLabel(
            f"📅 {rd}\n"
            f"⏱ 总学习时长: {total_sec // 60} 分钟 ({total_sec} 秒)\n"
            f"📊 学习段数: {len(intervals)}"
        )
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 14px; padding: 8px;")
        layout.addWidget(info)

        # Session intervals
        if intervals:
            layout.addWidget(QLabel("时间线:"))
            tl = QTextEdit()
            tl.setReadOnly(True)
            tl.setMaximumHeight(100)
            lines = []
            for iv in intervals[-20:]:  # last 20 sessions
                try:
                    st = datetime.fromisoformat(iv["start"]).strftime("%H:%M")
                except Exception:
                    st = "??:??"
                s = iv.get("seconds", 0)
                lines.append(f"  {st}  →  {s // 60}m{s % 60}s")
            tl.setText("\n".join(lines))
            layout.addWidget(tl)

        layout.addWidget(QLabel("应用使用情况:"))
        text = QTextEdit()
        text.setReadOnly(True)
        text.setMaximumHeight(120)
        apps = get_app_usage(rd)
        if apps:
            text.setText("\n".join(f"  {a['app_name']}: {a['total_seconds'] // 60}分钟 [{a['category']}]" for a in apps[:10]))
        else:
            text.setText("  无记录")
        layout.addWidget(text)

        btn = QPushButton("关闭")
        btn.setObjectName("btnSecondary")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


class CalendarPanel(QFrame):
    def __init__(self):
        super().__init__()
        self._year = date.today().year
        self._month = date.today().month
        self._scale_factor = 1.0
        self._last_scale = 0
        self._setup_ui()

    def _scale(self, w):
        s = w / 600  # reference 600px width
        self._scale_factor = max(0.55, min(2.0, s))

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        new_s = self.width() / 600
        new_s = max(0.55, min(2.0, new_s))
        # Only rebuild if scale changed meaningfully (avoids expensive rebuilds)
        if abs(new_s - self._last_scale) > 0.08:
            self._last_scale = new_s
            self._scale_factor = new_s
            self._build()

    def _setup_ui(self):
        self.setObjectName("calendarPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("日历统计")
        title.setObjectName("panelTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Scroll area for all content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("calendarScroll")
        scroll.viewport().setObjectName("calendarScroll")

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(6)
        cl.setContentsMargins(12, 8, 12, 12)

        nav = QHBoxLayout()
        nav.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._btn_prev = QPushButton("◀ 上月")
        self._btn_prev.setObjectName("btnSecondary")
        self._btn_prev.clicked.connect(self._prev)
        self._month_label = QLabel()
        self._month_label.setObjectName("monthLabel")
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._btn_next = QPushButton("下月 ▶")
        self._btn_next.setObjectName("btnSecondary")
        self._btn_next.clicked.connect(self._next)
        self._btn_today = QPushButton("今日")
        self._btn_today.setObjectName("btnSecondary")
        self._btn_today.clicked.connect(self._go_today)
        nav.addWidget(self._btn_prev)
        nav.addWidget(self._month_label)
        nav.addWidget(self._btn_today)
        nav.addWidget(self._btn_next)
        cl.addLayout(nav)

        self._grid = QGridLayout()
        self._grid.setSpacing(3)
        cl.addLayout(self._grid)

        self._summary = QLabel()
        self._summary.setObjectName("summaryLabel")
        self._summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._summary.setWordWrap(True)
        cl.addWidget(self._summary)
        cl.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

        self._build()

    def _build(self):
        self._clear_grid()
        self._scale(self.width())
        days = ["一", "二", "三", "四", "五", "六", "日"]
        pal = PALETTES.get(Config.theme(), PALETTES["light"])
        hdr_color = pal["hint_fg"]
        for i, d in enumerate(days):
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"font-weight: bold; padding: 4px; color: {hdr_color};")
            self._grid.addWidget(lbl, 0, i)

        self._month_label.setText(f"{self._year} 年 {self._month} 月")

        records = get_month_records(self._year, self._month)
        rmap = {r["record_date"]: r for r in records}

        first = date(self._year, self._month, 1)
        if self._month == 12:
            nm = date(self._year + 1, 1, 1)
        else:
            nm = date(self._year, self._month + 1, 1)
        last_day = (nm - timedelta(days=1)).day
        start_col = first.weekday()
        today = date.today()

        row = 1
        day = 1
        total = 0
        done = 0

        for i in range(start_col):
            self._grid.addWidget(QFrame(), row, i)

        col = start_col
        while day <= last_day:
            if col >= 7:
                col = 0
                row += 1
            d = date(self._year, self._month, day)
            ds = d.isoformat()
            r = rmap.get(ds, None)
            ts = r["total_seconds"] if r else 0
            tg = r["target_seconds"] if r else 0
            cell = DayCell(day, ds, ts, tg, d == today, self._scale_factor, self)
            cell.mousePressEvent = lambda e, ds=ds: self._detail(ds)
            self._grid.addWidget(cell, row, col)
            total += ts
            if tg > 0 and ts >= tg:
                done += 1
            day += 1
            col += 1

        h = total // 3600
        m = (total % 3600) // 60
        tgt = Config.daily_target_minutes()
        if tgt > 0:
            self._summary.setText(
                f"本月总时长: {h}h{m}m  |  日均: {total // max(1, last_day) // 60}m  |  "
                f"达标: {done}/{last_day}"
            )
        else:
            self._summary.setText(f"本月总时长: {h}h{m}m")

    def _clear_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def _go_today(self):
        today = date.today()
        if self._year != today.year or self._month != today.month:
            self._year = today.year
            self._month = today.month
            self._build()

    def _prev(self):
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self._build()

    def _next(self):
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self._build()

    def _detail(self, ds: str):
        DayDetailDialog(ds, self).exec()

    def refresh(self):
        self._build()
