# AGENTS.md — 小彘的工作台（单文件 PWA）

## 0. 项目位置（唯一 canonical —— 找错文件夹=改错项目，必须严格遵守）

- **唯一合法工作目录**：`C:\Users\cheng\Documents\Codex\2026-08-10\skill-1-skill-skill-md-2\小彘的工作台 - v2-workbuddy`
- **所有修改（改代码、跑脚本、提交、部署）只允许在这个文件夹内进行**，禁止在任何其他路径编辑本项目。
- **其他同名/相似文件夹都是旧副本，一律不要动、不要往里写、不要当成本项目**：
  - `C:\Users\cheng\WorkBuddy\2026-08-12-17-28-08\repo\`（workspace 旧副本，已镜像给 Codex，仅参考）
  - `D:\WorkBuddy-work\小彘的工作台 - v2-workbuddy\`（如有，为旧副本）
  - 任何 `repo_tmp\`、`repo\` 下的同名 `index.html` 只是临时验证下载，改完即删，绝不在那里改代码
- 确认当前位置是否正确：进入文件夹后看有没有 `.git`（含 origin → bearline1126-debug/xiaozhi-workbench）、`deploy_github.sh`、`AGENTS.md` 三件套；有才是 canonical。
- 版本号：`index.html` 顶部 `BUILD_VERSION = '2026-08-20-vXX'`，`sw.js` 的 `CACHE`/`BUILD` 三处必须同步递增。

## 1. 项目概述
单文件 PWA「小彘的工作台」：把复盘、习惯、英语积累、心愿星等个人管理功能集成到一个可「添加到手机桌面」、离线可用的本地网页应用，数据全部存本地，不上云。

## 2. 技术栈与环境
- 语言：HTML + 内联 CSS + 原生 JS（无框架、无构建步骤）；Python 仅用于离线生成种子数据
- 框架/库：零第三方依赖（纯原生，保持离线可用）
- 运行环境：浏览器（PWA standalone）；Node 22 仅做语法校验，Python 3.13 仅跑生成脚本
- 包管理器：无（前端零依赖）
- 其他关键依赖：Service Worker(`sw.js`) 做缓存/PWA；`localStorage` + `IndexedDB` 存储；GitHub Pages 托管

## 3. 项目架构与关键文件

### 3.0 目录结构（canonical 文件夹内）

```
小彘的工作台 - v2-workbuddy/          ← 唯一工作目录（所有修改只在这里）
├── AGENTS.md                         ← 本项目规则（本文件，已提交到 git）
├── index.html                        ← 单文件 PWA 主体（HTML+CSS+JS 全部内联，~4MB；BUILD_VERSION 在此）
├── sw.js                             ← Service Worker（CACHE/BUILD 版本号须与 index.html 同步递增）
├── manifest.json                     ← PWA 清单（名称由 sw.js 动态注入自定义名）
├── deploy_github.sh                  ← GitHub Pages 部署脚本（读 ~/.workbuddy/github-token.txt 的 PAT）
├── icon.png / icon-192.png           ← 应用图标（512/192）
├── assets/
│   └── welcome-default.jpg           ← 欢迎页默认壁纸
├── build_v49.py ~ build_v60.py       ← 离线生成脚本（英语种子池等注入 index.html；改种子数据请跑脚本，勿手改内联 JSON）
├── scripts/
│   ├── push.sh
│   └── push.ps1                      ← git push 辅助脚本
├── 工作台配置.md / 接手说明.md / v49-overview.md   ← 说明文档
├── 风格预览.html                     ← 风格预览页
├── run_v52.bat                       ← 旧启动脚本（勿依赖）
├── index.backup-20260811.html        ← 旧备份（勿动）
├── vercel.json                       ← 旧 Vercel 配置（当前只走 GitHub Pages，勿用）
└── .git/                             ← git 历史（origin: bearline1126-debug/xiaozhi-workbench）
```

- 数据入口：功能数据存 `localStorage`（统一 `Store` 工具类），媒体存 `IndexedDB`；英语种子池为内联 JSON `English.content`（约 5000 条，单文件内）
- 页面/路由：单页，按 `#page-xxx` section 切换；导航用 `UI.openFull` + `history.pushState` 接管物理返回（`popstate` 竞态曾导致黑屏，改逻辑需谨慎）
- 公共布局/组件：内联 CSS 变量主题(`--text/--accent` 等)；通用工具在 `Util`；各功能为全局对象(`English`/`Coin`/`WishShop` 等)
- 静态资源位置：`repo/` 根(`index.html`、`sw.js`、`manifest.json`、`icon.png`、`icon-192.png`、`assets/`)
- 配置文件位置：`manifest.json`（由 `sw.js` 动态注入自定义名）、`vercel.json`
- 特殊生成区（勿手改）：内联 `English.content` 大数组由 `build_v*.py` 注入，**改数据请改/跑生成脚本再注入，不要直接手改那段 JSON**；临时校验文件 `_check*.js`、`__pycache__/` 勿提交

## 4. 常用命令
```bash
# 语法校验：抽取内联 <script> 后 node 检查（本项目无 npm/构建）
python -c "import re;open('_check.js','w',encoding='utf-8').write('\n;\n'.join(re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', open('index.html',encoding='utf-8').read(), re.S)))"
node --check _check.js && echo OK

# 部署到 GitHub Pages（需 ~/.workbuddy/github-token.txt 含 ghp_/github_pat_）
bash deploy_github.sh

# 重新生成英语种子池并注入 index.html
python build_vXX.py
```
本地预览：浏览器直接打开 `index.html`，或部署后访问 GitHub Pages URL（线上版号见 `BUILD_VERSION`）。

## 5. 测试与验证方式
- 构建验证：本项目无构建步骤；改完 JS 必须用上面 `node --check` 校验整段内联脚本语法通过
- 视觉验证：桌面 + 手机 PWA 都检查关键页面；英语复习/测试为「单词+搭配两列并排」，窄屏不溢出
- 其他检查：`git diff` 审查改动、`git status` 确认文件变更；部署后用 `curl` 校验线上 `BUILD_VERSION` 与新标记/函数生效
- 遇环境问题无法验证时，必须向用户说明，不得假装通过

## 6. 代码规范与修改边界
- **只在第 0 节规定的 canonical 文件夹内改**：任何其他路径的同名项目文件夹一律视为旧副本，不改、不写、不当成本项目。
- 单文件原则：所有逻辑在 `index.html` 内联，不拆模块；文件已很大(~4MB)，新增功能优先复用 `Util`/`Store` 与现有模块对象
- 禁止引入新 UI 框架 / CSS 框架 / 大型依赖（保持零依赖、离线可用）
- 不修改生成物：勿手改 `English.content` 内联 JSON；勿提交 `_check*.js`、`__pycache__/`、`dist/`、`node_modules/`
- 函数/模块职责单一，不无必要膨胀

## 7. 编码行为准则
- 先思考再编码：实施前明确假设；多解时列选项，不擅自选
- 最小改动：只碰必须碰的，匹配现有风格（`Util.esc` 转义、全局对象、内联写法）；不「改进」无关代码、不重构没坏的东西
- 改动前先读懂相关逻辑：尤其 SRS 复习/测试解耦、PWA 黑屏规避用 `Util.openExternal` 而非 `target=_blank`
- 目标驱动：把指令变为可验证目标，分步执行并逐步验证（改一处即 `node --check`，必要时 `curl` 验线上）
