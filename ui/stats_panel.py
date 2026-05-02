"""
Statistics panel — weekly/monthly charts (QPainter), app usage ranking, time-period breakdown.
No matplotlib dependency.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QGroupBox, QTextEdit, QSizePolicy, QScrollArea,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QFontMetrics

from datetime import date, timedelta, datetime
from core.database import get_records_in_range, get_app_usage_range, get_total_stats, get_early_bird_count, get_night_owl_count
from core.config import Config
from core.theme import PALETTES


class _LineChart(QWidget):
    """Custom QPainter-drawn line chart for daily study trend."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dates = []
        self._values = []
        self._target = 0
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, dates, values, target=0):
        self._dates = dates
        self._values = values
        self._target = target
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        ml, mr, mt, mb = 45, 16, 16, 32
        cw, ch = w - ml - mr, h - mt - mb

        if not self._values or cw < 40 or ch < 20:
            p.setPen(QColor("#9ca3af"))
            p.setFont(QFont("", 10))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无数据")
            return

        max_val = max(self._values)
        if self._target > 0:
            max_val = max(max_val, self._target)
        max_val = max(max_val * 1.15, 10)

        n = len(self._values)
        step = cw / (n - 1) if n > 1 else cw

        # Grid lines
        grid_pen = QPen(QColor("#e5e7eb"), 1)
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        p.setFont(QFont("", 7))
        for i in range(5):
            y = mt + ch * i / 4
            p.setPen(grid_pen)
            p.drawLine(int(ml), int(y), int(w - mr), int(y))
            val = max_val * (1 - i / 4)
            p.setPen(QColor("#9ca3af"))
            p.drawText(QRectF(0, y - 10, ml - 6, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(int(val)))

        # X labels
        p.setPen(QColor("#9ca3af"))
        p.setFont(QFont("", 7))
        label_interval = max(1, n // 10)
        for i in range(n):
            if i % label_interval != 0 and i != n - 1:
                continue
            x = ml + step * i
            p.drawText(QRectF(x - 24, h - mb + 2, 48, 20), Qt.AlignmentFlag.AlignCenter, self._dates[i].strftime("%m/%d"))

        # Build line points
        pts = []
        for i, v in enumerate(self._values):
            x = ml + step * i
            y = mt + ch * (1 - v / max_val)
            pts.append((x, y))

        # Fill under line
        if len(pts) > 1:
            fill = QPainterPath()
            fill.moveTo(pts[0][0], mt + ch)
            for x, y in pts:
                fill.lineTo(x, y)
            fill.lineTo(pts[-1][0], mt + ch)
            fill.closeSubpath()
            p.fillPath(fill, QColor(79, 110, 247, 25))

        # Line
        p.setPen(QPen(QColor("#4f6ef7"), 2.5))
        path = QPainterPath()
        path.moveTo(pts[0][0], pts[0][1])
        for x, y in pts[1:]:
            path.lineTo(x, y)
        p.drawPath(path)

        # Dots
        for x, y in pts:
            p.setBrush(QColor("#4f6ef7"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)

        # Target line
        if self._target > 0:
            ty = mt + ch * (1 - self._target / max_val)
            pen = QPen(QColor("#ef4444"), 1.5)
            pen.setStyle(Qt.PenStyle.DashLine)
            p.setPen(pen)
            p.drawLine(int(ml), int(ty), int(w - mr), int(ty))
            p.setPen(QColor("#ef4444"))
            p.setFont(QFont("", 7))
            p.drawText(QRectF(w - mr - 60, ty - 18, 60, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, f"目标 {self._target}m")


class _BarChart(QWidget):
    """Custom QPainter-drawn bar chart for daily comparison."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dates = []
        self._values = []
        self._target = 0
        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, dates, values, target=0):
        self._dates = dates
        self._values = values
        self._target = target
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        ml, mr, mt, mb = 40, 12, 12, 28
        cw, ch = w - ml - mr, h - mt - mb

        if not self._values or cw < 40 or ch < 20:
            p.setPen(QColor("#9ca3af"))
            p.setFont(QFont("", 10))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无数据")
            return

        max_val = max(self._values)
        if self._target > 0:
            max_val = max(max_val, self._target)
        max_val = max(max_val * 1.2, 10)

        n = len(self._values)
        bar_w = min(28, cw // n - 4)
        gap = (cw - bar_w * n) / (n + 1)

        # Grid
        grid_pen = QPen(QColor("#e5e7eb"), 1)
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        p.setFont(QFont("", 7))
        for i in range(4):
            y = mt + ch * i / 3
            p.setPen(grid_pen)
            p.drawLine(int(ml), int(y), int(w - mr), int(y))
            val = max_val * (1 - i / 3)
            p.setPen(QColor("#9ca3af"))
            p.drawText(QRectF(0, y - 10, ml - 6, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(int(val)))

        # Bars
        label_interval = max(1, n // 8)
        for i, v in enumerate(self._values):
            x = ml + gap * (i + 1) + bar_w * i
            bar_h = ch * (v / max_val)
            y = mt + ch - bar_h

            if self._target > 0 and v >= self._target:
                color = QColor("#22c55e")
            elif v == 0:
                color = QColor("#d1d5db")
            else:
                color = QColor("#4f6ef7")
            p.setBrush(color)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(int(x), int(y), int(bar_w), int(bar_h), 3, 3)

            # X label
            if i % label_interval == 0 or i == n - 1:
                p.setPen(QColor("#9ca3af"))
                p.drawText(QRectF(x - 16, h - mb + 2, bar_w + 32, 20), Qt.AlignmentFlag.AlignCenter, self._dates[i].strftime("%m/%d"))

        # Target line
        if self._target > 0:
            ty = mt + ch * (1 - self._target / max_val)
            pen = QPen(QColor("#ef4444"), 1.5)
            pen.setStyle(Qt.PenStyle.DashLine)
            p.setPen(pen)
            p.drawLine(int(ml), int(ty), int(w - mr), int(ty))


class StatsPanel(QFrame):
    def __init__(self):
        super().__init__()
        self._mode = "weekly"
        self._scale_factor = 1.0
        self._ref_h = 500
        self._setup_ui()

    def _scale(self, h):
        s = h / self._ref_h
        self._scale_factor = max(0.55, min(2.0, s))
        # Scale chart height
        ch = max(80, int(160 * self._scale_factor))
        self._line_chart.setMinimumHeight(ch)
        self._bar_chart.setMinimumHeight(ch)
        # Scale app text area
        self._app_text.setMaximumHeight(int(100 * self._scale_factor))
        # Scale period text — use inline stylesheet to override QSS
        pf = max(10, int(14 * self._scale_factor))
        pal = PALETTES.get(Config.theme(), PALETTES["light"])
        tc = pal["hint_fg"]
        self._period_text.setStyleSheet(f"font-size: {pf}px; color: {tc}; background: transparent; padding: 4px;")
        # Scale badge text
        bf = max(10, int(13 * self._scale_factor))
        self._badge_text.setStyleSheet(f"font-size: {bf}px; color: {tc}; background: transparent; padding: 2px;")

    def _toggle_chart(self, mode: str):
        self._chart_mode = mode
        self._btn_line.setChecked(mode == "line")
        self._btn_bar.setChecked(mode == "bar")
        self._line_chart.setVisible(mode == "line")
        self._bar_chart.setVisible(mode == "bar")

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._scale(self.height())

    def _setup_ui(self):
        self.setObjectName("statsPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("数据报表")
        title.setObjectName("panelTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Scroll area for all content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("statsScroll")
        scroll.viewport().setObjectName("statsScroll")

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(8)
        cl.setContentsMargins(12, 8, 12, 12)

        # ── Summary cards row ──
        summary_layout = QHBoxLayout()
        self._total_label = QLabel("总时长: 0h")
        self._total_label.setObjectName("statCard")
        self._daily_avg_label = QLabel("日均: 0m")
        self._daily_avg_label.setObjectName("statCard")
        self._best_label = QLabel("最佳: 0m")
        self._best_label.setObjectName("statCard")
        summary_layout.addWidget(self._total_label)
        summary_layout.addWidget(self._daily_avg_label)
        summary_layout.addWidget(self._best_label)
        cl.addLayout(summary_layout)

        # ── Mode + chart toggle row ──
        toolbar = QHBoxLayout()
        toolbar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.setSpacing(8)
        self._btn_weekly = QPushButton("本周")
        self._btn_weekly.setObjectName("btnSecondary")
        self._btn_weekly.setCheckable(True)
        self._btn_weekly.setChecked(True)
        self._btn_weekly.clicked.connect(lambda: self._switch_mode("weekly"))
        self._btn_monthly = QPushButton("本月")
        self._btn_monthly.setObjectName("btnSecondary")
        self._btn_monthly.setCheckable(True)
        self._btn_monthly.clicked.connect(lambda: self._switch_mode("monthly"))
        toolbar.addWidget(self._btn_weekly)
        toolbar.addWidget(self._btn_monthly)
        toolbar.addSpacing(20)
        self._btn_line = QPushButton("📈 折线图")
        self._btn_line.setObjectName("btnSecondary")
        self._btn_line.setCheckable(True)
        self._btn_line.setChecked(True)
        self._btn_line.clicked.connect(lambda: self._toggle_chart("line"))
        self._btn_bar = QPushButton("📊 柱状图")
        self._btn_bar.setObjectName("btnSecondary")
        self._btn_bar.setCheckable(True)
        self._btn_bar.clicked.connect(lambda: self._toggle_chart("bar"))
        toolbar.addWidget(self._btn_line)
        toolbar.addWidget(self._btn_bar)
        cl.addLayout(toolbar)

        # ── Chart (shows one at a time) ──
        self._chart_stack = QVBoxLayout()
        self._chart_stack.setSpacing(0)
        self._line_chart = _LineChart()
        self._bar_chart = _BarChart()
        self._chart_stack.addWidget(self._line_chart)
        # bar chart is hidden initially
        cl.addLayout(self._chart_stack)

        # ── Two-column: period breakdown + app usage ──
        two_col = QHBoxLayout()
        two_col.setSpacing(8)

        period_group = QGroupBox("时段统计")
        period_group.setObjectName("settingsGroup")
        period_layout = QVBoxLayout(period_group)
        self._period_text = QLabel("🌅 上午: 0m\n☀️ 下午: 0m\n🌙 晚间: 0m")
        self._period_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._period_text.setWordWrap(True)
        period_layout.addWidget(self._period_text)
        two_col.addWidget(period_group)

        app_group = QGroupBox("应用排行")
        app_group.setObjectName("settingsGroup")
        app_layout = QVBoxLayout(app_group)
        self._app_text = QTextEdit()
        self._app_text.setReadOnly(True)
        self._app_text.setMaximumHeight(100)
        app_layout.addWidget(self._app_text)
        two_col.addWidget(app_group)

        cl.addLayout(two_col)

        # ── Achievement badges + focus score ──
        badge_group = QGroupBox("成就徽章")
        badge_group.setObjectName("settingsGroup")
        badge_layout = QVBoxLayout(badge_group)
        self._badge_text = QLabel("加载中...")
        self._badge_text.setWordWrap(True)
        self._badge_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_layout.addWidget(self._badge_text)
        score_layout = QHBoxLayout()
        score_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._focus_score_label = QLabel("📊 专注指数: --")
        self._focus_score_label.setObjectName("statCard")
        self._focus_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(self._focus_score_label)
        score_layout.addStretch()
        badge_layout.addLayout(score_layout)
        cl.addWidget(badge_group)

        # ── History button ──
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._btn_history = QPushButton("📋 查看历史记录")
        self._btn_history.setObjectName("btnSecondary")
        self._btn_history.clicked.connect(self._show_history)
        btn_layout.addWidget(self._btn_history)
        cl.addLayout(btn_layout)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

        self._chart_mode = "line"
        self._update_charts()

    def _switch_mode(self, mode: str):
        self._mode = mode
        self._btn_weekly.setChecked(mode == "weekly")
        self._btn_monthly.setChecked(mode == "monthly")
        self._update_charts()

    def _get_date_range(self) -> tuple[str, str]:
        today = date.today()
        if self._mode == "weekly":
            monday = today - timedelta(days=today.weekday())
            return monday.isoformat(), today.isoformat()
        first = today.replace(day=1)
        return first.isoformat(), today.isoformat()

    def _update_charts(self):
        start, end = self._get_date_range()
        records = get_records_in_range(start, end)

        # Summary
        if not records:
            self._total_label.setText("总时长: 0h")
            self._daily_avg_label.setText("日均: 0m")
            self._best_label.setText("最佳: 0m")
            self._line_chart.set_data([], [])
            self._bar_chart.set_data([], [])
            self._period_text.setText("🌅 上午: 0m\n☀️ 下午: 0m\n🌙 晚间: 0m")
            self._app_text.setText("暂无数据")
            return

        sorted_records = sorted(records, key=lambda x: x["record_date"])
        dates = []
        minutes = []
        for r in sorted_records:
            dates.append(datetime.strptime(r["record_date"], "%Y-%m-%d").date())
            minutes.append(r["total_seconds"] // 60)

        target = Config.daily_target_minutes()

        # Update charts
        self._line_chart.set_data(dates, minutes, target)
        self._bar_chart.set_data(dates, minutes, target)

        # Summary
        total_mins = sum(minutes)
        avg_mins = total_mins // len(minutes)
        best_mins = max(minutes)
        self._total_label.setText(f"总时长: {total_mins // 60}h{total_mins % 60}m")
        self._daily_avg_label.setText(f"日均: {avg_mins}m")
        self._best_label.setText(f"最佳: {best_mins}m")

        # Period breakdown
        self._update_period_breakdown(sorted_records)
        self._update_app_ranking(start, end)

    def _update_period_breakdown(self, records: list):
        import json
        morning = afternoon = evening = 0
        for r in records:
            intervals = json.loads(r.get("session_intervals", "[]"))
            for iv in intervals:
                secs = iv.get("seconds", 0)
                try:
                    h = datetime.fromisoformat(iv.get("start", "")).hour
                except (ValueError, TypeError):
                    morning += secs // 3
                    afternoon += secs // 3
                    evening += secs // 3
                    continue
                if h < 12: morning += secs
                elif h < 18: afternoon += secs
                else: evening += secs
        self._period_text.setText(
            f"🌅 上午: {morning // 60}m\n"
            f"☀️ 下午: {afternoon // 60}m\n"
            f"🌙 晚间: {evening // 60}m"
        )

    def _update_app_ranking(self, start: str, end: str):
        apps = get_app_usage_range(start, end)
        if not apps:
            self._app_text.setText("暂无应用使用数据")
            return
        lines = []
        for i, app in enumerate(apps[:10], 1):
            m = app["total_seconds"] // 60
            emoji = "📖" if app["category"] == "study" else "🎮" if app["category"] == "entertainment" else "💻"
            lines.append(f"{i}. {emoji} {app['app_name']}  {m}分钟")
        self._app_text.setText("\n".join(lines))

    def _update_badges(self):
        stats = get_total_stats()
        total_days = stats["total_days"]
        total_hours = stats["total_seconds"] // 3600
        days_met = stats["days_met_target"]
        best_streak = stats["best_streak"]
        early_bird = get_early_bird_count()
        night_owl = get_night_owl_count()

        badges = []
        if total_days >= 1:
            badges.append("🚀 第一步")
        if total_days >= 7:
            badges.append("📅 坚持一周")
        if total_days >= 30:
            badges.append("📅 坚持一月")
        if total_days >= 60:
            badges.append("💪 坚持60天")
        if total_days >= 100:
            badges.append("🏆 百日达人")
        if best_streak >= 7:
            badges.append(f"🔥 {best_streak}天连击")
        if best_streak >= 30:
            badges.append(f"⭐ 超级连击")
        if total_hours >= 10:
            badges.append("⏱ 十时达人")
        if total_hours >= 50:
            badges.append("⏱ 五十小时")
        if total_hours >= 100:
            badges.append("💯 百时达人")
        if total_hours >= 500:
            badges.append("👑 五百小时")
        if days_met >= 7:
            badges.append("🎯 达标7天")
        if days_met >= 30:
            badges.append("🎯 达标30天")
        if early_bird >= 3:
            badges.append("🌅 早起鸟")
        if night_owl >= 3:
            badges.append("🌙 夜猫子")

        if badges:
            self._badge_text.setText("  ".join(badges))
        else:
            self._badge_text.setText("💡 开始学习以解锁成就徽章")

        # Focus score (0-100)
        score = self._calc_focus_score(stats)
        self._focus_score_label.setText(f"📊 专注指数: {score}")

    def _calc_focus_score(self, stats: dict) -> int:
        """Calculate a 0-100 focus score based on consistency and volume."""
        days = stats["total_days"]
        hours = stats["total_seconds"] / 3600
        streak = stats["best_streak"]
        met = stats["days_met_target"]

        if days == 0:
            return 0

        # Consistency: days with activity / total tracked days
        consistency = min(40, int(days * 2))

        # Volume: hours logged (capped at 100h = 40 pts)
        volume = min(40, int(hours * 0.4))

        # Streak bonus
        streak_bonus = min(10, streak)

        # Target achievement
        achieve = min(10, int(met * 0.5))

        return min(100, consistency + volume + streak_bonus + achieve)

    def _show_history(self):
        from ui.history_dialog import HistoryDialog
        HistoryDialog(self).exec()

    def refresh(self):
        self._update_charts()
        self._update_badges()
        self._scale(self.height())
