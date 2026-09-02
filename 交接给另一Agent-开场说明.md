# 小彘的工作台 — 交接文档（开场说明 + 项目手册）

> 用法：把「一、开场白」整段复制给下一个 Agent 作为第一句话；「三、近期变更摘要」每轮交付后更新。
> 本文件是唯一背景手册（功能清单 / 数据结构 / 模块地图 / 风格参数 / 排障备忘都只在这里）；
> **规则一律以 `AGENTS.md` 为准**。本文件不写行号、不写版本快照（写死必过时），定位一律「搜索 `const Xxx =`」。

---

## 一、开场白（粘贴给新 Agent 的第一句）

我有个单文件 PWA 个人仪表盘「小彘的工作台」，现在交给你继续迭代。请先读项目根目录的 `AGENTS.md`（这是唯一规则入口，开工前必须读，里面写了目录、边界、版本号机制、部署方式、交付约定）。读完按我的需求批次动手。

## 二、项目关键信息（贴给他看）

- 工作目录（只能在这里改）：`C:\Users\cheng\Documents\Codex\2026-08-10\skill-1-skill-skill-md-2\小彘的工作台 - v2-workbuddy`
- 当前版本：以 `index.html` 里 `const BUILD_VERSION` 为准（搜索定位，勿信任何文档写的数字，包括本文件）
- 线上地址：https://bearline1126-debug.github.io/xiaozhi-workbench/
- GitHub 仓库：`https://github.com/bearline1126-debug/xiaozhi-workbench.git`（**必须 PUBLIC**，免费 Pages 不支持私有库）
- 代码结构：全部逻辑在 `index.html` 一个文件内联（HTML+CSS+JS，约 4MB、7000+ 行）；`sw.js` 是 Service Worker；`manifest.json` 是 PWA 清单
- **存储真相（重要，别信旧说法）**：用户记录在 IndexedDB `bysdash-store`（v27 起，无 5MB 上限）；系统标记在 localStorage `bysdash:`；敏感 key 在 `bysdash$secret:`（不进备份）；图片/视频在 IndexedDB `bysdash-media`。数据全部只在本机，仓库公开不泄露
- 部署：`bash deploy_github.sh`（内含版本三处一致性校验），随后 curl 验证线上 `BUILD_VERSION` 已变
- 本机环境：`git` / `bash` / `python` 不在系统 PATH，用便携版 `C:\Users\cheng\.workbuddy\binaries\PortableGit\versions\1.2.0\`（`cmd\git.exe`、`bin\bash.exe`）；`node` 在 PATH
- 进入文件夹必须同时看到 `.git` / `deploy_github.sh` / `AGENTS.md` 三件套，缺任一就是找错目录，立刻停下

## 三、近期变更摘要（每轮交付后更新本节，只留最近两三轮）

- **v107（2026-09-02 日记本手账改版 + 吐槽区）**：① 日记本恢复「两页左右并排」（撤销 v106 手机上下堆叠，遵从用户偏好）；② 手账固定配色——`@一日总结`=紫色底/白字、`打卡`=浅黄底/黑字、`开心小事`=粉色底、`吐槽区`=青色底；`今日完成`前缀 🏆、`开心小事`前缀 ⭐（见 `.db-box.purple/.yellow/.pink/.cyan`）；③ `@情绪日记`/`@碎碎念` 从咖色弱化改为**黑色正文无框段**（`.db-plain`），排在主框后；**碎碎念自动合并成一段话**（不再逐行）；`@习惯打卡`/`@作息` 保留咖色弱化放最底部；④ 周总结把「周几」移到日期下方横线之下（`.db-sum-day-line`）；⑤ 新增「**吐槽区**」——每日记录页加录入框 `#dlRants`（自动保存，同感恩日记地位），数据存 `success:<date>.rants`，已接入日记本（青色框 💬）和复盘 AI 一手记录（`Review.rangeText` 抓取"吐槽"，只发文字）。
- **v106（2026-09-02）**：① 复盘恢复「同一对话线程」——`Review.aiGenerate` 重新传 `threadKey:'review_growth'`，每次复盘结果真实累积进 localStorage `bysdash:ai_thread_review_growth`；复盘页面新增「查看发给 AI 的对话」按钮 + `#reviewRaw` 容器，绑定 `Review.viewRaw()`（生成后自动刷新），展示最近 8 轮完整原文（不再截断）；② `AI.ask` 新增 `options.fresh`——带线程但设 `fresh:true` 时，旧历史**仍累积进线程键**（对话连续可翻看）但**不喂给模型**（模型只凭本次一手记录作答，避免 v104 修过的「两周结果雷同」又复现）；③ 复盘发给 AI 的数据口径=按日历周期自动抓取（周→本周 ∥ 月→本月 ∥ 年→今年，均截止今天，非死板的近7/30/366条）的完整一手文字记录（含情绪/今日完成/习惯/主线任务/开心小事/情绪日记/碎碎念/作息，**图片一律排除只发文字**），不发二手结论——见 `Review.rangeText/prompt`；④ 日记本手机端适配——新增 `@media(max-width:760px)`：窄屏两页不再左右并排（会窄到一行放不下几个字、像清单不像书），改为上下堆叠、每页整行全宽，像一本书的单页、每行能排更多字。
- **v105（2026-09-02）**：① 语音改回纯本机秒响——移除 v104 的「在线 Google 真人 TTS 优先」（墙内连不上会点到很久才落到机械音），`English.speak` 直接走 speechSynthesis，音色取决于设备系统已装的 TTS（要自然音需在设备设置里装语音包，脚本无法代装）；② 固定搭配卡也加 🔊（`English.playPhrase`）；③ 复盘 AI 数据机制重构——`Review.prompt()` 按模式裁剪数据范围（周报只发近 7 天，不再一律 31 天），并把上一次同类复盘结论显式喂给 AI 承接提炼（`priorHint`），既避免重复灌全部原始记录，也避免「同对话框自动记忆」导致的复读雷同。
- **v104（2026-09-01）**：① 修「两周周复盘一模一样」——根因是生成时用了共享线程 `review_growth`，会把最近 10 条同类周报问答塞进 AI 上下文导致模型复读旧文；改为每次基于本次数据独立生成 + 更高温度（`Review.aiGenerate` 不再传 threadKey）；② 去复盘 markdown 符号——新增 `Review.md()` 把 `##`/`**`/`-` 等转成干净 HTML（`reviewOutput` 与历史记录 `Review.history` 都走渲染，加了 `.md-body` 样式），不再满屏 # 和 *；③ 日记本感动瞬间图片可左右翻页——新增通用全屏图片翻页查看器 `Media.gallery/galNav/galClose`（复用视觉灵感的 `.visual-viewer` 样式，左右循环切换），日记页 `DiaryBook` 感动瞬间缩略图点击改为 `Media.gallery`；④ 星愿瓶已完成心愿可撤回——新增 `WishShop.restoreStar` + `WishShop.starCard`（记录卡片上 ↺ 按钮），撤回后恢复为未兑换心愿 + 用新增的 `Coin.refund` 退回当时扣掉的金币（正数相抵，总额归零）；⑤ 英语每日单词加朗读喇叭 `English.playWord`（单词卡 🔊）；⑥ 朗读改用真人人声优先——`English.speak` 联网走 Google 神经网络 TTS（只发送要读的英文），失败/断网自动回落本机系统语音 `speakLocal`，不打断不报错（隐私：只发给语音服务要朗读的那句英文单词，不含任何个人记录）。
- v102（2026-08-22）：对话两段式（先英文整段、再中文逐行换行）；每日记录页加感恩瞬间图片上传（与感恩日记页共用 `success:<date>.images`）。
- v101/v100/v99/v98：对话逐行配对方法；例句翻译全自动；搜索三行制 + AI 补例句；离线大词库 `dict.json` 四层搜索链。
- v93（2026-08-22）工程大清理：① 删除全部历史产物（8 个 build_v*.py、run_v52.bat、vercel.json、scripts/push.*、风格预览.html、backup 快照、2 张图标中间产物 PNG），工作区收敛为运行时 6 文件 + 部署件 + 2 份文档；② 文档收敛 5→2：接手说明.md / 工作台配置.md / v49-overview.md 精华并入本文件后删除；③ AGENTS.md 与代码对齐（存储描述、缓存策略措辞、目录树、环境备注）；④ deploy_github.sh 增加版本三处一致性校验（不一致拒绝推送）；⑤ sw.js 顶部注释对齐 v91 实际策略（网络优先+缓存兜底，非「永不缓存」）；⑥ git gc 瘦身（27.8MB→2.4MB）。

## 四、项目简史（v18 → 现，一句话级）

- v18–v19：修 PWA 安装角标与自定义图标安装失败
- v20–v24：大功能期——主线任务、日记本翻书、睡眠/身体档案、星愿瓶（SVG）、感恩日记图片、碎碎念聚合
- v25–v26：安全稳定体检（备份格式校验、HTTPS-only、SW 只缓存本站）
- v27：数据层改混合 Store（IndexedDB `bysdash-store`），固定水彩图标，修 SW 括号错（SW 从未注册成功的根因）
- v29：删 CloudSync（云端同步功能整体下线）
- v30：首页/侧栏/更多大改；「生活智能分析」改名「生活万花筒」；运动时长改小时
- v31–v32：原图备份不压缩；欢迎页删 Bing 壁纸（`welcome_wallpaper` key 死亡）；本周汇总重写
- v33：拖动改几何命中（修手机长按拖不动）；备份改手动+月度自动；AI 词云
- v34：情绪精简 6 类；`deploy_github.sh` 诞生；英语种子池由 build 脚本注入（v35–v48 为脚本补丁期，细节见 git log）
- v49/v50：SRS 间隔复习（3/7/14 天）、金币扩到 11 法、习惯「删不掉」根因修复（补种逻辑）
- v84：SW 缓存策略血泪——HTML 不缓存根治「部署了手机不刷新」
- v87–v88：Companion（闲话铺）system prompt 迭代；openDetail 改单 div contenteditable（点开即读、点字即编辑）
- v89：千问 dashscope 自动 enable_search；欢迎句去重；金句库扩到 230 句
- v90：删 v87 残留 CSS 导致详情页 35% 留白；经验摘录抽句过滤
- v91：修 v84 回归——HTML 纯不缓存在网络不稳时白屏，改为 SWR（网络优先+缓存兜底）
- v92：闲话铺去刻板化；今日必做可编辑；欢迎语每日一变
- v93：见「近期变更摘要」

## 五、功能清单（route id ↔ 侧栏 ↔ 说明）

> 清单停在 v34 视角 + 部分后续更新；v35+ 新增/改动的功能以 `index.html` 代码为准（route 定义搜 `App.routes`）。

| # | 功能 | route id | 侧栏 | 说明 |
|---|---|---|---|---|
| 1 | 首页 | `home` | ☀️ 首页 | 欢迎页、励志语、今日进度、今日必做（v92 起可编辑可补）、文件夹式大入口、桌面卡片拖动排序/大小/折叠 |
| 2 | 分类页 | `hub` | 🧭 分类 | 日记/知识/生活分组页，组内可拖动排序、可隐藏恢复 |
| 3 | 每日记录 | `daily` | 🌙 每日记录 | 成功日记+追踪表+情绪日记三合一，一键 AI 复盘 |
| 4 | AI 陪伴（零时闲话铺） | `chat` | 🫧 AI 陪伴 | 连续对话；命中经验摘录附相关卡片；可生成个人使用说明书 |
| 5 | 感恩日记 | `success` | 📝 感恩日记 | 今天值得感恩的事、明天最重要的 3 件事 |
| 6 | 追踪表 | `tracker` | 📊 追踪表 | 自定义习惯（含说明小字）、情绪 emoji、周/月/年热力明细 |
| 7 | 情绪日记 | `mood` | 💭 情绪日记 | 事件长文、情绪符号、AI 事件复盘 |
| 8 | 复盘中心 | `review` | 🧠 复盘中心 | 周/月/年总结、年度计划与每日关联天数 |
| 9 | 个人认知库 | `self` | 🪞 认知库 | 优点、喜欢/不喜欢、关键词、边界、可控/不可控；清单类型可自定义 |
| 10 | 经验摘录 | `notes` | 📚 经验摘录 | 标题与关键词分离、标签/关键词下拉、搜索、按标签分块；点「去问它」跳 AI 陪伴 |
| 11 | 英语积累 | `english` | 📖 英语积累 | 每日一句/单词(含例句)/固定搭配/对话/写作；SRS 间隔复习（见排障备忘）；打卡/连续天数 |
| 12 | 视觉灵感 | `visual` | 🎨 视觉灵感 | 每日推荐、换一换、分类管理；图片/视频存原图大仓库 |
| 13 | 灵感速记 | `quick` | 📌 灵感速记 | 一句话快速记录，灵感池、内联编辑、复制 |
| 14 | 心愿/行动清单 | `wish` | ✅ 心愿行动 | 想做的事与下一步行动分开，完成进已完成区，可拖动排序 |
| 15 | 做菜栏 | `cooking` | 🍲 做菜栏 | 菜谱、标签下拉、图片、独立转盘（指针不转、中心弹出结果） |
| 16 | 运动打卡 | `sport` | 💪 运动打卡 | 类型/时间/时长（小时）、月度日历统计 |
| 17 | 穿搭助手 | `outfit` | 👗 穿搭助手 | 天气+穿搭（定位城市）、衣橱管理、按衣橱生成今日穿搭 |
| 18 | 生活万花筒 | `lifeAnalysis` | 📈 生活分析 | 总览+内联 SVG 图表+报告置顶；瓦片可拖动/隐藏；月/年报告 |
| 19 | 份子钱记录 | `gift` | 🧧 份子钱 | 收到/付出/净额、人情汇总、明细搜索、编辑与再记一笔 |
| 20 | 设置 | `settings` | ⚙️ 设置 | 完整备份（含图片视频）/轻备份/Markdown/CSV 导出；每月自动备份；AI key；存储用量（80% 黄 95% 红预警）；本地密码锁；自定义 App 名称 |

## 六、数据结构（Store key 速查）

统一经 `Store` 类读写（`Store.get(key, def)` / `Store.set` / `Store.setDaily`）。按日期存取是常态。

> 表列到 v34 + v49 后补充；**完整以代码为准**（搜 `Store.get(` / `Store.set(`）。已剔除 v29/v31 删除的死 key（`syncUrl`、`bysdash$secret:syncToken`、`_lastCloudSync`、`welcome_wallpaper`——代码里不存在，别照旧文档找）。

| Store key | 结构 | 归属 |
|---|---|---|
| `success:YYYY-MM-DD` | `{date,wins,tomorrow[]}` | 感恩日记 |
| `task_done:YYYY-MM-DD` | `[index]` | 今日必做完成态 |
| `home_widgets` / `home_entry_collapsed` / `home_hidden_widgets` / `home_hidden_entries` / `home_top_tiles` | 数组 | 首页布局 |
| `hub_pages_diary` / `hub_pages_knowledge` / `hub_pages_life` | `[id]` | 分类页排序 |
| `tracker_items` | `[{id,name,desc}]` | 追踪表（desc 为习惯说明小字） |
| `tracker:YYYY-MM-DD` | `{date,habits,mood,line,moodDiaryId?}` | 追踪/情绪 |
| `moods` | `[{id,date,time,symbol,text,summary}]` | 情绪日记（6 种情绪，`__moodsV34Migrated` 迁移标记） |
| `review_notes` / `review_results` / `review_last_{mode}` / `annual_plans` / `daily_plans:YYYY-MM-DD` / `lastWeeklyReview` | 复盘中心各组 | 复盘中心 |
| `self_categories` / `self_*` | 清单 | 认知库 |
| `notes` / `note_tags` / `note_keywords` / `note_editing` / `freq_*` | 经验摘录各组 | 经验摘录 |
| `ai_thread_review_growth` / `ai_thread_notes_qa` / `ai_thread_life_reports` / `ai_thread_companion_main` | `messages[]` | AI 连续对话历史 |
| `companion_msgs` | 用户消息 | 闲话铺 |
| `visuals` / `visual_daily_override` | 视觉灵感 | 视觉灵感 |
| `quick` | `[{id,date,text}]` | 灵感速记 |
| `wishes` | `[{id,date,type,text,done}]` | 心愿/行动 |
| `dishes` / `wheel_dishes` | 做菜/转盘 | 做菜栏 |
| `sport_types` / `sport_logs`（duration 单位小时，`_sportHoursMigrated` 迁移存量÷60） | 运动 | 运动打卡 |
| `clothes` / `cloth_last_*` | 衣橱/下拉默认值 | 穿搭助手 |
| `gifts` | `[{id,type,person,amount,event,date,note}]` | 份子钱 |
| `english_done:YYYY-MM-DD` / `openDays` | 打卡/打开天数 | 英语、每日 |
| `english_srs` / `english_mastered` / `english_today` / `english_today_test:日期` | SRS 复习库/已学库/当日内容缓存/当日测试 | 英语 SRS |
| `wins_library` / `wins_cursor` | 金句素材库/扫描游标 | Wins |
| `coin_history` | 按日去重的金币记录 | 金币 |
| `weather_city` | `string` | 穿搭 |
| `aiBase` / `aiModel` / `bysdash$secret:ai` | AI 配置（key 不进备份） | AI |
| `lockHash` | `string` | 密码锁 |
| `autoBackup` | `{on,lastMonth,dirName}` | 月度自动备份 |
| `_lastBackup` / `_lastWrite` / `_lastPage` / `_buildVersion` / `_storagePersisted` | 系统标记（localStorage `bysdash:`） | 系统 |
| `_schemaVersion` | number，**当前 4** | Migrate 迁移版本 |
| `__backupDir`（大仓库内） | FileSystemDirectoryHandle，不进备份 | 自动备份文件夹句柄 |
| `__rescueList` | `[{at,data}]` 最多 3 份 | 恢复前急救快照 |

## 七、模块地图（43 个全局对象，搜 `const Xxx =` 定位，勿信行号）

| 模块 | 职责 |
|---|---|
| `Store` | 数据层：localStorage 系统标记 + IndexedDB `bysdash-store` 持久化；启动 `await Store.init()` |
| `Util` | 日期/uid/esc 转义/防抖等基础工具 |
| `Media` | IndexedDB 大仓库 `bysdash-media`（图片视频原图） |
| `Migrate` | 一次性数据迁移（`_schemaVersion` 控制，只做加法） |
| `UI` | toast、确认弹窗、通用 item 渲染、`openFull` 全屏导航 |
| `DragSort` | 通用拖动排序（长按触发、几何矩形命中） |
| `AI` | OpenAI 兼容接口调用（DeepSeek/千问 dashscope） |
| `App` | 路由 `App.routes`、`App.go(id)`、启动初始化 |
| `StorageGuard` | `navigator.storage.persist()` 持久化存储申请 |
| `Daily` | 打开天数统计（`openDays`、连续打开 streak） |
| `Welcome` | 欢迎页（每日一句问候，v92 起每天只变一次） |
| `Hub` | 分类聚合页（diary/knowledge/life 三组） |
| `Home` | 首页桌面卡片 |
| `Success` | 感恩日记 + 明日必做 |
| `MustEditor` | 今日/明日必做结构化编辑器（v92 可编辑可补） |
| `MainQuest` | 主线任务（进度条、打卡） |
| `DiaryBook` | 日记本：双页 3D 翻书、`renderSpread`、本周汇总、日记归档、AI 词云 |
| `Wins` | 鼓励素材/金句库（`wins_library`，从 cursor 起扫描新素材） |
| `Tracker` | 习惯追踪表、`dayKey(date)` |
| `Mood` | 情绪日记 |
| `DailyLog` | 每日记录页，`_pendingDate` 支持补记历史日期 |
| `Companion` | 零时闲话铺（`dailyWhispers(date)` 按天聚合） |
| `Chart` | 内联 SVG 图表工具 |
| `AutoBackup` | 每月自动备份 |
| `Review` | 复盘中心 |
| `Self` | 个人认知库 |
| `Notes` | 经验摘录（openDetail 单 div contenteditable：点开即读、点字即编辑） |
| `Quick` | 灵感速记 |
| `Wish` | 心愿/行动（`wishId` 归属） |
| `WishShop` | 兑换铺：金币兑换 + 星愿瓶 + 心愿记录 |
| `English` | 英语积累（内联 `content` 约 5000 条种子 + SRS） |
| `Coin` | 金币系统：11 来源、`earn/spend/total`、`DAILY_CAP=10`、按日防重复 |
| `Visual` | 视觉灵感 |
| `Sport` | 运动打卡 |
| `Outfit` | 穿搭助手 |
| `Cooking` | 做菜栏 |
| `LifeAnalysis` | 生活万花筒 |
| `Gift` | 份子钱 |
| `Backup` | 备份/恢复/导出（含急救快照） |
| `AppCustom` | 自定义 App 名称（sw.js 启动时动态注入 manifest） |
| `Settings` | 设置页 |
| `Lock` | 本地密码锁 |
| `PWAInstall` | PWA 安装横幅 |

## 八、风格参数

选定版本：**照片绿荫**（来自用户石榴树照片的青绿天空、叶片绿、枝干棕、石榴红）。

```css
--bg:#eef7ef; --sidebar:#dfead6; --sidebar-text:#3b5d3d; --sidebar-active:#ffffff;
--card:#fffdf8; --text:#29362a; --text-dim:#6f7d6d; --accent:#6b984f; --accent-2:#c85346;
--radius:22px; --shadow:0 18px 50px rgba(38,54,40,.12);
--font:-apple-system,BlinkMacSystemFont,"PingFang SC","Segoe UI",sans-serif;
```

- 品牌 emoji：☀️；工作台名：小彘的工作台；短名称：小彘
- 图标：v27 起固定水彩插画（512+192 PNG），自定义图标功能已下线
- 用户偏好：安卓友好、简单好看、首页减少填写负担

## 九、用户画像与联网配置

- 用户：科研/写论文/读文献；诉求是低压力记录生活、情绪、习惯、成功日记，由 AI 做周/月/年复盘，识别精力高峰、焦虑触发点、边界与个人使用说明
- 隐私敏感度**高**（情绪日记、人际、份子钱等），数据严格本机，不上云
- 希望像手机 App 一样直接用，不懂代码

| 功能 | 服务 | key | 说明 |
|---|---|---|---|
| AI 分析/对话 | OpenAI 兼容接口，默认 DeepSeek，支持千问 | `ai`（`bysdash$secret:`，不进备份） | 用户自填地址/模型/key；只接受 HTTPS |
| 欢迎语/名言 | 同上，可选 | `ai` | 无 key 时用离线内置鼓励语（Wins 金句库 230 句） |
| 天气穿搭 | Open-Meteo + 浏览器定位 | 无 key | 定位失败手动填温/天气 |

平时数据只在本机；点「AI 分析/生成」时相关文本才发给用户配置的 AI 服务商。

## 十、排障备忘（真实踩坑档案，接手前过一遍）

1. **金币「没加」**：先查是否同日同来源已领过或触顶（日上限 10、11 种来源），再怀疑 bug。
2. **习惯删不掉**（v49 根因档案）：启动时「补种默认习惯」曾把删掉的当缺失补回——已改为仅列表首次不存在才种。若复发先查这个逻辑。
3. **密码框弹「保存密码」**（v49 根因档案）：`type=password` 触发 Chrome 密码管理器——用普通 input + `-webkit-text-security:disc`（解锁/AI key/改密三处都是）。
4. **英语 SRS 机制**（已对代码核实）：学完建条目、次日到期；连对 1/2/3 次分别隔 **3/7/14 天**再测，连对 **4 次**进已学库（`english_mastered`）；答错连对清零、当天重排。「今日测试」与复习区已解耦（v52+），测试固定单词 1 道+搭配 1 道。
5. **删代码后白屏**：查多余 `}` 或 `},,` 双逗号——曾两次整页 JS 报错；`node --check` 抽取校验可立刻定位（命令在 AGENTS.md 第 6 节）。
6. **popstate 竞态黑屏**：物理返回由 `UI.openFull` + `history.pushState` 接管，改这块逻辑前先读懂现有实现。
7. **PWA 打开外链黑屏**：用 `Util.openExternal`，不要 `target=_blank`。
8. **SW 括号错**（v27 档案）：fetch handler 多一个 `)` 会让 SW 静默注册失败（安装横幅/角标异常的隐蔽根因），改 sw.js 必做语法校验。
9. **部署后手机不刷新**：三处版本号漏改是最常见翻车点（deploy 脚本现在会校验拦截）；GitHub Pages 构建有 1~2 分钟延迟。

## 十一、我怎么给你提需求（请照这个节奏回）

- 一批发 6–8 条编号需求，常带截图；看到 `@image` 截图要结合 UI 实际判断，别凭空想象。
- 做完按 ① ② ③ 逐项回复，并附「变更摘要 + 线上地址」。
- 小步可验证，每次部署后主动 curl 验版本号。

## 十二、必须守的红线（摘自 AGENTS.md，以 AGENTS.md 为准）

- 版本号三处同步（index.html `BUILD_VERSION` + sw.js `CACHE`/`BUILD`），漏改 = 手机不刷新 = 白部署。
- 旧副本目录（`C:\Users\cheng\WorkBuddy\...`、`D:\WorkBuddy-work\...`）一律不动；只在 canonical 目录改。
- `English.content` 内联 JSON 大数组不要手改大段；小范围替换需明确说明。
- sw.js 缓存策略禁止改回 cache-first（v84/v91 血泪史，详见 AGENTS.md 第 4 节）。
- 不删 .git 历史；不擅自重构整体结构。
- 改完 JS 必做 `node --check` 校验；遇到环境问题无法验证必须说明，不得假装通过。
- v93 起工作区已清理干净：**不要往仓库里新增临时文件/脚本**，历史产物（build 脚本等）已删除，需要时从 git 历史找回。
