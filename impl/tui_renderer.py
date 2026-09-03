"""TUI 渲染实现（实现 ports.Renderer）。

职责：只把 presenter 产出的 View（视图语义）画到终端。
- 字符宽 / 排版 / 颜色都由本实现推导（View 本身不含单位/布局）。
- "View → 文本行"（render_lines）是纯函数，便于离线测试。

绘制策略：
- begin 进入备用屏并隐藏光标；每帧回到左上、清行重绘、擦掉上一帧多余的行。
- 不整屏 clear，避免闪烁。
"""
from __future__ import annotations

import atexit
import sys
import unicodedata

from presenter.view import (
    Error,
    ListBlock,
    Log,
    ProgressBar,
    Prompt,
    Section,
    Status,
    Table,
    Title,
    View,
)
from ports.renderer import Renderer

ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_DIM = "\x1b[2m"
ANSI_RED = "\x1b[31m"
ANSI_YELLOW = "\x1b[33m"
ANSI_CYAN = "\x1b[36m"

# 渲染里的装饰前缀（属于后端表现，不属于语义）
_MARK = {
    "highlight": "▶",
    "bullet": "•",
}


def disp_width(s: str) -> int:
    """字符串的显示宽度：东亚全角按 2 列计。"""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def _pad(s: str, width: int, align: str = "left") -> str:
    gap = width - disp_width(s)
    if gap <= 0:
        return s
    if align == "right":
        return " " * gap + s
    if align == "center":
        left = gap // 2
        return " " * left + s + " " * (gap - left)
    return s + " " * gap


def _truncate(s: str, width: int) -> str:
    if disp_width(s) <= width:
        return s
    out = ""
    used = 0
    for c in s:
        w = disp_width(c)
        if used + w > width - 1:
            break
        out += c
        used += w
    return out + "…"


def render_lines(view: View, width: int = 80) -> list[str]:
    """把 View 翻译成文本行（纯函数，供 render 与测试使用）。"""
    if not view.blocks:
        return []
    lines: list[str] = []
    for block in view.blocks:
        if isinstance(block, Title):
            lines.append(ANSI_BOLD + block.text + ANSI_RESET)
            lines.append("─" * width)
        elif isinstance(block, Section):
            if block.text:
                lines.append(f"  {ANSI_CYAN}── {block.text} ──{ANSI_RESET}")
        elif isinstance(block, Status):
            if block.text:
                lines.append(f"  ⚡ {block.text}")
        elif isinstance(block, Prompt):
            if block.text:
                lines.append(f"  {block.text}")
        elif isinstance(block, Error):
            if block.text:
                lines.append(f"  {ANSI_RED}⛔ {block.text}{ANSI_RESET}")
        elif isinstance(block, Log):
            for entry in block.lines:
                lines.append(f"  📋 {entry}")
        elif isinstance(block, ListBlock):
            if not block.items:
                continue
            for i, item in enumerate(block.items):
                mark = _MARK["highlight"] if i == block.highlight else "  "
                lines.append(f"  {mark} {item}")
        elif isinstance(block, ProgressBar):
            lines.append(_render_progress(block, width))
        elif isinstance(block, Table):
            lines.extend(_render_table(block, width))
        else:
            lines.append(str(block))
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def _render_progress(block: object, width: int) -> str:
    pb = block  # type: ProgressBar
    label = pb.label
    value = pb.value
    total = pb.max_value
    text = f"{ANSI_BOLD}{label}{ANSI_RESET}"
    if total <= 0:
        return f"  {text} ░"
    bar_w = max(4, min(24, width - disp_width(f"  {label}") - 14))
    filled = round(bar_w * value / total)
    bar = "█" * filled + "░" * (bar_w - filled)
    return f"  {text} [{bar}] {value}/{total}"


def _render_table(block: object, width: int) -> list[str]:
    tb = block  # type: Table
    out: list[str] = []
    if tb.title:
        out.append(f"  {ANSI_BOLD}{tb.title}{ANSI_RESET}")
    cols = tb.columns
    ncols = len(cols)
    rows = tb.rows
    if ncols == 0:
        return out

    # 每列显示宽度：由表头与内容的最大显示宽度决定（含 1 间距）
    def col_width(i: int) -> int:
        w = disp_width(cols[i])
        for row in rows:
            if i < len(row):
                w = max(w, disp_width(row[i]))
        return w + 1

    raw_w = [col_width(i) for i in range(ncols)]
    # 超出终端宽度时按比例收缩，至少保留每列 4
    budget = width - 4
    if sum(raw_w) > budget:
        scale = budget / sum(raw_w)
        raw_w = [max(4, int(w * scale)) for w in raw_w]
        # 仍有溢出则截到可用
        for i in range(ncols):
            raw_w[i] = min(raw_w[i], budget)

    def fmt_row(cells: list[str], header: bool = False) -> str:
        parts = []
        for i in range(ncols):
            cell = cells[i] if i < len(cells) else ""
            if header:
                parts.append(_pad(_truncate(cell, raw_w[i]), raw_w[i], "center"))
            else:
                parts.append(_pad(_truncate(cell, raw_w[i] - 1), raw_w[i] - 1))
        return "│".join(parts).rstrip()

    sep = "─" * min(width - 2, sum(raw_w) + ncols)
    out.append("  " + sep)
    out.append("  " + fmt_row(cols, header=True))
    out.append("  " + sep)
    for idx, row in enumerate(rows):
        mark = _MARK["highlight"] if idx == tb.highlight else "  "
        line = "  " + mark + fmt_row(row)
        if idx == tb.highlight:
            line = ANSI_YELLOW + line + ANSI_RESET
        out.append(line)
    out.append("  " + sep)
    return out


class TuiRenderer(Renderer):
    """基于终端备用屏 + ANSI 光标控制的渲染后端。"""

    def __init__(self) -> None:
        self._in_alt = False
        self._last_lines = 0
        self._atexit_ok = False
        self._out = sys.stdout

    def begin(self) -> None:
        if self._in_alt:
            return
        if not self._atexit_ok:
            atexit.register(self.close)
            self._atexit_ok = True
        self._out.write("\x1b[?1049h\x1b[?25l")
        self._out.flush()
        self._in_alt = True

    def render(self, view: View) -> None:
        self.begin()
        try:
            width = _terminal_width()
        except Exception:
            width = 80
        lines = render_lines(view, width)
        buf = ["\x1b[H"]
        for line in lines:
            buf.append("\x1b[2K" + line + "\r\n")
        if len(lines) < self._last_lines:
            for _ in range(self._last_lines - len(lines)):
                buf.append("\x1b[2K\r\n")
        buf.append("\x1b[J")
        self._out.write("".join(buf))
        self._out.flush()
        self._last_lines = len(lines)

    def close(self) -> None:
        if not self._in_alt:
            return
        self._out.write("\x1b[0m\x1b[?25h\x1b[?1049l")
        self._out.flush()
        self._in_alt = False
        self._last_lines = 0


def _terminal_width() -> int:
    import shutil

    return shutil.get_terminal_size().columns
