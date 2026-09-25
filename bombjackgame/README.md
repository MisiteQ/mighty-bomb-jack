# 炸弹杰克 · 飞牛 fnOS 应用包（fpk）

把《Mighty Bomb Jack》离线版打包成飞牛 NAS 的 fpk 应用：**无端口、无后台进程**，
安装后出现在飞牛 Web 桌面，点击图标即在桌面窗口内（iframe）打开游戏。

## 安装

飞牛 fnOS → 应用中心 → 右上角「手动安装」→ 选择 `bombjackgame.fpk`。

也可以在 fnOS 终端执行：`appcenter-cli install-fpk bombjackgame.fpk`

## 架构

- **CGI 入口（无端口）**：`app/ui/index.cgi` 是唯一入口，fnOS Web 服务通过
  `/cgi/ThirdParty/bombjackgame/index.cgi/` 调用它（调用前自动校验 NAS 登录态）。
  脚本按子路径路由：
  - `/`、`/nescore.wasm` 等 → `target/www/` 静态文件
  - `/saves/<文件>` → 运行数据目录（读档、按键配置、截图，只读）
  - `/__list`、`/__save`、`/__delete` → 存档 JSON API（POST body 即文件内容）
- **存档位置**：`/var/apps/bombjackgame/var/saves/`（即 `@appdata`，卸载应用不删除）。
  `cmd/install_callback` 会放开该目录权限，因为 CGI 进程的运行用户与应用用户不同。
- **manifest 要点**：`platform=all`（纯 WebAssembly，x86/ARM 通吃）、
  `ctl_stop=false`（静态应用隐藏启停按钮）、`checkport=false`（不占端口）。
- **桌面入口**：`app/ui/config` 中 `type: iframe`，内嵌打开。

## 目录结构

```
bombjackgame/
  manifest            应用元信息
  ICON.PNG / ICON_256.PNG   应用中心图标
  config/privilege    运行用户（package 模式）
  config/resource     数据共享声明
  cmd/                生命周期脚本（main=健康检查，install/upgrade 后准备存档目录）
  app/
    ui/
      config          桌面入口（iframe → /cgi/ThirdParty/bombjackgame/index.cgi/）
      index.cgi       CGI 路由入口（静态文件 + 存档 API）
      images/         桌面图标 64/256
    www/              游戏本体（index.html、game.nes、nescore.js、nescore.wasm）
```

## 修改后重新打包

```bash
# 需要 fnpack（同目录 fnpack.exe 或从 developer.fnnas.com 下载）
fnpack build -d bombjackgame
```

注意：在 Windows 上打包时 cmd/ 脚本会丢失执行位，需用 tarfile 把 `cmd/*` 的
mode 重设为 0755 后重打包（首次打包已处理，改动 cmd 脚本后记得重做）。

## 本地测试（不装 NAS）

`../cgi_sim.py` 用 bash 子进程真实执行 index.cgi，模拟 fnOS 的 CGI 网关：

```bash
python cgi_sim.py 9816
# 访问 http://127.0.0.1:9816/cgi/ThirdParty/bombjackgame/index.cgi/
```

存档 API 往返、静态资源、MIME（含 wasm）、目录穿越拦截均已验证通过。
