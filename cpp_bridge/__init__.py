"""cpp_bridge：加载 cpp-core-ng 编译产物，导出 Python 侧需要的边界类型。

只暴露产品边界（engine + 领域快照），cpp 内部类型不在此导出。
"""
import importlib.util
from pathlib import Path

_MODULE_NAME = "starrail_cpp_core_ng"
_ROOT = Path(__file__).resolve().parents[1]
_BUILD_DIR = _ROOT / "cpp-core-ng" / "build"


def _load():
    candidates = sorted(_BUILD_DIR.glob(f"{_MODULE_NAME}*.so"))
    if not candidates:
        raise RuntimeError(
            f"未找到编译产物 {_MODULE_NAME}.so。请先构建 cpp-core-ng：\n"
            "  cmake -S cpp-core-ng -B cpp-core-ng/build "
            "-DPython3_EXECUTABLE=<starrail-sim 环境的 python>\n"
            "  cmake --build cpp-core-ng/build"
        )
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, candidates[0])
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法从 {candidates[0]} 创建模块 spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_core = _load()

InputEvent = _core.InputEvent
BattleEngine = _core.BattleEngine
TeamEngine = _core.TeamEngine
BattleSnapshot = _core.BattleSnapshot
TeamSnapshot = _core.TeamSnapshot

__all__ = [
    "InputEvent",
    "BattleEngine",
    "TeamEngine",
    "BattleSnapshot",
    "TeamSnapshot",
]
