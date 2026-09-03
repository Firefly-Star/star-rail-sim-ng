"""os_keyboard 单元测试。

用管道模拟非终端输入，走 _read_char 的 isatty=False 分支，避免依赖真终端。
"""
import os

import pytest

from impl.os_keyboard import OsKeyboardInput


@pytest.fixture
def pipe_keyboard():
    """构造一个指向管道读端的 OsKeyboardInput，便于注入按键。"""
    r, w = os.pipe()
    kb = OsKeyboardInput(fd=r)
    yield kb, w
    try:
        os.close(r)
        os.close(w)
    except OSError:
        pass


def write_bytes(w, data: bytes):
    os.write(w, data)


class TestReadKeyBlocking:
    def test_returns_event_with_code(self, pipe_keyboard):
        kb, w = pipe_keyboard
        write_bytes(w, b"q")
        ev = kb.read_key_blocking()
        assert ev.code == "q"

    def test_ctrl_c_raises_keyboard_interrupt(self, pipe_keyboard):
        kb, w = pipe_keyboard
        write_bytes(w, b"\x03")
        with pytest.raises(KeyboardInterrupt):
            kb.read_key_blocking()


class TestCutoff:
    def test_drains_buffered_keys(self, pipe_keyboard):
        kb, w = pipe_keyboard
        write_bytes(w, b"ab")
        evs = kb.cutoff()
        assert [e.code for e in evs] == ["a", "b"]

    def test_empty_when_no_input(self, pipe_keyboard):
        kb, _w = pipe_keyboard
        assert kb.cutoff() == []

    def test_respects_max_reads(self, pipe_keyboard):
        kb, w = pipe_keyboard
        kb._max_reads = 3
        write_bytes(w, b"abcd")
        evs = kb.cutoff()
        assert len(evs) == 3

    def test_ctrl_c_raises_during_drain(self, pipe_keyboard):
        kb, w = pipe_keyboard
        write_bytes(w, b"a\x03")
        with pytest.raises(KeyboardInterrupt):
            kb.cutoff()


class TestBegin:
    def test_begin_is_safe_on_pipe(self, pipe_keyboard):
        # tcflush 对管道 fd 会抛 termios.error，begin 应吞掉
        kb, _w = pipe_keyboard
        kb.begin()

    def test_end_is_noop(self, pipe_keyboard):
        kb, _w = pipe_keyboard
        kb.end()
