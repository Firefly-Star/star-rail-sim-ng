# star-rail-sim-ng

星穹铁道回合制模拟器的重制版（ng）——基于旧项目经验的重构。

## 结构

```text
main.py                 组装根：选输入/渲染实现，驱动 team/battle engine
cpp-core-ng/            子模块：C++ 引擎（battle / team）+ 领域状态/快照 + pybind
cpp_bridge/             Python 侧加载 .so、导出边界类型
ports/                  纯契约（inputter / renderer）
presenter/              Python 中间层：领域快照 → 视图语义（View）
impl/                   具体实现（os_keyboard / tui_renderer）
module-board.json       开发进度真相源（见下）
```

## 开发进度：module-board.json

`module-board.json` 记录本项目**开发进度**，格式兼容 [module-board](https://github.com/Firefly-Star/module-board)（模块依赖图编辑器）。

- 每个节点 = 一个模块（python 一个 `.py`；cpp 一个 `.hpp+.cpp`）
- `deps`：依赖谁 → 边由它推导（被依赖 → 依赖者）
- 状态（frozen + implemented 共同决定，module-board 自动派生）：
  - `已实现`（绿）：功能已通
  - `依赖已齐·待实现`（紫）：接口已冻结且依赖全部实现，该实现它了
  - `已冻结·未实现`（蓝）：接口锁了，但还有依赖没实现
  - `未冻结·未实现`（琥珀）：还在设计阶段
- `later`：该模块"第一轮之后想改的点"（第二轮开发方向）

维护方式：用 module-board 打开/编辑本文件，改动后 `git add module-board.json && git commit`。判断"当前该实现谁 / 卡在哪"以它为准。

## 运行

```bash
# 需要先构建 cpp-core-ng（子模块）：
cmake -S cpp-core-ng -B cpp-core-ng/build -DPython3_EXECUTABLE=<starrail-sim 的 python>
cmake --build cpp-core-ng/build
# 再用 starrail-sim conda 环境运行：
python main.py
```

当前状态：骨架 + py-cpp 边界已冻结，具体战斗/组队实现按 module-board.json 的依赖顺序推进。
