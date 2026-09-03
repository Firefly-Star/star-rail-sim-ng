"""tui_renderer 单元测试。

render_lines 是纯函数（View → 文本行），可在无终端环境下直接断言；
实例的 ANSI 输出用 StringIO 捕获验证。
"""
import io
import re

from impl.tui_renderer import TuiRenderer, disp_width, render_lines
from presenter.view import (
    Error,
    ListBlock,
    Log,
    ProgressBar,
    Prompt,
    Section,
    Status,
    Table,
    Title,
    View,
)

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(lines):
    return [ANSI.sub("", l) for l in lines]


class TestDispWidth:
    def test_ascii_is_one(self):
        assert disp_width("abc") == 3

    def test_cjk_is_two(self):
        assert disp_width("希儿") == 4
        assert disp_width("a希") == 3


class TestRenderLines:
    def test_empty_view_returns_empty(self):
        assert render_lines(View()) == []

    def test_empty_text_blocks_skipped(self):
        lines = render_lines(View(blocks=[Title("T"), Error(""), Prompt(""), Status("")]), 40)
        joined = "\n".join(lines)
        assert "⛔" not in joined and "⚡" not in joined

    def test_title_underlined(self):
        lines = render_lines(View(blocks=[Title("标题")]), 40)
        assert plain(lines)[0] == "标题"

    def test_table_alignment_and_highlight(self):
        view = View(blocks=[Table(
            columns=["编号", "名称", "速度"],
            rows=[["1", "希儿", "115"], ["2", "布洛妮娅", "99"]],
            highlight=1,
        )])
        lines = plain(render_lines(view, 60))
        joined = "\n".join(lines)
        assert "编号" in joined and "名称" in joined
        assert "▶2" in joined          # 高亮行带 ▶ 标记
        assert "▶1" not in joined

    def test_list_highlight(self):
        view = View(blocks=[ListBlock(items=["a", "b"], highlight=0)])
        lines = plain(render_lines(view, 40))
        assert "▶ a" in lines[0]
        assert "▶" not in lines[1]

    def test_progress_contains_bar_and_numbers(self):
        view = View(blocks=[ProgressBar(label="EP", value=60, max_value=120)])
        line = "".join(render_lines(view, 60))
        assert "█" in line and "░" in line and "60/120" in line

    def test_log_lines(self):
        view = View(blocks=[Log(lines=["x", "y"])])
        lines = plain(render_lines(view, 40))
        assert "x" in lines[0] and "y" in lines[1]

    def test_unknown_block_falls_back_to_str(self):
        class Weird:
            def __str__(self):
                return "W?"
        view = View(blocks=[Weird()])
        assert plain(render_lines(view, 40))[0].strip() == "W?"


class TestTuiRendererInstance:
    def _make(self):
        buf = io.StringIO()
        r = TuiRenderer()
        r._out = buf
        return r, buf

    def test_begin_enters_alt_screen_and_hides_cursor(self):
        r, buf = self._make()
        r.begin()
        s = buf.getvalue()
        assert "\x1b[?1049h" in s and "\x1b[?25l" in s

    def test_render_homes_cursor_and_draws(self):
        r, buf = self._make()
        r.begin()
        r.render(View(blocks=[Title("你好"), Status("状态")]))
        s = buf.getvalue()
        assert "\x1b[H" in s
        assert "你好" in s and "状态" in s

    def test_close_restores_terminal(self):
        r, buf = self._make()
        r.begin()
        r.close()
        assert "\x1b[?25h\x1b[?1049l" in buf.getvalue()

    def test_close_is_idempotent(self):
        r, buf = self._make()
        r.begin()
        r.close()
        buf.truncate(0)
        buf.seek(0)
        r.close()
        assert buf.getvalue() == ""
