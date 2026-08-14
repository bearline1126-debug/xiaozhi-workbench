#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v59 补丁脚本 - 精确字符串替换，每处断言命中次数。

变更：
A. 菜篮子重构（Cooking）
   A1: 菜篮子头部的「+ 再来一道」按钮删除（移到卡片上）
   A2: CSS：旧 .dish-basket-card-item 横向布局 → 替换为 .dish-grid 3列网格 + .dish-card 卡片样式
   A3: Cooking.render 模板：横向卡片 → 网格卡片（图封面 + 名称 + 再来一道按钮 + 长按拖动）
   A4: 新增 Cooking.openDetail(id) 全屏查看详情 / Cooking.duplicate(id) 「再来一道」复制到表单
B. 经验摘录大分类卡片去大图（Notes）
   B1: Notes.render 大分类卡片删除顶部 nc-thumb 图片（移除 latestImgIds/latestImg 计算）
   B2: Notes._paintCatThumbs 删除（不再需要）
   B3: CSS .note-cat-card .nc-thumb 删除
C. 经验摘录全屏编辑去框去计数（Notes）
   C1: Notes.openDetail 删除 <div class="note-edit-foot"> 与「已插入 N 张图」span
   C2: Notes.openDetail 删除计数更新代码（input/初始化）
   C3: CSS textarea 边/背景去掉 + .note-edit-foot 删
D. 版本号 BUILD_VERSION + sw.js CACHE/BUILD 升到 v59
"""
import io
import sys
import re

PATH = r'C:\Users\cheng\WorkBuddy\2026-08-12-17-28-08\repo\index.html'
SW_PATH = r'C:\Users\cheng\WorkBuddy\2026-08-12-17-28-08\repo\sw.js'

def read(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()

def write(p, s):
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write(s)

def patch_once(content, old, new, label):
    """精确替换，断言命中 1 次。返回新内容。"""
    n = content.count(old)
    if n != 1:
        print(f'❌ [{label}] 命中 {n} 次（期望 1）— abort', file=sys.stderr)
        sys.exit(2)
    return content.replace(old, new, 1)

def main():
    h = read(PATH)

    # ========== A1: 删除菜篮子头部的「+ 再来一道」按钮 ==========
    A1_OLD = '<button class="btn ghost small" id="dishAddOneBtn" onclick="Cooking.addOne()" title="清空表单，开始录入下一道菜">+ 再来一道</button>'
    A1_NEW = ''  # 完全删除（不再需要，按钮移到每张卡片上）
    h = patch_once(h, A1_OLD, A1_NEW, 'A1 remove header 再来一道 button')

    # ========== A2: CSS 替换 .dish-basket-card-item 横向布局 → 新网格样式 ==========
    A2_OLD = """.dish-basket-card-item{flex-direction:row;align-items:center;padding:10px 12px;gap:10px}
.dish-basket-card-item .grow{flex:1;min-width:0;text-align:left;order:1}
.dish-basket-card-item .title{font-size:14px;font-weight:700;line-height:1.35;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dish-basket-card-item .dish-meta{font-size:11px;color:var(--text-dim);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dish-basket-card-item .dish-steps{font-size:11px;color:var(--text);line-height:1.5;margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;word-break:break-word}
.dish-basket-card-item .thumb{width:54px;height:54px;object-fit:cover;border-radius:8px;flex:none;order:2;margin:0;background:#e6e2cc}
.dish-basket-card-item .dish-actions{display:flex;flex-direction:column;align-items:center;gap:2px;flex:none;order:3}
.dish-basket-card-item .dish-actions button{font-size:15px;padding:4px 6px;line-height:1;min-height:28px}"""
    A2_NEW = """.dish-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:4px 2px}
.dish-card{position:relative;aspect-ratio:1/1;border-radius:12px;overflow:hidden;cursor:pointer;background:#e6e2cc;box-shadow:0 2px 6px rgba(38,54,40,.08);transition:transform .15s ease}
.dish-card:active{transform:scale(.97)}
.dish-card .dc-cover{width:100%;height:100%;object-fit:cover;display:block}
.dish-card .dc-placeholder{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:700;color:rgba(255,255,255,.85);background:linear-gradient(135deg,#86b667,#5a8a4a)}
.dish-card .dc-name{position:absolute;left:0;right:0;bottom:0;padding:6px 8px;font-size:12px;font-weight:600;color:#fff;background:linear-gradient(transparent,rgba(0,0,0,.62));line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;word-break:break-word}
.dish-card .dc-addone{position:absolute;top:4px;right:4px;width:28px;height:28px;border-radius:50%;border:0;background:rgba(255,255,255,.92);color:var(--accent);font-size:18px;font-weight:700;line-height:1;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.18);display:flex;align-items:center;justify-content:center;padding:0}
.dish-card .dc-addone:active{background:var(--accent);color:#fff}
.dish-detail{padding:0}
.dish-detail .dd-hero{width:100%;max-height:50vh;object-fit:cover;display:block;background:#e6e2cc}
.dish-detail .dd-noimg{width:100%;height:120px;background:linear-gradient(135deg,#86b667,#5a8a4a);display:flex;align-items:center;justify-content:center;font-size:48px;color:rgba(255,255,255,.85)}
.dish-detail .dd-body{padding:14px 16px}
.dish-detail .dd-name{font-size:18px;font-weight:700;margin-bottom:6px;color:var(--text);line-height:1.35}
.dish-detail .dd-tags{font-size:12px;color:var(--accent);margin-bottom:12px}
.dish-detail .dd-steps{font-size:14px;line-height:1.7;color:var(--text);white-space:pre-wrap;word-break:break-word;margin-bottom:16px}
.dish-detail .dd-actions{display:flex;gap:8px;padding-top:8px;border-top:1px dashed var(--line)}
.dish-detail .dd-actions .btn{flex:1}"""
    h = patch_once(h, A2_OLD, A2_NEW, 'A2 CSS dish-basket-card-item → grid+card')

    # ========== A3+A4: Cooking.render 模板 + 新增 openDetail/duplicate 函数 ==========
    # 替换整段 render 函数体内的 recipeHtml 模板（旧模板）→ 新网格模板
    A3_OLD = """    const recipeHtml = Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="list">${rows.map((x)=>{ const i=dishRecipes.findIndex(y=>y.id===x.id); return `<div class="item dish-basket-card-item${x._open?' open':''}" draggable="true" data-sort-id="${x.id}"><div class="grow"><div class="title">${Util.esc(x.name)}</div>${x.tags?`<div class="dish-meta">${Util.esc(x.tags)}</div>`:''}<div class="dish-steps">${Util.esc(x.steps||'')}</div></div>${x.photoId?Util.mediaImg(x.photoId):(x.photo?`<img class="thumb" src="${Util.esc(x.photo)}" alt="">`:'')}<div class="dish-actions"><button class="ui-fs-icon-btn" type="button" onclick="Cooking.edit('${x.id}')" title="编辑这道菜">✎</button><button class="ui-fs-icon-btn" type="button" onclick="Cooking.del('${x.id}')" title="删除">✕</button></div></div>`; }).join('')}</div></section>`).join(''):'';"""
    A3_NEW = """    /* v59：3列网格卡片，外层只显示图片封面 + 菜名，点 → 全屏看详情；每张卡片右上 + 按钮 = 再来一道（复制到表单）。长按拖动排序保留。 */
    const recipeHtml = Object.entries(groups).length?Object.entries(groups).map(([tag,rows])=>`<section style="margin-bottom:12px"><h2>${Util.esc(tag)}</h2><div class="dish-grid">${rows.map((x)=>{ const cover = x.photoId ? Util.mediaImg(x.photoId, x.name) : (x.photo ? `<img class="dc-cover" src="${Util.esc(x.photo)}" alt="${Util.esc(x.name)}">` : `<div class="dc-placeholder">${Util.esc((x.name||'?')[0])}</div>`); return `<div class="dish-card" draggable="true" data-sort-id="${x.id}" onclick="Cooking.openDetail('${x.id}')">${cover}<div class="dc-name">${Util.esc(x.name)}</div><button class="dc-addone" type="button" onclick="event.stopPropagation();Cooking.duplicate('${x.id}')" title="再来一道：复制这道菜到表单开始录入新菜">+</button></div>`; }).join('')}</div></section>`).join(''):'';"""
    h = patch_once(h, A3_OLD, A3_NEW, 'A3 Cooking.render cards → grid template')

    # 新增 Cooking.openDetail + Cooking.duplicate 在 Cooking.render 后面
    A4_ANCHOR_OLD = """    DragSort.bind('#dishList [data-sort-id]','dishes',()=>Cooking.render());
    /* v58：菜篮子图片渲染完异步 fill src（Util.mediaImg 是占位 img，靠 Media.paint 补） */
    Media.paint(dishListEl);
    this.paintWheelList();
  },"""
    A4_ANCHOR_NEW = """    DragSort.bind('#dishList [data-sort-id]','dishes',()=>Cooking.render());
    /* v58：菜篮子图片渲染完异步 fill src（Util.mediaImg 是占位 img，靠 Media.paint 补） */
    Media.paint(dishListEl);
    this.paintWheelList();
  },
  /* v59：点击网格卡片 → 全屏看详情（菜名 / 标签 / 步骤 / 图 / 编辑 / 删除） */
  openDetail(id){
    const it = this.list().find(x=>x.id===id); if(!it) return;
    const hero = it.photoId ? Util.mediaImg(it.photoId, it.name) : (it.photo ? `<img class="dd-hero" src="${Util.esc(it.photo)}" alt="${Util.esc(it.name)}">` : '<div class="dd-noimg">🍽</div>');
    const html = `
      <div class="dish-detail">
        ${hero}
        <div class="dd-body">
          <div class="dd-name">${Util.esc(it.name)}</div>
          ${it.tags?`<div class="dd-tags">🏷 ${Util.esc(it.tags)}</div>`:''}
          <div class="dd-steps">${it.steps ? Util.esc(it.steps) : '<span style="color:var(--text-dim)">（还没写做法）</span>'}</div>
          <div class="dd-actions">
            <button class="btn" onclick="Cooking.duplicate('${it.id}');UI.closeFull(true);">+ 再来一道</button>
            <button class="btn ghost" onclick="Cooking.edit('${it.id}');UI.closeFull(true);">✎ 编辑</button>
            <button class="btn ghost" style="color:var(--warn)" onclick="UI.closeFull(true);setTimeout(()=>Cooking.del('${it.id}'),120);">✕ 删除</button>
          </div>
        </div>
      </div>`;
    UI.openFull('🍽 '+it.name, html, '← 返回菜篮子');
    /* 全屏图异步 paint（非 mediaId 时 img 立即显示；mediaId 时靠 Media.paint 补 src） */
    setTimeout(()=>Media.paint(document.getElementById('uiFullBody')), 30);
  },
  /* v59：「再来一道」按钮（卡片上 / 详情视图上）：复制这道菜的名字/标签/步骤到表单，作为新菜录入（不复制图） */
  duplicate(id){
    const it = this.list().find(x=>x.id===id); if(!it) return;
    /* 取消编辑态 → 保存时会插入新菜 */
    Store.remove('dish_editing');
    if(typeof dishName !== 'undefined' && dishName) dishName.value = it.name || '';
    if(typeof dishTags !== 'undefined' && dishTags) dishTags.value = it.tags || '';
    if(typeof dishSteps !== 'undefined' && dishSteps) dishSteps.value = it.steps || '';
    if(typeof dishPhoto !== 'undefined' && dishPhoto) dishPhoto.value = '';
    this.render();
    (document.getElementById('page-cooking')||document.body)?.scrollIntoView?.({behavior:'smooth', block:'start'});
    setTimeout(()=>{ try{ document.getElementById('dishName')?.focus(); }catch(e){} }, 220);
    /* 如果在别的页面，回到做菜栏 */
    try{ if(typeof App !== 'undefined' && App.go) App.go('cooking'); }catch(e){}
    UI.toast('已预填：'+(it.name||'这道菜')+'；改完点「保存菜谱」即可');
  },"""
    h = patch_once(h, A4_ANCHOR_OLD, A4_ANCHOR_NEW, 'A4 add openDetail+duplicate')

    # ========== B1: Notes.render 删除大图 (latestImgIds/latestImg) ==========
    B1_OLD = """      const latest = items[0];
      /* v58：缩略图：最新一条的第一张图（去掉 [img:..] 后看首个内嵌图） */
      const latestImgIds = latest ? this._mediaInText(latest.text) : [];
      const latestImg = latestImgIds[0] ? Util.mediaImg(latestImgIds[0]) : '';
      const preview = latest ? (this._stripMedia(latest.text || '') || latest.title || '（空）').slice(0,140) : '';
      const count = items.length;
      const isEmpty = !latest;
      const date = latest ? (latest.date || '') : '';
      return `<div class="note-cat-card${isEmpty?' note-cat-empty':''}" onclick="Notes.openCat('${Util.esc(cat)}')">
        ${latestImg ? `<div class="nc-thumb">${latestImg}</div>` : ''}
        <div class="nc-head"><span class="nc-title">📁 ${Util.esc(cat)}</span><span class="nc-count">${count}</span></div>"""
    B1_NEW = """      const latest = items[0];
      /* v59：去掉分类卡片顶部大图（小卡片本身已经显示图，外层不再重复） */
      const preview = latest ? (this._stripMedia(latest.text || '') || latest.title || '（空）').slice(0,140) : '';
      const count = items.length;
      const isEmpty = !latest;
      const date = latest ? (latest.date || '') : '';
      return `<div class="note-cat-card${isEmpty?' note-cat-empty':''}" onclick="Notes.openCat('${Util.esc(cat)}')">
        <div class="nc-head"><span class="nc-title">📁 ${Util.esc(cat)}</span><span class="nc-count">${count}</span></div>"""
    h = patch_once(h, B1_OLD, B1_NEW, 'B1 Notes.render cat card remove big image')

    # ========== B2: Notes.render 删除 _paintCatThumbs 调用 ==========
    B2_OLD = """    /* v58：异步把大分类卡片里的图缩略图 fill 上（img 用 Media.paint 补 src） */
    setTimeout(()=>Notes._paintCatThumbs(), 30);"""
    B2_NEW = """    /* v59：分类卡片已无大图，无需 _paintCatThumbs */"""
    h = patch_once(h, B2_OLD, B2_NEW, 'B2 remove first _paintCatThumbs call')

    B2B_OLD = """    noteList.innerHTML = `<div class="note-cat-grid">${cards}${allCard}</div>`;
    /* v58：异步填充大分类卡片的图片缩略图（img 用 Media.paint） */
    setTimeout(()=>Notes._paintCatThumbs(), 0);
  },"""
    B2B_NEW = """    noteList.innerHTML = `<div class="note-cat-grid">${cards}${allCard}</div>`;
  },"""
    h = patch_once(h, B2B_OLD, B2B_NEW, 'B2 remove second _paintCatThumbs call')

    B2C_OLD = """  /* 把 [img:...] 占位符剥掉，用于纯文本预览 */
  _stripMedia(text){ return String(text||'').replace(/\[img:m_[a-zA-Z0-9_]+\]/g, '').trim(); },
  /* v58：把大分类卡片里的 [data-media] 占位 img 异步填充 src */
  _paintCatThumbs(){ Media.paint(document.getElementById('noteList')); },
  /* v54：mini-card 小预览（用在分类详情全屏 和 搜索结果）；v56：右上角删除键默认隐藏，长按卡片浮出 */"""
    B2C_NEW = """  /* 把 [img:...] 占位符剥掉，用于纯文本预览 */
  _stripMedia(text){ return String(text||'').replace(/\[img:m_[a-zA-Z0-9_]+\]/g, '').trim(); },
  /* v54：mini-card 小预览（用在分类详情全屏 和 搜索结果）；v56：右上角删除键默认隐藏，长按卡片浮出 */"""
    h = patch_once(h, B2C_OLD, B2C_NEW, 'B2 remove _paintCatThumbs function')

    # ========== B3: CSS 删除 .note-cat-card .nc-thumb 规则 ==========
    B3_OLD = """.note-cat-card .nc-thumb{width:100%;height:96px;overflow:hidden;border-radius:10px;margin-bottom:4px;background:#e6e2cc}
.note-cat-card .nc-thumb img.note-inline-img,.note-cat-card .nc-thumb img{width:100%;height:100%;object-fit:cover;display:block;border-radius:10px;margin:0;max-width:none;max-height:none}
"""
    B3_NEW = """"""
    h = patch_once(h, B3_OLD, B3_NEW, 'B3 remove .nc-thumb CSS')

    # ========== C1: Notes.openDetail 删除 <div class="note-edit-foot"> ==========
    C1_OLD = """    UI.openFull('', `
      <textarea id="noteEditPure" placeholder="写下你的经验、原则、观察..."></textarea>
      <div class="note-edit-foot"><span class="hint" id="noteEditPureCount"></span></div>
      <input type="file" id="noteEditPureFile" accept="image/*" multiple style="display:none" onchange="Notes.insertImages(this,'noteEditPure');Notes._autoSaveEdit()">
    `, '← 返回', null, rightBtn, /*hideTitle*/true);"""
    C1_NEW = """    /* v59：去掉文本框下面的「已插入 N 张图」提示，整屏只有 textarea + 隐藏文件输入 */
    UI.openFull('', `
      <textarea id="noteEditPure" placeholder="写下你的经验、原则、观察..."></textarea>
      <input type="file" id="noteEditPureFile" accept="image/*" multiple style="display:none" onchange="Notes.insertImages(this,'noteEditPure');Notes._autoSaveEdit()">
    `, '← 返回', null, rightBtn, /*hideTitle*/true);"""
    h = patch_once(h, C1_OLD, C1_NEW, 'C1 remove note-edit-foot div')

    # ========== C2: Notes.openDetail 删除 input 监听器里的计数更新代码 ==========
    C2_OLD = """    ta.addEventListener('input', ()=>{
      clearTimeout(timer);
      timer = setTimeout(()=>Notes._autoSaveEdit(), 600);
      const ids = (ta.value.match(/\[img:m_[a-zA-Z0-9_]+\]/g) || []).length;
      const cs = document.getElementById('noteEditPureCount');
      if(cs) cs.textContent = ids?('已插入 '+ids+' 张图'):'';
    });"""
    C2_NEW = """    ta.addEventListener('input', ()=>{
      clearTimeout(timer);
      timer = setTimeout(()=>Notes._autoSaveEdit(), 600);
    });"""
    h = patch_once(h, C2_OLD, C2_NEW, 'C2 remove counter update in input listener')

    # 初始化计数也删除
    C2B_OLD = """    /* 初始化计数 */
    const ids = (ta.value.match(/\[img:m_[a-zA-Z0-9_]+\]/g) || []).length;
    const cs = document.getElementById('noteEditPureCount'); if(cs) cs.textContent = ids?('已插入 '+ids+' 张图'):'';
    setTimeout(()=>ta.focus(), 60);"""
    C2B_NEW = """    setTimeout(()=>ta.focus(), 60);"""
    h = patch_once(h, C2B_OLD, C2B_NEW, 'C2 remove init counter')

    # ========== C3: CSS 调整：textarea 真的占满全屏无边无背景 + 删除 .note-edit-foot ==========
    C3_OLD = """/* v57：纯编辑全屏（openDetail）样式 —— textarea 占满高度，右下角 🖼 浮动圆形钮 */
/* v58：openDetail 详情纯编辑全屏 —— 整个全屏就是一个无边、无背景的 textarea，
   顶端右侧 🖼 按钮是从 UI.openFull 的 rightHtml 参数透传注入的；
   下面小灰字写「已插入 N 张图」是 note-edit-foot 的 hint。 */
.note-edit-pure{display:flex;flex-direction:column;height:100%;padding:0;margin:0}
.note-edit-pure textarea{flex:1;width:100%;border:0;outline:none;background:transparent;font-size:15px;line-height:1.7;padding:14px 16px;resize:none;font-family:inherit;color:var(--text);min-height:0}
.note-edit-pure textarea::placeholder{color:var(--text-dim)}
.note-edit-foot{padding:6px 16px 12px;font-size:11px;color:var(--text-dim);text-align:right}"""
    C3_NEW = """/* v59：openDetail 详情纯编辑全屏 —— 整个全屏就是一个无边、无背景的 textarea。
   之前的 .note-edit-pure wrapper 因为 HTML 没真的用上，所以 textarea 没被覆盖到全局边框/背景。
   现在直接用 ID 选择器 + !important 抵掉全局 input/textarea/select 默认边背景。
   用 :has() 让 ui-fs-body 在只含 textarea 时去掉 padding，textarea 真正占满全屏。 */
#noteEditPure{flex:1;width:100%;height:100%;border:0 !important;outline:none;background:transparent !important;font-size:15px;line-height:1.7;padding:14px 16px;resize:none;font-family:inherit;color:var(--text);min-height:0;box-sizing:border-box;display:block}
#noteEditPure::placeholder{color:var(--text-dim)}
.ui-fs-body:has(>#noteEditPure){padding:0;display:flex;flex-direction:column}"""
    h = patch_once(h, C3_OLD, C3_NEW, 'C3 CSS textarea no border/box')

    # ========== D: BUILD_VERSION 升到 v59 ==========
    D_OLD = "const BUILD_VERSION = '2026-08-14-v58';"
    D_NEW = "const BUILD_VERSION = '2026-08-14-v59';"
    h = patch_once(h, D_OLD, D_NEW, 'D BUILD_VERSION → v59')

    write(PATH, h)
    print('✅ index.html 已写入（v59）')

    # sw.js 升级
    sw = read(SW_PATH)
    sw = patch_once(sw, "const CACHE = 'xiaozhi-workbench-v58';", "const CACHE = 'xiaozhi-workbench-v59';", 'sw CACHE → v59')
    sw = patch_once(sw, "const BUILD = '2026-08-14-v58';", "const BUILD = '2026-08-14-v59';", 'sw BUILD → v59')
    write(SW_PATH, sw)
    print('✅ sw.js 已写入（v59）')

if __name__ == '__main__':
    main()
