"""OS 键盘输入实现（实现 ports.Inputter）。

职责：从终端采集按键，包装成 InputEvent(code) 转发；不做语义判断（由 cpp engine 决定）。
- 事件驱动界面（组队）：read_key_blocking —— 阻塞等一个键
- 时钟驱动界面（战斗）：cutoff —— 非阻塞截断当前已缓冲的按键批次

终端模式：每次读取临时切 raw（并保留 OPOST|ONLCR 使输出换行正常），读完即恢复，
避免长期占用 raw 影响渲染输出。Ctrl+C 在 raw 下表现为 \x03，这里转成 KeyboardInterrupt。
"""
from __future__ import annotations

import os
import select
import sys
import termios
import tty

from cpp_bridge import InputEvent
from ports.inputter import Inputter

_KEY_CANCEL = "\x03"


def _read_char(fd: int, timeout: float | None) -> str:
    """读一个字符；timeout 内无输入返回 ''，timeout=None 阻塞到有输入。"""
    if not os.isatty(fd):
        # 非终端（如管道/测试）：不做 raw 切换，仅按字节读
        ready, _, _ = select.select([fd], [], [], timeout)
        if not ready:
            return ""
        data = os.read(fd, 1)
        return data.decode("latin-1") if data else ""

    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        raw = termios.tcgetattr(fd)
        raw[1] |= termios.OPOST | termios.ONLCR
        termios.tcsetattr(fd, termios.TCSANOW, raw)
        ready, _, _ = select.select([fd], [], [], timeout)
        if not ready:
            return ""
        data = os.read(fd, 1)
        return data.decode("latin-1") if data else ""
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


class OsKeyboardInput(Inputter):
    """基于终端 OS 键盘缓冲的输入实现。"""

    def __init__(
        self,
        max_reads: int = 64,
        poll_seconds: float = 0.0,
        fd: int | None = None,
    ) -> None:
        if fd is None:
            try:
                fd = sys.stdin.fileno()
            except Exception:
                fd = 0  # 拿不到（如 pytest 伪 stdin）时回退到标准输入
        self._fd = fd
        self._max_reads = max_reads
        self._poll = poll_seconds

    def begin(self) -> None:
        """清空残留缓冲，避免前序阶段按键污染。"""
        try:
            termios.tcflush(self._fd, termios.TCIFLUSH)
        except termios.error:
            pass

    def read_key_blocking(self) -> InputEvent:
        """阻塞读取一个按键并返回 InputEvent。Ctrl+C → KeyboardInterrupt。"""
        ch = _read_char(self._fd, None)
        if ch == _KEY_CANCEL:
            raise KeyboardInterrupt
        return InputEvent(code=ch)

    def cutoff(self) -> list[InputEvent]:
        """截断当前已缓冲的按键批次，返回 InputEvent 列表。Ctrl+C → KeyboardInterrupt。"""
        events: list[InputEvent] = []
        for _ in range(self._max_reads):
            ch = _read_char(self._fd, self._poll)
            if not ch:
                break
            if ch == _KEY_CANCEL:
                raise KeyboardInterrupt
            events.append(InputEvent(code=ch))
        return events

    def end(self) -> None:
        """恢复终端。当前为每次读取临时 raw 用完即恢复，故无需额外动作。"""
