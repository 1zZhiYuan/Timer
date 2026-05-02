"""
History dialog — browse past study sessions and daily records.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor

from datetime import date
from core.database import export_all_records, get_pomodoro_sessions


class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("历史记录")
        self.setMinimumSize(650, 450)
        self.resize(750, 500)
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # ── Daily records tab ──
        daily_tab = QWidget()
        daily_layout = QVBoxLayout(daily_tab)
        self._daily_table = QTableWidget()
        self._daily_table.setColumnCount(4)
        self._daily_table.setHorizontalHeaderLabels(["日期", "学习时长", "目标", "达标"])
        self._daily_table.horizontalHeader().setStretchLastSection(True)
        self._daily_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._daily_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._daily_table.setAlternatingRowColors(True)
        daily_layout.addWidget(self._daily_table)
        tabs.addTab(daily_tab, "📅 每日记录")

        # ── Pomodoro tab ──
        pomo_tab = QWidget()
        pomo_layout = QVBoxLayout(pomo_tab)
        self._pomo_table = QTableWidget()
        self._pomo_table.setColumnCount(4)
        self._pomo_table.setHorizontalHeaderLabels(["日期", "专注数", "专注时长", "休息时长"])
        self._pomo_table.horizontalHeader().setStretchLastSection(True)
        self._pomo_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._pomo_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._pomo_table.setAlternatingRowColors(True)
        pomo_layout.addWidget(self._pomo_table)
        tabs.addTab(pomo_tab, "🍅 番茄记录")

        layout.addWidget(tabs)

        # Summary
        summary_layout = QHBoxLayout()
        self._summary_label = QLabel()
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_layout.addWidget(self._summary_label)
        layout.addLayout(summary_layout)

        btn = QPushButton("关闭")
        btn.setObjectName("btnPrimary")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        self._load_data()

    def _load_data(self):
        # Daily records
        records = export_all_records()
        self._daily_table.setRowCount(len(records))
        total_mins = 0
        total_days = len(records)
        for i, r in enumerate(records):
            mins = r["total_seconds"] // 60
            total_mins += mins
            tgt = r.get("target_seconds", 0) // 60
            met = "✓" if tgt > 0 and mins >= tgt else ("✗" if tgt > 0 else "-")

            self._daily_table.setItem(i, 0, QTableWidgetItem(r["record_date"]))
            self._daily_table.setItem(i, 1, QTableWidgetItem(f"{mins} 分钟"))

            tgt_item = QTableWidgetItem(f"{tgt} 分钟" if tgt > 0 else "未设置")
            self._daily_table.setItem(i, 2, tgt_item)

            met_item = QTableWidgetItem(met)
            c = "#22c55e" if met == "✓" else "#ef4444" if met == "✗" else "#9ca3af"
            met_item.setForeground(QBrush(QColor(c)))
            met_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._daily_table.setItem(i, 3, met_item)

        # Pomodoro records
        today = date.today()
        pomo_records = get_pomodoro_sessions(
            today.replace(year=today.year - 1).isoformat(),
            today.isoformat(),
        )
        self._pomo_table.setRowCount(len(pomo_records))
        total_pomos = 0
        for i, r in enumerate(pomo_records):
            total_pomos += r["completed_count"]
            self._pomo_table.setItem(i, 0, QTableWidgetItem(r["record_date"]))
            self._pomo_table.setItem(i, 1, QTableWidgetItem(str(r["completed_count"])))
            self._pomo_table.setItem(i, 2, QTableWidgetItem(f"{r['focus_minutes']} 分钟"))
            self._pomo_table.setItem(i, 3, QTableWidgetItem(f"{r['break_minutes']} 分钟"))

        h = total_mins // 60
        m = total_mins % 60
        self._summary_label.setText(
            f"共 {total_days} 天记录  |  总学习 {h}h{m}m  |  番茄总数 {total_pomos} 个"
        )
