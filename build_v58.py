#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v58 patch:
  1) UI: 去 ui-fs-x × 关闭按钮（DOM 不再渲染），改用 history.pushState/popstate
     接管浏览器物理返回键 / 滑动手势，全部走 _fsBack；同时支持 openFull 第 5 个
     参数 rightHtml + 第 6 个参数 hideTitle
  2) Notes.openDetail：去掉外层 note-edit-pure 框框，textarea 占满全屏；
     插入图片按钮只保留 🖼 符号，通过 openFull 的 rightHtml 放到顶部右上角；
     标题栏隐藏
  3) Notes 大分类卡片 nc-head 显示首张图片缩略图（用户在外面就能看到里面的图）
  4) Cooking：补 Cooking.edit() 函数；菜篮子卡片改为「图片右、文字左共享一行」；
     增加「再来一道」按钮；render 完调 Media.paint 让图片真正显示
  5) Home.quote：内置 100 条名言鸡汤，比例 20% 内置 / 40% 经验摘录素材 / 40% 联网搜
  6) 版本号 v58；sw.js 升 CACHE/BUILD
"""

import io, re, sys

PATH = r'C:\Users\cheng\WorkBuddy\2026-08-12-17-28-08\repo\index.html'

with io.open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

def assert_once(name, content, needle, n_expected):
    cnt = content.count(needle)
    if cnt != n_expected:
        print(f'ABORT: {name} expected {n_expected} hits, got {cnt}')
        print('--- first 240 chars of needle ---')
        print(needle[:240])
        sys.exit(1)

# ============================================================
# A) UI.openFull —— 不再渲染 ×；用 pushState/popstate 接管浏览器后退
# ============================================================
ui_open_old = (
    '  openFull(title, html, backLabel=\'← 返回\', onBack=null){\n'
    '    let box = document.getElementById(\'uiFullBox\');\n'
    '    if(!box){\n'
    '      box = document.createElement(\'div\'); box.id = \'uiFullBox\';\n'
    '      box.className = \'ui-fullscreen\';\n'
    '      box.innerHTML = `<div class="ui-fs-head"><button class="ui-fs-back" title="${Util.esc(backLabel)}">${Util.esc(backLabel)}</button><h3 id="uiFullTitle"></h3><button class="ui-fs-x" title="关闭">✕</button></div><div id="uiFullBody" class="ui-fs-body"></div>`;\n'
    '      document.body.appendChild(box);\n'
    '      box.querySelector(\'.ui-fs-x\').addEventListener(\'click\', ()=>UI.closeFull(true));\n'
    '      box.querySelector(\'.ui-fs-back\').addEventListener(\'click\', ()=>UI._fsBack());\n'
    '      /* v56：手机左右滑（快速横向 flick）返回上一层；与 mini-card 长按拖拽不冲突（拖拽需先长按>700ms，\n'
    '         这里只认 <500ms 的快速滑动）。 */\n'
    '      const fsBody = box.querySelector(\'#uiFullBody\');\n'
    '      let swX=0, swY=0, swT=0, swOn=false;\n'
    '      fsBody.addEventListener(\'touchstart\', e=>{ const t=e.touches[0]; swX=t.clientX; swY=t.clientY; swT=Date.now(); swOn=true; }, {passive:true});\n'
    '      fsBody.addEventListener(\'touchend\', e=>{\n'
    '        if(!swOn) return; swOn=false;\n'
    '        const t=e.changedTouches[0];\n'
    '        const dx=t.clientX-swX, dy=t.clientY-swY;\n'
    '        if(Math.abs(dx)>70 && Math.abs(dx) > Math.abs(dy)*1.5 && (Date.now()-swT) < 500){ UI._fsBack(); }\n'
    '      }, {passive:true});\n'
    '    }\n'
    '    /* 入栈：保存当前全屏状态（含滚动位置），← 才能回到这里 */\n'
    '    if(box.style.display === \'flex\'){\n'
    '      const curBody = document.getElementById(\'uiFullBody\');\n'
    '      this._fsHistory.push({\n'
    '        title: box.querySelector(\'#uiFullTitle\').textContent,\n'
    '        html: curBody ? curBody.innerHTML : \'\',\n'
    '        backLabel: box._backLabel || \'← 返回\',\n'
    '        onBack: box._onBack || null,\n'
    '        scroll: curBody ? curBody.scrollTop : 0\n'
    '      });\n'
    '    }\n'
    '    box._backLabel = backLabel || \'← 返回\';\n'
    '    box._onBack = onBack;\n'
    '    box.querySelector(\'.ui-fs-back\').textContent = box._backLabel;\n'
    '    box.querySelector(\'.ui-fs-back\').title = box._backLabel;\n'
    '    box.querySelector(\'#uiFullTitle\').textContent = title || \'\';\n'
    '    box.querySelector(\'#uiFullBody\').innerHTML = html || \'\';\n'
    '    box.style.display = \'flex\';\n'
    '    document.body.classList.add(\'ui-fs-on\');\n'
    '    document.documentElement.style.overflow = \'hidden\';\n'
    '    box.querySelector(\'#uiFullBody\').scrollTop = 0;\n'
    '    window.scrollTo({top:0, behavior:\'instant\'});\n'
    '  },'
)
ui_open_new = (
    '  /* v58：去掉右上角 × 关闭键（用户不要），改用 history.pushState/popstate 接管浏览器物理返回键 / 滑动手势 / 三键导航，\n'
    '     全部走 _fsBack；新增第 5 参数 rightHtml（渲染到头部右侧的按钮 HTML 列表）、第 6 参数 hideTitle（隐藏中标题）。 */\n'
    '  openFull(title, html, backLabel=\'← 返回\', onBack=null, rightHtml=\'\', hideTitle=false){\n'
    '    let box = document.getElementById(\'uiFullBox\');\n'
    '    if(!box){\n'
    '      box = document.createElement(\'div\'); box.id = \'uiFullBox\';\n'
    '      box.className = \'ui-fullscreen\';\n'
    '      box.innerHTML = `<div class="ui-fs-head"><button class="ui-fs-back"></button><h3 id="uiFullTitle"></h3><div class="ui-fs-right"></div></div><div id="uiFullBody" class="ui-fs-body"></div>`;\n'
    '      document.body.appendChild(box);\n'
    '      /* 不再绑 × 按钮 —— DOM 里也没有 × 元素 */\n'
    '      /* 点 ← 返回键：调 history.back() 让 popstate 统一走 _fsBack（更稳，避免和浏览器手势后退冲突） */\n'
    '      box.querySelector(\'.ui-fs-back\').addEventListener(\'click\', ()=>{\n'
    '        if(history.state && typeof history.state.uiFs === \'number\'){ history.back(); }\n'
    '        else { UI.closeFull(true); }\n'
    '      });\n'
    '      /* 全局 popstate：浏览器物理返回键、Edge/Chrome 滑动手势、四指返回都触发这里 → 统一 _fsBack */\n'
    '      window.addEventListener(\'popstate\', ()=>{\n'
    '        if(UI._silentFsClose) return;\n'
    '        if(!UI.isFullOpen()) return;\n'
    '        UI._fsBack();\n'
    '      });\n'
    '      UI._backBound = true;\n'
    '      /* v56+v58：手机横向 flick 也走 history.back()，与 popstate 统一 */\n'
    '      const fsBody = box.querySelector(\'#uiFullBody\');\n'
    '      let swX=0, swY=0, swT=0, swOn=false;\n'
    '      fsBody.addEventListener(\'touchstart\', e=>{ const t=e.touches[0]; swX=t.clientX; swY=t.clientY; swT=Date.now(); swOn=true; }, {passive:true});\n'
    '      fsBody.addEventListener(\'touchend\', e=>{\n'
    '        if(!swOn) return; swOn=false;\n'
    '        const t=e.changedTouches[0];\n'
    '        const dx=t.clientX-swX, dy=t.clientY-swY;\n'
    '        if(Math.abs(dx)>70 && Math.abs(dx) > Math.abs(dy)*1.5 && (Date.now()-swT) < 500){\n'
    '          if(history.state && typeof history.state.uiFs === \'number\'){ history.back(); }\n'
    '          else { UI.closeFull(true); }\n'
    '        }\n'
    '      }, {passive:true});\n'
    '    }\n'
    '    /* 入栈：保存当前全屏状态（含滚动位置） */\n'
    '    if(box.style.display === \'flex\'){\n'
    '      const curBody = document.getElementById(\'uiFullBody\');\n'
    '      this._fsHistory.push({\n'
    '        title: box.querySelector(\'#uiFullTitle\').textContent,\n'
    '        html: curBody ? curBody.innerHTML : \'\',\n'
    '        backLabel: box._backLabel || \'← 返回\',\n'
    '        onBack: box._onBack || null,\n'
    '        scroll: curBody ? curBody.scrollTop : 0\n'
    '      });\n'
    '    }\n'
    '    box._backLabel = backLabel || \'← 返回\';\n'
    '    box._onBack = onBack;\n'
    '    box.querySelector(\'.ui-fs-back\').textContent = box._backLabel;\n'
    '    box.querySelector(\'.ui-fs-back\').title = box._backLabel;\n'
    '    const titleEl = box.querySelector(\'#uiFullTitle\');\n'
    '    titleEl.textContent = title || \'\';\n'
    '    titleEl.style.display = hideTitle ? \'none\' : \'\';\n'
    '    box.querySelector(\'.ui-fs-right\').innerHTML = rightHtml || \'\';\n'
    '    box.querySelector(\'#uiFullBody\').innerHTML = html || \'\';\n'
    '    box.style.display = \'flex\';\n'
    '    document.body.classList.add(\'ui-fs-on\');\n'
    '    document.documentElement.style.overflow = \'hidden\';\n'
    '    box.querySelector(\'#uiFullBody\').scrollTop = 0;\n'
    '    window.scrollTo({top:0, behavior:\'instant\'});\n'
    '    /* 占位 history：让浏览器后退键 / 滑动手势触发 popstate → _fsBack 走这一格 */\n'
    '    const prevDepth = (history.state && typeof history.state.uiFs === \'number\') ? history.state.uiFs : 0;\n'
    '    history.pushState({uiFs: prevDepth + 1}, \'\');\n'
    '  },'
)
assert_once('UI.openFull old', html, ui_open_old, 1)
html = html.replace(ui_open_old, ui_open_new)
print('[A1] UI.openFull rewritten (no ×, pushState/popstate)')

# closeFull: reset=true 时把 uiFs 历史一起清掉（防止下次进站再来回弹层）
cf_old = (
    '  closeFull(reset=true){\n'
    '    if(reset){\n'
    '      /* × 一律关到最外层，清空栈 */\n'
    '      const box = document.getElementById(\'uiFullBox\');\n'
    '      if(box){\n'
    '        box.style.display = \'none\';\n'
    '        const body = document.getElementById(\'uiFullBody\');\n'
    '        if(body) body.innerHTML = \'\';\n'
    '        box._backLabel = null; box._onBack = null;\n'
    '      }\n'
    '      this._fsHistory = [];\n'
    '      document.body.classList.remove(\'ui-fs-on\');\n'
    '      document.documentElement.style.overflow = \'\';\n'
    '    } else {\n'
    '      this._fsBack();\n'
    '    }\n'
    '  },'
)
cf_new = (
    '  closeFull(reset=true){\n'
    '    if(reset){\n'
    '      /* 把所有 uiFs 占位 history 全 pop 掉 —— 浏览器循环 history.back() 同步分派 popstate，\n'
    '         _silentFsClose 让 popstate 监听器短路不触发 _fsBack。 */\n'
    '      let safety = 60;\n'
    '      this._silentFsClose = true;\n'
    '      try {\n'
    '        while (safety-- > 0 && history.state && typeof history.state.uiFs === \'number\') {\n'
    '          history.back();\n'
    '        }\n'
    '      } finally { this._silentFsClose = false; }\n'
    '      const box = document.getElementById(\'uiFullBox\');\n'
    '      if(box){\n'
    '        box.style.display = \'none\';\n'
    '        const body = document.getElementById(\'uiFullBody\');\n'
    '        if(body) body.innerHTML = \'\';\n'
    '        box._backLabel = null; box._onBack = null;\n'
    '      }\n'
    '      this._fsHistory = [];\n'
    '      document.body.classList.remove(\'ui-fs-on\');\n'
    '      document.documentElement.style.overflow = \'\';\n'
    '    } else {\n'
    '      this._fsBack();\n'
    '    }\n'
    '  },'
)
assert_once('UI.closeFull old', html, cf_old, 1)
html = html.replace(cf_old, cf_new)
print('[A2] UI.closeFull now drains history.uiFs')

# _fsBack: 栈空时也要把 history pop 干净（避免 history 残留导致下次进站误弹层）
fsb_old = (
    '  _fsBack(){\n'
    '    const prev = this._fsHistory.pop();\n'
    '    if(!prev){\n'
    '      /* 没有上级了，直接 close */\n'
    '      this.closeFull(true);\n'
    '      return;\n'
    '    }\n'
)
fsb_new = (
    '  _fsBack(){\n'
    '    /* popstate 触发时把 history 也清掉对应一层（让 history 与 _fsHistory 步进一致） */\n'
    '    if(!this._silentFsClose && history.state && typeof history.state.uiFs === \'number\'){\n'
    '      this._silentFsClose = true;\n'
    '      try { history.back(); } finally { this._silentFsClose = false; }\n'
    '    }\n'
    '    const prev = this._fsHistory.pop();\n'
    '    if(!prev){\n'
    '      /* 没有上级了，直接 close —— 这会再把 history 里残留 uiFs 也清掉 */\n'
    '      this.closeFull(true);\n'
    '      return;\n'
    '    }\n'
)
assert_once('UI._fsBack old', html, fsb_old, 1)
html = html.replace(fsb_old, fsb_new)
print('[A3] UI._fsBack now syncs with history on each step')

# CSS: 增加 ui-fs-right + ui-fs-icon-btn
css_anchor = '.ui-fs-back{font-size:14px}'
css_add = (
    css_anchor + '\n'
    '/* v58：头部右侧容器 / 单图标按钮样式（取代原本的 ✕ 关闭键） */\n'
    '.ui-fs-right{display:flex;align-items:center;gap:6px;flex:none}\n'
    '.ui-fs-icon-btn{border:0;background:transparent;font-size:20px;padding:6px 10px;cursor:pointer;color:var(--text);border-radius:8px;line-height:1}\n'
    '.ui-fs-icon-btn:hover{background:rgba(0,0,0,.06)}'
)
assert_once('ui-fs-back css anchor', html, css_anchor, 1)
html = html.replace(css_anchor, css_add)
print('[A4] CSS ui-fs-right + ui-fs-icon-btn added')

# ============================================================
# B) Notes.openDetail —— 去边框、按钮改右上角 🖼、去掉 head 标题
# ============================================================
od_old = (
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
)
od_new = (
    '  /* v58：详情 = 全屏纯文本编辑 —— 整个全屏就是一个无边 textarea，\n'
    '     顶部右侧一个 🖼 小图标（点击插入图片，符号替代之前大按钮）。\n'
    '     标题 / 分类 / 标签 / 保存 / 取消 / ✕ 都没有：默认自动保存、退栈即保存。 */\n'
    '  openDetail(id){\n'
    '    const it = this.list().find(x=>x.id===id); if(!it) return;\n'
    '    const rightBtn = `<button class="ui-fs-icon-btn" type="button" onclick="document.getElementById(\'noteEditPureFile\').click()" title="插入图片">🖼</button>`;\n'
    '    UI.openFull(\'\', `\n'
    '      <textarea id="noteEditPure" placeholder="写下你的经验、原则、观察..."></textarea>\n'
    '      <div class="note-edit-foot"><span class="hint" id="noteEditPureCount"></span></div>\n'
    '      <input type="file" id="noteEditPureFile" accept="image/*" multiple style="display:none" onchange="Notes.insertImages(this,\'noteEditPure\');Notes._autoSaveEdit()">\n'
    '    `, \'← 返回\', null, rightBtn, /*hideTitle*/true);\n'
)
assert_once('Notes.openDetail old', html, od_old, 1)
html = html.replace(od_old, od_new)
print('[B1] Notes.openDetail rewritten (no box, top-right 🖼)')

# CSS: 替换 note-edit-pure 样式 —— 去边框、占满全屏
ne_css_old = '.note-edit-pure{display:flex;flex-direction:column;height:calc(100% - 24px);padding:0 8px}\n.note-edit-pure textarea{flex:1;min-height:300px;font-size:15px;line-height:1.7;border-radius:10px;padding:12px;border:1px solid var(--line);background:#fffefa;resize:none}\n.note-edit-pure .btn-fab-insert{display:inline-flex;align-items:center;gap:6px;background:#6b984f;color:#fff;border:0;padding:8px 16px;border-radius:999px;font-size:13px;font-weight:700;box-shadow:0 6px 18px rgba(107,152,79,.35);cursor:pointer}\n.note-edit-pure .btn-fab-insert:hover{background:#5a8641}'
ne_css_new = (
    '/* v58：openDetail 详情纯编辑全屏 —— 整个全屏就是一个无边、无背景的 textarea，\n'
    '   顶端右侧 🖼 按钮是从 UI.openFull 的 rightHtml 参数透传注入的；\n'
    '   下面小灰字写「已插入 N 张图」是 note-edit-foot 的 hint。 */\n'
    '.note-edit-pure{display:flex;flex-direction:column;height:100%;padding:0;margin:0}\n'
    '.note-edit-pure textarea{flex:1;width:100%;border:0;outline:none;background:transparent;font-size:15px;line-height:1.7;padding:14px 16px;resize:none;font-family:inherit;color:var(--text);min-height:0}\n'
    '.note-edit-pure textarea::placeholder{color:var(--text-dim)}\n'
    '.note-edit-foot{padding:6px 16px 12px;font-size:11px;color:var(--text-dim);text-align:right}'
)
assert_once('css note-edit-pure old', html, ne_css_old, 1)
html = html.replace(ne_css_old, ne_css_new)
print('[B2] CSS note-edit-pure rewritten (fullscreen textarea)')

# ============================================================
# C) Notes 大分类卡片：显示首张图片缩略图 + 显示最新一条标题/预览
#    "把点进去里面的小卡片直接搬过去"
# ============================================================
nc_old = (
    '    const cards = cats.map(cat => {\n'
    '      const items = byCat[cat] || [];\n'
    '      const latest = items[0];\n'
    '      const preview = latest ? (this._stripMedia(latest.text || \'\') || latest.title || \'（空）\').slice(0,140) : \'\';\n'
    '      const count = items.length;\n'
    '      const isEmpty = !latest;\n'
    '      const date = latest ? (latest.date || \'\') : \'\';\n'
    '      return `<div class="note-cat-card${isEmpty?\' note-cat-empty\':\'\'}" onclick="Notes.openCat(\'${Util.esc(cat)}\')">\n'
    '        <div class="nc-head"><span class="nc-title">📁 ${Util.esc(cat)}</span><span class="nc-count">${count}</span></div>\n'
    '        <div class="nc-preview">${preview ? Util.esc(preview) : \'<span style="color:var(--text-dim)">点上面「保存摘录」会自动归到这里</span>\'}</div>\n'
    '        <div class="nc-date">${date ? (\'最新 · \'+Util.esc(date)) : \'还没有摘录\'}</div>\n'
    '      </div>`;\n'
    '    }).join(\'\');'
)
nc_new = (
    '    const cards = cats.map(cat => {\n'
    '      const items = byCat[cat] || [];\n'
    '      const latest = items[0];\n'
    '      /* v58：缩略图：最新一条的第一张图（去掉 [img:..] 后看首个内嵌图） */\n'
    '      const latestImgIds = latest ? this._mediaInText(latest.text) : [];\n'
    '      const latestImg = latestImgIds[0] ? Util.mediaImg(latestImgIds[0]) : \'\';\n'
    '      const preview = latest ? (this._stripMedia(latest.text || \'\') || latest.title || \'（空）\').slice(0,140) : \'\';\n'
    '      const count = items.length;\n'
    '      const isEmpty = !latest;\n'
    '      const date = latest ? (latest.date || \'\') : \'\';\n'
    '      return `<div class="note-cat-card${isEmpty?\' note-cat-empty\':\'\'}" onclick="Notes.openCat(\'${Util.esc(cat)}\')">\n'
    '        ${latestImg ? `<div class="nc-thumb">${latestImg}</div>` : \'\'}\n'
    '        <div class="nc-head"><span class="nc-title">📁 ${Util.esc(cat)}</span><span class="nc-count">${count}</span></div>\n'
    '        <div class="nc-preview">${preview ? Util.esc(preview) : \'<span style="color:var(--text-dim)">点上面「保存摘录」会自动归到这里</span>\'}</div>\n'
    '        <div class="nc-date">${date ? (\'最新 · \'+Util.esc(date)) : \'还没有摘录\'}</div>\n'
    '      </div>`;\n'
    '    }).join(\'\');\n'
    '    /* v58：异步把大分类卡片里的图缩略图 fill 上（img 用 Media.paint 补 src） */\n'
    '    setTimeout(()=>Notes._paintCatThumbs(), 30);'
)
assert_once('Notes cat card old', html, nc_old, 1)
html = html.replace(nc_old, nc_new)
print('[C1] Notes 大分类卡片加了缩略图占位 + paint hook')

# Notes.render 末尾调一次 paint（保证大分类卡片缩略图能填上）
# 在 Notes.render 的最后（"noteList.innerHTML = `<div class="note-cat-grid">${cards}${allCard}</div>`;" 后）
# 我们直接在 allCard 后面加 paint
nc_all_old = 'noteList.innerHTML = `<div class="note-cat-grid">${cards}${allCard}</div>`;'
nc_all_new = ('noteList.innerHTML = `<div class="note-cat-grid">${cards}${allCard}</div>`;\n'
              '    /* v58：异步填充大分类卡片的图片缩略图（img 用 Media.paint） */\n'
              '    setTimeout(()=>Notes._paintCatThumbs(), 0);')
assert_once('Notes render allCard', html, nc_all_old, 1)
html = html.replace(nc_all_old, nc_all_new)
print('[C2] Notes render 末尾 paint 大分类')

# 加 _paintCatThumbs helper + nc-thumb CSS
notes_paint_anchor = '  _stripMedia(text){ return String(text||\'\').replace(/\\[img:m_[a-zA-Z0-9_]+\\]/g, \'\').trim(); },'
notes_paint_new = (
    notes_paint_anchor + '\n'
    '  /* v58：把大分类卡片里的 [data-media] 占位 img 异步填充 src */\n'
    '  _paintCatThumbs(){ Media.paint(document.getElementById(\'noteList\')); },'
)
assert_once('Notes _stripMedia', html, notes_paint_anchor, 1)
html = html.replace(notes_paint_anchor, notes_paint_new)
print('[C3] Notes._paintCatThumbs helper added')

# nc-thumb CSS
nc_thumb_css_anchor = '.note-cat-card .nc-date{font-size:10px;color:var(--text-dim)}'
nc_thumb_css_new = (
    nc_thumb_css_anchor + '\n'
    '/* v58：大分类卡片顶部的图片缩略图（最新一条笔记的首张内嵌图） */\n'
    '.note-cat-card .nc-thumb{width:100%;height:96px;overflow:hidden;border-radius:10px;margin-bottom:4px;background:#e6e2cc}\n'
    '.note-cat-card .nc-thumb img.note-inline-img,.note-cat-card .nc-thumb img{width:100%;height:100%;object-fit:cover;display:block;border-radius:10px;margin:0;max-width:none;max-height:none}'
)
assert_once('css nc-date anchor', html, nc_thumb_css_anchor, 1)
html = html.replace(nc_thumb_css_anchor, nc_thumb_css_new)
print('[C4] CSS nc-thumb added')

# ============================================================
# D) Cooking —— 补 edit() + 卡片横向（图右字左共享一行）+ 来一道按钮 + Media.paint
# ============================================================
# D1) add() 增加 dish_editing 存在时 update 而不是 insert
ck_add_old = (
    '  async add(){\n'
    '    const name=dishName.value.trim();\n'
    '    if(!name)return;\n'
    '    const file=dishPhoto.files[0];\n'
    '    const saved = file ? await Media.save(file, \'life\').catch(()=>null) : null;\n'
    '    this.splitTag(dishTags.value).forEach(t=>Util.bump(\'dish_tags\',t)); Store.set(\'dishes\',[{id:Util.uid(),name,tags:dishTags.value.trim(),steps:dishSteps.value.trim(),photoId:saved?.id||\'\',photo:\'\'},...this.list()]);\n'
    '    Store.set(\'wheel_dishes\',[...new Set(this.wheel().concat(name))]);\n'
    '    dishName.value=dishTags.value=dishSteps.value=\'\';\n'
    '    dishPhoto.value=\'\';\n'
    '    Coin.checkCookingNew();\n'
    '    this.render();\n'
    '  },'
)
ck_add_new = (
    '  async add(){\n'
    '    const name=dishName.value.trim();\n'
    '    if(!name)return;\n'
    '    const file=dishPhoto.files[0];\n'
    '    const saved = file ? await Media.save(file, \'life\').catch(()=>null) : null;\n'
    '    this.splitTag(dishTags.value).forEach(t=>Util.bump(\'dish_tags\',t));\n'
    '    const editing = Store.get(\'dish_editing\',\'\');\n'
    '    const list = this.list();\n'
    '    if(editing && list.find(x=>x.id===editing)){\n'
    '      /* v58：编辑模式下覆盖原条目（保留 photoId，新上传才覆盖） */\n'
    '      const newId = saved?.id || (list.find(x=>x.id===editing)?.photoId || \'\');\n'
    '      Store.set(\'dishes\', list.map(x=>x.id===editing?{...x,name,tags:dishTags.value.trim(),steps:dishSteps.value.trim(),photoId:newId}:x));\n'
    '      Store.remove(\'dish_editing\');\n'
    '      UI.toast(\'已更新：\'+name);\n'
    '    } else {\n'
    '      Store.set(\'dishes\',[{id:Util.uid(),name,tags:dishTags.value.trim(),steps:dishSteps.value.trim(),photoId:saved?.id||\'\',photo:\'\'},...list]);\n'
    '      Store.set(\'wheel_dishes\',[...new Set(this.wheel().concat(name))]);\n'
    '      Coin.checkCookingNew();\n'
    '      UI.toast(\'已添加：\'+name);\n'
    '    }\n'
    '    dishName.value=dishTags.value=dishSteps.value=\'\';\n'
    '    dishPhoto.value=\'\';\n'
    '    this.render();\n'
    '  },'
)
assert_once('Cooking.add old', html, ck_add_old, 1)
html = html.replace(ck_add_old, ck_add_new)
print('[D1] Cooking.add 加了 dish_editing 分支')

# D2) 卡片模板：横向（图右字左共享一行）+ 动作按钮 inline 右侧
dish_card_old = (
    '/* v57：按 Quick/Notes 灵感小卡模板重构 —— 图片缩略图 + 菜名/标签/步骤整行在上，按钮 ✎ / ✕ 在下方一行；移除 ↑↓；长按拖动排序 */\n'
    '    const recipeHtml = Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="list">${rows.map((x)=>{ const i=dishRecipes.findIndex(y=>y.id===x.id); return `<div class="item dish-basket-card-item${x._open?\' open\':\'\'}" draggable="true" data-sort-id="${x.id}">${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class="thumb" src="${Util.esc(x.photo)}" alt="">`:\'\')}<div class="grow"><div class="title">${Util.esc(x.name)}</div>${x.tags?`<div class="dish-meta">${Util.esc(x.tags)}</div>`:\'\'}<div class="dish-steps">${Util.esc(x.steps||\'\')}</div></div><div class="dish-foot"><button class="btn ghost small" onclick="Cooking.edit(\'${x.id}\')" title="编辑这道菜">✎ 编辑</button><button class="del small" onclick="Cooking.del(\'${x.id}\')" title="删除">✕</button></div></div>`; }).join(\'\')}</div></section>`).join(\'\'):\'\';'
)
dish_card_new = (
    '/* v58：按 v57 灵感小卡模板再升级 —— 横向布局（图片右、文字左共享一行），按钮 ✎ / ✕ 移到卡片右侧列里（不单独一行），不再有 ↑↓；长按拖动排序 */\n'
    '    const recipeHtml = Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="list">${rows.map((x)=>{ const i=dishRecipes.findIndex(y=>y.id===x.id); return `<div class="item dish-basket-card-item${x._open?\' open\':\'\'}" draggable="true" data-sort-id="${x.id}"><div class="grow"><div class="title">${Util.esc(x.name)}</div>${x.tags?`<div class="dish-meta">${Util.esc(x.tags)}</div>`:\'\'}<div class="dish-steps">${Util.esc(x.steps||\'\')}</div></div>${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class="thumb" src="${Util.esc(x.photo)}" alt="">`:\'\')}<div class="dish-actions"><button class="ui-fs-icon-btn" type="button" onclick="Cooking.edit(\'${x.id}\')" title="编辑这道菜">✎</button><button class="ui-fs-icon-btn" type="button" onclick="Cooking.del(\'${x.id}\')" title="删除">✕</button></div></div>`; }).join(\'\')}</div></section>`).join(\'\'):\'\';'
)
assert_once('dish card old', html, dish_card_old, 1)
html = html.replace(dish_card_old, dish_card_new)
print('[D2] 菜篮子卡片：图右字左横向布局 + 按钮 inline')

# D3) render 末尾调 Media.paint 让图片真正显示
ck_render_anchor = 'dishListEl.innerHTML = recipeHtml + empty;\n    DragSort.bind(\'#dishList [data-sort-id]\',\'dishes\',()=>Cooking.render());\n    this.paintWheelList();'
ck_render_new = (
    'dishListEl.innerHTML = recipeHtml + empty;\n'
    '    DragSort.bind(\'#dishList [data-sort-id]\',\'dishes\',()=>Cooking.render());\n'
    '    /* v58：菜篮子图片渲染完异步 fill src（Util.mediaImg 是占位 img，靠 Media.paint 补） */\n'
    '    Media.paint(dishListEl);\n'
    '    this.paintWheelList();'
)
assert_once('Cooking render paint', html, ck_render_anchor, 1)
html = html.replace(ck_render_anchor, ck_render_new)
print('[D3] Cooking.render 末尾调 Media.paint')

# D4) 补 Cooking.edit() + 加一道（addOne） + 更新 dish-basket-card-item CSS
ck_del_anchor = '  del(id){ Store.set(\'dishes\',this.list().filter(x=>x.id!==id)); this.render(); },'
ck_del_new = (
    '  /* v57 + v58：菜篮子卡片点 ✎ 编辑 → 滚到顶部表单并预填；如果当前已经在编辑这一条则取消编辑 */\n'
    '  edit(id){\n'
    '    const it=this.list().find(x=>x.id===id); if(!it) return;\n'
    '    const cur = Store.get(\'dish_editing\',\'\');\n'
    '    if(cur === id){\n'
    '      /* 已经在编辑这一条：再次点 ✎ 取消编辑（恢复成"再来一道"状态） */\n'
    '      this.addOne();\n'
    '      UI.toast(\'已退出编辑\');\n'
    '      return;\n'
    '    }\n'
    '    Store.set(\'dish_editing\', id);\n'
    '    if(typeof dishName !== \'undefined\' && dishName) dishName.value = it.name || \'\';\n'
    '    if(typeof dishTags !== \'undefined\' && dishTags) dishTags.value = it.tags || \'\';\n'
    '    if(typeof dishSteps !== \'undefined\' && dishSteps) dishSteps.value = it.steps || \'\';\n'
    '    this.render();\n'
    '    (document.getElementById(\'page-cooking\')||document.body)?.scrollIntoView?.({behavior:\'smooth\', block:\'start\'});\n'
    '    setTimeout(()=>{ try{ document.getElementById(\'dishName\')?.focus(); }catch(e){} }, 220);\n'
    '    UI.toast(\'正在编辑：\'+(it.name||\'这道菜\')+\'；改完点「保存菜谱」即可，留空直接回来等存新菜\');\n'
    '  },\n'
    '  /* v58：「再来一道」—— 清空表单 + 退出编辑状态 + 滚到顶部 + 聚焦菜名 */\n'
    '  addOne(){\n'
    '    Store.remove(\'dish_editing\');\n'
    '    if(typeof dishName !== \'undefined\' && dishName) dishName.value = \'\';\n'
    '    if(typeof dishTags !== \'undefined\' && dishTags) dishTags.value = \'\';\n'
    '    if(typeof dishSteps !== \'undefined\' && dishSteps) dishSteps.value = \'\';\n'
    '    if(typeof dishPhoto !== \'undefined\' && dishPhoto) dishPhoto.value = \'\';\n'
    '    this.render();\n'
    '    (document.getElementById(\'page-cooking\')||document.body)?.scrollIntoView?.({behavior:\'smooth\', block:\'start\'});\n'
    '    setTimeout(()=>{ try{ document.getElementById(\'dishName\')?.focus(); }catch(e){} }, 220);\n'
    '  },\n'
    '  del(id){ Store.set(\'dishes\',this.list().filter(x=>x.id!==id)); this.render(); },'
)
assert_once('Cooking.del anchor', html, ck_del_anchor, 1)
html = html.replace(ck_del_anchor, ck_del_new)
print('[D4] Cooking.edit + addOne added')

# D5) 菜篮子上方加「再来一道」按钮（look at the page-cooking HTML section）
# 找到做菜栏的写表单那块，找 dishBasketToggle (菜篮子整体折叠钮) 或 dishBasketCount 旁边加入口
# 在 dishBasketCount 后面插一个「+ 再来一道」钮
ck_toggle_anchor = '<span id="dishBasketCount"></span>'
# 注：这 anchor 可能在不同行，我们要找的是页面里的调用入口。我们改为：找 '<div id="dishList"' 之前最近的 id="dishBasketWrap" 头？
# 直接打 hover：在 toggleBtn 旁边加一个 "再来一道" 按钮 —— 但简单做法是在表单 dishPhoto 之后立刻插一个 btn row

# 我用更明确的 anchor：菜篮子外层容器 <div id="dishBasketWrap" ...>，找它的开头标签
ck_wrap_anchor = '<div id="dishBasketWrap"'
if ck_wrap_anchor in html:
    wrap_old = '<div id="dishBasketWrap"'
    # 找到 wrap 这一行紧跟的 <h2 ... />+<button id="dishBasketToggle"/>，在 toggle 按钮之后插一个 + 再来一道 按钮
    # 找 dish-basket-toggle class 的那个按钮，恰好 1 处
    toggle_anchor = 'dish-basket-toggle"'
    cnt = html.count(toggle_anchor)
    if cnt == 1:
        idx = html.index(toggle_anchor)
        end_btn_idx = html.index('</button>', idx)
        insert_pos = end_btn_idx + len('</button>')
        addone_btn = '<button class="btn ghost small" id="dishAddOneBtn" onclick="Cooking.addOne()" title="清空表单，开始录入下一道菜">+ 再来一道</button>'
        html = html[:insert_pos] + addone_btn + html[insert_pos:]
        print('[D5] + 再来一道 按钮插到 toggle 按钮旁边')
    else:
        print(f'[D5] skip: dish-basket-toggle count={cnt}')

# D6) CSS 调整菜篮子卡片为横向
css_dish_old = (
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
css_dish_new = (
    '/* v58：菜篮子小卡 —— 横向布局：左边文字（占主要空间），右边小缩略图，再右边一列动作按钮（✎ / ✕）；\n'
    '   不要再独立一行放按钮，也不要 ↑↓；长按整张卡片可拖动排序（DragSort.bind） */\n'
    '.dish-basket-card-item{flex-direction:row;align-items:center;padding:10px 12px;gap:10px}\n'
    '.dish-basket-card-item .grow{flex:1;min-width:0;text-align:left;order:1}\n'
    '.dish-basket-card-item .title{font-size:14px;font-weight:700;line-height:1.35;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n'
    '.dish-basket-card-item .dish-meta{font-size:11px;color:var(--text-dim);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n'
    '.dish-basket-card-item .dish-steps{font-size:11px;color:var(--text);line-height:1.5;margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;word-break:break-word}\n'
    '.dish-basket-card-item .thumb{width:54px;height:54px;object-fit:cover;border-radius:8px;flex:none;order:2;margin:0;background:#e6e2cc}\n'
    '.dish-basket-card-item .dish-actions{display:flex;flex-direction:column;align-items:center;gap:2px;flex:none;order:3}\n'
    '.dish-basket-card-item .dish-actions button{font-size:15px;padding:4px 6px;line-height:1;min-height:28px}'
)
assert_once('css dish-basket old', html, css_dish_old, 1)
html = html.replace(css_dish_old, css_dish_new)
print('[D6] CSS dish-basket-card-item 改横向布局')

# ============================================================
# E) Home.quote —— 100 条内置、20% 内置 / 40% 经验摘录 / 40% 联网
# ============================================================
# E1) 把 25 条内置数组扩到 100 条（保持原有句子 + 加 75 条新句子）
quote_builtin_old = (
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
    '          /* 摘录的"素材句"：取第一句（剥掉 [img:..]），<=60 字 */\n'
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
)
quote_builtin_new = (
    '    /* v58：100 条内置鸡汤/名言/鼓气语录（涵盖自我、行动、休息、坚持、关系、记录、时间、选择、心态、习惯） */\n'
    '    const builtin = [\n'
    '      /* === 自我 / 自洽 === */\n'
    '      \'把简单的事重复做，做扎实。\',\'你比自己想象的更有韧性。\',\'你不必完美，你只需要真实地往前走。\',\'一个稳定的内心，比任何技巧都珍贵。\',\'懂得停下的人，才有走得更远的资格。\',\'允许自己今天只做一件事，那也是胜利。\',\'先照顾好心情，事情自然跟得上。\',\'你给时间以耐心，时间就给你以答案。\',\'别让昨天的疲惫，偷走今天的你。\',\'所谓成长，是把模糊的感觉变成清晰的字句。\',\'能承认"我今天不太好"，就是一种力量。\',\'有时候慢一步，是为了走得稳一点。\',\'你是你自己最久的伙伴，善待自己。\',\'先和自己和解，外面才会宽敞。\',\'情绪不是敌人，是信使。\',\'看见自己，已经是一大步。\',\'不是所有问题都要立刻解决，先陪着它一会儿。\',\'今天的自己，比昨天多懂一点点，就够了。\',\'你此刻的状态，并不决定你的方向。\',\'凡事过不去的时候，给自己两分钟。\',\'与其等风来，不如先站直了。\',\'先稳住呼吸，再稳住心。\',\'一个人吃饭、走路的你，也很好。\',\'别拿别人的尺子量自己的路。\',\'今天的稳健，就是明天的自由。\',\'不必把所有事扛在肩上。\',\'你能掌控的，远比你以为的多。\',\'先照顾好自己，再去照亮别人。\',\'你的身体记得你所有的好。\',\'不必为没发生的事，先学会担忧。\',\n'
    '      /* === 行动 / 开始 === */\n'
    '      \'先完成最小的一步，世界就会让路。\',\'慢慢来，比较快。\',\'先做该做的事，再做想做的事。\',\'勇敢不是不害怕，是怕着还能继续。\',\'所谓艰难，常常是开始之后才消失的。\',\'把脑子里那一行字，先写下来。\',\'一小时专心干一件事，胜过八小时犹豫。\',\'先把话筒递给自己，再问别人怎么看。\',\'事来则应，事去则忘。\',\'做，比想更接近答案。\',\'今天只要完成一件事，也是完整的一天。\',\'先动起来，身体会带着脑子走。\',\'把大目标拆成今天能做的一件小事。\',\'一边做一边调整，比先想完美靠谱。\',\'先做出 60 分，再改到 80 分，比追求 100 分停滞不前实际得多。\',\'把第一步迈出去，路就会自己接你。\',\'别等所有灯都绿了才起步。\',\'先做三分钟，做着做着就停不下来。\',\'今天不亮也可以航行，靠罗盘就行。\',\'别问"做不做得到"，先问"愿不愿意开始"。\',\n'
    '      /* === 时间 / 当下 === */\n'
    '      \'日子是用心过的，不是用日历数的。\',\'今天的微小积累，明天会以你不曾预料的方式回来。\',\'不赶路，才看得到路。\',\'把握今天的方法，就是把一件事做完整。\',\'时间不多，但你有一整天。\',\'先把眼前的五分钟过好。\',\'今日事，今日毕，是一种温柔的自由。\',\'慢慢变好，就是最好的状态。\',\'把今天过成你会感谢的样子。\',\'别高估一天能做的事，别低估一年能做的事。\',\'再远的路，迈开第一步就缩短了一半。\',\'今天最值得花时间的，往往是最简单的事。\',\'早睡，就是给明天最好的礼物。\',\'哪怕只专心 25 分钟，世界也会停顿。\',\'少即是多，慢即是快。\',\'今天的天气好不好，不影响你今天过得好不好。\',\'把今天过好，明天自然会来。\',\'过去的事改不了，今天的你还没定型。\',\'专注一件小事，是最实在的修行。\',\'日历会过期，你的成长不会。\',\n'
    '      /* === 坚持 / 积累 === */\n'
    '      \'坚持不是因为厉害，是因为已经成了习惯。\',\'微小的事重复做，就会变成你的样子。\',\'坚持久了，灵感也会回头找你。\',\'今天的难，明天的你回头看时已不算什么。\',\'不与别人比速度，只和昨天的自己比坚持。\',\'慢慢走，也是一种快。\',\'把"再坚持一下"放在嘴边。\',\'连续做到第七天，你会发现新东西。\',\'最难的那一步，往往就是最有价值的那一步。\',\'凡是让你熬过去的，都会让你长出铠甲。\',\n'
    '      /* === 选择 / 思维 === */\n'
    '      \'先想清楚要什么，再决定做什么。\',\'保持好奇，世界就会持续对你展开。\',\'不确定的时候，就选让你心里更安静的那个。\',\'把眼光放远，今天的难题会变小。\',\'别让一个困难，挡住所有可能性。\',\'答案常常出现在停下来的那一刻。\',\'能拒绝，也是一种自由。\',\'重要的事，要先跟自己的心商量。\',\'不必每件事都立刻选，慢一拍也是一种清白。\',\'少想"万一"，多看"现在"。\',\'把"我应该"换成"我愿意"，生活会轻一些。\',\'真问题常常藏在表面问题后面。\',\'把担心写在纸上，脑子就能腾出空。\',\'要紧的不是想做多少事，是做对的那件事。\',\n'
    '      /* === 关系 / 善意 === */\n'
    '      \'对你温柔一点的人，也值得你温柔一点。\',\'一句温和的话，能接住一整天的疲惫。\',\'先学会倾听，再开口表达。\',\'把今天的一份好意留给身边的人。\',\'谢谢你，就是很轻又有力的一句话。\',\'你对世界的善意，会在某个转角遇见你。\',\n'
    '      /* === 记录 / 反思 === */\n'
    '      \'认真记录的人，不会被生活遗忘。\',\'人要在事上磨，心要在静处养。\',\'随手记下来，比灵感记得更久。\',\'写出来，会替你把心腾空。\',\'回头看，你会发现那时的自己比你想象的强大。\',\'今天写下的字，明天会替你感谢。\',\'记下来，是给明天的自己留一句话。\',\'记一笔账，三分钟；给明天的你，三十分钟礼物。\',\'回头翻一翻，比刷手机更疗愈。\',\'今天的观察，会变成以后的判断。\'\n'
    '    ];\n'
    '    /* v58：来源比例 → 20% 内置、40% 经验摘录素材抽句、40% 联网搜（用用户已设好的 AI base/model/key，通常是千问 / deepseek 都行） */\n'
    '    const roll = Math.random();\n'
    '    let out = \'\';\n'
    '    if(roll < 0.2){\n'
    '      out = pickFrom(builtin);\n'
    '    } else if(roll < 0.6){\n'
    '      const noteCat = Store.get(\'home_quote_note_cat\', Notes.cats()[0] || \'\');\n'
    '      if(noteCat){\n'
    '        const pool = Notes.list().filter(x => (x.cat||\'\') === noteCat);\n'
    '        const pick = pool.length ? pool[Math.floor(Math.random()*pool.length)] : null;\n'
    '        if(pick){\n'
    '          /* 摘录的"素材句"：取第一句（剥掉 [img:..]），<=60 字 */\n'
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
)
assert_once('Home.quote builtin old', html, quote_builtin_old, 1)
html = html.replace(quote_builtin_old, quote_builtin_new)
print('[E1] Home.quote 内置 100 条 + 比例 20/40/40')

# ============================================================
# F) 升版本号 v58
# ============================================================
ver_old = "const BUILD_VERSION = '2026-08-14-v57';"
ver_new = "const BUILD_VERSION = '2026-08-14-v58';"
assert_once('BUILD_VERSION old', html, ver_old, 1)
html = html.replace(ver_old, ver_new)
print('[F1] BUILD_VERSION -> v58')

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print('\\n=== v58 patch done ===')
