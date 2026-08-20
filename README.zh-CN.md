> 📖 English documentation: [README.md](README.md)

# 🌤️ SkyViewTUI

> 一个运行在终端里的天气仪表盘，支持实时 GIF 动画。

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Textual](https://img.shields.io/badge/Textual-0.50+-green.svg)](https://textualize.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📖 SkyViewTUI 是什么？

**SkyViewTUI** 是一款美观、以键盘操作为核心的天气仪表盘，直接在终端中运行。它可以展示：

- **当前天气**（温度、湿度、风速、体感温度）
- **逐小时预报**（未来 12 小时）
- **3 天每日预报**
- **侧边栏实时 GIF 动画**（按 `n` 键切换）

基于 [Textual](https://textualize.io) 构建，数据来自 [Open-Meteo](https://open-meteo.com)（无需 API 密钥！）。

---

## ✨ 功能特性

- 🎨 **丰富的 TUI 界面** —— 仪表盘式布局，背景颜色随天气状况动态变化
- 🌍 **智能定位** —— 通过 IP 自动探测，或通过 `--city` 参数手动指定城市
- 🔄 **实时 GIF 播放** —— 侧边栏动画支持循环切换（`n` 键）
- ⌨️ **键盘快捷键** —— `1`（当前）、`2`（逐小时）、`3`（每日）、`r`（刷新）、`q`（退出）切换视图
- 🌡️ **可配置** —— 偏好设置保存在 `~/.weather-config.toml`（城市、温度单位、主题）
- ☁️ **天气图标** —— 为各种天气状况提供 ASCII 图标（☀️🌧️❄️⛈️）
- 📡 **WebDAV 同步** —— 可选地将配置同步到云端

---

## 🚀 安装

### 前置条件

- Python 3.9 或更高版本
- [pip](https://pip.pypa.io/)

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/sicnutaolei/SkyViewTUI.git
cd SkyViewTUI

# 2. 创建并激活虚拟环境
python -m venv .venv
# Windows 下：
.venv\Scripts\activate
# Linux/macOS 下：
source .venv/bin/activate

# 3. 安装依赖
pip install -e .
```

### 通过 pip 快速开始

```bash
# 直接从 GitHub 安装
pip install git+https://github.com/sicnutaolei/SkyViewTUI.git
skyviewtui --city "Beijing"
```

---

## 🎮 使用方法

### 基本用法

```bash
# 通过 IP 自动探测位置
python -m weather_tui.app

# 指定城市
python -m weather_tui.app --city "Beijing"

# 指定城市并指定自定义 GIF
python -m weather_tui.app --city "Deyang" --gif "path/to/your.gif"
```

### 键盘快捷键

| 按键 | 功能 |
|-----|------|
| `1` | 当前天气视图 |
| `2` | 逐小时预报视图 |
| `3` | 3 天每日预报视图 |
| `r` | 刷新天气数据 |
| `n` 或 `→` | 下一张 GIF 动画 |
| `q` | 退出 |

---

## ⚙️ 配置

SkyViewTUI 会将你的偏好保存在 `~/.weather-config.toml`：

```toml
city = "Deyang"
units = "celsius"          # 或 "fahrenheit"
theme = "default"

[webdav]
url = "https://dav.jianguoyun.com/dav/"
username = "your_email"
password = "your_app_password"
sync_enabled = false
```

---

## 📂 项目结构

```
SkyViewTUI/
├── weather_tui/
│   ├── app.py              # 主程序入口
│   ├── screens/
│   │   └── main.py         # 主 TUI 界面
│   ├── weather/
│   │   ├── api.py          # Open-Meteo API 调用
│   │   ├── geocode.py      # 城市名 → 经纬度
│   │   ├── ip_location.py  # 基于 IP 的定位
│   │   └── weather_icons.py # WMO 代码映射
│   ├── config/
│   │   ├── manager.py      # 配置读写
│   │   └── webdav.py       # WebDAV 同步
│   └── widgets/
│       └── gif_player.py   # GIF 动画播放器
├── app.tcss                # Textual 样式表
├── pyproject.toml          # 依赖与元数据
├── .gitignore
└── README.md
```

---

## 🛠️ 依赖项

- [Textual](https://textualize.io) —— TUI 框架
- [httpx](https://www.python-httpx.org/) —— 异步 HTTP 客户端
- [Pillow](https://python-pillow.org/) —— 图像处理
- [chafa.py](https://github.com/hpjansson/chafa) —— GIF 转 ANSI 字符画
- [tomli-w](https://github.com/hukkin/tomli-w) —— TOML 写入
- [webdavclient3](https://github.com/ezhov/webdavclient3) —— WebDAV 同步（可选）

---

## 📸 截图

*（在此添加你的截图：将图片保存为项目根目录下的 screenshot.png）*

---

## 📄 许可证

本项目基于 MIT 许可证开源 —— 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [Open-Meteo](https://open-meteo.com/) 提供免费的天气 API
- [Textual](https://textualize.io/) 提供强大的 TUI 框架
- [chafa](https://hpjansson.org/chafa/) 提供终端图像渲染能力

---

## 🤝 参与贡献

欢迎贡献！随时提出 Issue 或提交 Pull Request。

---

**用 ❤️ 和 Python 打造**
