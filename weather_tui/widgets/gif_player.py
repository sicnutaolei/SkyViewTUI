"""GIF 终端字符画播放器。"""

from __future__ import annotations

from pathlib import Path
from typing import List

from PIL import Image
from rich.text import Text
from textual.widgets import Static

try:
    import chafa
    from chafa import Canvas, CanvasConfig, PixelType
    CHAFA_AVAILABLE = True
except Exception:
    CHAFA_AVAILABLE = False


class GifPlayer(Static):
    DEFAULT_CSS = """
    GifPlayer {
        width: 100%;
        height: 100%;
        background: #0f141c;
        padding: 1;
        content-align: center middle;
    }
    """

    def __init__(
        self,
        gif_path: str | Path | None = None,
        fps: int = 5,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.gif_path = Path(gif_path) if gif_path else None
        self.fps = max(1, fps)
        self._frames: List[Text] = []
        self._index = 0
        self._timer = None
        self.update("[dim]🎞️ 等待加载动画…[/]")

    def on_mount(self) -> None:
        self.run_worker(self._start_playback(), exclusive=True)

    def load_gif(self, new_path: str | Path) -> None:
        """切换并播放新的 GIF：停止旧动画、重置帧、重新加载。"""
        self._stop_timer()
        self._frames = []
        self._index = 0
        self.gif_path = Path(new_path)
        self.update("[dim]🎞️ 加载中…[/]")
        self.run_worker(self._start_playback(), exclusive=True)

    async def _start_playback(self) -> None:
        # 等待组件挂载（兼容旧版 Textual）
        import asyncio
        while not self.is_mounted:
            await asyncio.sleep(0.01)
        if not self.is_mounted:
            return
        await self._prepare_frames()
        if not self.is_mounted:
            return
        if self._frames:
            self.update(self._frames[0])
            self._timer = self.set_interval(1.0 / self.fps, self._next_frame)
        elif not CHAFA_AVAILABLE:
            self.update("[red]chafa.py 未安装[/]")
        elif not self.gif_path or not self.gif_path.exists():
            self.update("[dim]未找到 GIF 文件[/]")
        # else: _prepare_frames 已写入具体错误信息

    async def _prepare_frames(self) -> None:
        if not CHAFA_AVAILABLE:
            self.update("[red]chafa.py 未安装[/]")
            return
        if not self.gif_path or not self.gif_path.exists():
            self.update("[dim]未找到 GIF 文件[/]")
            return
        try:
            frames: List[Text] = []
            with Image.open(self.gif_path) as img:
                n_frames = getattr(img, "n_frames", 1)
                for i in range(n_frames):
                    img.seek(i)
                    frame = img.convert("RGBA")
                    frames.append(self._render_frame(frame))
            self._frames = frames
        except Exception as exc:
            self.update(f"[red]加载 GIF 失败：{exc}[/]")

    def _render_frame(self, image: Image.Image) -> Text:
        # 确保是 RGBA
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        bg_color = (11, 14, 20)  # #0b0e14

        # 合成到纯色背景，避免透明 / 绿底残留
        bg_image = Image.new("RGBA", image.size, bg_color + (255,))
        composited = Image.alpha_composite(bg_image, image)
        composited_rgb = composited.convert("RGB")
        final_bg = Image.new("RGB", composited.size, bg_color)
        final_bg.paste(composited_rgb, (0, 0))

        # chafa 转换
        config = CanvasConfig()
        config.width = 40
        config.height = 20
        config.pixel_mode = chafa.PixelMode.CHAFA_PIXEL_MODE_SYMBOLS
        config.canvas_mode = chafa.CanvasMode.CHAFA_CANVAS_MODE_TRUECOLOR
        config.calc_canvas_geometry(final_bg.width, final_bg.height, 0.5)

        canvas = Canvas(config)
        pixels = final_bg.tobytes()
        canvas.draw_all_pixels(
            PixelType.CHAFA_PIXEL_RGB8,
            pixels,
            final_bg.width,
            final_bg.height,
            final_bg.width * 3,
        )
        ansi = canvas.print().decode(errors="replace")
        if not ansi.strip():
            return Text("🎞️ [dim]动画加载中[/]")
        return Text.from_ansi(ansi)

    def _next_frame(self) -> None:
        if not self.is_mounted or not self._frames:
            return
        self._index = (self._index + 1) % len(self._frames)
        self.update(self._frames[self._index])

    def _stop_timer(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer = None

    def stop(self) -> None:
        self._stop_timer()
