"""presenter.battle：战斗领域快照 → 视图语义。

cpp 只出领域状态；本模块负责把战斗界面该显示什么组织成 View，
交给 renderer 画。
"""
from cpp_bridge import BattleSnapshot

from presenter.view import View


class BattlePresenter:
    """把战斗 engine 的领域快照翻译成 View。"""

    def build_view(self, snapshot: BattleSnapshot) -> View:
        """构造战斗界面的视图语义。

        snapshot：cpp BattleEngine.get_snapshot() 产出的 BattleSnapshot。
        """
        raise NotImplementedError("BattlePresenter.build_view: 待实现")
