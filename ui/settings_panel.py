"""
Settings panel — daily target, sedentary reminder, theme, auto-start, data export.
"""
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSpinBox, QComboBox, QCheckBox, QGroupBox,
    QFormLayout, QFileDialog, QMessageBox, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.config import Config
from core.database import export_all_records, export_app_usage_all
from core.theme import THEME_NAMES


class SettingsPanel(QFrame):
    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        self.setObjectName("settingsPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("设置")
        title.setObjectName("panelTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Scroll area to prevent content clipping at any window size
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("settingsScroll")
        scroll.viewport().setObjectName("settingsScroll")

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(10)
        cl.setContentsMargins(12, 8, 12, 12)

        # ── Daily target ──
        g = QGroupBox("每日学习目标")
        g.setObjectName("settingsGroup")
        f = QFormLayout(g)
        self._target_spin = QSpinBox()
        self._target_spin.setRange(0, 1440)
        self._target_spin.setSuffix(" 分钟")
        self._target_spin.setSpecialValueText("未设置")
        self._target_spin.valueChanged.connect(Config.set_daily_target_minutes)
        f.addRow("每日目标:", self._target_spin)
        cl.addWidget(g)

        # ── Pomodoro ──
        g = QGroupBox("番茄钟")
        g.setObjectName("settingsGroup")
        f = QFormLayout(g)
        self._focus_spin = QSpinBox()
        self._focus_spin.setRange(1, 120)
        self._focus_spin.setSuffix(" 分钟")
        self._focus_spin.valueChanged.connect(Config.set_pomodoro_focus)
        f.addRow("专注时长:", self._focus_spin)
        self._break_spin = QSpinBox()
        self._break_spin.setRange(1, 60)
        self._break_spin.setSuffix(" 分钟")
        self._break_spin.valueChanged.connect(Config.set_pomodoro_break)
        f.addRow("休息时长:", self._break_spin)
        cl.addWidget(g)

        # ── Sedentary ──
        g = QGroupBox("久坐提醒")
        g.setObjectName("settingsGroup")
        v = QVBoxLayout(g)
        self._sed_check = QCheckBox("启用久坐提醒")
        self._sed_check.toggled.connect(Config.set_sedentary_enabled)
        v.addWidget(self._sed_check)
        h = QHBoxLayout()
        self._sed_spin = QSpinBox()
        self._sed_spin.setRange(5, 240)
        self._sed_spin.setSuffix(" 分钟")
        self._sed_spin.valueChanged.connect(Config.set_sedentary_interval)
        h.addWidget(QLabel("提醒间隔:"))
        h.addWidget(self._sed_spin)
        h.addStretch()
        v.addLayout(h)
        cl.addWidget(g)

        # ── App monitor ──
        g = QGroupBox("应用使用统计")
        g.setObjectName("settingsGroup")
        v = QVBoxLayout(g)
        self._app_check = QCheckBox("启用应用统计（后台记录各软件使用时长）")
        self._app_check.toggled.connect(Config.set_app_monitor_enabled)
        v.addWidget(self._app_check)
        cl.addWidget(g)

        # ── Theme ──
        g = QGroupBox("主题")
        g.setObjectName("settingsGroup")
        h = QHBoxLayout(g)
        self._theme_combo = QComboBox()
        for k, n in THEME_NAMES.items():
            self._theme_combo.addItem(n, k)
        self._theme_combo.currentIndexChanged.connect(self._on_theme)
        h.addWidget(QLabel("界面主题:"))
        h.addWidget(self._theme_combo)
        h.addStretch()
        cl.addWidget(g)

        # ── Auto-start ──
        g = QGroupBox("启动设置")
        g.setObjectName("settingsGroup")
        v = QVBoxLayout(g)
        self._auto_check = QCheckBox("开机自启")
        self._auto_check.toggled.connect(self._on_auto_start)
        v.addWidget(self._auto_check)
        cl.addWidget(g)

        # ── Export ──
        g = QGroupBox("数据导出")
        g.setObjectName("settingsGroup")
        h = QHBoxLayout(g)
        self._btn_txt = QPushButton("导出 TXT")
        self._btn_txt.setObjectName("btnSecondary")
        self._btn_txt.clicked.connect(lambda: self._export("txt"))
        self._btn_xlsx = QPushButton("导出 Excel")
        self._btn_xlsx.setObjectName("btnSecondary")
        self._btn_xlsx.clicked.connect(lambda: self._export("xlsx"))
        h.addWidget(self._btn_txt)
        h.addWidget(self._btn_xlsx)
        h.addStretch()
        cl.addWidget(g)

        # ── About ──
        g = QGroupBox("关于")
        g.setObjectName("settingsGroup")
        v = QVBoxLayout(g)
        about_label = QLabel(
            'Timer v1.0 — 轻量学习计时工具<br>'
            '作者: <a href="https://1zzhiyuan.github.io/" style="color: #4f6ef7; text-decoration: none;">ZhiYuan</a>'
        )
        about_label.setOpenExternalLinks(True)
        about_label.setStyleSheet("font-size: 13px; font-weight: normal; line-height: 1.6;")
        v.addWidget(about_label)
        cl.addWidget(g)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

    def _load_settings(self):
        self._target_spin.setValue(Config.daily_target_minutes())
        self._focus_spin.setValue(Config.pomodoro_focus())
        self._break_spin.setValue(Config.pomodoro_break())
        self._sed_check.setChecked(Config.sedentary_enabled())
        self._sed_spin.setValue(Config.sedentary_interval())
        self._app_check.setChecked(Config.app_monitor_enabled())
        self._auto_check.setChecked(Config.auto_start())
        idx = self._theme_combo.findData(Config.theme())
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)

    def _on_theme(self, idx: int):
        if idx < 0:
            return
        key = self._theme_combo.itemData(idx)
        Config.set_theme(key)
        self.theme_changed.emit(key)

    def _on_auto_start(self, checked: bool):
        Config.set_auto_start(checked)
        try:
            import winreg
            import sys
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            if checked:
                app = sys.argv[0]
                if not app.endswith(".exe"):
                    app = f'"{sys.executable}" "{__file__}"'
                winreg.SetValueEx(key, "Timer", 0, winreg.REG_SZ, app)
            else:
                try:
                    winreg.DeleteValue(key, "Timer")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    def _export(self, fmt: str):
        records = export_all_records()
        app_records = export_app_usage_all()

        if fmt == "txt":
            path, _ = QFileDialog.getSaveFileName(self, "导出为 TXT",
                f"timer_{date.today().isoformat()}.txt", "文本文件 (*.txt)")
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write("=== Timer 学习记录 ===\n\n")
                f.write("--- 每日记录 ---\n")
                for r in records:
                    mins = r["total_seconds"] // 60
                    t = f"{r['target_seconds'] // 60}分钟" if r.get("target_seconds") else "未设置"
                    f.write(f"{r['record_date']}: {mins}分钟 (目标: {t})\n")
                f.write("\n--- 应用使用记录 ---\n")
                for r in app_records[:50]:
                    f.write(f"{r['record_date']} | {r['app_name']}: {r['total_seconds'] // 60}分钟 [{r['category']}]\n")
            QMessageBox.information(self, "导出成功", f"已导出到:\n{path}")

        elif fmt == "xlsx":
            path, _ = QFileDialog.getSaveFileName(self, "导出为 Excel",
                f"timer_{date.today().isoformat()}.xlsx", "Excel 文件 (*.xlsx)")
            if not path:
                return
            try:
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                ws.title = "每日记录"
                ws.append(["日期", "学习时长(分钟)", "目标(分钟)", "分段数据"])
                for r in records:
                    ws.append([
                        r["record_date"],
                        r["total_seconds"] // 60,
                        r.get("target_seconds", 0) // 60 if r.get("target_seconds") else "",
                        r.get("session_intervals", ""),
                    ])
                ws2 = wb.create_sheet("应用使用")
                ws2.append(["日期", "应用名称", "使用时长(分钟)", "类别"])
                for r in app_records:
                    ws2.append([r["record_date"], r["app_name"], r["total_seconds"] // 60, r["category"]])
                wb.save(path)
                QMessageBox.information(self, "导出成功", f"已导出到:\n{path}")
            except ImportError:
                QMessageBox.warning(self, "导出失败", "导出 Excel 需要安装 openpyxl:\npip install openpyxl")

    def refresh(self):
        self._load_settings()
