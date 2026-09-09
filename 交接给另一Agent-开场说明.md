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

- **v135（2026-09-09 备份误报/体积膨胀+文案收尾——修「写入失败却已保存」、缩略图翻倍、文件名/文案/存储显示全套）**：针对 APK 真机反馈逐项修。①**导出/备份排除 `:thumb` 缩略图（修体积膨胀根因）**：`Media.exportAll()` 和 `NativeBackup.streamBackup()` 的媒体列表都过滤掉 `:thumb` 键——缩略图可从原图重建、随原图一起进大仓库，此前它被一起打包进备份导致文件翻倍（用户「导入 103M 后重存变 154M」的根因）；`mediaCount` 也随之指向「仅原件」的准确数字。②**备份文件名带日期时间戳并按名倒序**：`AutoBackup.fileName()` 改为 `小彘的工作台-备份-YYYYMMDD-HHMMSS.json`（新增 `Util.stamp()`），`fullName()` 同步；桌面恢复 `restore()` 改为读已选文件夹里的**最新一份**（新增 `AutoBackup.latestBackupName(dir)` 扫描 `小彘...-备份-*.json` 取字典序最大）。③**修「写入失败却已保存」误报 + 真实错误透出**：`BackupSavePlugin.promote()` 转正成功后的删 `.prev` 收尾改成 `safeDelete()`（全 try/catch 永不抛），绝不让「转正成功后的清理异常」误报成「写入失败」；`NativeBackup` 增 `lastErr`，`streamBackup` 失败时记下原生 reject 的 message，`runNow`/`exportFull` 的 toast 改为透出真实原因（`写入失败：<原文>`），再遇失败用户/开发者能一眼看到卡点。④**文案**：设置卡「备份与导出」→「导出与导入」，「恢复」按钮→「导入」，「本机大仓库（IndexedDB）」→「本机存储（数据只存在这台设备）」，删除「无 5 MB 限制」行。⑤**存储空间显示去掉误导**：`renderStorage` 不再掺入 `navigator.storage.estimate()` 的「浏览器可用 200GB」（APK 是应用不占浏览器配额），改只显示本应用真实用量（文字+媒体 KB/MB + 文件数），进度条以 2GB 作参考上限（纯提示）。⑥**「清理残留」说明写清**：卡片标注「只删除不再被任何记录引用的旧图片/视频；你的文字记录和正在使用的图片都不会被删」。⑦**排查「导入后保存位置被改成导入路径」**：确认 `autoBackup.dirUri/dirName` 只在 `pickFolder()` 写，`Backup.importFile/importFull` 全程不碰它（见下「未变项」）。语法校验通过；版本三处同步 `2026-09-09-v135`；release APK 已重打并解包验：内置 v135、sw cache v135、「导出与导入」与 `:thumb` 逻辑生效、dex 含 `BackupSavePlugin.safeDelete`（原生改动已编入）。

- **⚠️ v135 需要真机复测的两点（本轮代码已加固但无真机无法 100% 确认根因）**：①真机「点立即备份提示写入失败但文件其实已在」——原生已把「转正成功后清理」改为永不抛异常，并让失败 toast 显示原生真实 message。**请用户装新 APK 后复测：若仍报失败，务必截图 toast 里的具体 error message**（现在已透出本地文件系统的确切原因），据此可精确定位。②「导入后保存位置被改为导入路径」——代码里导入不写保存位置配置；若复现，请用户确认：是在「设置→导入」后看到「保存位置」那个栏变了，还是只是系统文件选择器默认停留在上次导入的文件夹（后者是 Android 系统行为、非本应用改动）。两者处理方式不同。

- **v134（2026-09-09 按审计意见给备份画上句号——导出已流式可靠，新增 100MB 级导入流式化 + 失败如实反馈 + 原生转正保旧备份）**：按审计结论（当前 APK 确实是 v132、v133 导入仍是整读、原生转正先删旧文件不安全、写入用静态变量）逐项收口。①**导出完整性头**：`streamBackup` 顶层加 `"format":"xiaozhi-backup-v2"` + `mediaCount`（每媒体逐个 count，与旧格式/旧备份完全兼容，额外字段不影响导入）；仍保持「文字一次写 + 媒体逐个 base64 分块追加 + ]} 收尾」的流式单 JSON，JS 内存峰值仍只占单个文件。②**大文件导入流式化（修高风险「100MB 整文件 JSON.parse 撑爆 WebView」）**：`Backup.importFile` 按文件大小分路——≤20MB 走原快速整读路径；>20MB 走新增 `Backup.importFull(f)`：**纯 JS 字节级扫描**（`File.slice`+`FileReader.readAsArrayBuffer`+`TextDecoder`）定位顶层 `"media":[` 与每个媒体对象的字节区间（不建整包大字符串、内存 O(1)），头部文字一次性 `Store.importAll`，媒体逐个「读区间→解码→写回大仓库→释放」，内存上限 = 最大单个媒体。恢复结果用 `Media.restore` 的 `{ok,fail}` 如实反馈：有失败会 `alert` 报数量，不再盲目「恢复成功」。③**原生临时文件安全转正（修高风险「先删旧再改名，转正失败丢备份」）**：`BackupSavePlugin.promote()` 改为——先试直接 `rename(.part→正式)`；provider 不支持覆盖时，把旧备份挪成 `.prev` 再转正，转正失败则把 `.prev` 挪回恢复旧备份，全部成功才删 `.prev`。任何分支旧的正式备份都不被提前删除。④**写入会话改实例字段 + 显式关闭（修中风险「static 全局 writer」）**：去掉 `static currentWriter/currentKey`，改为实例字段，换 `dir/file`、出错、写结束时都 `closeWriteSession()`（同时关 `OutputStreamWriter` 与 `ParcelFileDescriptor` 句柄），残留 `.part` 下次以 `"w"` 截断自愈。⑤**Emoji 分块（风险 3）与恢复计数（风险 5）核实**：分块早已按码点边界切（`streamBackup` 的 4788 行逻辑），本轮未动；`Media.restore` 早已返回 `{ok,fail}`，本轮把 `importFile` 的反馈接上了它。网页端语法校验通过；版本三处同步 `2026-09-09-v134`。**真机恢复入口走文件选择器（`importFile` 拿 JS File）而非 SAF 目录，故导入流式化做在纯 JS 侧**（原生 `readNextMedia` 无法接到文件选择器，已撤回，原生插件只留 `pickFolder`+`writeChunk`，保持无死代码）。release APK `keystore-release/拾光手账-v134-release.apk`（解包验内含 v134、`BackupSave` 插件、安全转正逻辑）。

- **v133（2026-09-09 原生备份落地——「设置一次保存路径，之后直接保存，不再每次选」）**：本轮把 v132 的「选文件夹/立即备份闪退」从根上解决。①**选文件夹不再误触备份**：`AutoBackup.pickFolder()` 手机端只调 `NativeBackup.pickFolder()`（Android `ACTION_OPEN_DOCUMENT_TREE` 选任意文件夹 + `takePersistableUriPermission` 长期记住授权），持久化为 `cfg.dirUri/dirName`，绝不在此触发 `exportFull`。②**备份改为流式单 JSON 直写，不再弹分享面板 / 不再在 JS 里拼整包大字符串**：新增原生插件 `BackupSavePlugin.java`（`android/app/.../cn/xiaozhi/workbench/`,已注册进 `MainActivity`，`build.gradle` 加 `androidx.documentfile`）。`NativeBackup.streamBackup(dir, fileName)` 采用**流式拼接**：文字一次写入（`Store.exportAll` 去尾 `}` 拼 `,"media":[`），然后**每个媒体「读一个 base64→单条记录分块追加→随即释放」**，最后 `]}` 收尾——全程 JS 内存峰值只占一两个文件大小，**绝不把 100MB 整包一次性 stringify**（那是手机 WebView 被打爆的根因）。每块 512KB 逐块 `writeChunk` 跨桥（避开整段大 JSON 一次性过桥），原生侧先写 `.part` 临时文件、最后一块原子转正，避免留半个坏文件。**文件仍是单 JSON、仍可导入，与网页端格式完全一致**。手机端 `runNow`：未设 `dirUri` → 提示先「选择保存位置」；已设 → `streamBackup` 直写，成功后记 `lastMonth`。**月度提醒 `check()` 直接复用 `runNow`**：已设路径就静默直写，不再弹选位置。③**删「360 云盘同步」冗余**：去掉桌面同步文件夹里的「历史副本 + 分类原图」导出（`historyName/historyDir/exportMediaFolders` 已删），备份只写一份「小彘的工作台-备份.json」，符合"只要设个路径能备份"。④**修复两个失效的 `NativeBackup.shareFile` 调用**（该函数从未定义，手机上调用必抛错静默失败）：`runNow` 原生分支改为直接走 `dirUri` 直写；`Backup.exportFull` 手机端如已设路径→`streamBackup` 流式写，未设→提示先设路径。⑤**设置文案精简**：卡片改名「备份到文件夹」，说明压成一句（先选一次位置，之后立即备份/每月提醒都直接写进该文件夹），开关去掉独立「保存」按钮改内联 `onchange`. 版本三处同步 `2026-09-09-v133`。**需重新打包 APK 才能让手机端吃到 v133**（网页侧已改好、语法校验通过；原生插件/Settings 文案/分块写入均已就绪）。

> v132 ~ v134 历史见 git 提交记录，本文档只保留最近三轮。

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
