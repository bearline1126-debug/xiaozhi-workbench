# AGENTS.md — 小彘的工作台（单文件 PWA）

> 本文件是项目的**唯一规则入口**。开工前必须读它；改完重大项目结构必须更新它（见第 10 节）。

---

## 0. 入口：项目从哪里开始读（强制）

- **任何任务（改代码 / 部署 / 排查 / 加功能）开始前，必须先读本文件。**
  - 支持 AGENTS.md 自动注入的工具（Codex / WorkBuddy 等）会自动加载；若不确定是否已加载，**先读一遍再动手**。
- 阅读顺序：本文件（规则）→ 需要时查 `接手说明.md`（部署细节 / 模块地图 / 版本历史）→ `工作台配置.md`（功能清单 / 数据结构 / 风格参数）。
- **开工前确认工作目录**：进入文件夹后必须同时看到三件套——`.git`、`deploy_github.sh`、`AGENTS.md`；缺任一则说明找错文件夹，**立即停下**，切回第 1 节的 canonical 目录。

---

## 1. 唯一工作目录（canonical）

- **唯一合法工作目录**：`C:\Users\cheng\Documents\Codex\2026-08-10\skill-1-skill-skill-md-2\小彘的工作台 - v2-workbuddy`
- **所有修改（改代码 / 跑脚本 / 提交 / 部署）只允许在这个文件夹内进行**，禁止在任何其他路径编辑本项目。
- 其他同名 / 相似文件夹都是旧副本，**一律不要动、不要往里写、不要当成本项目**：
  - `C:\Users\cheng\WorkBuddy\2026-08-12-17-28-08\repo\`（workspace 旧副本，仅参考）
  - `D:\WorkBuddy-work\小彘的工作台 - v2-workbuddy\`（如有，为旧副本）
  - 任何 `repo_tmp\`、`repo\` 下的同名 `index.html` 只是临时验证下载，改完即删，绝不在那里改代码
- 版本号：见第 4 节，三处同步递增。

---

## 2. 目录结构（文件应该放在哪里）

```
小彘的工作台 - v2-workbuddy/            ← 唯一工作目录（所有修改只在这里）
├── AGENTS.md                         ← 项目规则入口（本文件，强制读取，已提交 git）
├── index.html                        ← 单文件 PWA 主体（HTML+CSS+JS 全内联，约 4MB；BUILD_VERSION 在此）
├── sw.js                             ← Service Worker（CACHE/BUILD 须与 index.html 同步递增）
├── manifest.json                     ← PWA 清单（App 名称由 sw.js 启动时动态注入）
├── deploy_github.sh                  ← GitHub Pages 部署脚本（读 ~/.workbuddy/github-token.txt 的 PAT）
├── icon.png / icon-192.png           ← 应用图标（512 / 192，固定水彩插画）
├── assets/
│   └── welcome-default.jpg           ← 欢迎页默认壁纸
├── scripts/
│   ├── push.sh
│   └── push.ps1                      ← git push 辅助脚本（token 仅内存变量使用，不落盘）
├── build_v49.py ~ build_v60.py       ← 历史生成脚本（早期注入英语种子池；缺 v50/54/55/56；
│                                        v60 之后已改为直接编辑 index.html，不再跑脚本）
├── 接手说明.md                       ← 交接文档（部署流程/模块地图/版本历史；部分信息过时，仅作背景参考）
├── 工作台配置.md                     ← 配置参考（功能清单/数据结构/风格参数；停留在 v34，仅作背景参考）
├── v49-overview.md                   ← v49 版本说明（历史）
├── 风格预览.html                     ← 风格预览页
├── index.backup-20260811.html        ← 旧备份快照（勿动，勿删）
├── run_v52.bat                       ← 旧启动脚本（勿依赖，勿删）
├── vercel.json                       ← 旧 Vercel 配置（当前只走 GitHub Pages，勿用，勿删）
├── Modern_mobile_app_icon__*.png     ← 历史图标生成中间产物（勿动）
├── Transform_this_image_into_a_pe_*.png ← 历史图标生成中间产物（勿动）
├── .gitignore
└── .git/                             ← git 历史（origin: bearline1126-debug/xiaozhi-workbench，分支 master）
```

- **数据入口**：功能数据存 `localStorage`（统一 `Store` 工具类，命名空间 `bysdash:`，敏感数据 `bysdash$secret:` 不进备份），媒体（图片/视频）存 IndexedDB 大仓库 `bysdash-media`；英语种子池为内联 JSON `English.content`（约 5000 条）。
- **页面 / 路由**：单页，按 `#page-xxx` section 切换；导航用 `UI.openFull` + `history.pushState` 接管物理返回（`popstate` 竞态曾导致黑屏，改逻辑需谨慎）。
- **模块**：各功能为全局对象（`Util` / `Store` / `Media` / `UI` / `App` / `Home` / `Hub` / `DiaryBook` / `Tracker` / `Mood` / `DailyLog` / `English` / `Coin` / `Wish` / `WishShop` 等），方法通过 `onclick="Module.method()"` 内联绑定。

---

## 3. 边界：哪些地方不能碰

1. **旧副本**：第 1 节列出的其他路径同名文件夹，一律不改、不写、不当成本项目。
2. **历史产物（勿动勿删）**：`index.backup-20260811.html`、`run_v52.bat`、`vercel.json`、根目录两张 `*_*.png` 中间产物、`build_v*.py` 脚本。
3. **生成区（勿手改）**：内联 `English.content` 大数组由 `build_v*.py` 注入——**改数据不要直接手改那段 JSON**，改 / 跑生成脚本再注入，或明确说明后小范围替换。
4. **临时文件（勿提交）**：`_check*.js`、`__pycache__/`、`dist/`、`node_modules/`。
5. **sw.js 缓存策略（勿改回）**：v84 起 HTML **永不缓存**（详见第 4 节），禁止改回 cache-first，否则复现"部署了用户看不到"。
6. **不删 .git 历史**；不擅自重构整体结构，单文件 PWA 的模块边界已经稳定。

---

## 4. 版本号与缓存策略（部署三件套）

- **版本号三处必须同步递增**（一次部署三处一起 +1）：
  1. `index.html` 顶部 `const BUILD_VERSION = '2026-08-22-v92';`
  2. `sw.js` 顶部 `const CACHE = 'xiaozhi-workbench-v92';`
  3. `sw.js` 顶部 `const BUILD = '2026-08-22-v92';`
- **sw.js 缓存策略（v84 血泪史，勿改）**：
  - install：立即 `skipWaiting`，**不预缓存 HTML**（只预缓存静态资源，单个 `cache.add` 失败不阻塞）
  - activate：**强制清掉所有旧 cache**
  - fetch：HTML **永远走网络、永不缓存**；其他资源缓存优先
  - 作用：根治"部署了新版本用户手机还是旧版"
- 版本号漏改 = 用户手机不刷新 = 白部署，这是本项目最常见的翻车点。

---

## 5. 技术栈与硬约束

- 语言：HTML + 内联 CSS + 原生 JS（**无框架、无构建步骤**）；Python 仅用于早期离线生成种子数据
- 框架/库：**零第三方依赖**（保持离线可用）；Node 22 仅做语法校验，Python 3.13 仅跑生成脚本
- 数据：全本地（localStorage + IndexedDB），**不上云**；仓库公开也不泄露用户数据
- 部署：GitHub Pages（`https://bearline1126-debug.github.io/xiaozhi-workbench/`）
- 中文 UI；AI 分析 / 天气等联网功能仅按需调用，其余离线可用

---

## 6. 常用命令

```bash
# 语法校验（本项目无 npm/构建；改完 JS 必做，不过会整页白屏）
python -c "import re;open('_check.js','w',encoding='utf-8').write('\n;\n'.join(re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', open('index.html',encoding='utf-8').read(), re.S)))"
node --check _check.js && echo OK
# 校验后删除 _check.js（勿提交）

# 部署到 GitHub Pages（需 ~/.workbuddy/github-token.txt 含 ghp_/github_pat_）
bash deploy_github.sh

# 手动 push（防错：insteadOf 方向不能反，写反会卡死）
git -c url."https://TOKEN@github.com/".insteadOf="https://github.com/" push origin master
# ⚠️ WorkBuddy 里 git push 需 dangerouslyDisableSandbox:true（沙箱拦截网络）
# 已沉淀 skill：git-push-github，优先用它

# 验证线上版本号（GitHub Pages 构建约 1~2 分钟延迟）
curl -s "https://bearline1126-debug.github.io/xiaozhi-workbench/index.html" | grep -o "BUILD_VERSION = '[^']*'"
```

---

## 7. 测试与验证方式

- **构建验证**：本项目无构建步骤；改完 JS 必须用第 6 节 `node --check` 校验内联脚本语法通过（语法错 = 整页白屏）
- **视觉验证**：桌面 + 手机 PWA 都检查关键页面（英语复习/测试为「单词+搭配两列并排」，窄屏不溢出；日记 3D 翻页方向；首页卡片拖动）
- **其他检查**：`git diff` 审查改动、`git status` 确认文件变更；部署后用 `curl` 校验线上 `BUILD_VERSION` 与新标记/函数生效
- **遇到环境问题无法验证时，必须向用户说明，不得假装通过**

---

## 8. 代码规范与修改边界

- **只在第 1 节 canonical 文件夹内改**；其他路径的同名项目一律视为旧副本
- 单文件原则：所有逻辑在 `index.html` 内联，不拆模块；新增功能优先复用 `Util` / `Store` / 现有模块对象
- 文件/函数职责单一；禁止引入新 UI 框架 / CSS 框架 / 大型依赖（保持零依赖、离线可用）
- 不手改 `English.content` 内联 JSON；不提交 `_check*.js`、`__pycache__/`、`dist/`、`node_modules/`
- 删代码后检查多余 `}` 或 `},,` 双逗号（曾两次因此整页 JS 报错）

---

## 9. 编码行为准则

- **先思考再编码**：实施前明确假设；多解时列选项，不擅自选；有更简单的方法直说
- **改动前先读懂**：相关文件现有逻辑先理解再动手；尤其 SRS 复习/测试解耦、PWA 黑屏规避用 `Util.openExternal` 而非 `target=_blank`
- **最小改动**：只碰必须碰的，匹配现有风格（`Util.esc` 转义、全局对象、内联 `onclick` 写法）；不「改进」无关代码、不重构没坏的东西
- **目标驱动**：把指令变为可验证目标，分步执行并逐步验证（改一处即 `node --check`，必要时 `curl` 验线上）

---

## 10. 交付与验收（用户习惯，必须遵守）

- 用户以**编号批次**提需求（6–8 项/批），做完按编号逐项验收 → 回复按 `① ② ③…` 结构化，并附**变更摘要 + 线上地址**
- 看到 `@image` 截图，**必须结合截图判断** UI 期望
- 改动小步、可验证；每次部署后主动 `curl` 验证版本号
- 常把任务交接给另一个 AI → 每次交付需附带可粘贴的：**开场说明 + 变更摘要 + GitHub Pages 部署链接**

---

## 11. 规则更新机制（重大调整后马上写进本文件）

- **触发条件**（出现任一即必须在本任务内同步更新本文件对应小节）：
  - 新增 / 删除 / 移动了项目文件（目录结构变化 → 更新第 2 节）
  - 改变了部署方式、版本号机制、缓存策略（→ 更新第 4 / 6 节）
  - 改变了存储方案、命名空间、数据格式（→ 更新第 2 节数据入口）
  - 出现了新的「不能碰」的文件或目录（→ 更新第 3 节）
- **判断标准**：一个完全没参与过本项目的 AI，只看本文件能否安全开工？不能 → 必须补。
- 小改动（改某个功能逻辑）不需要改规则；但涉及上述结构变化的，**绝不允许只改代码不更新规则**。
- `接手说明.md` / `工作台配置.md` 是背景资料：发生结构变化时顺手同步或标注过时即可，不必追求实时。
