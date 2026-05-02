"""
Theme management — QSS generated from color palettes.
Add a palette dict to PALETTES to create a new theme.
"""
from string import Template

_QSS = Template("""
/* ── Base ── */
QMainWindow, QWidget {
    background-color: $bg;
    color: $fg;
    font-family: "Microsoft YaHei", "Segoe UI", "PingFang SC", sans-serif;
    font-size: 14px;
}
QFrame#timerPanel, QFrame#calendarPanel, QFrame#statsPanel,
QFrame#settingsPanel, QFrame#pomodoroPanel {
    background-color: $bg;
    border: none;
}

/* ── Home Timer ── */
QLabel#homeTime { color: $home_time_fg; background: transparent; border: none; padding: 0; margin: 0; }
QLabel#homeHint { font-size: 14px; color: $hint_fg; padding: 2px 0; }
QLabel#homeStats { font-size: 12px; color: $hint_fg; background: transparent; border: none; padding: 0; }
QPushButton#homeBtn {
    background-color: $accent; color: white; border: none; border-radius: 25px;
    padding: 4px 36px; font-size: 16px; font-weight: bold; letter-spacing: 2px;
}
QPushButton#homeBtn:hover { background-color: $accent_hover; }
QPushButton#homeBtn:pressed { background-color: $accent_pressed; }
QPushButton#homeBtnReset {
    background-color: $reset_bg; color: white; border: none; border-radius: 25px;
    padding: 4px 20px; font-size: 14px; font-weight: bold;
}
QPushButton#homeBtnReset:hover { background-color: $reset_hover; }
QPushButton#homeBtnReset:disabled { background-color: $border_color; color: $hint_fg; }
QPushButton#homeBtnMini {
    background-color: transparent; color: $hint_fg; border: 1px solid $card_border;
    border-radius: 25px; font-weight: bold;
}
QPushButton#homeBtnMini:hover { background-color: $hover_bg; border-color: $accent; }
QFrame#homeProg { background-color: $prog_bg; border-radius: 2px; }
QFrame#homeBar { background-color: $accent; border-radius: 2px; }

/* ── Panel Title ── */
QLabel#panelTitle { font-size: 19px; font-weight: bold; color: $fg; padding: 12px 0 8px 0; }

QLabel#pomodoroDisplay {
    color: $pomo_fg; background-color: $pomo_bg; border-radius: 18px;
    padding: 18px 10px; border: 1px solid $pomo_border; font-size: 52px; font-weight: bold;
}
QLabel#pomodoroState { font-size: 18px; color: $pomo_fg; }
QLabel#pomodoroCount { font-size: 14px; color: $hint_fg; }
QLabel#monthLabel, QLabel#summaryLabel { font-size: 16px; font-weight: bold; color: $fg; padding: 4px; }
QLabel#statCard {
    background-color: $card_bg; border: 1px solid $card_border; border-radius: 10px;
    padding: 16px 20px; font-size: 15px; font-weight: bold; color: $fg; min-width: 110px;
}

/* ── Group Boxes ── */
QGroupBox#settingsGroup {
    background-color: $card_bg; border: 1px solid $card_border;
    border-radius: 12px; margin-top: 16px;
    padding: 22px 18px 16px 18px; font-size: 15px; font-weight: bold; color: $fg;
}
QGroupBox#settingsGroup::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; }

/* ── Buttons ── */
QPushButton#btnPrimary {
    background-color: $accent; color: white; border: none;
    border-radius: 10px; padding: 10px 24px; font-size: 15px; font-weight: bold; min-height: 38px;
}
QPushButton#btnPrimary:hover { background-color: $accent_hover; }
QPushButton#btnPrimary:disabled { background-color: $disabled_bg; color: $disabled_fg; }

QPushButton#btnSecondary {
    background-color: $card_bg; color: $fg;
    border: 1px solid $card_border; border-radius: 10px;
    padding: 10px 20px; font-size: 14px; min-height: 38px;
}
QPushButton#btnSecondary:hover { background-color: $hover_bg; border-color: $accent; }
QPushButton#btnSecondary:checked { background-color: $accent; color: white; border-color: $accent; }

QPushButton#btnDanger {
    background-color: $card_bg; color: $danger_fg;
    border: 1px solid $danger_border; border-radius: 10px;
    padding: 10px 20px; font-size: 14px; min-height: 38px;
}
QPushButton#btnDanger:hover { background-color: $danger_hover_bg; border-color: $danger_fg; }
QPushButton#btnDanger:disabled { background-color: $card_bg; color: $disabled_fg; border-color: $border_color; }

/* ── Nav Bar ── */
QFrame#navBar { background-color: $nav_bg; border-top: 1px solid $nav_top_border; }
QPushButton#navBtn {
    background-color: transparent; color: $nav_icon; border: none;
    font-size: 20px; padding: 0; margin: 0; border-top: 3px solid transparent;
}
QPushButton#navBtn:hover { color: $accent; background-color: $nav_hover_bg; }
QPushButton#navBtn:checked { color: $accent; border-top: 3px solid $accent; background-color: $nav_active_bg; }

/* ── Inputs ── */
QComboBox, QSpinBox {
    background-color: $card_bg; border: 1px solid $card_border;
    border-radius: 8px; padding: 6px 12px; min-height: 34px; font-size: 14px; color: $fg;
}
QComboBox:hover, QSpinBox:hover { border-color: $accent; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView { background-color: $card_bg; color: $fg; selection-background-color: $accent; border: none; }

QCheckBox { spacing: 10px; font-size: 14px; color: $fg; }
QCheckBox::indicator { width: 20px; height: 20px; border-radius: 5px; border: 2px solid $hint_fg; }
QCheckBox::indicator:checked { background-color: $accent; border-color: $accent; }
QCheckBox::indicator:hover { border-color: $accent; }

QScrollBar:vertical { width: 6px; background: transparent; border-radius: 3px; }
QScrollBar::handle:vertical { background: $scroll_bg; border-radius: 3px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: $scroll_hover; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QTextEdit { background-color: $card_bg; border: 1px solid $card_border; border-radius: 8px; padding: 8px; color: $fg; }
QDialog { background-color: $card_bg; color: $fg; }
QMessageBox { background-color: $card_bg; color: $fg; }
""")

# ─── Color Palettes ────────────────────────────────────────────────────────────

PALETTES = {
    "light": {
        "bg": "#f0f2f5",
        "fg": "#1f2937",
        "hint_fg": "#6b7280",
        "card_bg": "#ffffff",
        "card_border": "transparent",
        "border_color": "#e5e7eb",
        "accent": "#4f6ef7",
        "accent_hover": "#3b5de7",
        "accent_pressed": "#2f4fd6",
        "disabled_bg": "#c7d2fe",
        "disabled_fg": "#a5b4fc",
        "hover_bg": "#f3f4f6",
        "prog_bg": "#e5e7eb",
        "nav_bg": "#ffffff",
        "nav_top_border": "#e5e7eb",
        "nav_icon": "#9ca3af",
        "nav_hover_bg": "rgba(79, 110, 247, 0.06)",
        "nav_active_bg": "rgba(79, 110, 247, 0.08)",
        "pomo_fg": "#ef4444",
        "pomo_bg": "#ffffff",
        "pomo_border": "transparent",
        "home_time_fg": "#1f2937",
        "reset_bg": "#6b7280",
        "reset_hover": "#4b5563",
        "danger_fg": "#ef4444",
        "danger_border": "#fca5a5",
        "danger_hover_bg": "#fef2f2",
        "scroll_bg": "#c4c8d0",
        "scroll_hover": "#9ca3af",
    },
    "dark": {
        "bg": "#1a1b1e",
        "fg": "#f3f4f6",
        "hint_fg": "#9ca3af",
        "card_bg": "#27282d",
        "card_border": "#3f3f46",
        "border_color": "#3f3f46",
        "accent": "#6b8cff",
        "accent_hover": "#5a7ce8",
        "accent_pressed": "#4b6bda",
        "disabled_bg": "#3f3f46",
        "disabled_fg": "#6b7280",
        "hover_bg": "#323338",
        "prog_bg": "#3f3f46",
        "nav_bg": "#27282d",
        "nav_top_border": "#3f3f46",
        "nav_icon": "#6b7280",
        "nav_hover_bg": "rgba(107, 140, 255, 0.08)",
        "nav_active_bg": "rgba(107, 140, 255, 0.10)",
        "pomo_fg": "#f87171",
        "pomo_bg": "#27282d",
        "pomo_border": "#3f3f46",
        "home_time_fg": "#f3f4f6",
        "reset_bg": "#52525b",
        "reset_hover": "#6b7280",
        "danger_fg": "#f87171",
        "danger_border": "#7f1d1d",
        "danger_hover_bg": "#450a0a",
        "scroll_bg": "#3f3f46",
        "scroll_hover": "#52525b",
    },
    "ocean": {
        "bg": "#eef2ff",
        "fg": "#1e293b",
        "hint_fg": "#64748b",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "border_color": "#cbd5e1",
        "accent": "#3b82f6",
        "accent_hover": "#2563eb",
        "accent_pressed": "#1d4ed8",
        "disabled_bg": "#bfdbfe",
        "disabled_fg": "#93c5fd",
        "hover_bg": "#f1f5f9",
        "prog_bg": "#e2e8f0",
        "nav_bg": "#ffffff",
        "nav_top_border": "#e2e8f0",
        "nav_icon": "#94a3b8",
        "nav_hover_bg": "rgba(59, 130, 246, 0.06)",
        "nav_active_bg": "rgba(59, 130, 246, 0.08)",
        "pomo_fg": "#3b82f6",
        "pomo_bg": "#ffffff",
        "pomo_border": "#e2e8f0",
        "home_time_fg": "#1e293b",
        "reset_bg": "#64748b",
        "reset_hover": "#475569",
        "danger_fg": "#ef4444",
        "danger_border": "#fca5a5",
        "danger_hover_bg": "#fef2f2",
        "scroll_bg": "#c4c8d0",
        "scroll_hover": "#94a3b8",
    },
    "forest": {
        "bg": "#f0fdf4",
        "fg": "#166534",
        "hint_fg": "#6b7280",
        "card_bg": "#ffffff",
        "card_border": "#dcfce7",
        "border_color": "#bbf7d0",
        "accent": "#22c55e",
        "accent_hover": "#16a34a",
        "accent_pressed": "#15803d",
        "disabled_bg": "#bbf7d0",
        "disabled_fg": "#86efac",
        "hover_bg": "#f0fdf4",
        "prog_bg": "#dcfce7",
        "nav_bg": "#ffffff",
        "nav_top_border": "#dcfce7",
        "nav_icon": "#86efac",
        "nav_hover_bg": "rgba(34, 197, 94, 0.06)",
        "nav_active_bg": "rgba(34, 197, 94, 0.08)",
        "pomo_fg": "#16a34a",
        "pomo_bg": "#ffffff",
        "pomo_border": "#dcfce7",
        "home_time_fg": "#166534",
        "reset_bg": "#6b7280",
        "reset_hover": "#4b5563",
        "danger_fg": "#ef4444",
        "danger_border": "#fca5a5",
        "danger_hover_bg": "#fef2f2",
        "scroll_bg": "#c4c8d0",
        "scroll_hover": "#9ca3af",
    },
    "sunset": {
        "bg": "#fff7ed",
        "fg": "#431407",
        "hint_fg": "#9a7b6a",
        "card_bg": "#ffffff",
        "card_border": "#fed7aa",
        "border_color": "#fdc4a6",
        "accent": "#f97316",
        "accent_hover": "#ea580c",
        "accent_pressed": "#c2410c",
        "disabled_bg": "#fed7aa",
        "disabled_fg": "#fdba74",
        "hover_bg": "#fff7ed",
        "prog_bg": "#fed7aa",
        "nav_bg": "#ffffff",
        "nav_top_border": "#fed7aa",
        "nav_icon": "#fdba74",
        "nav_hover_bg": "rgba(249, 115, 22, 0.06)",
        "nav_active_bg": "rgba(249, 115, 22, 0.08)",
        "pomo_fg": "#ea580c",
        "pomo_bg": "#ffffff",
        "pomo_border": "#fed7aa",
        "home_time_fg": "#431407",
        "reset_bg": "#9a7b6a",
        "reset_hover": "#7c5f4f",
        "danger_fg": "#ef4444",
        "danger_border": "#fca5a5",
        "danger_hover_bg": "#fef2f2",
        "scroll_bg": "#c4c8d0",
        "scroll_hover": "#9ca3af",
    },
}

# Dark variants for ocean/forest/sunset
DARK_PALETTES = {
    "ocean": {
        "bg": "#0f172a",
        "fg": "#e2e8f0",
        "hint_fg": "#64748b",
        "card_bg": "#1e293b",
        "card_border": "#334155",
        "border_color": "#334155",
        "accent": "#3b82f6",
        "accent_hover": "#2563eb",
        "accent_pressed": "#1d4ed8",
        "disabled_bg": "#1e3a5f",
        "disabled_fg": "#475569",
        "hover_bg": "#1e293b",
        "prog_bg": "#334155",
        "nav_bg": "#1e293b",
        "nav_top_border": "#334155",
        "nav_icon": "#475569",
        "nav_hover_bg": "rgba(59, 130, 246, 0.10)",
        "nav_active_bg": "rgba(59, 130, 246, 0.15)",
        "pomo_fg": "#60a5fa",
        "pomo_bg": "#1e293b",
        "pomo_border": "#334155",
        "home_time_fg": "#e2e8f0",
        "reset_bg": "#475569",
        "reset_hover": "#64748b",
        "danger_fg": "#f87171",
        "danger_border": "#7f1d1d",
        "danger_hover_bg": "#450a0a",
        "scroll_bg": "#334155",
        "scroll_hover": "#475569",
    },
    "forest": {
        "bg": "#052e16",
        "fg": "#f0fdf4",
        "hint_fg": "#6b7280",
        "card_bg": "#14532d",
        "card_border": "#166534",
        "border_color": "#166534",
        "accent": "#22c55e",
        "accent_hover": "#16a34a",
        "accent_pressed": "#15803d",
        "disabled_bg": "#14532d",
        "disabled_fg": "#4a7c5a",
        "hover_bg": "#166534",
        "prog_bg": "#166534",
        "nav_bg": "#14532d",
        "nav_top_border": "#166534",
        "nav_icon": "#4a7c5a",
        "nav_hover_bg": "rgba(34, 197, 94, 0.10)",
        "nav_active_bg": "rgba(34, 197, 94, 0.15)",
        "pomo_fg": "#4ade80",
        "pomo_bg": "#14532d",
        "pomo_border": "#166534",
        "home_time_fg": "#f0fdf4",
        "reset_bg": "#4a7c5a",
        "reset_hover": "#6b8c7b",
        "danger_fg": "#f87171",
        "danger_border": "#7f1d1d",
        "danger_hover_bg": "#450a0a",
        "scroll_bg": "#166534",
        "scroll_hover": "#22c55e",
    },
    "sunset": {
        "bg": "#1c1917",
        "fg": "#fef3c7",
        "hint_fg": "#9a7b6a",
        "card_bg": "#292524",
        "card_border": "#44403c",
        "border_color": "#44403c",
        "accent": "#f97316",
        "accent_hover": "#ea580c",
        "accent_pressed": "#c2410c",
        "disabled_bg": "#3a2a1a",
        "disabled_fg": "#6b4f3a",
        "hover_bg": "#3a2a1a",
        "prog_bg": "#44403c",
        "nav_bg": "#292524",
        "nav_top_border": "#44403c",
        "nav_icon": "#6b4f3a",
        "nav_hover_bg": "rgba(249, 115, 22, 0.10)",
        "nav_active_bg": "rgba(249, 115, 22, 0.15)",
        "pomo_fg": "#fb923c",
        "pomo_bg": "#292524",
        "pomo_border": "#44403c",
        "home_time_fg": "#fef3c7",
        "reset_bg": "#6b4f3a",
        "reset_hover": "#9a7b6a",
        "danger_fg": "#f87171",
        "danger_border": "#7f1d1d",
        "danger_hover_bg": "#450a0a",
        "scroll_bg": "#44403c",
        "scroll_hover": "#6b4f3a",
    },
}

# Display names for UI
THEME_NAMES = {
    "light": "☀️ 简约浅色",
    "dark": "🌙 深色护眼",
    "ocean": "🌊 静谧蓝",
    "forest": "🌿 护眼绿",
    "sunset": "🌅 暖阳橙",
}


def get_style(theme: str) -> str:
    """Generate full QSS for the given theme key."""
    palette = PALETTES.get(theme) or PALETTES["light"]
    return _QSS.substitute(**palette)
