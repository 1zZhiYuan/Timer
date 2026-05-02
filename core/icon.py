"""
App icon — generates a clean clock icon using QPainter at runtime.
No external image files needed.
"""
import math
import struct
from io import BytesIO
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QPointF, QBuffer, QIODevice

ACCENT = QColor("#4f6ef7")
WHITE = QColor("#ffffff")


def make_icon(size: int = 256) -> QIcon:
    """Generate a clean clock/timer icon — blue bg + white hands (visible at all sizes)."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    cx, cy = size / 2, size / 2
    margin = size * 0.06
    r = (size - 2 * margin) / 2

    # Blue circle background
    p.setBrush(ACCENT)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx, cy), r, r)

    # Thin white clock rim
    rim_r = r * 0.82
    p.setPen(QPen(WHITE, max(1.5, size * 0.022)))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QPointF(cx, cy), rim_r, rim_r)

    # White hour hand — points to ~10 o'clock
    p.setPen(QPen(WHITE, max(2.5, size * 0.05)))
    h_angle = math.radians(-150)
    h_len = rim_r * 0.55
    p.drawLine(QPointF(cx, cy),
               QPointF(cx + h_len * math.cos(h_angle), cy + h_len * math.sin(h_angle)))

    # White minute hand — points to ~2 o'clock
    p.setPen(QPen(WHITE, max(1.5, size * 0.028)))
    m_angle = math.radians(-60)
    m_len = rim_r * 0.72
    p.drawLine(QPointF(cx, cy),
               QPointF(cx + m_len * math.cos(m_angle), cy + m_len * math.sin(m_angle)))

    # White center dot
    dot_r = max(2, size * 0.035)
    p.setBrush(WHITE)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx, cy), dot_r, dot_r)

    p.end()
    return QIcon(pix)


def make_ico_data() -> bytes:
    """Generate .ico file bytes with PNG entries (reliable on Windows 10/11)."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    for s in sizes:
        pix = make_icon(s).pixmap(s)
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        pix.save(buf, "PNG")
        images.append(bytes(buf.data().data()))
        buf.close()

    out = BytesIO()
    out.write(struct.pack("<HHH", 0, 1, len(images)))
    offset = 6 + len(images) * 16
    for img_data, s in zip(images, sizes):
        dim = s if s < 256 else 0
        out.write(struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(img_data), offset))
        offset += len(img_data)
    for img_data in images:
        out.write(img_data)
    return out.getvalue()
