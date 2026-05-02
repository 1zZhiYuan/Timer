"""
Core timer engine: start/pause/reset, auto-archive by day.
Emits signals for UI updates.
"""
import json
import time
from datetime import datetime, date
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from core.database import get_or_create_record, update_daily_seconds


class TimerEngine(QObject):
    tick_signal = pyqtSignal(int)  # current session seconds
    daily_updated = pyqtSignal(int)  # daily total seconds
    state_changed = pyqtSignal()  # fires on start / pause / reset

    def __init__(self):
        super().__init__()
        self._session_seconds = 0       # current session elapsed
        self._running = False
        self._paused = False
        self._start_time = None
        self._elapsed_before_pause = 0
        self._last_checkpoint = 0       # seconds already persisted by _archive_check
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._archive_timer = QTimer(self)
        self._archive_timer.timeout.connect(self._archive_check)
        self._archive_timer.start(30000)  # every 30s

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def session_seconds(self) -> int:
        return self._session_seconds

    def start(self):
        if self._running and not self._paused:
            return
        if self._paused:
            # resume
            self._paused = False
            self._start_time = time.time()
            self._timer.start(1000)
        else:
            self._session_seconds = 0
            self._running = True
            self._paused = False
            self._elapsed_before_pause = 0
            self._start_time = time.time()
            self._timer.start(1000)
            self._last_checkpoint = 0
        self.state_changed.emit()

    def pause(self):
        if not self._running or self._paused:
            return
        self._paused = True
        self._timer.stop()
        if self._start_time:
            self._elapsed_before_pause += int(time.time() - self._start_time)
            self._start_time = None
        self._archive()
        self.state_changed.emit()

    def reset(self):
        self._running = False
        self._paused = False
        self._timer.stop()
        # save the elapsed time before resetting
        if self._session_seconds > 0:
            self._archive()
        self._session_seconds = 0
        self._start_time = None
        self._elapsed_before_pause = 0
        self._last_checkpoint = 0
        self.state_changed.emit()

    def stop(self):
        """Alias for reset — stops and archives."""
        self.reset()

    def _tick(self):
        if not self._start_time:
            return
        now = time.time()
        total = self._elapsed_before_pause + int(now - self._start_time)
        self._session_seconds = total
        self.tick_signal.emit(total)

    def _archive(self):
        """Persist delta since last checkpoint to today's record."""
        delta = self._session_seconds - self._last_checkpoint
        if delta <= 0:
            return
        today = date.today().isoformat()
        record = get_or_create_record(today)
        new_total = record["total_seconds"] + delta
        intervals = json.loads(record.get("session_intervals", "[]"))
        intervals.append({
            "start": datetime.now().isoformat(),
            "seconds": delta,
        })
        update_daily_seconds(today, new_total, json.dumps(intervals))
        self._last_checkpoint = self._session_seconds
        self.daily_updated.emit(new_total)

    def _archive_check(self):
        """Background archive — flush elapsed time every 30s."""
        if not self._running or self._paused or not self._start_time:
            return
        total = self._elapsed_before_pause + int(time.time() - self._start_time)
        if total > self._session_seconds:
            diff = total - self._session_seconds
            self._session_seconds = total
            today = date.today().isoformat()
            record = get_or_create_record(today)
            new_total = record["total_seconds"] + diff
            intervals = json.loads(record.get("session_intervals", "[]"))
            intervals.append({
                "start": datetime.now().isoformat(),
                "seconds": diff,
            })
            update_daily_seconds(today, new_total, json.dumps(intervals))
            self._last_checkpoint = total
            self.daily_updated.emit(new_total)

    def get_daily_total(self, record_date: str = None) -> int:
        if record_date is None:
            record_date = date.today().isoformat()
        record = get_or_create_record(record_date)
        return record["total_seconds"]
