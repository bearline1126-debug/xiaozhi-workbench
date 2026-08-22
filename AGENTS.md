# AGENTS.md — 小彘的工作台（单文件 PWA）

> 本文件是项目的**唯一规则入口**。开工前必须读它；改完重大项目结构必须更新它（见第 10 节）。

---

## 0. 入口：项目从哪里开始读（强制）

- **任何任务（改代码 / 部署 / 排查 / 加功能）开始前，必须先读本文件。**
  - 支持 AGENTS.md 自动注入的工具（Codex / WorkBuddy 等）会自动加载；若不确定是否已加载，**先读一遍再动手**。
- 阅读顺序：本文件（规则）→ `交接给另一Agent-开场说明.md`（项目手册：功能清单 / 数据结构 / 模块地图 / 风格参数 / 排障备忘）。
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
小彘的工作台 - v2-workbuddy/            ← 唯一工作目录（所有修改只在这里；v93 起工作区已清理，只留必需文件）
├── AGENTS.md                         ← 项目规则入口（本文件，强制读取）
├── 交接给另一Agent-开场说明.md         ← 项目手册（开场白/功能清单/数据结构/模块地图/风格参数/排障备忘）
├── index.html                        ← 单文件 PWA 主体（HTML+CSS+JS 全内联，约 4MB；搜 const BUILD_VERSION 定位版本号）
├── dict.json                         ← 离线英汉大词库（ECDICT 筛选版约 5.9 万词条，3.2MB；英语搜索第三层兜底；由仓库外一次性生成，勿手改）
├── sw.js                             ← Service Worker（CACHE/BUILD 须与 index.html 同步递增）
├── manifest.json                     ← PWA 清单（App 名称由 sw.js 启动时动态注入）
├── deploy_github.sh                  ← GitHub Pages 部署脚本（唯一部署工具；含版本三处一致性校验；
│                                        读 ~/.workbuddy/github-token.txt 的 PAT）
├── icon.png / icon-192.png           ← 应用图标（512 / 192，固定水彩插画）
├── assets/
│   └── welcome-default.jpg           ← 欢迎页默认壁纸
├── .gitignore
└── .git/                             ← git 历史（origin: bearline1126-debug/xiaozhi-workbench，分支 master）
```

> v93 清理说明：历史产物（8 个 `build_v*.py` 生成脚本、`run_v52.bat`、`vercel.json`、`scripts/push.*`、`风格预览.html`、`index.backup-*.html`、2 张图标中间产物 PNG、三份旧文档）已全部删除；需要时从 git 历史找回（gitignored 的除外）。**不要再往仓库里堆积此类文件。**

- **数据入口（v27 起的真相）**：统一走 `Store` 工具类——用户记录存 IndexedDB `bysdash-store`（无 5MB 上限），系统标记存 localStorage `bysdash:`，敏感数据 `bysdash$secret:`（不进备份），媒体（图片/视频原图）存 IndexedDB 大仓库 `bysdash-media`；英语种子池为内联 JSON `English.content`（约 5000 条）。
- **页面 / 路由**：单页，按 `#page-xxx` section 切换；导航用 `UI.openFull` + `history.pushState` 接管物理返回（`popstate` 竞态曾导致黑屏，改逻辑需谨慎）。
- **模块**：各功能为全局 `const Xxx = {...}` 对象（共 43 个，完整清单与职责见交接文档「模块地图」；核心：`Util` / `Store` / `Media` / `UI` / `App` / `Home` / `DiaryBook` / `English` / `Coin` 等），定位一律搜 `const Xxx =`，勿信行号；方法通过 `onclick="Module.method()"` 内联绑定。

---

## 3. 边界：哪些地方不能碰

1. **旧副本**：第 1 节列出的其他路径同名文件夹，一律不改、不写、不当成本项目。
2. **生成区（勿手改）**：内联 `English.content` 大数组（约 5000 条）——生成脚本已删除（v93），**不要手改大段 JSON**；小范围替换必须先向用户说明，大改需重建生成流程。
3. **临时文件（勿提交、勿留在仓库）**：`_check*.js`、`__pycache__/`、`dist/`、`node_modules/`；校验用的临时文件用完即删。工作区保持只含第 2 节清单内的文件。
4. **sw.js 缓存策略（勿改回）**：HTML 网络优先 + 缓存兜底（详见第 4 节），禁止改回 cache-first，否则复现"部署了用户看不到"。
5. **不删 .git 历史**；不擅自重构整体结构，单文件 PWA 的模块边界已经稳定。

---

## 4. 版本号与缓存策略（部署三件套）

- **版本号三处必须同步递增**（一次部署三处一起 +1；deploy 脚本会校验，不一致拒绝推送）：
  1. `index.html` 内 `const BUILD_VERSION = '2026-08-22-v93';`（在文件中部，搜索定位）
  2. `sw.js` 顶部 `const CACHE = 'xiaozhi-workbench-v93';`
  3. `sw.js` 顶部 `const BUILD = '2026-08-22-v93';`
- **sw.js 缓存策略（v84 + v91 血泪史，勿改）**：
  - install：立即 `skipWaiting`，不预缓存 HTML（只预缓存 4 个静态资源，单个 `cache.add` 失败不阻塞）
  - activate：**强制清掉所有旧 cache**
  - fetch：HTML **网络优先 + 缓存兜底**（v84 曾改为纯不缓存，v91 发现网络不稳/离线时会白屏，改为 SWR：网络成功回填缓存，失败回退缓存副本）；其他资源 cache-first
  - 作用：既保证"部署后用户能拿到新版"，又保证断网/弱网时应用打得开
- 版本号漏改 = 用户手机不刷新 = 白部署，这是本项目最常见的翻车点（现已由部署脚本自动拦截）。

---

## 5. 技术栈与硬约束

- 语言：HTML + 内联 CSS + 原生 JS（**无框架、无构建步骤**）；早期用 Python 脚本注入种子数据，v60 起直接编辑 index.html，Python 不再需要
- 框架/库：**零第三方依赖**（保持离线可用）；Node 仅做语法校验
- 数据：全本地（IndexedDB + localStorage），**不上云**；仓库公开也不泄露用户数据
- 部署：GitHub Pages（`https://bearline1126-debug.github.io/xiaozhi-workbench/`），仓库必须 PUBLIC
- 中文 UI；AI 分析 / 天气等联网功能仅按需调用，其余离线可用

---

## 6. 常用命令

> **本机环境**：`git` / `bash` / `python` 不在系统 PATH。便携版在 `C:\Users\cheng\.workbuddy\binaries\PortableGit\versions\1.2.0\`（`cmd\git.exe`、`bin\bash.exe`）；`node` / `curl` 在 PATH。

```bash
# 语法校验（改完 JS 必做，语法错 = 整页白屏）
node -e 'const fs=require("fs");const h=fs.readFileSync("index.html","utf8");const s=[...h.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join("\n;\n");fs.writeFileSync("_check.js",s)'
node --check _check.js && echo OK
# 校验后删除 _check.js（勿提交）

# 部署到 GitHub Pages（唯一部署方式；需 ~/.workbuddy/github-token.txt 含 ghp_/github_pat_）
# 脚本会先校验三处版本号一致，不一致直接拒绝推送
bash deploy_github.sh

# 备用：手动 push（防错：insteadOf 方向不能反，写反会卡死）
git -c url."https://TOKEN@github.com/".insteadOf="https://github.com/" push origin master
# ⚠️ 沙箱环境里 git push 需 dangerouslyDisableSandbox:true（拦截网络）

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
- 不手改 `English.content` 内联 JSON 大段；不提交 `_check*.js`、`__pycache__/`、`dist/`、`node_modules/`；不向仓库新增临时文件/脚本/备份快照
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
- **文档分工与维护契约**：AGENTS.md 管规则；`交接给另一Agent-开场说明.md` 管背景手册 + 每轮变更摘要（每轮交付后更新其第三节）。两份文档**一律不写行号、不写版本号快照**（写死必过时，定位用 `const Xxx =` 搜索，版本以 `BUILD_VERSION` 为准）。
