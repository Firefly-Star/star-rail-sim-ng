"""输入端口契约。

职责：Python 只负责"采集输入并转发成 InputEvent"，不做任何语义判断。
事件是否合法、代表什么、处于哪个界面，一律由 cpp engine 判断。

InputEvent 由 cpp 定义（engine 是输入的消费者），本契约只引用它的类型。
为了不引入运行时依赖，类型标注只在类型检查时可见（TYPE_CHECKING）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cpp_bridge import InputEvent


class Inputter(ABC):
    """输入源的生命周期与取输入接口。

    一个界面通常只使用 read_key_blocking 或 cutoff 中的一种：
    - 事件驱动界面（组队）：read_key_blocking
    - 时钟驱动界面（战斗）：cutoff
    """

    @abstractmethod
    def begin(self) -> None:
        """进入输入模式：清空残留缓冲，必要时切换 raw mode。"""

    @abstractmethod
    def read_key_blocking(self) -> InputEvent:
        """阻塞读取一次输入并返回一个 InputEvent（如组队界面）。"""

    @abstractmethod
    def cutoff(self) -> list[InputEvent]:
        """在 tick 起始点截断当前已缓冲的输入批次（如战斗界面）。

        只取截止前已到达的输入，截止后新来的输入归下一个 tick。
        """

    @abstractmethod
    def end(self) -> None:
        """退出输入模式，恢复终端。"""
