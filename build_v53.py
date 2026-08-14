#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v53：6 项反馈修复
  1) 经验摘录文字换行到右半边：让 .note-item 改 column 布局，.grow 占满宽度
  2) 菜篮子更显眼：保留折叠按钮 + 加边框 + 加 N 道菜徽章
  3) 首页桌面转盘点不进做菜栏：去掉 .wheel-mini-box 的 stopPropagation
  4) 份子钱下拉框变窄：让 .row > * 自动平分宽度
  5) 下拉项加 × 删除按钮：扩展 Util.Combo，加 Combo.remove(scope, val)
  6) 英语积累卡片字号统一：4 张卡片 .desc 和 .hint 用统一字号
"""
import io, sys, json

PATH = r'C:\Users\cheng\WorkBuddy\2026-08-12-17-28-08\repo\index.html'

def esc_js(s):
    """Escape a Python string for use inside a JS single-quoted string literal."""
    return s.replace('\\', '\\\\').replace("'", "\\'")

with io.open(PATH, 'r', encoding='utf-8') as f:
    s = f.read()

changes = []
def rep(text, old, new, label):
    n = text.count(old)
    if n == 0:
        print('!! MISS', label)
        sys.exit(1)
    changes.append((label, n))
    return text.replace(old, new, 1)

# 1) 经验摘录：.note-item 改 column 布局
OLD = """.quick-actions{display:flex;flex-wrap:wrap;gap:4px;justify-content:flex-start;margin-top:6px;padding-top:6px;border-top:1px dashed #ece6cf;width:100%}\n/* v52：菜篮子框（整体 dishList 容器）折叠/展开 */"""
NEW = """.quick-actions{display:flex;flex-wrap:wrap;gap:4px;justify-content:flex-start;margin-top:6px;padding-top:6px;border-top:1px dashed #ece6cf;width:100%}\n/* v52：菜篮子框（整体 dishList 容器）折叠/展开 */\n/* v53：经验摘录卡片让 .grow 占满宽度（标题+内容在上，按钮行在下） */\n.note-item{flex-direction:column;align-items:stretch}\n.note-item .grow{width:100%}\n.note-item .quick-actions{justify-content:flex-end;border-top:1px dashed #d8d4be;margin-top:8px;padding-top:8px}\n.note-item .desc{font-size:13px;line-height:1.55}\n.note-item .title{font-size:14px;font-weight:700;line-height:1.4}"""
# careful: there is no \n literal in source, it's two lines
OLD = """.quick-actions{display:flex;flex-wrap:wrap;gap:4px;justify-content:flex-start;margin-top:6px;padding-top:6px;border-top:1px dashed #ece6cf;width:100%}
/* v52：菜篮子框（整体 dishList 容器）折叠/展开 */"""
NEW = """.quick-actions{display:flex;flex-wrap:wrap;gap:4px;justify-content:flex-start;margin-top:6px;padding-top:6px;border-top:1px dashed #ece6cf;width:100%}
/* v52：菜篮子框（整体 dishList 容器）折叠/展开 */
/* v53：经验摘录卡片让 .grow 占满宽度（标题+内容在上，按钮行在下） */
.note-item{flex-direction:column;align-items:stretch}
.note-item .grow{width:100%}
.note-item .quick-actions{justify-content:flex-end;border-top:1px dashed #d8d4be;margin-top:8px;padding-top:8px}
.note-item .desc{font-size:13px;line-height:1.55}
.note-item .title{font-size:14px;font-weight:700;line-height:1.4}"""
s = rep(s, OLD, NEW, '1. notes .note-item column 布局')

# 2) 菜篮子：加边框 + N 道菜徽章
OLD = """.dish-basket-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.dish-basket-toggle{font-size:12px;padding:4px 10px;min-height:30px}
.dish-basket-body.collapsed{display:none}"""
NEW = """.dish-basket-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding-bottom:8px;border-bottom:1px dashed #d8d4be}
.dish-basket-toggle{font-size:12px;padding:5px 12px;min-height:30px}
.dish-basket-body.collapsed{display:none}
/* v53：菜篮子容器加绿色边框和数量徽章，让用户能直接看到 */
.dish-basket-card{border:1px dashed #9bb07f;background:rgba(245,249,239,.55);padding:12px;border-radius:14px}
.dish-basket-card .dish-basket-head h2{display:inline-block;margin:0;font-size:16px;color:#3a4a3f}
.dish-basket-count{display:inline-block;background:#9bb07f;color:#fff;font-size:11px;border-radius:999px;padding:2px 8px;margin-left:8px;font-weight:700;vertical-align:middle}"""
s = rep(s, OLD, NEW, '2a. 菜篮子容器 CSS')

OLD = """<div class="card"><div class="dish-basket-head"><h2 style="display:inline-block;margin:0">我的菜</h2><button class="btn ghost small dish-basket-toggle" onclick="Cooking.toggleBasket()" title="折叠/展开菜篮子" id="dishBasketToggle">折叠 ▾</button></div><div id="dishList" class="dish-basket-body"></div></div>"""
NEW = """<div class="dish-basket-card"><div class="dish-basket-head"><h2>🧺 菜篮子<span id="dishBasketCount" class="dish-basket-count">0</span></h2><button class="btn ghost small dish-basket-toggle" onclick="Cooking.toggleBasket()" title="折叠/展开菜篮子" id="dishBasketToggle">折叠 ▾</button></div><div id="dishList" class="dish-basket-body"></div></div>"""
s = rep(s, OLD, NEW, '2b. 菜篮子 HTML 替换')

# 2c) 让 Cooking.render 写入数量徽章
OLD = """    const toggleBtn = document.getElementById('dishBasketToggle');
    if(toggleBtn){ toggleBtn.textContent = basketOpen ? '折叠 ▾' : '展开 ▸'; }"""
NEW = """    const toggleBtn = document.getElementById('dishBasketToggle');
    if(toggleBtn){ toggleBtn.textContent = basketOpen ? '折叠 ▾' : '展开 ▸'; }
    const basketCount = document.getElementById('dishBasketCount');
    if(basketCount){ basketCount.textContent = this.list().length + ' 道'; }"""
s = rep(s, OLD, NEW, '2c. 菜篮子数量徽章')

# 3) 首页桌面转盘：去掉 stopPropagation 让 wheel-mini 的 onclick 生效
OLD = """if(id==='wheel') return `<div class="wheel-mini" onclick="App.go('cooking')" title="点转盘进入做菜栏"><div class="wheel-mini-box" onclick="event.stopPropagation()"><div class="wheel-mini-pointer"></div><div class="wheel-mini-disk" id="homeWheel"></div><div class="wheel-result-bingo small" id="homeBingo" onclick="event.stopPropagation();App.go('cooking')"></div></div><button class="btn ghost small" id="homeWheelSpin" onclick="event.stopPropagation();Cooking.spin('home')">转一下</button><div class="hint" id="homeSpinResult">—</div></div>`;"""
NEW = """if(id==='wheel') return `<div class="wheel-mini" onclick="App.go('cooking')" title="点转盘进入做菜栏" style="cursor:pointer"><div class="wheel-mini-box"><div class="wheel-mini-pointer"></div><div class="wheel-mini-disk" id="homeWheel"></div><div class="wheel-result-bingo small" id="homeBingo"></div></div><button class="btn ghost small" id="homeWheelSpin" onclick="event.stopPropagation();Cooking.spin('home')">转一下</button><div class="hint" id="homeSpinResult">—</div></div>`;"""
s = rep(s, OLD, NEW, '3a. 主页转盘 stopPropagation 移除')

# 3b) bingo show 时仍可点击进做菜（避免「要转出结果才能点进」）
OLD = """.wheel-result-bingo.show{opacity:1;pointer-events:auto;transform:translate(-50%,-50%) scale(1)}"""
NEW = """.wheel-result-bingo.show{opacity:1;pointer-events:auto;transform:translate(-50%,-50%) scale(1);cursor:pointer}"""
s = rep(s, OLD, NEW, '3b. bingo 指针')

# 4) 份子钱：.row > * 自动 flex:1
OLD = """.row{display:flex;gap:8px;align-items:center}
.row.wrap{flex-wrap:wrap}"""
NEW = """.row{display:flex;gap:8px;align-items:center}
.row.wrap{flex-wrap:wrap}
/* v53：.row 内子元素若没显式宽度，自动平分（避免份子钱金额/日期被挤到像素宽） */
.row > *{min-width:0;flex:1 1 0}"""
s = rep(s, OLD, NEW, '4. .row 平分宽度')

# 4b) dishTags 也成 row 形式（display:flex 但 gap:0），让标签输入框平分
OLD = """        <div style="display:flex;gap:0"><input id="dishTags" placeholder="标签，如：快手菜 / 晚饭 / 清淡"><button type="button" class="combo-toggle" onclick="Util.Combo.open('dishTags','dish_tags',event)" title="选已有标签">▾</button></div>"""
NEW = """        <div style="display:flex;gap:0"><input id="dishTags" placeholder="标签，如：快手菜 / 晚饭 / 清淡" style="flex:1;border-radius:8px 0 0 8px"><button type="button" class="combo-toggle" onclick="Util.Combo.open('dishTags','dish_tags',event)" title="选已有标签">▾</button></div>"""
s = rep(s, OLD, NEW, '4b. dishTags input flex:1')

# 5) 下拉项 ×：Util.Combo 加删除按钮 + remove 方法
# 注意：scope 是用户输入的，不能直接拼到 onclick 里，所以要预先 JSON 序列化
OLD = """    if(!opts.length){
      pop.innerHTML = '<div class="combo-empty">还没有候选，先在上面输入一个试试</div>';
    } else {
      pop.innerHTML = '<div class="combo-tip">点击下方候选 → 自动填入</div>' +
        opts.map(o=>`<div class="combo-item" data-val="${Util.esc(o)}">${Util.esc(o)}</div>`).join('');
    }"""
NEW = """    if(!opts.length){
      pop.innerHTML = '<div class="combo-empty">还没有候选，先在上面输入一个试试</div>';
    } else {
      /* v53：每条候选右侧加 × 按钮（点击从历史池删除该词） */
      pop.innerHTML = '<div class="combo-tip">点击下方候选 → 自动填入 · 右侧 × 删除</div>' +
        opts.map(o=>`<div class="combo-item" data-val="${Util.esc(o)}" onclick="event.stopPropagation()"><span class="combo-item-text">${Util.esc(o)}</span><button type="button" class="combo-item-del" onclick="event.stopPropagation();Util.Combo.remove('${esc_js(scope)}','${esc_js(o)}',this)" title="从候选池删除这条">×</button></div>`).join('');
    }"""
s = rep(s, OLD, NEW, '5a. Combo pop 添加 ×')

# 5b) 加 Combo.remove 实现（黑名单方式：值写入 combo_removed_<scope>，_collect 过滤）
OLD = """  _pick(input, v){
    const cur = input.value.trim();
    if(!cur){ input.value = v; }"""
NEW = """  /* v53：从候选池删除一个值（黑名单方式：值加入 combo_removed_<scope>，下次 _collect 自动过滤） */
  remove(scope, val, btn){
    if(!confirm('要从「'+scope+'」候选里永久删除「'+val+'」吗？')) return;
    const k = 'combo_removed_'+scope;
    const cur = Store.get(k, []);
    if(!cur.includes(val)) Store.set(k, [...cur, val]);
    if(btn){
      const item = btn.closest('.combo-item');
      if(item){
        item.style.transition = 'opacity .2s, transform .2s';
        item.style.opacity = '0.3';
        item.style.transform = 'translateX(8px)';
        setTimeout(()=>{ item.remove(); if(!this._pop.querySelector('.combo-item')){ this.close(); UI.toast('已删除，可重新输入'); } }, 220);
      }
    } else {
      this.close();
      UI.toast('已删除');
    }
  },
  _pick(input, v){
    const cur = input.value.trim();
    if(!cur){ input.value = v; }"""
s = rep(s, OLD, NEW, '5b. Combo.remove 实现')

# 5c) _collect 过滤黑名单
OLD = """  _collect(scope){
    let items = [];
    if(scope === 'note_tags') items = Notes.list().flatMap(x => Notes.splitTags(x.tags));
    else if(scope === 'note_keywords') items = Notes.list().flatMap(x => Notes.splitTags(x.keywords));
    else if(scope === 'dish_tags') items = Cooking.list().flatMap(x => Cooking.splitTag(x.tags));
    else if(scope === 'gift_person') items = Gift.list().map(x => x.person);
    else if(scope === 'gift_event') items = Gift.list().map(x => x.event);
    const unique = [...new Set(items.filter(Boolean))];
    return Util.byUse(scope, unique).slice(0, 12);
  }"""
NEW = """  _collect(scope){
    let items = [];
    if(scope === 'note_tags') items = Notes.list().flatMap(x => Notes.splitTags(x.tags));
    else if(scope === 'note_keywords') items = Notes.list().flatMap(x => Notes.splitTags(x.keywords));
    else if(scope === 'dish_tags') items = Cooking.list().flatMap(x => Cooking.splitTag(x.tags));
    else if(scope === 'gift_person') items = Gift.list().map(x => x.person);
    else if(scope === 'gift_event') items = Gift.list().map(x => x.event);
    /* v53：过滤掉用户已删除的候选（黑名单） */
    const removed = new Set(Store.get('combo_removed_'+scope, []));
    const unique = [...new Set(items.filter(Boolean))].filter(x => !removed.has(x));
    return Util.byUse(scope, unique).slice(0, 12);
  }"""
s = rep(s, OLD, NEW, '5c. Combo._collect 过滤黑名单')

# 5d) Combo 弹层点击分流
OLD = """    pop.onclick = (e) => {
      const it = e.target.closest('.combo-item');
      if(!it) return;
      this._pick(input, it.dataset.val);
      this.close();
      input.focus();
    };"""
NEW = """    pop.onclick = (e) => {
      if(e.target.closest('.combo-item-del')) return;  /* × 自己处理 */
      const it = e.target.closest('.combo-item');
      if(!it) return;
      this._pick(input, it.dataset.val);
      this.close();
      input.focus();
    };"""
s = rep(s, OLD, NEW, '5d. Combo 点击分流')

# 5e) × 按钮样式
OLD = """.combo-item{padding:9px 12px;font-size:14px;cursor:pointer;line-height:1.3;border-bottom:1px solid transparent}
.combo-item:hover,.combo-item:active{background:#f3f5ef}"""
NEW = """.combo-item{padding:9px 12px;font-size:14px;cursor:pointer;line-height:1.3;border-bottom:1px solid transparent;display:flex;align-items:center;gap:8px}
.combo-item-text{flex:1;word-break:break-word}
.combo-item-del{border:0;background:transparent;color:var(--text-dim);font-size:18px;line-height:1;padding:2px 6px;cursor:pointer;border-radius:6px;opacity:.6;flex:none}
.combo-item-del:hover{background:#f3d0cd;color:#c85346;opacity:1}
.combo-item:hover,.combo-item:active{background:#f3f5ef}"""
s = rep(s, OLD, NEW, '5e. Combo × 样式')

# 6) 英语卡片字体统一
OLD = """    englishCards.innerHTML=[
      `<div class=\"card\"><h2>💬 每日一句</h2><div class=\"desc\">${Util.esc(d.quote)}<br><span style=\"color:var(--text-dim)\">${Util.esc(d.quoteZh)}</span></div>${doneFn('每日一句')?'<div style=\"margin-top:10px;color:var(--accent);font-weight:700;font-size:13px\">✅ 已完成</div>':`<div style=\"display:flex;gap:6px;margin-top:10px\"><button class=\"btn small\" onclick=\"English.playQuote()\" title=\"朗读\">🔊</button><button class=\"btn small ghost\" onclick=\"English.done('每日一句')\">完成学习</button></div>`}</div>`,
      `<div class=\"card\"><h2>🔤 每日单词</h2><div class=\"desc\">${Util.esc(d.word)}<br>${Util.esc(d.wordZh)}</div><div class=\"hint\" style=\"margin-top:6px\">例句：${Util.esc(d.example||'')}</div>${doneFn('每日单词')?'<div style=\"margin-top:10px;color:var(--accent);font-weight:700;font-size:13px\">✅ 已完成</div>':`<button class=\"btn small\" style=\"margin-top:10px\" onclick=\"English.done('每日单词')\">完成学习</button>`}</div>`,
      `<div class=\"card\"><h2>🧩 固定搭配</h2><div class=\"desc\">${Util.esc(d.phrase)} · ${Util.esc(d.phraseZh)}</div>${d.phraseEx?`<div class=\"hint\" style=\"margin-top:6px\">例句：${Util.esc(d.phraseEx)}</div>`:''}${doneFn('固定搭配')?'<div style=\"margin-top:10px;color:var(--accent);font-weight:700;font-size:13px\">✅ 已完成</div>':`<button class=\"btn small\" style=\"margin-top:10px\" onclick=\"English.done('固定搭配')\">完成学习</button>`}</div>`,
      `<div class=\"card\"><h2>🗣️ 每日对话</h2><div class=\"desc\">${Util.esc(d.dialog).replace(/\\n/g,'<br>')}<br><span style=\"color:var(--text-dim)\">${Util.esc(d.dialogZh).replace(/\\n/g,'<br>')}</span></div>${doneFn('每日对话')?'<div style=\"margin-top:10px;color:var(--accent);font-weight:700;font-size:13px\">✅ 已完成</div>':`<div style=\"display:flex;gap:6px;margin-top:10px\"><button class=\"btn small\" onclick=\"English.playDialog()\" title=\"朗读对话\">🔊</button><button class=\"btn small ghost\" onclick=\"English.done('每日对话')\">完成学习</button></div>`}</div>`
    ].join('');"""
NEW = """    /* v53：4 张卡片字号/小字/按钮位置全部统一（主内容 14px、中文释义 13px、辅助例句 12px） */
    const engMain = (txt) => `<div class="eng-main">${txt}</div>`;
    const engZh = (txt) => `<div class="eng-zh">${txt}</div>`;
    const engEx = (txt) => `<div class="eng-ex">例句：${txt}</div>`;
    const engDone = () => '<div class="eng-done">✅ 已完成</div>';
    const engActs = (btns) => `<div class="eng-acts">${btns}</div>`;
    englishCards.innerHTML=[
      `<div class=\"card\"><h2>💬 每日一句</h2>${engMain(Util.esc(d.quote))}${engZh(Util.esc(d.quoteZh))}${doneFn('每日一句')?engDone():engActs(`<button class=\"btn small\" onclick=\"English.playQuote()\" title=\"朗读\">🔊</button><button class=\"btn small ghost\" onclick=\"English.done('每日一句')\">完成学习</button>`)}</div>`,
      `<div class=\"card\"><h2>🔤 每日单词</h2>${engMain(Util.esc(d.word))}${engZh(Util.esc(d.wordZh))}${d.example?engEx(Util.esc(d.example)):''}${doneFn('每日单词')?engDone():`<button class=\"btn small eng-finish\" onclick=\"English.done('每日单词')\">完成学习</button>`}</div>`,
      `<div class=\"card\"><h2>🧩 固定搭配</h2>${engMain(Util.esc(d.phrase)+' · '+Util.esc(d.phraseZh))}${d.phraseEx?engEx(Util.esc(d.phraseEx)):''}${doneFn('固定搭配')?engDone():`<button class=\"btn small eng-finish\" onclick=\"English.done('固定搭配')\">完成学习</button>`}</div>`,
      `<div class=\"card\"><h2>🗣️ 每日对话</h2>${engMain(Util.esc(d.dialog).replace(/\\n/g,'<br>'))}${engZh(Util.esc(d.dialogZh).replace(/\\n/g,'<br>'))}${doneFn('每日对话')?engDone():engActs(`<button class=\"btn small\" onclick=\"English.playDialog()\" title=\"朗读对话\">🔊</button><button class=\"btn small ghost\" onclick=\"English.done('每日对话')\">完成学习</button>`)}</div>`
    ].join('');"""
s = rep(s, OLD, NEW, '6a. 英语 4 卡 HTML 统一')

# 6b) 英语卡片统一样式
OLD = """.card h2{font-family:var(--title-font);font-size:17px;margin-bottom:10px}"""
NEW = """.card h2{font-family:var(--title-font);font-size:17px;margin-bottom:10px}
/* v53：英语积累 4 张卡片统一字号 */
.eng-main{font-size:14px;line-height:1.5;font-weight:600;color:var(--text);word-break:break-word}
.eng-zh{font-size:13px;line-height:1.55;color:var(--text-dim);margin-top:4px;word-break:break-word}
.eng-ex{font-size:12px;line-height:1.5;color:var(--text-dim);margin-top:6px;background:rgba(0,0,0,.03);padding:8px 10px;border-radius:8px;word-break:break-word}
.eng-done{margin-top:10px;color:var(--accent);font-weight:700;font-size:13px}
.eng-acts{display:flex;gap:6px;margin-top:10px}
.eng-finish{margin-top:10px}"""
s = rep(s, OLD, NEW, '6b. 英语卡片 CSS 统一')

# 升级版本号到 v53
s = rep(s, "const BUILD_VERSION = '2026-08-14-v52';", "const BUILD_VERSION = '2026-08-14-v53';", 'BUMP index BUILD_VERSION v53')

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(s)

print(f'OK: {len(changes)} 处替换落盘')
for label, n in changes:
    print(f'  - {label}: {n}')
