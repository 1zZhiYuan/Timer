# ⏱ Timer — 轻量学习计时统计工具

**Timer** 是一款 Windows 桌面端的专注计时与学习统计工具。纯本地运行，无需联网，数据完全由用户掌控。无广告、无监控、无多余权限。适合自习、备考、远程办公等场景下的时间管理。

> **作者**: [ZhiYuan](https://1zzhiyuan.github.io/)

## ✨ 功能一览

| 功能 | 说明 |
|------|------|
| ⏱ **专注计时器** | 开始 / 暂停 / 继续 / 重置，自动记录每日学习时长，进度条展示目标完成率 |
| 🍅 **番茄钟** | 自定义专注 / 休息时长（默认 25+5），完成后自动同步到学习记录，支持跳过与重置 |
| ⛶ **迷你模式** | 一键切换为仅显示时钟和操作按钮的迷你窗口，专注时减少视觉干扰 |
| 📅 **日历视图** | 按月展示每日学习时长，达标自动标记（达标绿 / 未达标黄 / 无记录白），一键跳转今日 |
| 📊 **数据报表** | 趋势图表（折线图 / 柱状图可切换），汇总卡片（总时长 / 日均 / 最佳），时段拆分统计 |
| 💻 **应用统计** | 后台静默统计各软件使用时长，自动分类（学习 / 娱乐 / 其他） |
| 🌅 **时段分析** | 自动划分上午 / 下午 / 晚间，统计各时段学习占比 |
| 🎯 **每日目标** | 自定义每日目标时长，进度条展示完成率，连续达标天数统计 |
| 🏆 **成就系统** | 18 项成就徽章 + 专注指数评分（0-100），追踪学习里程碑 |
| 💺 **久坐提醒** | 自定义间隔时间，温和弹窗提醒起身活动 |
| 🖥 **系统托盘** | 关闭窗口最小化到托盘，后台持续计时，托盘菜单快捷操作 |
| 🌗 **主题系统** | 5 种精选配色：简约浅色、深色护眼、静谧蓝、护眼绿、暖阳橙 |
| 🔄 **自适应缩放** | 所有面板包裹 QScrollArea，字体与元素随窗口大小自适应，任意尺寸均可完整显示 |
| 📤 **数据导出** | 支持导出为 TXT / Excel |
| 🎨 **程序图标** | 运行时 QPainter 自动绘制时钟图标，EXE 文件嵌入同款 .ico |

## 🚀 快速开始

### 方式一：直接运行

下载 `dist/Timer.exe`，双击运行。无需安装 Python。

### 方式二：源码运行

```bash
git clone https://github.com/your-username/Timer.git
cd Timer
pip install -r requirements.txt
python main.py
```

## 📁 项目结构

```
Timer/
├── main.py                    # 应用入口（DPI 感知 + 高 DPI 适配）
├── requirements.txt           # 依赖清单
├── Timer.spec                 # PyInstaller 打包配置
│
├── core/                      # 核心逻辑层
│   ├── database.py            # SQLite 数据库层
│   ├── timer_engine.py        # 计时引擎（开始 / 暂停 / 归档）
│   ├── app_monitor.py         # Windows 前台窗口监控
│   ├── config.py              # 配置管理
│   ├── icon.py                # 应用图标生成（QPainter 运行时绘制 + .ico 生成）
│   └── theme.py               # 主题系统（模板引擎 + 5 套调色板）
│
├── ui/                        # 界面模块
│   ├── main_window.py         # 主窗口 + 底部导航 + 系统托盘 + 周报弹窗
│   ├── timer_panel.py         # 计时主页（含进度条、连续天数、迷你模式）
│   ├── calendar_panel.py      # 日历视图（按月网格，主题自适应）
│   ├── stats_panel.py         # 数据报表（QPainter 自绘图表、成就徽章）
│   ├── pomodoro_panel.py      # 番茄钟面板（持久化计数、与学习记录联动）
│   ├── settings_panel.py      # 设置面板（目标、番茄钟、久坐、主题、导出）
│   └── history_dialog.py      # 历史记录弹窗（双标签页）
│
├── assets/
│   └── timer.ico              # 编译用程序图标（由 icon.py 自动生成）
```

## 🎨 主题系统

Timer 内置 5 套完整配色方案，切换即时生效，所有控件颜色跟随主题联动：

| 主题 | 特点 |
|------|------|
| ☀️ 简约浅色 | 默认主题，白底蓝字，清晰明快 |
| 🌙 深色护眼 | 暗色背景低对比度，适合夜间使用 |
| 🌊 静谧蓝 | 蓝色系主调，柔和舒适 |
| 🌿 护眼绿 | 绿色系配色，长时间使用减轻疲劳 |
| 🌅 暖阳橙 | 暖色调橙蓝搭配，活力温暖 |

主题系统基于 `string.Template` + 调色板字典实现，每个主题 ~25 个颜色变量覆盖全部控件。添加新主题只需在 `PALETTES` 中增加一组颜色值。

## 🗄 数据存储

所有数据保存在本地 SQLite 数据库：

```
%USERPROFILE%\.timer\timer.db
```

| 表 | 说明 |
|------|------|
| `daily_records` | 每日学习时长、分段时间线、目标设定 |
| `app_usage` | 应用使用时长与分类 |
| `pomodoro_sessions` | 番茄钟完成记录 |
| `settings` | 用户偏好设置 |

工具完全离线运行，不产生任何网络请求，数据不会离开你的电脑。

## 🛠 自行编译

```bash
pip install -r requirements.txt pyinstaller
# 首次编译前先生成 .ico（后续无需重复执行）
python -c "from PyQt6.QtWidgets import QApplication; import sys; a=QApplication(sys.argv); from core.icon import make_ico_data; open('assets/timer.ico','wb').write(make_ico_data())"
python -m PyInstaller Timer.spec
# 编译产物位于 dist/Timer.exe
```

> 编译后 exe 约 45-50 MB，主要来自 PyQt6 及其依赖，属单文件打包的正常体积。如需减小体积可自行精简依赖并调整打包配置。

## 🏗 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.7+ | 运行时 |
| PyQt6 | 桌面 GUI 框架 |
| SQLite | 本地嵌入式数据库 |
| psutil + pywin32 | Windows 前台进程监控 |
| plyer | 跨平台桌面通知 |
| PyInstaller | 单文件 exe 打包 |
| openpyxl *(可选)* | Excel 导出 |

> Timer 使用 PyQt6 的 QPainter 自绘图表（折线图、柱状图），无 matplotlib 依赖。

## 💡 设计思路

- **纯本地优先** — 所有数据存本地，无账号、无同步、无隐私泄露风险
- **自绘图表** — 使用 QPainter 绘制图表，避免引入 matplotlib 等重型依赖
- **响应式布局** — 所有面板支持窗口缩放，字体与元素自适应，全部包裹 QScrollArea
- **主题模板化** — QSS 基于 string.Template 生成，调色板与样式分离，易于扩展
- **模块化架构** — core 层与 ui 层分离，各面板独立，信号/槽解耦

## 📄 License

MIT License

Copyright (c) 2026 ZhiYuan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
