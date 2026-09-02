"""TUI（命令行）渲染实现（实现 ports.Renderer）。

职责：只把 presenter 产出的 View（视图语义）画到终端。
- 不解析领域状态、不做逻辑判断
- 字符宽度 / 排版 / 高亮样式由本实现自行推导
"""
from ports.renderer import Renderer
from presenter.view import View


class TuiRenderer(Renderer):
    """基于终端备用屏 + ANSI 光标控制的渲染后端。"""

    def __init__(self) -> None:
        # TODO(实现): 备用屏状态 / 上次绘制行数等状态在这里初始化。
        pass

    def begin(self) -> None:
        """进入渲染模式（备用屏 + 隐藏光标）。"""
        raise NotImplementedError("TuiRenderer.begin: 待实现")

    def render(self, view: View) -> None:
        """按视图语义画一帧。"""
        raise NotImplementedError("TuiRenderer.render: 待实现")

    def close(self) -> None:
        """退出渲染模式，恢复终端。"""
        raise NotImplementedError("TuiRenderer.close: 待实现")
