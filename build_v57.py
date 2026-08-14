#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v57 patch: 菜篮子/经验摘录详情/欢迎页/默认首页"""

import io, re, sys

PATH = r'C:\Users\cheng\WorkBuddy\2026-08-12-17-28-08\repo\index.html'

with io.open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

def assert_once(name, content, needle, n_expected):
    cnt = content.count(needle)
    if cnt != n_expected:
        print(f'ABORT: {name} expected {n_expected} hits, got {cnt}')
        print('--- first 200 chars of needle ---')
        print(needle[:200])
        sys.exit(1)

# ------------------------------------------------------------------
# 1) 菜篮子卡片：照灵感小卡模板做（column 布局，文字在上、按钮在下、保留编辑+删除，移除 ↑↓）
# ------------------------------------------------------------------
old_dish = (
    '    /* v51 菜品折叠：默认收起只显示菜名 + ▾ 展开按钮 */\n'
    '    const recipeHtml = Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="list">${rows.map((x)=>{ const i=dishRecipes.findIndex(y=>y.id===x.id); return `<div class="item dish-item${x._open?\' open\':\'\'}" draggable="true" data-sort-id="${x.id}">${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class="thumb" src="${Util.esc(x.photo)}" alt="">`:\'\')}<div class="grow"><div class="dish-name">${Util.esc(x.name)}</div>${x.tags?`<div class="dish-meta">${Util.esc(x.tags)}</div>`:\'\'}<div class="dish-steps">${Util.esc(x.steps||\'\')}</div></div><button class="del dish-toggle" onclick="Cooking.toggleOpen(\'${x.id}\')" title="展开/收起">▾</button><button class="del" onclick="Cooking.move(${i},-1)">↑</button><button class="del" onclick="Cooking.move(${i},1)">↓</button><button class="del" onclick="Cooking.del(\'${x.id}\')">✕</button></div>`; }).join(\'\')}</div></section>`).join(\'\'):\'\';'
)

new_dish = (
    '    /* v57：按 Quick/Notes 灵感小卡模板重构 —— 图片缩略图 + 菜名/标签/步骤整行在上，按钮 ✎ / ✕ 在下方一行；移除 ↑↓；长按拖动排序 */\n'
    '    const recipeHtml = Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="list">${rows.map((x)=>{ const i=dishRecipes.findIndex(y=>y.id===x.id); return `<div class="item dish-basket-card-item${x._open?\' open\':\'\'}" draggable="true" data-sort-id="${x.id}">${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class="thumb" src="${Util.esc(x.photo)}" alt="">`:\'\')}<div class="grow"><div class="title">${Util.esc(x.name)}</div>${x.tags?`<div class="dish-meta">${Util.esc(x.tags)}</div>`:\'\'}<div class="dish-steps">${Util.esc(x.steps||\'\')}</div></div><div class="dish-foot"><button class="btn ghost small" onclick="Cooking.edit(\'${x.id}\')" title="编辑这道菜">✎ 编辑</button><button class="del small" onclick="Cooking.del(\'${x.id}\')" title="删除">✕</button></div></div>`; }).join(\'\')}</div></section>`).join(\'\'):\'\';'
)

assert_once('dish-card old', html, old_dish, 1)
html = html.replace(old_dish, new_dish)
print('[1] dish card template updated')

# add Cooking.edit (jump to top, prefill form) if not present
ed_old = 'del(id){ Store.set(\'dishes\',this.list().filter(x=>x.id!==id)); this.render(); UI.toast(\'已删除\'); }'
ed_repl = (
    ed_old + ',\n'
    '  /* v57：菜篮子卡片点 ✎ 编辑 → 滚到顶部表单并预填（与 Quick.editStart 一致） */\n'
    '  edit(id){\n'
    '    const it=this.list().find(x=>x.id===id); if(!it) return;\n'
    '    Store.set(\'dish_editing\', id);\n'
    '    if(dishName) dishName.value = it.name || \'\';\n'
    '    if(dishTags) dishTags.value = it.tags || \'\';\n'
    '    if(dishSteps) dishSteps.value = it.steps || \'\';\n'
    '    this.render();\n'
    '    document.getElementById(\'page-cooking\')?.scrollIntoView?.({behavior:\'smooth\', block:\'start\'});\n'
    '    setTimeout(()=>{ document.getElementById(\'dishName\')?.focus(); }, 200);\n'
    '    UI.toast(\'正在编辑：\'+(it.name||\'这道菜\'));\n'
    '  },'
)
# remove existing trailing comma if any
if ed_old in html and 'edit(id){' not in html[max(0,html.find(ed_old)-500):html.find(ed_old)+500]:
    html = html.replace(ed_old, ed_repl)
    print('[1.5] Cooking.edit added')
else:
    print('[1.5] skip: Cooking.edit already present or block not found')

# remove the move() call references (kept internal for old code). Just stub move so callers don't break.
mv_old = '  move(i,d){ const a=this.list(); const j=i+d; if(j<0||j>=a.length)return; [a[i],a[j]]=[a[j],a[i]]; Store.set(\'dishes\',a); this.render(); },'
mv_new = '  /* v57：菜篮子卡片不再有 ↑↓ 按钮，改成长按拖动排序（DragSort.bind）；保留 move() 以防有老链接误点。 */\n  move(i,d){ UI.toast(\'菜篮子已改为长按拖动排序，不再有 ↑↓\'); },'
assert_once('move stub', html, mv_old, 1)
html = html.replace(mv_old, mv_new)
print('[1.6] Cooking.move stubbed (long-press drag instead)')

# 把 PhotoId 图片的卡片样式切换 - 在 CSS 里加规则
css_dish_old = '.dish-item{... 现有}'
# 我们直接 patch CSS 加 .dish-basket-card-item 规则
css_anchor = '.dish-item .dish-name{font-size:13px;font-weight:600;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
css_add = (
    css_anchor + '\n'
    '/* v57：菜篮子小卡按 Quick/Notes 灵感小卡模板 —— column 布局、图片正方小缩略图、文字整行在上、按钮在下面 */\n'
    '.dish-basket-card-item{flex-direction:column;align-items:stretch;padding:10px}\n'
    '.dish-basket-card-item .thumb{width:64px;height:64px;object-fit:cover;border-radius:8px;margin:0 auto 6px}\n'
    '.dish-basket-card-item .grow{width:100%;text-align:left}\n'
    '.dish-basket-card-item .title{font-size:14px;font-weight:700;line-height:1.4;margin-bottom:2px}\n'
    '.dish-basket-card-item .dish-meta{font-size:11px;color:var(--text-dim);margin-top:2px}\n'
    '.dish-basket-card-item .dish-steps{font-size:12px;color:var(--text);line-height:1.6;margin-top:4px;white-space:pre-wrap;word-break:break-word;max-height:120px;overflow:hidden}\n'
    '.dish-basket-card-item .dish-foot{display:flex;justify-content:space-between;align-items:center;margin-top:8px;padding-top:6px;border-top:1px dashed #d8d4be}\n'
    '.dish-basket-card-item .dish-foot .btn.ghost{font-size:12px;padding:4px 10px;min-height:28px}\n'
    '.dish-basket-card-item .del.small{font-size:13px;padding:4px 8px;min-height:28px}'
)
assert_once('css dish anchor', html, css_anchor, 1)
html = html.replace(css_anchor, css_add)
print('[1.7] CSS dish-basket-card-item added')

# ------------------------------------------------------------------
# 2) 经验摘录：openDetail 改成"全屏 = 编辑模式"自动保存
#    ✕ 关闭键在 UI.openFull 里去掉（用户不喜欢）；右下角加 🖼 插入图片
# ------------------------------------------------------------------
op_old = (
    '  /* v55：单条详情改用全屏（替代之前 UI.modal 弹窗）。v56：去掉右下角删除键（防误触，删除移到小卡长按）；\n'
    '     编辑改为在当前全屏内联进行，不再跳回初始页。 */\n'
    '  openDetail(id){\n'
    '    const it = this.list().find(x=>x.id===id); if(!it) return;\n'
    '    const title = it.title || Util.firstSentence(this._stripMedia(it.text)) || \'（无标题）\';\n'
    '    UI.openFull(\'📝 \'+title, `<div id="noteDetailInner"></div>`, \'← 返回\');\n'
    '    this._paintDetail(id);\n'
    '  },'
)
op_new = (
    '  /* v57：详情 = 全屏纯文本编辑。无标题/分类/标签输入框、无保存/取消按钮 —— 默认自动保存；\n'
    '     右下角 🖼 插入图片（带文字说明）。删除另放在小卡长按浮出的红色 ✕。 */\n'
    '  openDetail(id){\n'
    '    const it = this.list().find(x=>x.id===id); if(!it) return;\n'
    '    const title = it.title || Util.firstSentence(this._stripMedia(it.text)) || \'（无标题）\';\n'
    '    UI.openFull(\'📝 \'+title, `\n'
    '      <div class="note-edit-pure">\n'
    '        <textarea id="noteEditPure" placeholder="写下你的经验、原则、观察..."></textarea>\n'
    '        <div class="row" style="margin-top:10px;align-items:center"><span class="hint" id="noteEditPureCount"></span><button class="btn-fab-insert" type="button" onclick="document.getElementById(\'noteEditPureFile\').click()" title="插入图片">🖼 插入图片</button></div>\n'
    '      </div>\n'
    '      <input type="file" id="noteEditPureFile" accept="image/*" multiple style="display:none" onchange="Notes.insertImages(this,\'noteEditPure\');Notes._autoSaveEdit()">\n'
    '    `, \'← 返回\');\n'
    '    const ta = document.getElementById(\'noteEditPure\'); if(!ta) return;\n'
    '    ta.value = it.text || \'\';\n'
    '    /* 自动保存：失焦 600ms / 退栈时保存 */\n'
    '    let timer = null;\n'
    '    ta.addEventListener(\'input\', ()=>{\n'
    '      clearTimeout(timer);\n'
    '      timer = setTimeout(()=>Notes._autoSaveEdit(), 600);\n'
    '      const ids = (ta.value.match(/\\[img:m_[a-zA-Z0-9_]+\\]/g) || []).length;\n'
    '      const cs = document.getElementById(\'noteEditPureCount\');\n'
    '      if(cs) cs.textContent = ids?(\'已插入 \'+ids+\' 张图\'):\'\';\n'
    '    });\n'
    '    /* 退栈时强制刷一次：UI.openFull 把 onBack 存在 box._onBack */\n'
    '    const box = document.getElementById(\'uiFullBox\');\n'
    '    if(box){\n'
    '      const oldBack = box._onBack;\n'
    '      box._onBack = ()=>{ try{ Notes._autoSaveEdit(); }catch(e){} if(typeof oldBack === \'function\'){ try{ oldBack(); }catch(e){} } };\n'
    '    }\n'
    '    /* 初始化计数 */\n'
    '    const ids = (ta.value.match(/\\[img:m_[a-zA-Z0-9_]+\\]/g) || []).length;\n'
    '    const cs = document.getElementById(\'noteEditPureCount\'); if(cs) cs.textContent = ids?(\'已插入 \'+ids+\' 张图\'):\'\';\n'
    '    setTimeout(()=>ta.focus(), 60);\n'
    '    /* id 暂存，供 _autoSaveEdit 用 */\n'
    '    this._fsEditingId = id;\n'
    '  },\n'
    '  /* v57：详情全屏自动保存 —— 用上次记录到的 _fsEditingId，把 text 写回 notes */\n'
    '  _autoSaveEdit(){\n'
    '    const id = this._fsEditingId;\n'
    '    const ta = document.getElementById(\'noteEditPure\');\n'
    '    if(!id || !ta) return;\n'
    '    const text = ta.value;\n'
    '    const textNoMedia = String(text||\'\').replace(/\\[img:m_[a-zA-Z0-9_]+\\]/g,\'\').trim();\n'
    '    const title = Util.firstSentence(textNoMedia);\n'
    '    const list = this.list();\n'
    '    const idx = list.findIndex(x=>x.id===id);\n'
    '    if(idx<0) return;\n'
    '    if(!title && !textNoMedia){\n'
    '      /* 空内容：等价于删除这条（用户退栈后再撤太烦） */\n'
    '      Store.set(\'notes\', list.filter(x=>x.id!==id));\n'
    '      this.render();\n'
    '      if(this._fsMode) this._renderOpenGrid();\n'
    '      return;\n'
    '    }\n'
    '    list[idx] = {...list[idx], text, title: list[idx].title || title, updatedAt:new Date().toISOString()};\n'
    '    Store.set(\'notes\', list);\n'
    '  },'
)
assert_once('Notes.openDetail old', html, op_old, 1)
html = html.replace(op_old, op_new)
print('[2] Notes.openDetail rewritten (pure edit mode + auto-save)')

# 旧的 _paintDetail / editInFull / saveEditInFull 都作废，简化处理：保留 _paintDetail 做只读预览（左滑回上层时显示），但用户已选择直接编辑，所以让 _paintDetail 跳到 openDetail
pd_old = (
    '  /* 详情内容绘制（openDetail 与保存后复用，不重新入栈） */\n'
    '  _paintDetail(id){\n'
    '    const root = document.getElementById(\'noteDetailInner\'); if(!root) return;\n'
    '    const it = this.list().find(x=>x.id===id); if(!it) return;\n'
    '    const title = it.title || Util.firstSentence(this._stripMedia(it.text)) || \'（无标题）\';\n'
    '    const textHtml = this._renderTextWithMedia(it.text || \'\');\n'
    '    const meta = [it.cat?\'# \'+it.cat:\'\', it.tags?\'🔖 \'+it.tags:\'\', it.date].filter(Boolean).join(\'　\');\n'
    '    root.innerHTML = `\n'
    '      <div class="note-detail-text">${textHtml}</div>\n'
    '      <div class="note-detail-meta">${Util.esc(meta)}</div>\n'
    '      <div class="note-cat-actions">\n'
    '        <button class="btn ghost small" onclick="Notes.copy(\'${id}\')">⧉ 复制全文</button>\n'
    '        <button class="btn small" onclick="Notes.editInFull(\'${id}\')">✎ 编辑</button>\n'
    '      </div>`;\n'
    '    const t = document.getElementById(\'uiFullTitle\'); if(t) t.textContent = \'📝 \'+title;\n'
    '    Media.paint(root);\n'
    '  },'
)
pd_new = (
    '  /* v57：老 _paintDetail 已被 openDetail 取代为「纯编辑模式」。保留同名空函数以防老调用，但内容跳到 openDetail。 */\n'
    '  _paintDetail(id){\n'
    '    if(this._fsEditingId === id) return; /* 已经在编辑态 */\n'
    '    this.openDetail(id);\n'
    '  },'
)
assert_once('_paintDetail old', html, pd_old, 1)
html = html.replace(pd_old, pd_new)
print('[2.1] Notes._paintDetail redirected to openDetail')

# 旧的 editInFull 全屏编辑框整个删掉（标题/分类/标签都不要）
eif_old = (
    '  /* v56：在详情全屏里直接编辑（不跳回初始页），底部有「🖼 插入图片」 */\n'
    '  editInFull(id){\n'
    '    const it = this.list().find(x=>x.id===id); if(!it) return;\n'
    '    const cats = this.cats();\n'
    '    const selOpts = cats.map(c=>`<option value="${Util.esc(c)}" ${c===it.cat?\'selected\':\'\'}>${Util.esc(c)}</option>`).join(\'\');\n'
    '    UI.openFull(\'✎ 编辑\', `\n'
    '      <div class="note-edit-in-full">\n'
    '        <input id="noteEditTextTitle" placeholder="标题（选填）" value="${Util.esc(it.title||\'\')}">\n'
    '        <select id="noteEditTextCat" style="margin-top:8px">${selOpts}</select>\n'
    '        <textarea id="noteEditText" placeholder="内容。可点下面「🖼 插入图片」在文字之间插入图片" style="margin-top:8px">${Util.esc(it.text||\'\')}</textarea>\n'
    '        <div style="margin-top:8px"><label style="margin-top:0;font-size:13px">标签</label><div style="display:flex;gap:0"><input id="noteEditTextTags" placeholder="逗号分隔，如：情绪,边界" value="${Util.esc(it.tags||\'\')}"><button type="button" class="combo-toggle" onclick="Util.Combo.open(\'noteEditTextTags\',\'note_tags\',event)" title="选已有标签">▾</button></div></div>\n'
    '        <div class="row" style="margin-top:8px"><button class="btn ghost small" type="button" onclick="document.getElementById(\'noteEditFile\').click()">🖼 插入图片</button><span class="hint" id="noteEditMediaCount" style="margin-left:auto"></span></div>\n'
    '        <div class="row" style="margin-top:10px;justify-content:flex-end"><button class="btn ghost" onclick="Notes.openDetail(\'${id}\')">取消</button><button class="btn" onclick="Notes.saveEditInFull(\'${id}\')">保存</button></div>\n'
    '      </div>\n'
    '      <input type="file" id="noteEditFile" accept="image/*" multiple style="display:none" onchange="Notes.insertImages(this,\'noteEditText\')">\n'
    '    `, \'← 返回\', ()=>Notes.openDetail(id));\n'
    '    Media.paint(document.getElementById(\'uiFullBody\'));\n'
    '  },\n'
    '  saveEditInFull(id){\n'
    '    const ta = document.getElementById(\'noteEditText\');\n'
    '    if(!ta) return;\n'
    '    const text = ta.value;\n'
    '    const textNoMedia = String(text||\'\').replace(/\\[img:m_[a-zA-Z0-9_]+\\]/g,\'\').trim();\n'
    '    const title = (document.getElementById(\'noteEditTextTitle\')?.value||\'\').trim() || Util.firstSentence(textNoMedia);\n'
    '    if(!title && !textNoMedia) return UI.toast(\'至少写点内容\');\n'
    '    const cat = document.getElementById(\'noteEditTextCat\')?.value || this.cats()[0];\n'
    '    const tags = (document.getElementById(\'noteEditTextTags\')?.value||\'\').trim();\n'
    '    Store.set(\'notes\', this.list().map(x=>x.id===id?{...x, title, text, tags, cat, updatedAt:new Date().toISOString()}:x));\n'
    '    this.render();\n'
    '    this._paintDetail(id);\n'
    '    UI.toast(\'已保存\');\n'
    '  },'
)
# 把 editInFull/saveEditInFull 替换为 no-op（提示用户已统一到 openDetail）
eif_new = (
    '  /* v57：editInFull 已并入 openDetail —— 详情=编辑，自动保存。保留同名空函数以防老链接误调 */\n'
    '  editInFull(id){ this.openDetail(id); },\n'
    '  saveEditInFull(id){ this._autoSaveEdit(); },'
)
assert_once('editInFull old', html, eif_old, 1)
html = html.replace(eif_old, eif_new)
print('[2.2] editInFull/saveEditInFull collapsed into openDetail')

# ------------------------------------------------------------------
# CSS：note-edit-pure 全屏编辑样式 + 移除右上 × 钮的影响（UI.openFull 已经不画 ×）
# ------------------------------------------------------------------
css_nep_old = '.note-edit-in-full textarea{min-height:180px;resize:vertical;line-height:1.6}'
css_nep_new = (
    '/* v57：纯编辑全屏（openDetail）样式 —— textarea 占满高度，右下角 🖼 浮动圆形钮 */\n'
    '.note-edit-pure{display:flex;flex-direction:column;height:calc(100% - 24px);padding:0 8px}\n'
    '.note-edit-pure textarea{flex:1;min-height:300px;font-size:15px;line-height:1.7;border-radius:10px;padding:12px;border:1px solid var(--line);background:#fffefa;resize:none}\n'
    '.note-edit-pure .btn-fab-insert{display:inline-flex;align-items:center;gap:6px;background:#6b984f;color:#fff;border:0;padding:8px 16px;border-radius:999px;font-size:13px;font-weight:700;box-shadow:0 6px 18px rgba(107,152,79,.35);cursor:pointer}\n'
    '.note-edit-pure .btn-fab-insert:hover{background:#5a8641}\n'
    + css_nep_old
)
assert_once('css nep anchor', html, css_nep_old, 1)
html = html.replace(css_nep_old, css_nep_new)
print('[2.3] note-edit-pure CSS added')

# ------------------------------------------------------------------
# 3) 图片不显示的 bug 排查 —— 经验摘录分类详情 _renderOpenGrid 已经在末尾 paint Media。
#    需要做的是：保存 editInFull/_autoSaveEdit 后同步刷新网格（小卡缩略图必须 paint）。
#    已经在 _autoSaveEdit 里加渲染 + _renderOpenGrid。
#    另：_miniCard 里 for 缩略图 [img:m_xxx] 用法已用 _mediaInText + note-inline-img，需确保 paint 后这些图被解析。
#    检查 note-inline-img 样式是否存在，没有就加：
# ------------------------------------------------------------------
if 'note-inline-img' not in html:
    # 如果不存在则加
    nii_css = (
        '.note-inline-img{width:48px;height:48px;object-fit:cover;border-radius:6px;cursor:pointer;background:#e6e2cc}'
    )
    # 找一个合适的位置插入（在 .nmc-* 之前）
    anchor = '.note-mini-card{position'
    if anchor in html:
        html = html.replace(nii_css, '').replace(anchor, nii_css + '\n' + anchor, 1)
        print('[3.0] CSS note-inline-img inserted')

# 再确保 _renderOpenGrid 真的调用了 Media.paint（已有）。确认 _autoSaveEdit 调用 _renderOpenGrid（已加）
# 再确认 detail 模式（openDetail 已不需要 paint 因为是 textarea + [img:..] 占位）。

# ------------------------------------------------------------------
# 4) 删掉 Welcome.maybeShow 启动弹屏；homeQuote 重写为名言/鸡汤/摘录抽句
# ------------------------------------------------------------------
# 4.1 App.init 中 Welcome.maybeShow() 去掉 —— 改为只渲染一句欢迎语到 homeQuote
ini_old = '    Welcome.maybeShow();\n    AutoBackup.check();'
ini_new = '    AutoBackup.check();'
assert_once('App.init Welcome', html, ini_old, 1)
html = html.replace(ini_old, ini_new)
print('[4.1] Welcome.maybeShow() removed from boot')

# 4.2 hide welcomeScreen + 上传壁纸钮 —— 留 DOM 但 css .welcome{display:none}
# 简化做法：直接把 welcomeScreen 元素 hidden（更彻底）
ws_old = '<div class="welcome" id="welcomeScreen">\n  <div class="welcome-card">'
ws_new = '<div class="welcome" id="welcomeScreen" style="display:none!important">\n  <div class="welcome-card">'
assert_once('welcomeScreen DOM', html, ws_old, 1)
html = html.replace(ws_old, ws_new)
print('[4.2] welcomeScreen hidden (still in DOM for backward compatibility)')

# 4.3 重写 Home.quote —— 从内置名言库 + 经验摘录欢迎语分类 + 联网搜（如果有 AI key）
quote_old = (
    '  quote(){\n'
    '    const last = Store.get(\'welcomeLast\', {});\n'
    '    if(last.date === Util.today() && last.quote) return last.quote;\n'
    '    const q=[\'把简单的事重复做，做扎实。\',\'人要在事上磨，心要在静处养。\',\'先完成最小的一步，世界就会让路。\',\'真正的秩序，是知道今天只做哪三件事。\'];\n'
    '    return q[new Date().getDate()%q.length];\n'
    '  },'
)
quote_new = (
    '  /* v57：欢迎语 —— 三类素材按权重随机抽一句：内置名言/鸡汤 + 经验摘录某分类下随机一条（用户可设置素材分类） + 联网搜（如果设了 AI key）。\n'
    '     不写日期、不写客套话、不超过 3 行。 */\n'
    '  quote(){\n'
    '    const today = Util.today();\n'
    '    const last = Store.get(\'welcome_quote_cache\', {});\n'
    '    if(last.date === today && last.text) return last.text;\n'
    '    const pickFrom = (arr) => arr && arr.length ? arr[Math.floor(Math.random()*arr.length)] : \'\';\n'
    '    const builtin = [\n'
    '      \'把简单的事重复做，做扎实。\',\n'
    '      \'你比自己想象的更有韧性。\',\n'
    '      \'先完成最小的一步，世界就会让路。\',\n'
    '      \'慢慢来，比较快。\',\n'
    '      \'懂得停下的人，才有走得更远的资格。\',\n'
    '      \'真正的进步，是今天的自己比昨天多懂一点点。\',\n'
    '      \'允许自己今天只做一件事，那也是胜利。\',\n'
    '      \'把今天过成你会感谢的样子。\',\n'
    '      \'先照顾好心情，事情自然跟得上。\',\n'
    '      \'你不必完美，你只需要真实地往前走。\',\n'
    '      \'人要在事上磨，心要在静处养。\',\n'
    '      \'今天的微小积累，明天会以你不曾预料的方式回来。\',\n'
    '      \'先做该做的事，再做想做的事。\',\n'
    '      \'保持好奇，世界就会持续对你展开。\',\n'
    '      \'勇敢不是不害怕，是怕着还能继续。\',\n'
    '      \'别让昨天的疲惫，偷走今天的你。\',\n'
    '      \'所谓成长，是把模糊的感觉变成清晰的字句。\',\n'
    '      \'认真记录的人，不会被生活遗忘。\',\n'
    '      \'你给时间以耐心，时间就给你以答案。\',\n'
    '      \'日子是用心过的，不是用日历数的。\',\n'
    '      \'先想清楚要什么，再决定做什么。\',\n'
    '      \'慢慢变好，就是最好的状态。\',\n'
    '      \'一个稳定的内心，比任何技巧都珍贵。\',\n'
    '      \'今天的稳健，就是明天的自由。\',\n'
    '      \'不赶路，才看得到路。\'\n'
    '    ];\n'
    '    /* 来源比例：40% 内置、40% 摘录素材、20% 联网（失败就回退内置） */\n'
    '    const roll = Math.random();\n'
    '    let out = \'\';\n'
    '    if(roll < 0.4){\n'
    '      out = pickFrom(builtin);\n'
    '    } else if(roll < 0.8){\n'
    '      const noteCat = Store.get(\'home_quote_note_cat\', Notes.cats()[0] || \'\');\n'
    '      if(noteCat){\n'
    '        const pool = Notes.list().filter(x => (x.cat||\'\') === noteCat);\n'
    '        const pick = pool.length ? pool[Math.floor(Math.random()*pool.length)] : null;\n'
    '        if(pick){\n'
    '          /* 摘录的\"素材句\"：取第一句（剥掉 [img:..]），<=60 字 */\n'
    '          const raw = String(pick.text||pick.title||\'\').replace(/\\[img:m_[a-zA-Z0-9_]+\\]/g,\'\').trim();\n'
    '          const first = (raw.split(/[\\n。!?]/)[0]||\'\').slice(0,60).trim();\n'
    '          if(first) out = first;\n'
    '        }\n'
    '      }\n'
    '      if(!out) out = pickFrom(builtin);\n'
    '    } else {\n'
    '      /* 联网（异步但 quote() 同步返回，所以这里 fire-and-forget：\n'
    '         把上一句缓存先用上，联网成功后更新 homeQuote 即可） */\n'
    '      out = pickFrom(builtin);\n'
    '      this._refreshQuoteOnline(today);\n'
    '    }\n'
    '    /* 截断到 60 字以内（3 行） */\n'
    '    out = String(out||pickFrom(builtin)).replace(/\\s+/g,\' \').trim().slice(0,80);\n'
    '    Store.set(\'welcome_quote_cache\', {date:today, text:out});\n'
    '    return out;\n'
    '  },\n'
    '  /* v57：联网拿一句鸡汤（异步；只 fire-and-forget，不阻塞 quote） */\n'
    '  async _refreshQuoteOnline(today){\n'
    '    const key = Store.getSecret(\'ai\');\n'
    '    if(!key) return;\n'
    '    const base = Store.get(\'aiBase\',\'https://api.deepseek.com/v1/chat/completions\');\n'
    '    const model = Store.get(\'aiModel\',\'deepseek-chat\');\n'
    '    try{\n'
    '      const r = await fetch(base, {method:\'POST\',headers:{\'Content-Type\':\'application/json\',Authorization:\'Bearer \'+key},body:JSON.stringify({model,messages:[{role:\'system\',content:\'你是一个温暖的中文金句助手。回答只输出 1 句话，不少于 8 字、不超过 30 字，不带任何日期、称谓（不要出现"你/您好/今天"等）、不带 emoji。\'},{role:\'user\',content:\'请生成一句积极、鼓舞人心的中文短句。\'}],temperature:.95,max_tokens:60})});\n'
    '      if(!r.ok) return;\n'
    '      const data = await r.json();\n'
    '      const text = (data.choices?.[0]?.message?.content||\'\').replace(/[\\r\\n]/g,\'\').trim();\n'
    '      if(text){\n'
    '        const safe = text.slice(0,80);\n'
    '        Store.set(\'welcome_quote_cache\', {date:today, text:safe});\n'
    '        const el = document.getElementById(\'homeQuote\');\n'
    '        if(el) el.textContent = safe;\n'
    '      }\n'
    '    }catch(e){ /* 静默 */ }\n'
    '  },'
)
assert_once('Home.quote old', html, quote_old, 1)
html = html.replace(quote_old, quote_new)
print('[4.3] Home.quote rewritten (3 sources, no date/客套)')

# ------------------------------------------------------------------
# 5) 经验摘录 → 加"欢迎语素材分类"设置项（UI 入口：设置页里加上，否则加在 Notes 列表里）
#    简单处理：把它放进 manage categories 的 modal 提示里 —— 也可以新建 Notes._quoteSource 引用。
#    这里放在 Notes.editCategories 附近：
# ------------------------------------------------------------------
ec_old = 'editCategories(){'
if ec_old in html and 'home_quote_note_cat' not in html:
    ec_insert = (
        '/* v57：在管理分类底部加「📣 欢迎语素材分类」下拉 —— 当前选哪个分类，就从这个分类随机抽一句做首页欢迎语 */\n'
        '  quoteSourceCat(){ return Store.get(\'home_quote_note_cat\', this.cats()[0] || \'\'); },\n'
        '  setQuoteSourceCat(c){ Store.set(\'home_quote_note_cat\', c); UI.toast(\'已设 \'<<\'<<<\'<<<\'<\'<<c?c:\'\'<\'<<\': \'<<\'<<<\'<<\': \'+c+\' 分类的摘录，下次刷新首页会用里面的一句做欢迎语\'); },\n'
    )
    # 安全插入：用 marker
    marker = '  /* v51：管理摘录分类（增删改） */\n  editCategories(){'
    html = html.replace(marker, '  quoteSourceCat(){ return Store.get(\'home_quote_note_cat\', this.cats()[0] || \'\'); },\n  setQuoteSourceCat(c){ Store.set(\'home_quote_note_cat\', c); Store.remove(\'welcome_quote_cache\'); Home.render(); UI.toast(\'已设：欢迎语将从「\',\'+c+\'」分类里随机抽一句\'); },\n' + marker, 1)
    print('[5] Notes.quoteSourceCat + setQuoteSourceCat added (helper API; UI hook optional)')
else:
    print('[5] skip: marker not found or already patched')

# ------------------------------------------------------------------
# 6) App.init 刷新默认回首页：删 _lastPage 持久化（每次刷新都是 home）
# ------------------------------------------------------------------
goto_old = (
    '    const last = Store.get(\'_lastPage\',\'home\');\n'
    '    const start = this.routes.some(r=>r.id===last)?last:\'home\';\n'
    '    history.replaceState({page:start}, \'\', \'#\'+start);\n'
    '    this.go(start, {push:false});'
)
goto_new = (
    '    /* v57：刷新（重新打开）总是回首页，不再读 _lastPage 持久化 */\n'
    '    Store.remove(\'_lastPage\');\n'
    '    history.replaceState({page:\'home\'}, \'\', \'#home\');\n'
    '    this.go(\'home\', {push:false});'
)
assert_once('App.init lastPage', html, goto_old, 1)
html = html.replace(goto_old, goto_new)
print('[6] App.init default home (no _lastPage)')

# ------------------------------------------------------------------
# 7) 升版本号
# ------------------------------------------------------------------
ver_old = "const BUILD_VERSION = '2026-08-14-v56';"
ver_new = "const BUILD_VERSION = '2026-08-14-v57';"
assert_once('BUILD_VERSION old', html, ver_old, 1)
html = html.replace(ver_old, ver_new)
print('[7] BUILD_VERSION -> v57')

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print('\\n=== v57 patch done ===')
