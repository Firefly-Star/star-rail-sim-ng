#!/usr/bin/env python3
"""
star-rail-sim-ng 组装根（composition root）。

职责：
- 选择输入/渲染实现（现在：OS 键盘 + TUI；未来可换鼠标 / Web）
- 接好 engine（team / battle 都在 cpp_core）
- 用 presenter 把领域快照翻译成视图语义，交给渲染后端
- 驱动各 engine：battle 走时钟驱动的 7 步 tick；team 走事件驱动（无时钟）

依赖方向：这里只做组装，不含业务逻辑。
"""

from impl.os_keyboard import OsKeyboardInput
from impl.tui_renderer import TuiRenderer
from presenter.team import TeamPresenter
from presenter.battle import BattlePresenter
from cpp_bridge import TeamEngine, BattleEngine


def main() -> None:
    # —— 组装根：选具体实现 ——
    inputter = OsKeyboardInput()
    renderer = TuiRenderer()

    try:
        inputter.begin()
        renderer.begin()

        # —— 组队 engine：事件驱动。没有时钟，按一个键处理一个，不空转 ——
        team_engine = TeamEngine()
        team_engine.init()
        snapshot = team_engine.get_snapshot()        # 首帧初始快照
        while not team_engine.is_over():
            renderer.render(TeamPresenter().build_view(snapshot))
            inputs = inputter.read_key_blocking()    # 阻塞等一个按键
            team_engine.compute_next(inputs)         # 应用到状态（选择/确认）
            snapshot = team_engine.get_snapshot()    # 取更新后的快照

        # —— 战斗 engine：时钟驱动。阵容来源未定（将由组队结果给出），暂无参 init ——
        battle_engine = BattleEngine()
        battle_engine.init()
        while not battle_engine.is_over():
            battle_engine.begin_tick_timing()
            inputs = inputter.cutoff()
            battle_engine.exchange_state_buffers()
            snapshot = battle_engine.get_snapshot()           # 领域快照（cpp）
            renderer.render(BattlePresenter().build_view(snapshot))                               # 渲染后端
            battle_engine.compute_next(inputs)
            battle_engine.wait_until_tick_end()

    except KeyboardInterrupt:
        pass
    finally:
        renderer.close()
        inputter.end()


if __name__ == "__main__":
    main()
