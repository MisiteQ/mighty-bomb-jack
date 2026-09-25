# 炸弹杰克 · Mighty Bomb Jack 离线版（Windows PC + 飞牛 fnOS）

经典 FC/NES 游戏 **《Mighty Bomb Jack》（マイティボンジャック）** 的完全离线重发行版本，
基于 WebAssembly 模拟核心，提供两个发行形态：

- **Windows PC 便携版**：免安装、免联网、自带 Python 运行时，解压双击即玩
- **飞牛 fnOS 应用包（.fpk）**：安装后出现在 fnOS Web 桌面，无端口、无后台进程，点击即在桌面窗口中游玩

支持 **6 槽位磁盘存档、自定义按键、暂停、截图、音量调节、全屏** 等增强功能。

---

> ## 发布者声明
>
> - 本仓库的发布者（Publisher）为 **[Misite齊（MisiteQ）](https://github.com/MisiteQ)**，**并非游戏的开发者或版权方**。
> - 游戏《Mighty Bomb Jack》的版权归其原始开发者/发行商所有（详见下方[第三方组件与版权](#第三方组件与版权)）。本项目不主张对游戏本体的任何权利，仅为怀旧、学习与保存目的进行非商业性整理与再分发。
> - 除游戏 ROM 与第三方开源组件外，本仓库中的包装代码（启动脚本、本地服务器、CGI 入口、页面外壳等）由发布者编写，以 **MIT 协议** 开放。
> - 如版权方认为本仓库内容涉及侵权，请通过 GitHub Issue 联系，发布者将在核实后及时移除相关内容。

---

## 下载

请前往 [Releases 页面](https://github.com/MisiteQ/mighty-bomb-jack/releases) 下载：

| 文件 | 适用平台 | 说明 |
|---|---|---|
| `bombjack-pc-v1.0.4-portable.zip` | Windows PC | 便携版，**内置 Python 运行时**，解压即用 |
| `bombjackgame-v1.0.4.fpk` | 飞牛 fnOS | 通用包（纯 WebAssembly，x86 / ARM 通用） |
| `bombjackgame-v1.0.4-x86.fpk` | 飞牛 fnOS (x86) | x86 专用包 |
| `bombjackgame-v1.0.4-arm.fpk` | 飞牛 fnOS (ARM) | ARM 专用包 |

> 克隆本仓库得到的是源码，**不包含** PC 版内置的便携 Python 运行时（约 12MB）；
> 需要免安装体验的用户请直接下载上面的便携版 zip。

## 快速开始

### Windows PC 便携版

1. 解压 `bombjack-pc-v1.0.4-portable.zip`
2. 双击文件夹内的 `start.bat` —— 本地服务器在后台无窗口运行，并自动打开浏览器访问 <http://127.0.0.1:9806/>
   - 优先使用包内自带的 `runtime/` 便携 Python；未携带运行时时自动回退到系统已安装的 Python
   - 重复双击 `start.bat` 不会启动第二个服务器，只会重新打开浏览器
3. 点击画面中央的「点击开始游戏」即可开玩
4. 游戏结束后可双击 `stop_server.bat` 停止后台服务器（不停止也不影响游玩）

整个文件夹可直接复制到 U 盘 / 其他 Windows 电脑，无需联网、无需安装任何软件。

### 飞牛 fnOS

1. 打开 fnOS → 应用中心 → 右上角「手动安装」
2. 选择下载的 `.fpk` 文件（通用包即可；如有架构对应专用包也可选用）
3. 安装完成后，桌面会出现「炸弹杰克」图标，点击即在桌面窗口内打开游戏

也可以在 fnOS 终端执行：

```bash
appcenter-cli install-fpk bombjackgame-v1.0.4.fpk
```

## 操作说明

| 按键 | 功能 |
|---|---|
| 方向键 | 移动 / 上下 |
| X | 跳跃（A，空中按住可悬停） |
| Z | B 键 |
| Enter | 开始 / 暂停 |
| Backspace | Select |
| F8 | 快捷截图 |
| F10 | 重置游戏（回到标题画面） |

工具栏还提供：6 槽位存档管理（存/读/覆盖/删除，持久化到磁盘）、8 动作自定义改键、
暂停/继续、截图（PNG 自动下载并留存一份）、音量滑条、4:3 全屏、重置与退出（自动存档）。

## 仓库结构

```
.
├── bombjack-pc/              # Windows PC 便携版源码
│   ├── index.html            # 游戏页面外壳（虚拟手柄转发、工具栏、存档 UI）
│   ├── nescore.js            # 模拟核心加载器（Emscripten 生成）
│   ├── nescore.wasm          # 模拟核心二进制（FCEUmm NES 核心）
│   ├── game.nes              # 游戏 ROM（版权归 Tecmo 所有）
│   ├── serve.py              # 本地静态/存档服务器（纯 Python 标准库）
│   ├── start.bat             # 一键启动（自动选择便携/系统 Python）
│   ├── stop_server.bat       # 停止后台服务器
│   ├── saves/                # 存档槽位、按键配置、截图（运行时生成，已 gitignore）
│   ├── runtime/              # 内置便携 Python 3.13（发布包内提供，仓库中不跟踪）
│   └── README.md             # PC 版详细说明与技术备注
├── bombjackgame/             # 飞牛 fnOS 应用包源码
│   ├── manifest              # 应用元信息（无端口、无后台、platform=all）
│   ├── ICON.PNG / ICON_256.PNG
│   ├── cmd/                  # 生命周期脚本（安装后准备存档目录等）
│   ├── config/               # 运行用户与资源声明
│   ├── app/
│   │   ├── ui/
│   │   │   ├── config        # 桌面入口（iframe → CGI）
│   │   │   ├── index.cgi     # CGI 路由（静态文件 + 存档 JSON API，无端口）
│   │   │   └── images/       # 桌面图标
│   │   └── www/              # 游戏本体（同 PC 版页面与核心）
│   └── README.md             # fnOS 版架构与打包说明
├── fnnas_docs.md             # 飞牛 fnOS 开发者文档合集（参考资料）
└── fnpack.exe                # fpk 打包工具（仓库中不跟踪，从飞牛开发者平台下载）
```

## 从源码重新打包 fnOS 应用

使用飞牛官方打包工具 `fnpack`（Windows 版即本项目发布用的 `fnpack.exe`，
其他平台可从飞牛开发者平台下载）：

```bash
fnpack build -d bombjackgame
```

> Windows 上打包时 `cmd/` 下的 shell 脚本会丢失可执行位，需用 tarfile 把
> `cmd/*` 的 mode 重设为 0755 后重打包（详见 `bombjackgame/README.md`）。

## 技术要点

- **模拟核心**：FCEUmm（libretro NES 核心）经 Emscripten 编译为 WebAssembly，
  浏览器内运行，纯前端计算；核心只接受合成键盘事件，页面转发层把真实按键转换为合成事件
- **PC 版服务器**：`serve.py` 仅用 Python 标准库实现，监听 127.0.0.1:9806，
  提供静态文件与 `/__list`、`/__save`、`/__delete` 存档 API；存档即真实磁盘文件，
  刷新、重启浏览器甚至重启电脑都不会丢失
- **fnOS 版**：不监听任何端口，`app/ui/index.cgi` 是唯一入口，由 fnOS Web 服务
  经 `/cgi/ThirdParty/bombjackgame/index.cgi/` 调用（调用前自动校验 NAS 登录态）；
  存档位于 `/var/apps/bombjackgame/var/saves/`（卸载应用不删除）
- 纯 WebAssembly 无原生二进制，一套包同时支持 x86 与 ARM 设备

## 第三方组件与版权

| 组件 | 权利方 / 协议 | 说明 |
|---|---|---|
| **Mighty Bomb Jack**（游戏 ROM `game.nes`） | © **Tecmo / Tehkan**（1986 街机版，1987 FC/NES 版） | 游戏的名称、角色、画面、音乐及 ROM 数据的全部版权归原权利方所有。本项目为非商业的怀旧保存与技术研究性质再分发 |
| **FCEUmm**（`nescore.wasm` 模拟核心） | 各贡献者，**GPLv2** | 任天堂 NES 模拟器核心，上游：<https://github.com/libretro/libretro-fceumm> |
| **Emscripten**（`nescore.js` 运行时胶水代码） | Emscripten 作者，MIT / UIUC License | <https://emscripten.org/> |
| **Python 3.13 embeddable**（仅便携版 `runtime/`） | Python Software Foundation，PSF License | <https://www.python.org/> |
| **飞牛 fnOS / fnpack** | 飞牛（fnOS） | 应用框架与打包工具，文档参考 <https://developer.fnnas.com/>（见 `fnnas_docs.md`） |

本仓库包装代码（`serve.py`、`start.bat`、`index.cgi`、`cmd/*`、`index.html` 页面外壳等，
不含上述第三方组件）按 **MIT License** 授权：

```
Copyright (c) 2026 Misite齊 (MisiteQ)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

## 免责声明

本项目与 Tecmo、Koei Tecmo、任天堂、飞牛（fnOS）等公司**没有任何隶属、赞助或认可关系**，
所有商标与游戏版权归各自所有者。若相关内容侵犯了您的权益，请通过 Issue 联系发布者处理。
