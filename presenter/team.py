"""presenter.team：组队领域快照 → 视图语义。

cpp 只出领域状态；本模块负责把组队界面（选友方 / 选敌方 / 确认）
该显示什么组织成 View，交给 renderer 画。
"""
from cpp_bridge import TeamSnapshot

from presenter.view import View


class TeamPresenter:
    """把组队 engine 的领域快照翻译成 View。"""

    def build_view(self, snapshot: TeamSnapshot) -> View:
        """构造组队界面的视图语义。

        snapshot：cpp TeamEngine.get_snapshot() 产出的 TeamSnapshot。
        """
        raise NotImplementedError("TeamPresenter.build_view: 待实现")
