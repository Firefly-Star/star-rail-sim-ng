"""渲染端口契约。

renderer 负责把 presenter 产出的 View（视图语义）画到自己的介质上。
它不解析任何领域状态，也不做战斗 / 组队的逻辑判断。

边界约定：
- View 是 presenter 提供的 DTO，作为渲染契约的载荷类型被本契约引用；
  它必须保持纯数据、零依赖（见 presenter/view.py），
  否则 import 本模块会拖入 presenter 的其余逻辑或 cpp 链。
- presenter 不得反向 import ports，避免循环依赖。

未来接 Web / 动画 / OpenGL 时，新增一个 Renderer 实现即可。
"""
from abc import ABC, abstractmethod

from presenter.view import View


class Renderer(ABC):
    """渲染后端生命周期与绘图接口。"""

    @abstractmethod
    def begin(self) -> None:
        """进入渲染模式（如 TUI 的备用屏 + 隐藏光标）。"""

    @abstractmethod
    def render(self, view: View) -> None:
        """按视图语义画一帧。"""

    @abstractmethod
    def close(self) -> None:
        """退出渲染模式，恢复终端。"""
