"""可复用信息卡片组件：显示「标签 + 数值」。"""

from __future__ import annotations

from textual.widgets import Static


class InfoCard(Static):
    """一个带边框的小卡片，展示一项指标。

    注意：不要覆盖父类的 ``_render``（那是 Textual 内部用于生成可视内容的
    方法）。这里直接调用 ``update`` 设置内容即可。
    """

    DEFAULT_CSS = """
    InfoCard {
        border: round $secondary;
        padding: 1 2;
        margin: 1 1;
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self, label: str = "", value: str = "", **kwargs):
        super().__init__(**kwargs)
        self._label = label
        self._value = value
        self.update(self._content())

    def _content(self) -> str:
        return f"[b]{self._label}[/b]\n{self._value}"

    def set_value(self, value: str) -> None:
        self._value = value
        self.update(self._content())
