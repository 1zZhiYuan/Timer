"""
Configuration manager — wraps the settings table in SQLite.
"""
from core.database import get_setting, set_setting


class Config:
    """Type-safe access to application settings."""

    # Keys
    DAILY_TARGET = "daily_target_minutes"
    SEDENTARY_INTERVAL = "sedentary_interval_minutes"
    POMODORO_FOCUS = "pomodoro_focus_minutes"
    POMODORO_BREAK = "pomodoro_break_minutes"
    THEME = "theme"
    AUTO_START = "auto_start"
    APP_MONITOR_ENABLED = "app_monitor_enabled"
    SEDENTARY_ENABLED = "sedentary_enabled"

    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        val = get_setting(key, str(default))
        try:
            return int(val)
        except ValueError:
            return default

    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        val = get_setting(key, "true" if default else "false")
        return val.lower() in ("true", "1", "yes")

    @classmethod
    def get_str(cls, key: str, default: str = "") -> str:
        return get_setting(key, default)

    @classmethod
    def set_int(cls, key: str, value: int):
        set_setting(key, str(value))

    @classmethod
    def set_bool(cls, key: str, value: bool):
        set_setting(key, "true" if value else "false")

    @classmethod
    def set_str(cls, key: str, value: str):
        set_setting(key, value)

    # ─── Convenience accessors ────────────────────────────────────────────────

    @classmethod
    def daily_target_minutes(cls) -> int:
        return cls.get_int(cls.DAILY_TARGET, 120)

    @classmethod
    def set_daily_target_minutes(cls, minutes: int):
        cls.set_int(cls.DAILY_TARGET, max(0, minutes))

    @classmethod
    def sedentary_interval(cls) -> int:
        """Return interval in minutes."""
        return cls.get_int(cls.SEDENTARY_INTERVAL, 60)

    @classmethod
    def set_sedentary_interval(cls, minutes: int):
        cls.set_int(cls.SEDENTARY_INTERVAL, max(1, minutes))

    @classmethod
    def pomodoro_focus(cls) -> int:
        return cls.get_int(cls.POMODORO_FOCUS, 25)

    @classmethod
    def set_pomodoro_focus(cls, minutes: int):
        cls.set_int(cls.POMODORO_FOCUS, max(1, minutes))

    @classmethod
    def pomodoro_break(cls) -> int:
        return cls.get_int(cls.POMODORO_BREAK, 5)

    @classmethod
    def set_pomodoro_break(cls, minutes: int):
        cls.set_int(cls.POMODORO_BREAK, max(1, minutes))

    @classmethod
    def theme(cls) -> str:
        return cls.get_str(cls.THEME, "light")

    @classmethod
    def set_theme(cls, theme: str):
        cls.set_str(cls.THEME, theme)

    @classmethod
    def auto_start(cls) -> bool:
        return cls.get_bool(cls.AUTO_START, False)

    @classmethod
    def set_auto_start(cls, enabled: bool):
        cls.set_bool(cls.AUTO_START, enabled)

    @classmethod
    def app_monitor_enabled(cls) -> bool:
        return cls.get_bool(cls.APP_MONITOR_ENABLED, True)

    @classmethod
    def set_app_monitor_enabled(cls, enabled: bool):
        cls.set_bool(cls.APP_MONITOR_ENABLED, enabled)

    @classmethod
    def sedentary_enabled(cls) -> bool:
        return cls.get_bool(cls.SEDENTARY_ENABLED, True)

    @classmethod
    def set_sedentary_enabled(cls, enabled: bool):
        cls.set_bool(cls.SEDENTARY_ENABLED, enabled)
