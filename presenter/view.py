"""视图语义：presenter 产出、renderer 消费的中间结构。

约定：
- 只描述"内容 + 结构 + 状态"，不含单位 / 尺寸 / 位置 / 颜色。
- 单位（px / 字符宽）、排版、高亮样式都是渲染后端自己推导的事。
- 当前是一组"简单语义块"起步，后续按需扩充；不引入复杂布局引擎。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Title:
    """大标题。"""
    text: str


@dataclass
class Section:
    """分节标题。"""
    text: str


@dataclass
class Table:
    """表格：标题 + 列头 + 数据行 + 高亮行索引。"""
    title: str = ""
    columns: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    highlight: int = -1  # -1 表示无高亮


@dataclass
class ListBlock:
    """列表：若干条目 + 高亮索引。"""
    items: list[str] = field(default_factory=list)
    highlight: int = -1


@dataclass
class ProgressBar:
    """进度条（如 EP）。value/max_value 为数值，宽度由后端决定。"""
    label: str = ""
    value: int = 0
    max_value: int = 0


@dataclass
class Status:
    """当前状态区文本。"""
    text: str = ""


@dataclass
class Prompt:
    """等待输入的提示行。"""
    text: str = ""


@dataclass
class Log:
    """日志区，若干行。"""
    lines: list[str] = field(default_factory=list)


@dataclass
class Error:
    """报错区，短暂可见。"""
    text: str = ""


@dataclass
class View:
    """一帧的完整视图：按显示顺序排列的简单语义块。

    screen 仅用于调试 / 后端选择标题等展示细节，不参与逻辑判断。
    """
    screen: str = ""
    blocks: list[Any] = field(default_factory=list)  # Title/Section/Table/... 混合
