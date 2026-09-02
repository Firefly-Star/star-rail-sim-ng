"""OS 键盘输入实现（实现 ports.Inputter）。

职责：从终端取输入并构造成 InputEvent 转发，不做语义判断（语义由 cpp engine 决定）。
- 事件驱动界面（组队）用 read_key_blocking
- 时钟驱动界面（战斗）用 cutoff
"""
from __future__ import annotations

from cpp_bridge import InputEvent
from ports.inputter import Inputter


class OsKeyboardInput(Inputter):
    """基于终端 OS 输入缓冲的键盘输入。"""

    def __init__(self) -> None:
        # TODO(实现): raw mode / 缓冲等状态在这里初始化。
        pass

    def begin(self) -> None:
        """进入输入模式：清空残留缓冲。"""
        raise NotImplementedError("OsKeyboardInput.begin: 待实现")

    def read_key_blocking(self) -> InputEvent:
        """阻塞读取一次输入并返回一个 InputEvent。"""
        raise NotImplementedError("OsKeyboardInput.read_key_blocking: 待实现")

    def cutoff(self) -> list[InputEvent]:
        """截断当前已缓冲的输入批次，返回 InputEvent 列表。"""
        raise NotImplementedError("OsKeyboardInput.cutoff: 待实现")

    def end(self) -> None:
        """退出输入模式，恢复终端。"""
        raise NotImplementedError("OsKeyboardInput.end: 待实现")
